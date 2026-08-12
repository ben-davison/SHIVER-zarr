import xarray as xr
import numpy as np
import dask.array as da
import glob
import os
import sys
import zarr
import rioxarray
import pickle
import json
from datetime import datetime
import re

# --- HELPERS ---
def get_highest_version_files(base_dir, region_wildcard, file_wildcard):
    """Finds all region directories, picks the highest v1.* folder, and returns the target files."""
    files = []
    region_dirs = glob.glob(os.path.join(base_dir, region_wildcard))
    for rdir in region_dirs:
        v_dirs = sorted(glob.glob(os.path.join(rdir, "v*")))
        if not v_dirs: continue
        highest_v_dir = v_dirs[-1] # Grabs the last one (e.g., v1.2 instead of v1.1)
        files.extend(glob.glob(os.path.join(highest_v_dir, file_wildcard)))
    return files

def write_ome_metadata(zarr_path, max_level, master_x, master_y):
    """Writes standard OME-NGFF v0.4 multiscales metadata to the root .zattrs file."""
    dx = float(abs(master_x[1].values - master_x[0].values))
    dy = float(abs(master_y[1].values - master_y[0].values))
    
    datasets = []
    # Dynamically generate metadata for however many levels the while-loop created
    for lvl in range(max_level + 1):
        factor = 2 ** lvl  # 1, 2, 4, 8, 16...
        datasets.append({
            "path": str(lvl),
            "coordinateTransformations": [
                {
                    "type": "scale",
                    "scale": [1.0, dy * factor, dx * factor] # [time, y, x] absolute spacing
                }
            ]
        })
        
    multiscales_metadata = {
        "multiscales": [
            {
                "version": "0.4",
                "name": "greenland_multisource_velocity",
                "axes": [
                    {"name": "time", "type": "time"},
                    {"name": "y", "type": "space", "unit": "meter"},
                    {"name": "x", "type": "space", "unit": "meter"}
                ],
                "datasets": datasets,
                "type": "gaussian",
                "metadata": {
                    "description": "Multisource Greenland ice surface velocity pyramid/multiscale store"
                }
            }
        ]
    }
    
    os.makedirs(zarr_path, exist_ok=True)
    zattrs_path = os.path.join(zarr_path, ".zattrs")
    existing_attrs = {}
    if os.path.exists(zattrs_path):
        try:
            with open(zattrs_path, 'r') as f:
                existing_attrs = json.load(f)
        except:
            pass
            
    existing_attrs.update(multiscales_metadata)
    with open(zattrs_path, 'w') as f:
        json.dump(existing_attrs, f, indent=2)


# --- 1. PROMICE Processing ---
def preprocess_promice(file_path):
    """Opens, formats, and converts units for a single PROMICE NetCDF file."""
    ds = xr.open_dataset(file_path, decode_times=True)
    
    # 1. Keep relevant variables
    vars_to_keep = [
        'land_ice_surface_velocity_magnitude',
        'land_ice_surface_velocity_magnitude_std',
        'land_ice_surface_easting_velocity',
        'land_ice_surface_northing_velocity',
        'land_ice_surface_easting_velocity_std',
        'land_ice_surface_northing_velocity_std',
        'crs',
        'time_bnds'
    ]
    ds = ds[vars_to_keep]
    
    # 2. Rename to match our schema
    ds = ds.rename({
        'land_ice_surface_velocity_magnitude': 'speed',
        'land_ice_surface_velocity_magnitude_std': 'speed_error',
        'land_ice_surface_easting_velocity': 'vx',
        'land_ice_surface_northing_velocity': 'vy',
        'land_ice_surface_easting_velocity_std': 'vx_error',
        'land_ice_surface_northing_velocity_std': 'vy_error',
        'crs': 'spatial_ref'
    })
    
    # 3. Process all velocity/error variables (convert m/day to m/year, round to 1 decimal place, set attributes)
    vel_vars = ['speed', 'speed_error', 'vx', 'vy', 'vx_error', 'vy_error']
    for var in vel_vars:
        ds[var] = np.round(ds[var] * 365.25, 1)
        ds[var].attrs['units'] = 'm/year'
        ds[var].attrs['grid_mapping'] = 'spatial_ref'
    
    # 4. Add data_source identifier
    ds['data_source'] = xr.DataArray(np.array(["PROMICE"], dtype="<U50"), dims=["time"])
    
    # 5. Fix time bounds dimensions and clean encoding
    if 'time_bnds' in ds and ds['time_bnds'].dims == ('bnds', 'time'):
        ds['time_bnds'] = ds['time_bnds'].transpose('time', 'bnds')
        
    for var in ['time', 'time_bnds']:
        if var in ds:
            ds[var].encoding.clear()
            
    return ds

# 2. MEaSUREs (monthly, quarterly, annual, winter)
def parse_measures_time(filename):
    """Extracts start, end, and midpoint datetimes from a MEaSUREs filename."""
    # Example: GL_vel_mosaic_Monthly_01Dec14_31Dec14_vv_v05.0.tif
    parts = os.path.basename(filename).split('_')
    start_str = parts[4] # e.g., 01Dec14
    end_str = parts[5]   # e.g., 31Dec14
    
    start_dt = datetime.strptime(start_str, "%d%b%y")
    end_dt = datetime.strptime(end_str, "%d%b%y")
    mid_dt = start_dt + (end_dt - start_dt) / 2
    
    return np.datetime64(mid_dt), np.array([np.datetime64(start_dt), np.datetime64(end_dt)])


def preprocess_measures(vv_file, master_x, master_y, source_label):
    """Loads MEaSUREs GeoTIFFs, calculates error, and interpolates to master grid."""
    # 1. Deduce filepaths for all components
    ex_file = vv_file.replace('_vv_', '_ex_')
    ey_file = vv_file.replace('_vv_', '_ey_')
    vx_file = vv_file.replace('_vv_', '_vx_')
    vy_file = vv_file.replace('_vv_', '_vy_')
    
    # Extract times
    time_mid, time_bnds = parse_measures_time(vv_file)
    
    # 2. Load GeoTIFFs (squeeze removes the 'band' dimension)
    vv = rioxarray.open_rasterio(vv_file).squeeze('band', drop=True)
    vx = rioxarray.open_rasterio(vx_file).squeeze('band', drop=True)
    vy = rioxarray.open_rasterio(vy_file).squeeze('band', drop=True)
    ex = rioxarray.open_rasterio(ex_file).squeeze('band', drop=True)
    ey = rioxarray.open_rasterio(ey_file).squeeze('band', drop=True)
    
    # Mask out the -1 no-data values with NaN before interpolating
    vv = vv.where(vv != -1)
    vx = vx.where(vx != -1)
    vy = vy.where(vy != -1)
    ex = ex.where(ex != -1)
    ey = ey.where(ey != -1)
    
    # 3. Interpolate to PROMICE (master) grid
    vv_interp = vv.interp(x=master_x, y=master_y, method="nearest")
    vx_interp = vx.interp(x=master_x, y=master_y, method="nearest")
    vy_interp = vy.interp(x=master_x, y=master_y, method="nearest")
    ex_interp = ex.interp(x=master_x, y=master_y, method="nearest")
    ey_interp = ey.interp(x=master_x, y=master_y, method="nearest")
    
    # Calculate hypotenuse for speed error
    err_interp = np.sqrt(ex_interp**2 + ey_interp**2)
    
    # 4. Extract values and round to 1 decimal place
    speed_vals = np.round(vv_interp.values, 1)
    vx_vals = np.round(vx_interp.values, 1)
    vy_vals = np.round(vy_interp.values, 1)
    
    speed_error_vals = np.round(err_interp.values, 1)
    vx_error_vals = np.round(ex_interp.values, 1)
    vy_error_vals = np.round(ey_interp.values, 1)
    
    # 5. Assemble into standard Dataset format
    ds = xr.Dataset({
        'speed': (['time', 'y', 'x'], np.expand_dims(speed_vals, axis=0), {'units': 'm/year', 'grid_mapping': 'spatial_ref'}),
        'vx': (['time', 'y', 'x'], np.expand_dims(vx_vals, axis=0), {'units': 'm/year', 'grid_mapping': 'spatial_ref'}),
        'vy': (['time', 'y', 'x'], np.expand_dims(vy_vals, axis=0), {'units': 'm/year', 'grid_mapping': 'spatial_ref'}),
        'speed_error': (['time', 'y', 'x'], np.expand_dims(speed_error_vals, axis=0), {'units': 'm/year', 'grid_mapping': 'spatial_ref'}),
        'vx_error': (['time', 'y', 'x'], np.expand_dims(vx_error_vals, axis=0), {'units': 'm/year', 'grid_mapping': 'spatial_ref'}),
        'vy_error': (['time', 'y', 'x'], np.expand_dims(vy_error_vals, axis=0), {'units': 'm/year', 'grid_mapping': 'spatial_ref'}),
        'data_source': (['time'], np.array([source_label], dtype="<U50"))
    }, coords={
        'time': (['time'], [time_mid]),
        'time_bnds': (['time', 'bnds'], [time_bnds]),
        'y': (['y'], master_y.values),
        'x': (['x'], master_x.values),
    })
    
    return ds


# --- 3. Mouginot Processing ---
def parse_mouginot_time(filename):
    # Example: vel_2010-07-01_2011-06-31.nc
    base = os.path.basename(filename).replace('vel_', '').replace('.nc', '')
    start_str, end_str = base.split('_')
    
    # Fix the impossible June 31st date trap
    if end_str.endswith('-06-31'):
        end_str = end_str.replace('-06-31', '-06-30')
        
    start_dt = datetime.strptime(start_str, "%Y-%m-%d")
    end_dt = datetime.strptime(end_str, "%Y-%m-%d")
    mid_dt = start_dt + (end_dt - start_dt) / 2
    return np.datetime64(mid_dt), np.array([np.datetime64(start_dt), np.datetime64(end_dt)])

def preprocess_mouginot(file_path, master_x, master_y):
    time_mid, time_bnds = parse_mouginot_time(file_path)
    
    ds_raw = xr.open_dataset(file_path)
    
    # 1. Replace FillValues (0) with NaN so they don't corrupt the interpolation
    vx_raw = ds_raw['VX'].where(ds_raw['VX'] != 0)
    vy_raw = ds_raw['VY'].where(ds_raw['VY'] != 0)
    
    # Calculate speed
    speed_raw = np.sqrt(vx_raw**2 + vy_raw**2)
    
    # 2. Calculate errors (5% of the absolute value)
    speed_error_raw = speed_raw * 0.05
    vx_error_raw = np.abs(vx_raw) * 0.05
    vy_error_raw = np.abs(vy_raw) * 0.05
    
    # 3. Interpolate to master grid
    speed_interp = speed_raw.interp(x=master_x, y=master_y, method="nearest")
    vx_interp = vx_raw.interp(x=master_x, y=master_y, method="nearest")
    vy_interp = vy_raw.interp(x=master_x, y=master_y, method="nearest")
    
    speed_error_interp = speed_error_raw.interp(x=master_x, y=master_y, method="nearest")
    vx_error_interp = vx_error_raw.interp(x=master_x, y=master_y, method="nearest")
    vy_error_interp = vy_error_raw.interp(x=master_x, y=master_y, method="nearest")
    
    # 4. Extract values, transpose to match y,x dims, and round to 1 decimal place
    speed_vals = np.round(speed_interp.transpose('y', 'x').values, 1)
    vx_vals = np.round(vx_interp.transpose('y', 'x').values, 1)
    vy_vals = np.round(vy_interp.transpose('y', 'x').values, 1)
    
    speed_error_vals = np.round(speed_error_interp.transpose('y', 'x').values, 1)
    vx_error_vals = np.round(vx_error_interp.transpose('y', 'x').values, 1)
    vy_error_vals = np.round(vy_error_interp.transpose('y', 'x').values, 1)
    
    # 5. Construct final dataset with consistent schema
    ds = xr.Dataset({
        'speed': (['time', 'y', 'x'], np.expand_dims(speed_vals, axis=0), {'units': 'm/year', 'grid_mapping': 'spatial_ref'}),
        'vx': (['time', 'y', 'x'], np.expand_dims(vx_vals, axis=0), {'units': 'm/year', 'grid_mapping': 'spatial_ref'}),
        'vy': (['time', 'y', 'x'], np.expand_dims(vy_vals, axis=0), {'units': 'm/year', 'grid_mapping': 'spatial_ref'}),
        'speed_error': (['time', 'y', 'x'], np.expand_dims(speed_error_vals, axis=0), {'units': 'm/year', 'grid_mapping': 'spatial_ref'}),
        'vx_error': (['time', 'y', 'x'], np.expand_dims(vx_error_vals, axis=0), {'units': 'm/year', 'grid_mapping': 'spatial_ref'}),
        'vy_error': (['time', 'y', 'x'], np.expand_dims(vy_error_vals, axis=0), {'units': 'm/year', 'grid_mapping': 'spatial_ref'}),
        'data_source': (['time'], np.array(["Mouginot_annual"], dtype="<U50"))
    }, coords={
        'time': (['time'], [time_mid]), 'time_bnds': (['time', 'bnds'], [time_bnds]),
        'y': (['y'], master_y.values), 'x': (['x'], master_x.values),
    })
    
    return ds


# --- 4. ITS_LIVE Processing ---
def parse_itslive_time(filename):
    # Example: ITS_LIVE_velocity_120m_RGI05A_1986_V02.1.nc
    year_str = os.path.basename(filename).split('_')[5]
    start_dt = datetime(int(year_str), 1, 1)
    end_dt = datetime(int(year_str), 12, 31)
    mid_dt = start_dt + (end_dt - start_dt) / 2
    return np.datetime64(mid_dt), np.array([np.datetime64(start_dt), np.datetime64(end_dt)])

def preprocess_itslive(file_path, master_x, master_y):
    time_mid, time_bnds = parse_itslive_time(file_path)
    ds_raw = xr.open_dataset(file_path)
    
    # Mask out the respective fill values
    v = ds_raw['v'].where(ds_raw['v'] != -32767)
    vx = ds_raw['vx'].where(ds_raw['vx'] != -32767)
    vy = ds_raw['vy'].where(ds_raw['vy'] != -32767)
    v_error = ds_raw['v_error'].where(ds_raw['v_error'] != 32767)
    vx_error = ds_raw['vx_error'].where(ds_raw['vx_error'] != 32767)
    vy_error = ds_raw['vy_error'].where(ds_raw['vy_error'] != 32767)
    
    # Interpolate to master grid
    speed_interp = v.interp(x=master_x, y=master_y, method="nearest")
    vx_interp = vx.interp(x=master_x, y=master_y, method="nearest")
    vy_interp = vy.interp(x=master_x, y=master_y, method="nearest")
    speed_error_interp = v_error.interp(x=master_x, y=master_y, method="nearest")
    vx_error_interp = vx_error.interp(x=master_x, y=master_y, method="nearest")
    vy_error_interp = vy_error.interp(x=master_x, y=master_y, method="nearest")
    
    # Ensure dimensions are ordered correctly (y, x) before expanding to 3D
    speed_vals = np.round(speed_interp.transpose('y', 'x').values, 1)
    vx_vals = np.round(vx_interp.transpose('y', 'x').values, 1)
    vy_vals = np.round(vy_interp.transpose('y', 'x').values, 1)
    speed_error_vals = np.round(speed_error_interp.transpose('y', 'x').values, 1)
    vx_error_vals = np.round(vx_error_interp.transpose('y', 'x').values, 1)
    vy_error_vals = np.round(vy_error_interp.transpose('y', 'x').values, 1)
    
    ds = xr.Dataset({
        'speed': (['time', 'y', 'x'], np.expand_dims(speed_vals, axis=0), {'units': 'm/year', 'grid_mapping': 'spatial_ref'}),
        'vx': (['time', 'y', 'x'], np.expand_dims(vx_vals, axis=0), {'units': 'm/year', 'grid_mapping': 'spatial_ref'}),
        'vy': (['time', 'y', 'x'], np.expand_dims(vy_vals, axis=0), {'units': 'm/year', 'grid_mapping': 'spatial_ref'}),
        'speed_error': (['time', 'y', 'x'], np.expand_dims(speed_error_vals, axis=0), {'units': 'm/year', 'grid_mapping': 'spatial_ref'}),
        'vx_error': (['time', 'y', 'x'], np.expand_dims(vx_error_vals, axis=0), {'units': 'm/year', 'grid_mapping': 'spatial_ref'}),
        'vy_error': (['time', 'y', 'x'], np.expand_dims(vy_error_vals, axis=0), {'units': 'm/year', 'grid_mapping': 'spatial_ref'}),
        'data_source': (['time'], np.array(["ITS_LIVE_annual"], dtype="<U50"))
    }, coords={
        'time': (['time'], [time_mid]), 'time_bnds': (['time', 'bnds'], [time_bnds]),
        'y': (['y'], master_y.values), 'x': (['x'], master_x.values),
    })
    return ds


# --- 5. ESA CCI Sentinel-1 Processing ---
def preprocess_esacci_s1(file_path, target_idx, master_x, master_y):
    # Using .isel() fixes duplicate time bugs safely
    ds_raw = xr.open_dataset(file_path, decode_times=True)
    ds_slice = ds_raw.isel(time=target_idx) 
    
    # 1. Extract variables and convert to m/year
    vx_raw = ds_slice['land_ice_surface_east_velocity'] * 365.25
    vy_raw = ds_slice['land_ice_surface_north_velocity'] * 365.25
    
    # Calculate speed
    speed_raw = np.sqrt(vx_raw**2 + vy_raw**2)
    
    # 2. Calculate errors (5% of the absolute value)
    speed_error_raw = speed_raw * 0.05
    vx_error_raw = np.abs(vx_raw) * 0.05
    vy_error_raw = np.abs(vy_raw) * 0.05
    
    # 3. Interpolate to master grid
    speed_interp = speed_raw.interp(x=master_x, y=master_y, method="nearest")
    vx_interp = vx_raw.interp(x=master_x, y=master_y, method="nearest")
    vy_interp = vy_raw.interp(x=master_x, y=master_y, method="nearest")
    
    speed_error_interp = speed_error_raw.interp(x=master_x, y=master_y, method="nearest")
    vx_error_interp = vx_error_raw.interp(x=master_x, y=master_y, method="nearest")
    vy_error_interp = vy_error_raw.interp(x=master_x, y=master_y, method="nearest")
    
    # 4. Extract values, transpose to match y,x dims, and round to 1 decimal place
    speed_vals = np.round(speed_interp.transpose('y', 'x').values, 1)
    vx_vals = np.round(vx_interp.transpose('y', 'x').values, 1)
    vy_vals = np.round(vy_interp.transpose('y', 'x').values, 1)
    
    speed_error_vals = np.round(speed_error_interp.transpose('y', 'x').values, 1)
    vx_error_vals = np.round(vx_error_interp.transpose('y', 'x').values, 1)
    vy_error_vals = np.round(vy_error_interp.transpose('y', 'x').values, 1)
    
    # 5. Construct final dataset with consistent schema
    ds = xr.Dataset({
        'speed': (['time', 'y', 'x'], np.expand_dims(speed_vals, axis=0), {'units': 'm/year', 'grid_mapping': 'spatial_ref'}),
        'vx': (['time', 'y', 'x'], np.expand_dims(vx_vals, axis=0), {'units': 'm/year', 'grid_mapping': 'spatial_ref'}),
        'vy': (['time', 'y', 'x'], np.expand_dims(vy_vals, axis=0), {'units': 'm/year', 'grid_mapping': 'spatial_ref'}),
        'speed_error': (['time', 'y', 'x'], np.expand_dims(speed_error_vals, axis=0), {'units': 'm/year', 'grid_mapping': 'spatial_ref'}),
        'vx_error': (['time', 'y', 'x'], np.expand_dims(vx_error_vals, axis=0), {'units': 'm/year', 'grid_mapping': 'spatial_ref'}),
        'vy_error': (['time', 'y', 'x'], np.expand_dims(vy_error_vals, axis=0), {'units': 'm/year', 'grid_mapping': 'spatial_ref'}),
        'data_source': (['time'], np.array(["ESA_CCI_Sentinel-1"], dtype="<U50"))
    }, coords={
        'y': (['y'], master_y.values), 'x': (['x'], master_x.values),
    })
    
    return ds


# --- 6. ESA CCI Sentinel-2 Processing ---
def preprocess_esacci_s2(file_path, target_idx, master_x, master_y):
    ds_raw = xr.open_dataset(file_path, decode_times=True)
    ds_slice = ds_raw.isel(time=target_idx)
    
    # 1. Extract variables and convert to m/year
    vx_raw = ds_slice['land_ice_surface_easting_velocity'] * 365.25
    vy_raw = ds_slice['land_ice_surface_northing_velocity'] * 365.25
    
    # Calculate speed
    speed_raw = np.sqrt(vx_raw**2 + vy_raw**2)
    
    # 2. Calculate errors (5% of the absolute value)
    speed_error_raw = speed_raw * 0.05
    vx_error_raw = np.abs(vx_raw) * 0.05
    vy_error_raw = np.abs(vy_raw) * 0.05
    
    # 3. Interpolate to master grid
    speed_interp = speed_raw.interp(x=master_x, y=master_y, method="nearest")
    vx_interp = vx_raw.interp(x=master_x, y=master_y, method="nearest")
    vy_interp = vy_raw.interp(x=master_x, y=master_y, method="nearest")
    
    speed_error_interp = speed_error_raw.interp(x=master_x, y=master_y, method="nearest")
    vx_error_interp = vx_error_raw.interp(x=master_x, y=master_y, method="nearest")
    vy_error_interp = vy_error_raw.interp(x=master_x, y=master_y, method="nearest")
    
    # 4. Extract values, transpose to match y,x dims, and round to 1 decimal place
    speed_vals = np.round(speed_interp.transpose('y', 'x').values, 1)
    vx_vals = np.round(vx_interp.transpose('y', 'x').values, 1)
    vy_vals = np.round(vy_interp.transpose('y', 'x').values, 1)
    
    speed_error_vals = np.round(speed_error_interp.transpose('y', 'x').values, 1)
    vx_error_vals = np.round(vx_error_interp.transpose('y', 'x').values, 1)
    vy_error_vals = np.round(vy_error_interp.transpose('y', 'x').values, 1)
    
    # 5. Construct final dataset with consistent schema
    ds = xr.Dataset({
        'speed': (['time', 'y', 'x'], np.expand_dims(speed_vals, axis=0), {'units': 'm/year', 'grid_mapping': 'spatial_ref'}),
        'vx': (['time', 'y', 'x'], np.expand_dims(vx_vals, axis=0), {'units': 'm/year', 'grid_mapping': 'spatial_ref'}),
        'vy': (['time', 'y', 'x'], np.expand_dims(vy_vals, axis=0), {'units': 'm/year', 'grid_mapping': 'spatial_ref'}),
        'speed_error': (['time', 'y', 'x'], np.expand_dims(speed_error_vals, axis=0), {'units': 'm/year', 'grid_mapping': 'spatial_ref'}),
        'vx_error': (['time', 'y', 'x'], np.expand_dims(vx_error_vals, axis=0), {'units': 'm/year', 'grid_mapping': 'spatial_ref'}),
        'vy_error': (['time', 'y', 'x'], np.expand_dims(vy_error_vals, axis=0), {'units': 'm/year', 'grid_mapping': 'spatial_ref'}),
        'data_source': (['time'], np.array(["ESA_CCI_Sentinel-2"], dtype="<U50"))
    }, coords={
        'y': (['y'], master_y.values), 'x': (['x'], master_x.values),
    })
    
    return ds


# --- 7. ESA CCI CSK Processing ---
def preprocess_esacci_csk(file_path, target_idx, master_x, master_y):
    ds_raw = xr.open_dataset(file_path, decode_times=True)
    ds_slice = ds_raw.isel(time=target_idx)
    
    # 1. Extract variables and convert to m/year
    speed_raw = ds_slice['land_ice_surface_velocity_magnitude'] * 365.25
    vx_raw = ds_slice['land_ice_surface_easting_velocity'] * 365.25
    vy_raw = ds_slice['land_ice_surface_northing_velocity'] * 365.25
    
    speed_error_raw = ds_slice['land_ice_surface_velocity_magnitude_std'] * 365.25
    vx_error_raw = ds_slice['land_ice_surface_easting_velocity_std'] * 365.25
    vy_error_raw = ds_slice['land_ice_surface_northing_velocity_std'] * 365.25
    
    # 2. Interpolate to master grid
    speed_interp = speed_raw.interp(x=master_x, y=master_y, method="nearest")
    vx_interp = vx_raw.interp(x=master_x, y=master_y, method="nearest")
    vy_interp = vy_raw.interp(x=master_x, y=master_y, method="nearest")
    
    speed_error_interp = speed_error_raw.interp(x=master_x, y=master_y, method="nearest")
    vx_error_interp = vx_error_raw.interp(x=master_x, y=master_y, method="nearest")
    vy_error_interp = vy_error_raw.interp(x=master_x, y=master_y, method="nearest")
    
    # 3. Extract values, transpose to match y,x dims, and round to 1 decimal place
    speed_vals = np.round(speed_interp.transpose('y', 'x').values, 1)
    vx_vals = np.round(vx_interp.transpose('y', 'x').values, 1)
    vy_vals = np.round(vy_interp.transpose('y', 'x').values, 1)
    
    speed_error_vals = np.round(speed_error_interp.transpose('y', 'x').values, 1)
    vx_error_vals = np.round(vx_error_interp.transpose('y', 'x').values, 1)
    vy_error_vals = np.round(vy_error_interp.transpose('y', 'x').values, 1)
    
    # 4. Construct final dataset with consistent schema
    ds = xr.Dataset({
        'speed': (['time', 'y', 'x'], np.expand_dims(speed_vals, axis=0), {'units': 'm/year', 'grid_mapping': 'spatial_ref'}),
        'vx': (['time', 'y', 'x'], np.expand_dims(vx_vals, axis=0), {'units': 'm/year', 'grid_mapping': 'spatial_ref'}),
        'vy': (['time', 'y', 'x'], np.expand_dims(vy_vals, axis=0), {'units': 'm/year', 'grid_mapping': 'spatial_ref'}),
        'speed_error': (['time', 'y', 'x'], np.expand_dims(speed_error_vals, axis=0), {'units': 'm/year', 'grid_mapping': 'spatial_ref'}),
        'vx_error': (['time', 'y', 'x'], np.expand_dims(vx_error_vals, axis=0), {'units': 'm/year', 'grid_mapping': 'spatial_ref'}),
        'vy_error': (['time', 'y', 'x'], np.expand_dims(vy_error_vals, axis=0), {'units': 'm/year', 'grid_mapping': 'spatial_ref'}),
        'data_source': (['time'], np.array(["ESA_CCI_CSK"], dtype="<U50"))
    }, coords={
        'y': (['y'], master_y.values), 'x': (['x'], master_x.values),
    })
    
    return ds

# --- 8. ESA CCI ERS1-2/Envisat, ERS2-95/96, PALSAR 2006-2011 & ERS1 (northern basins)  Processing ---
def preprocess_esacci_ers_env(file_path, target_idx, master_x, master_y, source_label="ESA_CCI_ERS1-2_Envisat"):
    ds_raw = xr.open_dataset(file_path, decode_times=True)
    ds_slice = ds_raw.isel(time=target_idx)
    
    # 1. Extract vx and vy
    if 'land_ice_surface_easting_velocity' in ds_slice and 'land_ice_surface_northing_velocity' in ds_slice:
        vx_raw = ds_slice['land_ice_surface_easting_velocity'] * 365.25
        vy_raw = ds_slice['land_ice_surface_northing_velocity'] * 365.25
    elif 'land_ice_surface_east_velocity' in ds_slice and 'land_ice_surface_north_velocity' in ds_slice:
        vx_raw = ds_slice['land_ice_surface_east_velocity'] * 365.25
        vy_raw = ds_slice['land_ice_surface_north_velocity'] * 365.25
    else:
        raise KeyError(f"No valid velocity component variables found in {file_path}")
        
    # 2. Extract speed
    if 'land_ice_surface_velocity_magnitude' in ds_slice:
        speed_raw = ds_slice['land_ice_surface_velocity_magnitude'] * 365.25
    else:
        speed_raw = np.sqrt(vx_raw**2 + vy_raw**2)
        
    # 3. Extract vx_error and vy_error
    if 'land_ice_surface_easting_velocity_std' in ds_slice and 'land_ice_surface_northing_velocity_std' in ds_slice:
        vx_error_raw = ds_slice['land_ice_surface_easting_velocity_std'] * 365.25
        vy_error_raw = ds_slice['land_ice_surface_northing_velocity_std'] * 365.25
    else:
        # Fallback: 5% of the absolute value of the components
        vx_error_raw = np.abs(vx_raw) * 0.05
        vy_error_raw = np.abs(vy_raw) * 0.05

    # 4. Extract speed error
    if 'land_ice_surface_velocity_magnitude_std' in ds_slice:
        speed_error_raw = ds_slice['land_ice_surface_velocity_magnitude_std'] * 365.25
    elif 'land_ice_surface_easting_velocity_std' in ds_slice and 'land_ice_surface_northing_velocity_std' in ds_slice:
        # If speed error is missing but component errors exist, calculate it
        speed_error_raw = np.sqrt(vx_error_raw**2 + vy_error_raw**2)
    else:
        speed_error_raw = speed_raw * 0.05
        
    # 5. Interpolate to master grid
    speed_interp = speed_raw.interp(x=master_x, y=master_y, method="nearest")
    vx_interp = vx_raw.interp(x=master_x, y=master_y, method="nearest")
    vy_interp = vy_raw.interp(x=master_x, y=master_y, method="nearest")
    
    speed_error_interp = speed_error_raw.interp(x=master_x, y=master_y, method="nearest")
    vx_error_interp = vx_error_raw.interp(x=master_x, y=master_y, method="nearest")
    vy_error_interp = vy_error_raw.interp(x=master_x, y=master_y, method="nearest")
    
    # 6. Extract values, transpose to match y,x dims, and round to 1 decimal place
    speed_vals = np.round(speed_interp.transpose('y', 'x').values, 1)
    vx_vals = np.round(vx_interp.transpose('y', 'x').values, 1)
    vy_vals = np.round(vy_interp.transpose('y', 'x').values, 1)
    
    speed_error_vals = np.round(speed_error_interp.transpose('y', 'x').values, 1)
    vx_error_vals = np.round(vx_error_interp.transpose('y', 'x').values, 1)
    vy_error_vals = np.round(vy_error_interp.transpose('y', 'x').values, 1)
    
    # 7. Construct final dataset
    ds = xr.Dataset({
        'speed': (['time', 'y', 'x'], np.expand_dims(speed_vals, axis=0), {'units': 'm/year', 'grid_mapping': 'spatial_ref'}),
        'vx': (['time', 'y', 'x'], np.expand_dims(vx_vals, axis=0), {'units': 'm/year', 'grid_mapping': 'spatial_ref'}),
        'vy': (['time', 'y', 'x'], np.expand_dims(vy_vals, axis=0), {'units': 'm/year', 'grid_mapping': 'spatial_ref'}),
        'speed_error': (['time', 'y', 'x'], np.expand_dims(speed_error_vals, axis=0), {'units': 'm/year', 'grid_mapping': 'spatial_ref'}),
        'vx_error': (['time', 'y', 'x'], np.expand_dims(vx_error_vals, axis=0), {'units': 'm/year', 'grid_mapping': 'spatial_ref'}),
        'vy_error': (['time', 'y', 'x'], np.expand_dims(vy_error_vals, axis=0), {'units': 'm/year', 'grid_mapping': 'spatial_ref'}),
        'data_source': (['time'], np.array([source_label], dtype="<U50"))
    }, coords={
        'y': (['y'], master_y.values), 'x': (['x'], master_x.values),
    })
    
    return ds


# --- 9. ESA CCI Winter Processing ---
def parse_cci_winter_time(file_path):
    """Parses time bounds directly from netcdf global attributes."""
    with xr.open_dataset(file_path) as ds:
        # Slice [:10] in case the string has 'T00:00:00' appended
        start_str = ds.attrs.get('time_coverage_start')[:10]
        end_str = ds.attrs.get('time_coverage_end')[:10]
        
    start_dt = datetime.strptime(start_str, "%Y-%m-%d")
    end_dt = datetime.strptime(end_str, "%Y-%m-%d")
    mid_dt = start_dt + (end_dt - start_dt) / 2
    
    return np.datetime64(mid_dt), np.array([np.datetime64(start_dt), np.datetime64(end_dt)])

def preprocess_esacci_winter(file_path, master_x, master_y):
    """Processes 2D Winter ESA CCI datasets."""
    ds_raw = xr.open_dataset(file_path)
    
    # Time
    if 'time' in ds_raw.dims:
        ds_raw = ds_raw.squeeze('time', drop=True)
    
    # 1. Extract vx and vy
    vx_raw = ds_raw.get('land_ice_surface_easting_velocity', ds_raw.get('land_ice_surface_east_velocity')) * 365.25
    vy_raw = ds_raw.get('land_ice_surface_northing_velocity', ds_raw.get('land_ice_surface_north_velocity')) * 365.25
    
    # 2. Extract speed
    if 'land_ice_surface_velocity_magnitude' in ds_raw:
        speed_raw = ds_raw['land_ice_surface_velocity_magnitude'] * 365.25
    else:
        speed_raw = np.sqrt(vx_raw**2 + vy_raw**2)
        
    # 3. Extract vx_error and vy_error
    if 'land_ice_surface_easting_velocity_std' in ds_raw and 'land_ice_surface_northing_velocity_std' in ds_raw:
        vx_error_raw = ds_raw['land_ice_surface_easting_velocity_std'] * 365.25
        vy_error_raw = ds_raw['land_ice_surface_northing_velocity_std'] * 365.25
    else:
        # Fallback: 5% of the absolute value of the components
        vx_error_raw = np.abs(vx_raw) * 0.05
        vy_error_raw = np.abs(vy_raw) * 0.05

    # 4. Extract speed error
    if 'land_ice_surface_velocity_stddev' in ds_raw:
        speed_error_raw = ds_raw['land_ice_surface_velocity_stddev'] * 365.25
    elif 'land_ice_surface_velocity_magnitude_std' in ds_raw:
        speed_error_raw = ds_raw['land_ice_surface_velocity_magnitude_std'] * 365.25
    elif 'land_ice_surface_velocity_magnuitude_std' in ds_raw: # yes, there is an ESA CCI dataset with this variable name
        speed_error_raw = ds_raw['land_ice_surface_velocity_magnuitude_std'] * 365.25
    else:
        std_x = ds_raw.get('land_ice_surface_easting_velocity_std', ds_raw.get('land_ice_surface_easting_stddev'))
        std_y = ds_raw.get('land_ice_surface_northing_velocity_std', ds_raw.get('land_ice_surface_northing_stddev'))
        if std_x is not None and std_y is not None:
            speed_error_raw = np.sqrt(std_x**2 + std_y**2) * 365.25
        else:
            speed_error_raw = speed_raw * 0.05
    
    # 5. Interpolate to master grid
    speed_interp = speed_raw.interp(x=master_x, y=master_y, method="nearest")
    vx_interp = vx_raw.interp(x=master_x, y=master_y, method="nearest")
    vy_interp = vy_raw.interp(x=master_x, y=master_y, method="nearest")
    
    speed_error_interp = speed_error_raw.interp(x=master_x, y=master_y, method="nearest")
    vx_error_interp = vx_error_raw.interp(x=master_x, y=master_y, method="nearest")
    vy_error_interp = vy_error_raw.interp(x=master_x, y=master_y, method="nearest")
    
    # 6. Extract values, transpose to match y,x dims, and round to 1 decimal place
    speed_vals = np.round(speed_interp.transpose('y', 'x').values, 1)
    vx_vals = np.round(vx_interp.transpose('y', 'x').values, 1)
    vy_vals = np.round(vy_interp.transpose('y', 'x').values, 1)
    
    speed_error_vals = np.round(speed_error_interp.transpose('y', 'x').values, 1)
    vx_error_vals = np.round(vx_error_interp.transpose('y', 'x').values, 1)
    vy_error_vals = np.round(vy_error_interp.transpose('y', 'x').values, 1)
    
    # 7. Construct final dataset with consistent schema
    ds = xr.Dataset({
        'speed': (['time', 'y', 'x'], np.expand_dims(speed_vals, axis=0), {'units': 'm/year', 'grid_mapping': 'spatial_ref'}),
        'vx': (['time', 'y', 'x'], np.expand_dims(vx_vals, axis=0), {'units': 'm/year', 'grid_mapping': 'spatial_ref'}),
        'vy': (['time', 'y', 'x'], np.expand_dims(vy_vals, axis=0), {'units': 'm/year', 'grid_mapping': 'spatial_ref'}),
        'speed_error': (['time', 'y', 'x'], np.expand_dims(speed_error_vals, axis=0), {'units': 'm/year', 'grid_mapping': 'spatial_ref'}),
        'vx_error': (['time', 'y', 'x'], np.expand_dims(vx_error_vals, axis=0), {'units': 'm/year', 'grid_mapping': 'spatial_ref'}),
        'vy_error': (['time', 'y', 'x'], np.expand_dims(vy_error_vals, axis=0), {'units': 'm/year', 'grid_mapping': 'spatial_ref'}),
        'data_source': (['time'], np.array(["ESA_CCI_winter"], dtype="<U50"))
    }, coords={
        'y': (['y'], master_y.values), 'x': (['x'], master_x.values),
    })
    
    return ds


# --- 10. ENVEO Processing ---
def parse_enveo_time(filename):
    """Automatically grabs the two 8-digit dates (YYYYMMDD) from any ENVEO filename string."""
    base = os.path.basename(filename)
    dates = re.findall(r'(20\d{6})', base)
    
    start_dt = datetime.strptime(dates[0], "%Y%m%d")
    end_dt = datetime.strptime(dates[1], "%Y%m%d")
    mid_dt = start_dt + (end_dt - start_dt) / 2
    
    return np.datetime64(mid_dt), np.array([np.datetime64(start_dt), np.datetime64(end_dt)])

def preprocess_enveo_tiff(mag_file, master_x, master_y):
    std_file = mag_file.replace('_mag.tif', '_stdev.tif')
    vxvy_file = mag_file.replace('_mag.tif', '.tif')
    
    # Open single-band datasets
    mag = rioxarray.open_rasterio(mag_file).squeeze('band', drop=True)
    std = rioxarray.open_rasterio(std_file).squeeze('band', drop=True)
    
    # 1. Parse vx and vy from the 3-band geotiff
    vxvy = rioxarray.open_rasterio(vxvy_file)
    vx = vxvy.sel(band=1).drop_vars('band')
    vy = vxvy.sel(band=2).drop_vars('band')
    
    # Safely mask native NoData values if they exist
    if mag.rio.nodata is not None: 
        mag = mag.where(mag != mag.rio.nodata)
    if std.rio.nodata is not None: 
        std = std.where(std != std.rio.nodata)
    if vxvy.rio.nodata is not None: 
        vx = vx.where(vx != vxvy.rio.nodata)
        vy = vy.where(vy != vxvy.rio.nodata)
        
    # Interpolate to master grid
    mag_interp = mag.interp(x=master_x, y=master_y, method="nearest")
    std_interp = std.interp(x=master_x, y=master_y, method="nearest")
    vx_interp = vx.interp(x=master_x, y=master_y, method="nearest")
    vy_interp = vy.interp(x=master_x, y=master_y, method="nearest")
    
    # Convert all components to m/year
    speed_vals = mag_interp.values * 365.25
    speed_error_vals = std_interp.values * 365.25
    vx_vals = vx_interp.values * 365.25
    vy_vals = vy_interp.values * 365.25
    
    # 2. Calculate vx_error and vy_error based on proportional contribution
    # We use np.errstate to suppress division-by-zero warnings in off-ice/nodata regions
    with np.errstate(divide='ignore', invalid='ignore'):
        # Proportion of speed belonging to vx and vy (avoiding division by zero)
        vx_prop = np.where(speed_vals > 0, np.abs(vx_vals) / speed_vals, 0)
        vy_prop = np.where(speed_vals > 0, np.abs(vy_vals) / speed_vals, 0)
        
    vx_error_vals = speed_error_vals * vx_prop
    vy_error_vals = speed_error_vals * vy_prop
    
    # 3. Round everything to 1 decimal place to reduce Zarr volume
    speed_vals = np.round(speed_vals, 1)
    speed_error_vals = np.round(speed_error_vals, 1)
    vx_vals = np.round(vx_vals, 1)
    vy_vals = np.round(vy_vals, 1)
    vx_error_vals = np.round(vx_error_vals, 1)
    vy_error_vals = np.round(vy_error_vals, 1)
    
    # Build dataset
    ds = xr.Dataset({
        'speed': (['time', 'y', 'x'], np.expand_dims(speed_vals, axis=0), {'units': 'm/year', 'grid_mapping': 'spatial_ref'}),
        'vx': (['time', 'y', 'x'], np.expand_dims(vx_vals, axis=0), {'units': 'm/year', 'grid_mapping': 'spatial_ref'}),
        'vy': (['time', 'y', 'x'], np.expand_dims(vy_vals, axis=0), {'units': 'm/year', 'grid_mapping': 'spatial_ref'}),
        'speed_error': (['time', 'y', 'x'], np.expand_dims(speed_error_vals, axis=0), {'units': 'm/year', 'grid_mapping': 'spatial_ref'}),
        'vx_error': (['time', 'y', 'x'], np.expand_dims(vx_error_vals, axis=0), {'units': 'm/year', 'grid_mapping': 'spatial_ref'}),
        'vy_error': (['time', 'y', 'x'], np.expand_dims(vy_error_vals, axis=0), {'units': 'm/year', 'grid_mapping': 'spatial_ref'}),
        'data_source': (['time'], np.array(["ENVEO_annual"], dtype="<U50"))
    }, coords={
        'y': (['y'], master_y.values), 'x': (['x'], master_x.values),
    })
    return ds

def preprocess_enveo_nc(file_path, master_x, master_y):
    ds_raw = xr.open_dataset(file_path)
    
    speed_raw = ds_raw['land_ice_surface_velocity_magnitude'] * 365.25
    vx_raw = ds_raw['land_ice_surface_easting_velocity'] * 365.25
    vy_raw = ds_raw['land_ice_surface_northing_velocity'] * 365.25
    vx_error_raw = ds_raw['land_ice_surface_easting_stddev'] * 365.25
    vy_error_raw = ds_raw['land_ice_surface_northing_stddev'] * 365.25
    speed_error_raw = np.sqrt(vx_error_raw**2 + vy_error_raw**2)
    
    speed_interp = speed_raw.interp(x=master_x, y=master_y, method="nearest")
    vx_interp = vx_raw.interp(x=master_x, y=master_y, method="nearest")
    vy_interp = vy_raw.interp(x=master_x, y=master_y, method="nearest")
    speed_error_interp = speed_error_raw.interp(x=master_x, y=master_y, method="nearest")
    vx_error_interp = vx_error_raw.interp(x=master_x, y=master_y, method="nearest")
    vy_error_interp = vy_error_raw.interp(x=master_x, y=master_y, method="nearest")
    
    speed_vals = np.round(speed_interp.transpose('y', 'x').values, 1)
    vx_vals = np.round(vx_interp.transpose('y', 'x').values, 1)
    vy_vals = np.round(vy_interp.transpose('y', 'x').values, 1)
    speed_error_vals = np.round(speed_error_interp.transpose('y', 'x').values, 1)
    vx_error_vals = np.round(vx_error_interp.transpose('y', 'x').values, 1)
    vy_error_vals = np.round(vy_error_interp.transpose('y', 'x').values, 1)
    
    ds = xr.Dataset({
        'speed': (['time', 'y', 'x'], np.expand_dims(speed_vals, axis=0), {'units': 'm/year', 'grid_mapping': 'spatial_ref'}),
        'vx': (['time', 'y', 'x'], np.expand_dims(vx_vals, axis=0), {'units': 'm/year', 'grid_mapping': 'spatial_ref'}),
        'vy': (['time', 'y', 'x'], np.expand_dims(vy_vals, axis=0), {'units': 'm/year', 'grid_mapping': 'spatial_ref'}),
        'speed_error': (['time', 'y', 'x'], np.expand_dims(speed_error_vals, axis=0), {'units': 'm/year', 'grid_mapping': 'spatial_ref'}),
        'vx_error': (['time', 'y', 'x'], np.expand_dims(vx_error_vals, axis=0), {'units': 'm/year', 'grid_mapping': 'spatial_ref'}),
        'vy_error': (['time', 'y', 'x'], np.expand_dims(vy_error_vals, axis=0), {'units': 'm/year', 'grid_mapping': 'spatial_ref'}),
        'data_source': (['time'], np.array(["ENVEO_annual"], dtype="<U50"))
    }, coords={
        'y': (['y'], master_y.values), 'x': (['x'], master_x.values),
    })
    return ds



# --- 11. SHIFT Processing ---
def parse_shift_time(date_str):
    """Extracts datetimes from SHIFT YYYYMMDD_YYYYMMDD strings."""
    start_str, end_str = date_str.split('_')
    start_dt = datetime.strptime(start_str, "%Y%m%d")
    end_dt = datetime.strptime(end_str, "%Y%m%d")
    mid_dt = start_dt + (end_dt - start_dt) / 2
    return np.datetime64(mid_dt), np.array([np.datetime64(start_dt), np.datetime64(end_dt)])

def read_shift_med(filepath):
    """Safely reads the 'med' column from a SHIFT metadata text file."""
    if not os.path.exists(filepath):
        return np.nan
    try:
        with open(filepath, 'r') as f:
            lines = f.readlines()
        if len(lines) < 2: 
            return np.nan
            
        headers = lines[0].split()
        values = lines[1].split()
        
        if 'med' in headers:
            med_idx = headers.index('med')
            val = float(values[med_idx])
            # Return NaN if the parsed value is basically nodata
            if np.isnan(val) or val == -9999 or val == -1:
                return np.nan
            return val
    except:
        pass
    return np.nan

def read_shift_std(filepath):
    """Safely reads the 'std' column from a SHIFT metadata text file."""
    if not os.path.exists(filepath):
        return np.nan
    try:
        with open(filepath, 'r') as f:
            lines = f.readlines()
        if len(lines) < 2: 
            return np.nan
            
        headers = lines[0].split()
        values = lines[1].split()
        
        if 'std' in headers:
            std_idx = headers.index('std')
            val = float(values[std_idx])
            # Return NaN if the parsed value is basically nodata
            if np.isnan(val) or val == -9999 or val == -1:
                return np.nan
            return val
    except:
        pass
    return np.nan

def preprocess_shift(epoch_dir, master_x, master_y):
    date_str = os.path.basename(epoch_dir)
    speed_file = os.path.join(epoch_dir, f"S_{date_str}_200m_raw.tif")
    vx_file = os.path.join(epoch_dir, f"U_{date_str}_200m_raw.tif")
    vy_file = os.path.join(epoch_dir, f"V_{date_str}_200m_raw.tif")
    meta_dir = os.path.join(epoch_dir, "metadata")
    
    # 1. Load velocity components (Already in m/year)
    speed = rioxarray.open_rasterio(speed_file).squeeze('band', drop=True)
    vx = rioxarray.open_rasterio(vx_file).squeeze('band', drop=True)
    vy = rioxarray.open_rasterio(vy_file).squeeze('band', drop=True)
    if speed.rio.nodata is not None: 
        speed = speed.where(speed != speed.rio.nodata)
    if vx.rio.nodata is not None: 
        vx = vx.where(vx != vx.rio.nodata)
    if vy.rio.nodata is not None: 
        vy = vy.where(vy != vy.rio.nodata)
        
    speed_interp = speed.interp(x=master_x, y=master_y, method="nearest")
    vx_interp = vx.interp(x=master_x, y=master_y, method="nearest")
    vy_interp = vy.interp(x=master_x, y=master_y, method="nearest")
    
    # 2. Extract Error Metadata
    vx_error_scalar = read_shift_std(os.path.join(meta_dir, f"rock_mask_U_metadata_200m_{date_str}.txt"))
    vy_error_scalar = read_shift_std(os.path.join(meta_dir, f"rock_mask_V_metadata_200m_{date_str}.txt"))
    
    speed_error_scalar = np.nan
    
    if not (np.isnan(vx_error_scalar) or np.isnan(vy_error_scalar)):
        speed_error_scalar = np.sqrt(vx_error_scalar**2 + vy_error_scalar**2)
    else:
        vx_error_scalar = read_shift_std(os.path.join(meta_dir, f"off_ice_U_metadata_200m_{date_str}.txt"))
        vy_error_scalar = read_shift_std(os.path.join(meta_dir, f"off_ice_V_metadata_200m_{date_str}.txt"))
        if not (np.isnan(vx_error_scalar) or np.isnan(vy_error_scalar)):
            speed_error_scalar = np.sqrt(vx_error_scalar**2 + vy_error_scalar**2)

    # 3. Apply Error (Constant Scalar or 5% Fallback)
    if np.isnan(speed_error_scalar):
        speed_error_interp = speed_interp * 0.05
    else:
        # Create a spatial array matching the speed footprint, filled with the single scalar value
        speed_error_interp = xr.full_like(speed_interp, speed_error_scalar)
        speed_error_interp = speed_error_interp.where(speed_interp.notnull())
    # 3b. VX
    if np.isnan(vx_error_scalar):
        vx_error_interp = abs(vx_interp) * 0.05
    else:
        # Create a spatial array matching the vx footprint, filled with the single scalar value
        vx_error_interp = xr.full_like(vx_interp, vx_error_scalar)
        vx_error_interp = vx_error_interp.where(vx_interp.notnull())
    # 3c. VY    
    if np.isnan(vy_error_scalar):
        vy_error_interp = abs(vy_interp) * 0.05
    else:
        # Create a spatial array matching the vy footprint, filled with the single scalar value
        vy_error_interp = xr.full_like(vy_interp, vy_error_scalar)
        vy_error_interp = vy_error_interp.where(vy_interp.notnull())

    speed_vals = np.round(speed_interp.values, 1)
    vx_vals = np.round(vx_interp.values, 1)
    vy_vals = np.round(vy_interp.values, 1)
    speed_error_vals = np.round(speed_error_interp.values, 1)
    vx_error_vals = np.round(vx_error_interp.values, 1) 
    vy_error_vals = np.round(vy_error_interp.values, 1)
    
    ds = xr.Dataset({
        'speed': (['time', 'y', 'x'], np.expand_dims(speed_vals, axis=0), {'units': 'm/year', 'grid_mapping': 'spatial_ref'}),
        'vx': (['time', 'y', 'x'], np.expand_dims(vx_vals, axis=0), {'units': 'm/year', 'grid_mapping': 'spatial_ref'}),
        'vy': (['time', 'y', 'x'], np.expand_dims(vy_vals, axis=0), {'units': 'm/year', 'grid_mapping': 'spatial_ref'}),
        'speed_error': (['time', 'y', 'x'], np.expand_dims(speed_error_vals, axis=0), {'units': 'm/year', 'grid_mapping': 'spatial_ref'}),
        'vx_error': (['time', 'y', 'x'], np.expand_dims(vx_error_vals, axis=0), {'units': 'm/year', 'grid_mapping': 'spatial_ref'}),
        'vy_error': (['time', 'y', 'x'], np.expand_dims(vy_error_vals, axis=0), {'units': 'm/year', 'grid_mapping': 'spatial_ref'}),
        'data_source': (['time'], np.array(["SHIFT"], dtype="<U50"))
    }, coords={
        'y': (['y'], master_y.values), 'x': (['x'], master_x.values),
    })
    return ds


# --- HPC PYRAMID BUILDER LOGIC ---

OUTPUT_ZARR = "/mnt/parscratch/users/gg1bjd/Data/Velocity/Greenland/multisource_zarr/greenland_multisource_velocity_spatial.zarr"
CATALOG_FILE = "/mnt/parscratch/users/gg1bjd/Data/Velocity/Greenland/multisource_zarr/master_epoch_catalog_spatial.pkl"

def build_catalog_and_skeleton():
    """Run ONCE by a single job to map files and initialize nested Zarr structure levels."""
    promice_dir = "/mnt/parscratch/users/gg1bjd/Data/Velocity/Greenland/PROMICE_edition5"
    measures_monthly_dir = "/mnt/parscratch/users/gg1bjd/Data/Velocity/Greenland/MEaSUREs_monthly"
    measures_quarterly_dir = "/mnt/parscratch/users/gg1bjd/Data/Velocity/Greenland/MEaSUREs_quarterly"
    measures_annual_dir = "/mnt/parscratch/users/gg1bjd/Data/Velocity/Greenland/MEaSUREs_annual"
    measures_winter_dir = "/mnt/parscratch/users/gg1bjd/Data/Velocity/Greenland/MEaSUREs_winter"
    mouginot_dir = "/mnt/parscratch/users/gg1bjd/Data/Velocity/Greenland/Mouginot_annual"
    itslive_dir = "/mnt/parscratch/users/gg1bjd/Data/Velocity/Greenland/ITS_LIVE_annual"
    esacci_dir = "/mnt/parscratch/users/gg1bjd/Data/Velocity/Greenland/ESA_CCI/greenland_ice_velocity"
    enveo_dir = "/mnt/parscratch/users/gg1bjd/Data/Velocity/Greenland/ENVEO"
    shift_dir = "/mnt/parscratch/users/gg1bjd/SCADI/output/Sentinel1/Greenland/mosaic/subregions/lev/date_pairs"
    
    print("Cataloging files and generating noisy unique times...")
    epochs = []
    
    # 1. PROMICE
    for f in sorted(glob.glob(os.path.join(promice_dir, "*.nc"))):
        with xr.open_dataset(f, decode_times=True) as temp_ds:
            t = temp_ds['time'].values[0]
            tb = temp_ds['time_bnds'].values
            if temp_ds['time_bnds'].dims == ('bnds', 'time'): tb = temp_ds['time_bnds'].transpose('time', 'bnds').values[0]
            else: tb = tb[0] if tb.ndim > 1 else tb
            epochs.append({'time': t, 'time_bnds': tb, 'source': 'PROMICE', 'path': f})
            
    # 2. MEaSUREs monthly
    for f in sorted(glob.glob(os.path.join(measures_monthly_dir, "*_vv_*.tif"))):
        t, tb = parse_measures_time(f)
        epochs.append({'time': t, 'time_bnds': tb, 'source': 'MEaSUREs_monthly', 'path': f})
        
    # 3. MEaSUREs quarterly
    for f in sorted(glob.glob(os.path.join(measures_quarterly_dir, "*_vv_*.tif"))):
        t, tb = parse_measures_time(f)
        epochs.append({'time': t, 'time_bnds': tb, 'source': 'MEaSUREs_quarterly', 'path': f})
        
    # 4. MEaSUREs annual
    for f in sorted(glob.glob(os.path.join(measures_annual_dir, "*_vv_*.tif"))):
        t, tb = parse_measures_time(f)
        epochs.append({'time': t, 'time_bnds': tb, 'source': 'MEaSUREs_annual', 'path': f})
        
    # 5. MEaSUREs winter
    for f in sorted(glob.glob(os.path.join(measures_winter_dir, "*_vv_*.tif"))):
        t, tb = parse_measures_time(f)
        epochs.append({'time': t, 'time_bnds': tb, 'source': 'MEaSUREs_winter', 'path': f})
        
    # 6. Mouginot
    for f in sorted(glob.glob(os.path.join(mouginot_dir, "*.nc"))):
        t, tb = parse_mouginot_time(f)
        epochs.append({'time': t, 'time_bnds': tb, 'source': 'Mouginot_annual', 'path': f})
        
    # 7. ITS_LIVE
    for f in sorted(glob.glob(os.path.join(itslive_dir, "*.nc"))):
        t, tb = parse_itslive_time(f)
        epochs.append({'time': t, 'time_bnds': tb, 'source': 'ITS_LIVE_annual', 'path': f})
        
    # 8. ESA CCI Winter
    for f in get_highest_version_files(esacci_dir, "greenland_ice_velocity_map_winter_*", "*.nc"):
        t, tb = parse_cci_winter_time(f)
        epochs.append({'time': t, 'time_bnds': tb, 'source': 'ESA_CCI_winter', 'path': f})

    # 9. ENVEO
    for f in sorted(glob.glob(os.path.join(enveo_dir, "*", "*_mag.tif"))) + sorted(glob.glob(os.path.join(enveo_dir, "*_mag.tif"))):
        t, tb = parse_enveo_time(f)
        epochs.append({'time': t, 'time_bnds': tb, 'source': 'ENVEO_annual', 'path': f})
    for f in sorted(glob.glob(os.path.join(enveo_dir, "*", "C3S_GrIS_IV_250m_S1_*.nc"))) + sorted(glob.glob(os.path.join(enveo_dir, "C3S_GrIS_IV_250m_S1_*.nc"))):
        t, tb = parse_enveo_time(f)
        epochs.append({'time': t, 'time_bnds': tb, 'source': 'ENVEO_annual', 'path': f})

    # 10. SHIFT
    for d in sorted(glob.glob(os.path.join(shift_dir, "*_*"))):
        date_str = os.path.basename(d)
        if os.path.exists(os.path.join(d, f"S_{date_str}_200m_raw.tif")):
            t, tb = parse_shift_time(date_str)
            epochs.append({'time': t, 'time_bnds': tb, 'source': 'SHIFT', 'path': d})

    # 11. ESA CCI Timeseries
    cci_sources = [
        (get_highest_version_files(esacci_dir, "*250m_s1_*", "*.nc"), 'ESA_CCI_Sentinel-1'),
        (get_highest_version_files(esacci_dir, "*50m_s2_*", "*[tT]ime[sS]eries*.nc"), 'ESA_CCI_Sentinel-2'),
        (get_highest_version_files(esacci_dir, "*250m_csk_*", "*[tT]ime[sS]eries*.nc"), 'ESA_CCI_CSK'),
        (get_highest_version_files(esacci_dir, "*_iv_ERS1_2_ES_*", "*.nc"), 'ESA_CCI_ERS1-2_Envisat'),
        (get_highest_version_files(esacci_dir, "greenland_margin_ERS*", "*.nc"), 'ESA_CCI_ERS2_1995-1996'),
        (get_highest_version_files(esacci_dir, "greenland_margin_PALSAR*", "*.nc"), 'ESA_CCI_PALSAR'),
        (get_highest_version_files(esacci_dir, "greenland_northern*", "*.nc"), 'ESA_CCI_ERS1_1991-1992')
    ]
    for file_list, source_name in cci_sources:
        for f in file_list:
            with xr.open_dataset(f, decode_times=True) as temp_ds:
                for idx in range(temp_ds.sizes['time']):
                    ds_slice = temp_ds.isel(time=idx) 
                    t = ds_slice['time'].values
                    if 'time_bnds' in ds_slice:
                        tb = ds_slice['time_bnds'].values
                        if tb.ndim > 1: tb = tb.flatten()[:2]
                    else: tb = np.array([t, t])
                    epochs.append({'time': t, 'time_bnds': tb, 'idx': idx, 'source': source_name, 'path': f})
        
    # Sort ALL chronologically by the true base time
    epochs = sorted(epochs, key=lambda d: d['time'])
    
    # Guarantee strict uniqueness deterministically
    for i in range(1, len(epochs)):
        if epochs[i]['time'] <= epochs[i-1]['time']:
            # Calculate the exact offset needed to be 1ms greater than the previous time
            diff = epochs[i-1]['time'] - epochs[i]['time']
            offset = diff + np.timedelta64(1, 'ms')
            
            # Apply to both time and time_bnds
            epochs[i]['time'] += offset
            epochs[i]['time_bnds'] += offset

    total_epochs = len(epochs)
    print(f"Found {total_epochs} total epochs for the FULL build.")

    # Save to disk so workers know the master index map
    with open(CATALOG_FILE, 'wb') as f:
        pickle.dump(epochs, f)

    print("Extracting master grid from PROMICE...")
    first_promice = next(item['path'] for item in epochs if item['source'] == 'PROMICE')
    ds_master = preprocess_promice(first_promice)
    
    # Extract times, time bounds and sources from the catalog
    times = [ep['time'] for ep in epochs]
    time_bnds = [ep['time_bnds'] for ep in epochs]
    sources = np.array([ep['source'] for ep in epochs], dtype="<U50")
    
    # Generate Skeletons dynamically until 1024x1024 condition is met
    current_ds_master = ds_master
    level = 0
    
    while True:
        master_x = current_ds_master['x']
        master_y = current_ds_master['y']
        
        print(f"Initializing skeleton for Group '{level}' | Shape: ({total_epochs}, {master_y.size}, {master_x.size})", flush=True)
        
        # Ensure block boundary adjustments if spatial dims fall below 1024
        ch_y = min(1024, master_y.size)
        ch_x = min(1024, master_x.size)
        chunk_def = (1, ch_y, ch_x)
        
        # Create empty 3D dask array
        empty_array_3D = da.empty((total_epochs, master_y.size, master_x.size), chunks=chunk_def, dtype=np.float32)

        ds_skeleton = xr.Dataset({
            'speed': (['time', 'y', 'x'], empty_array_3D, ds_master['speed'].attrs),
            'vx': (['time', 'y', 'x'], empty_array_3D, ds_master['vx'].attrs),
            'vy': (['time', 'y', 'x'], empty_array_3D, ds_master['vy'].attrs),
            'speed_error': (['time', 'y', 'x'], empty_array_3D, ds_master['speed_error'].attrs),
            'vx_error': (['time', 'y', 'x'], empty_array_3D, ds_master['vx_error'].attrs),
            'vy_error': (['time', 'y', 'x'], empty_array_3D, ds_master['vy_error'].attrs),
            'spatial_ref': ([], ds_master['spatial_ref'].values, ds_master['spatial_ref'].attrs),
            'data_source': (['time'], sources)
        }, coords={
            'time': (['time'], np.array(times), ds_master['time'].attrs),
            'time_bnds': (['time', 'bnds'], np.array(time_bnds), ds_master['time_bnds'].attrs),
            'y': (['y'], master_y.values, ds_master['y'].attrs),
            'x': (['x'], master_x.values, ds_master['x'].attrs),
        })

        for var in ['time', 'time_bnds']: ds_skeleton[var].encoding.clear()
        encoding = {
            'speed': {'chunks': chunk_def}, 
            'vx': {'chunks': chunk_def}, 
            'vy': {'chunks': chunk_def}, 
            'speed_error': {'chunks': chunk_def}, 
            'vx_error': {'chunks': chunk_def}, 
            'vy_error': {'chunks': chunk_def}, 
            'data_source': {'chunks': (total_epochs,), 'dtype': '<U50'} 
        }
        
        ds_skeleton.to_zarr(OUTPUT_ZARR, group=str(level), compute=False, encoding=encoding, mode='w' if level == 0 else 'a')
        
        # Termination condition: dataset fits entirely in a single 1024x1024 chunk
        if master_x.size <= 1024 and master_y.size <= 1024:
            print(f"Pyramid architecture target reached at Group '{level}'.", flush=True)
            break
            
        # Coarsen coordinates & layout boundaries by a factor of 2 for next group loop
        # We use boundary='pad' to ensure edge arrays don't throw size errors on odd numbers
        current_ds_master = current_ds_master.coarsen(x=2, y=2, boundary='pad').mean(keep_attrs=True)
        level += 1

    print("Writing structural OME-NGFF multiscale attrs to root directory...")
    # Pass 'level' (which now represents max_level) to the metadata writer
    write_ome_metadata(OUTPUT_ZARR, level, ds_master['x'], ds_master['y'])
    print("Pyramid skeletons initialized successfully!")


def process_worker(target_source, batch_start=None, batch_end=None):
    """Run by multiple parallel jobs. Loads catalog, filters by source, downsamples and inserts data."""
    print(f"Worker started for source: {target_source}")
    with open(CATALOG_FILE, 'rb') as f:
        epochs = pickle.load(f)
        
    first_promice = next(item['path'] for item in epochs if item['source'] == 'PROMICE')
    ds_master = xr.open_dataset(first_promice)
    master_x, master_y = ds_master['x'], ds_master['y']
    
    # 1. Filter for source while retaining the global index 'i' for the Zarr region write
    source_epochs = [(i, ep) for i, ep in enumerate(epochs) if ep['source'] == target_source]
    
    # 2. Slice the list if batch arguments were provided
    if batch_start is not None and batch_end is not None:
        source_epochs = source_epochs[batch_start:batch_end]
        
    print(f"Processing {len(source_epochs)} epochs for {target_source} (Indices {batch_start} to {batch_end})")
    
    for global_i, ep in source_epochs:
        print(f"  [Global Index: {global_i}] Processing {os.path.basename(ep['path'])}")
        
        # Dispatch to appropriate function...
        if ep['source'] == 'PROMICE': ds_slice = preprocess_promice(ep['path'])
        elif ep['source'].startswith('MEaSUREs'): ds_slice = preprocess_measures(ep['path'], master_x, master_y, ep['source'])
        elif ep['source'] == 'Mouginot_annual': ds_slice = preprocess_mouginot(ep['path'], master_x, master_y)
        elif ep['source'] == 'ITS_LIVE_annual': ds_slice = preprocess_itslive(ep['path'], master_x, master_y)
        elif ep['source'] == 'ESA_CCI_winter': ds_slice = preprocess_esacci_winter(ep['path'], master_x, master_y)
        elif ep['source'] == 'SHIFT': ds_slice = preprocess_shift(ep['path'], master_x, master_y)
        elif ep['source'] == 'ENVEO_annual': 
            if ep['path'].endswith('.tif'): ds_slice = preprocess_enveo_tiff(ep['path'], master_x, master_y)
            else: ds_slice = preprocess_enveo_nc(ep['path'], master_x, master_y)
        elif ep['source'] == 'ESA_CCI_Sentinel-1': ds_slice = preprocess_esacci_s1(ep['path'], ep['idx'], master_x, master_y)
        elif ep['source'] == 'ESA_CCI_Sentinel-2': ds_slice = preprocess_esacci_s2(ep['path'], ep['idx'], master_x, master_y)
        elif ep['source'] == 'ESA_CCI_CSK': ds_slice = preprocess_esacci_csk(ep['path'], ep['idx'], master_x, master_y)
        elif ep['source'] in ['ESA_CCI_ERS1-2_Envisat', 'ESA_CCI_ERS2_1995-1996', 'ESA_CCI_PALSAR', 'ESA_CCI_ERS1_1991-1992']: 
            ds_slice = preprocess_esacci_ers_env(ep['path'], ep['idx'], master_x, master_y, source_label=ep['source'])
            
        # Push single epoch values sequentially across all initialized resolution tiers
        level = 0
        while True:
            # Isolate 2D raster payload data arrays matching structural shapes 
            ds_to_write = ds_slice.drop_vars(['x', 'y', 'spatial_ref', 'time', 'time_bnds', 'source'], errors='ignore')
            
            # 3. Use the global index to write to the exact correct time coordinate
            ds_to_write.to_zarr(OUTPUT_ZARR, group=str(level), region={'time': slice(global_i, global_i+1)})
            
            # Break loop if current layout scale matches the single-chunk threshold condition
            if ds_slice['x'].size <= 1024 and ds_slice['y'].size <= 1024:
                break
                
            # Construct subsequent structural slice downsampled grid properties
            ds_next = xr.Dataset()
            
            # 4. Downsample
            vars_to_downsample = ['speed', 'vx', 'vy', 'speed_error', 'vx_error', 'vy_error']
            for var in vars_to_downsample:
                if var in ds_slice:
                    if 'y' in ds_slice[var].dims and 'x' in ds_slice[var].dims:
                        ds_next[var] = ds_slice[var].coarsen(x=2, y=2, boundary='pad').mean(keep_attrs=True)
                    else:
                        ds_next[var] = ds_slice[var]
                    
            # Reassign metadata array fields not bound to standard grid definitions
            ds_next['data_source'] = ds_slice['data_source']
            ds_next = ds_next.assign_coords({
                'x': ds_slice['x'].coarsen(x=2, boundary='pad').mean(keep_attrs=True),
                'y': ds_slice['y'].coarsen(y=2, boundary='pad').mean(keep_attrs=True)
            })
            
            ds_slice = ds_next
            level += 1
        
    print(f"Worker for {target_source} (Indices {batch_start}-{batch_end}) completed!")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py [init | process SOURCE_NAME [start] [end] | consolidate]")
        sys.exit(1)
        
    command = sys.argv[1]
    
    if command == "init":
        build_catalog_and_skeleton()
    elif command == "process":
        if len(sys.argv) < 3:
            print("Please provide a data source name. (e.g. python script.py process PROMICE)")
            sys.exit(1)
            
        source_target = sys.argv[2]
        batch_start, batch_end = None, None
        
        # If batch boundaries are provided via CLI arguments
        if len(sys.argv) >= 5:
            batch_start = int(sys.argv[3])
            batch_end = int(sys.argv[4])
            
        process_worker(source_target, batch_start, batch_end)
    elif command == "consolidate":
        zarr.consolidate_metadata(OUTPUT_ZARR)
        print("OME-Zarr metadata multi-level hierarchy consolidated successfully!")