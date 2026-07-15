import xarray as xr
import numpy as np
import dask.array as da
import glob
import os
import sys
import zarr
import rioxarray
import pickle
from datetime import datetime
import random
import re
# --- HELPERS ---
def apply_noise(t, tb):
    """Adds 1 to 1000 milliseconds of random noise to ensure strictly unique Zarr coordinates."""
    noise = np.timedelta64(random.randint(1, 1000), 'ms')
    return np.datetime64(t) + noise, np.array(tb, dtype='datetime64[ns]') + noise

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

# --- 1. PROMICE Processing ---
def preprocess_promice(file_path):
    """Opens, formats, and converts units for a single PROMICE NetCDF file."""
    ds = xr.open_dataset(file_path, decode_times=True)
    
    vars_to_keep = [
        'land_ice_surface_velocity_magnitude',
        'land_ice_surface_velocity_magnitude_std',
        'crs',
        'time_bnds'
    ]
    ds = ds[vars_to_keep]
    
    ds = ds.rename({
        'land_ice_surface_velocity_magnitude': 'speed',
        'land_ice_surface_velocity_magnitude_std': 'error',
        'crs': 'spatial_ref'
    })
    
    # Convert m/day to m/year
    ds['speed'] = ds['speed'] * 365.25
    ds['error'] = ds['error'] * 365.25
    
    # Update metadata
    ds['speed'].attrs['units'] = 'm/year'
    ds['error'].attrs['units'] = 'm/year'
    ds['speed'].attrs['grid_mapping'] = 'spatial_ref'
    ds['error'].attrs['grid_mapping'] = 'spatial_ref'
    
    ds['data_source'] = xr.DataArray(np.array(["PROMICE"], dtype="<U50"), dims=["time"])
    
    if ds['time_bnds'].dims == ('bnds', 'time'):
        ds['time_bnds'] = ds['time_bnds'].transpose('time', 'bnds')
        
    for var in ['time', 'time_bnds']:
        if var in ds:
            ds[var].encoding.clear()
            
    return ds


# --- 2. MEaSUREs monthly Processing ---
def parse_measures_monthly_time(filename):
    """Extracts start, end, and midpoint datetimes from a MEaSUREs filename."""
    # Example: GL_vel_mosaic_Monthly_01Dec14_31Dec14_vv_v05.0.tif
    parts = os.path.basename(filename).split('_')
    start_str = parts[4] # e.g., 01Dec14
    end_str = parts[5]   # e.g., 31Dec14
    
    start_dt = datetime.strptime(start_str, "%d%b%y")
    end_dt = datetime.strptime(end_str, "%d%b%y")
    mid_dt = start_dt + (end_dt - start_dt) / 2
    
    return np.datetime64(mid_dt), np.array([np.datetime64(start_dt), np.datetime64(end_dt)])

def preprocess_measures_monthly(vv_file, master_x, master_y):
    """Loads MEaSUREs GeoTIFFs, calculates error, and interpolates to master grid."""
    # Deduce ex and ey filepaths
    ex_file = vv_file.replace('_vv_', '_ex_')
    ey_file = vv_file.replace('_vv_', '_ey_')
    
    # Extract times
    time_mid, time_bnds = parse_measures_monthly_time(vv_file)
    
    # Load GeoTIFFs (squeeze removes the 'band' dimension)
    vv = rioxarray.open_rasterio(vv_file).squeeze('band', drop=True)
    ex = rioxarray.open_rasterio(ex_file).squeeze('band', drop=True)
    ey = rioxarray.open_rasterio(ey_file).squeeze('band', drop=True)
    
    # Mask out the -1 no-data values with NaN before interpolating
    vv = vv.where(vv != -1)
    ex = ex.where(ex != -1)
    ey = ey.where(ey != -1)
    
    # Interpolate to PROMICE (master) grid
    vv_interp = vv.interp(x=master_x, y=master_y, method="nearest")
    ex_interp = ex.interp(x=master_x, y=master_y, method="nearest")
    ey_interp = ey.interp(x=master_x, y=master_y, method="nearest")
    
    # Calculate hypotenuse for error
    err_interp = np.sqrt(ex_interp**2 + ey_interp**2)
    
    # Assemble into standard Dataset format
    ds = xr.Dataset({
        # We add 'time' as the first dimension, and use np.expand_dims to make the data 3D (1, y, x)
        'speed': (['time', 'y', 'x'], np.expand_dims(vv_interp.values, axis=0), {'units': 'm/year', 'grid_mapping': 'spatial_ref'}),
        'error': (['time', 'y', 'x'], np.expand_dims(err_interp.values, axis=0), {'units': 'm/year', 'grid_mapping': 'spatial_ref'}),
        'data_source': (['time'], np.array(["MEaSUREs_monthly"], dtype="<U50"))
    }, coords={
        'time': (['time'], [time_mid]),
        'time_bnds': (['time', 'bnds'], [time_bnds]),
        'y': (['y'], master_y.values),
        'x': (['x'], master_x.values),
    })
    
    return ds


# --- 3. MEaSUREs quarterly Processing ---
def parse_measures_quarterly_time(filename):
    """Extracts start, end, and midpoint datetimes from a MEaSUREs quarterly filename."""
    # Example: GL_vel_mosaic_Quarterly_01Sep24_30Nov24_vy_v05.0.tif
    parts = os.path.basename(filename).split('_')
    start_str = parts[4] # e.g., 01Dec14
    end_str = parts[5]   # e.g., 31Dec14
    
    start_dt = datetime.strptime(start_str, "%d%b%y")
    end_dt = datetime.strptime(end_str, "%d%b%y")
    mid_dt = start_dt + (end_dt - start_dt) / 2
    
    return np.datetime64(mid_dt), np.array([np.datetime64(start_dt), np.datetime64(end_dt)])

def preprocess_measures_quarterly(vv_file, master_x, master_y):
    """Loads MEaSUREs GeoTIFFs, calculates error, and interpolates to master grid."""
    # Deduce ex and ey filepaths
    ex_file = vv_file.replace('_vv_', '_ex_')
    ey_file = vv_file.replace('_vv_', '_ey_')
    
    # Extract times
    time_mid, time_bnds = parse_measures_quarterly_time(vv_file)
    
    # Load GeoTIFFs (squeeze removes the 'band' dimension)
    vv = rioxarray.open_rasterio(vv_file).squeeze('band', drop=True)
    ex = rioxarray.open_rasterio(ex_file).squeeze('band', drop=True)
    ey = rioxarray.open_rasterio(ey_file).squeeze('band', drop=True)
    
    # Mask out the -1 no-data values with NaN before interpolating
    vv = vv.where(vv != -1)
    ex = ex.where(ex != -1)
    ey = ey.where(ey != -1)
    
    # Interpolate to PROMICE (master) grid
    vv_interp = vv.interp(x=master_x, y=master_y, method="nearest")
    ex_interp = ex.interp(x=master_x, y=master_y, method="nearest")
    ey_interp = ey.interp(x=master_x, y=master_y, method="nearest")
    
    # Calculate hypotenuse for error
    err_interp = np.sqrt(ex_interp**2 + ey_interp**2)
    
    # Assemble into standard Dataset format
    ds = xr.Dataset({
        # We add 'time' as the first dimension, and use np.expand_dims to make the data 3D (1, y, x)
        'speed': (['time', 'y', 'x'], np.expand_dims(vv_interp.values, axis=0), {'units': 'm/year', 'grid_mapping': 'spatial_ref'}),
        'error': (['time', 'y', 'x'], np.expand_dims(err_interp.values, axis=0), {'units': 'm/year', 'grid_mapping': 'spatial_ref'}),
        'data_source': (['time'], np.array(["MEaSUREs_quarterly"], dtype="<U50"))
    }, coords={
        'time': (['time'], [time_mid]),
        'time_bnds': (['time', 'bnds'], [time_bnds]),
        'y': (['y'], master_y.values),
        'x': (['x'], master_x.values),
    })
    
    return ds


# --- 4. MEaSUREs annual Processing ---
def parse_measures_annual_time(filename):
    """Extracts start, end, and midpoint datetimes from a MEaSUREs annual filename."""
    # Example: GL_vel_mosaic_Annual_01Dec22_30Nov23_vv_v05.0.tif
    parts = os.path.basename(filename).split('_')
    start_str = parts[4] # e.g., 01Dec14
    end_str = parts[5]   # e.g., 31Dec14
    
    start_dt = datetime.strptime(start_str, "%d%b%y")
    end_dt = datetime.strptime(end_str, "%d%b%y")
    mid_dt = start_dt + (end_dt - start_dt) / 2
    
    return np.datetime64(mid_dt), np.array([np.datetime64(start_dt), np.datetime64(end_dt)])

def preprocess_measures_annual(vv_file, master_x, master_y):
    """Loads MEaSUREs GeoTIFFs, calculates error, and interpolates to master grid."""
    # Deduce ex and ey filepaths
    ex_file = vv_file.replace('_vv_', '_ex_')
    ey_file = vv_file.replace('_vv_', '_ey_')
    
    # Extract times
    time_mid, time_bnds = parse_measures_annual_time(vv_file)
    
    # Load GeoTIFFs (squeeze removes the 'band' dimension)
    vv = rioxarray.open_rasterio(vv_file).squeeze('band', drop=True)
    ex = rioxarray.open_rasterio(ex_file).squeeze('band', drop=True)
    ey = rioxarray.open_rasterio(ey_file).squeeze('band', drop=True)
    
    # Mask out the -1 no-data values with NaN before interpolating
    vv = vv.where(vv != -1)
    ex = ex.where(ex != -1)
    ey = ey.where(ey != -1)
    
    # Interpolate to PROMICE (master) grid
    vv_interp = vv.interp(x=master_x, y=master_y, method="nearest")
    ex_interp = ex.interp(x=master_x, y=master_y, method="nearest")
    ey_interp = ey.interp(x=master_x, y=master_y, method="nearest")
    
    # Calculate hypotenuse for error
    err_interp = np.sqrt(ex_interp**2 + ey_interp**2)
    
    # Assemble into standard Dataset format
    ds = xr.Dataset({
        # We add 'time' as the first dimension, and use np.expand_dims to make the data 3D (1, y, x)
        'speed': (['time', 'y', 'x'], np.expand_dims(vv_interp.values, axis=0), {'units': 'm/year', 'grid_mapping': 'spatial_ref'}),
        'error': (['time', 'y', 'x'], np.expand_dims(err_interp.values, axis=0), {'units': 'm/year', 'grid_mapping': 'spatial_ref'}),
        'data_source': (['time'], np.array(["MEaSUREs_annual"], dtype="<U50"))
    }, coords={
        'time': (['time'], [time_mid]),
        'time_bnds': (['time', 'bnds'], [time_bnds]),
        'y': (['y'], master_y.values),
        'x': (['x'], master_x.values),
    })
    
    return ds


# --- 5. MEaSUREs winter Processing ---
def parse_measures_winter_time(filename):
    """Extracts start, end, and midpoint datetimes from a MEaSUREs winter filename."""
    # Example: GL_vel_mosaic_Winter_02Sep09_07May10_vv_v02.1.tif (renamed for ease to include dates as per https://nsidc.org/data/nsidc-0478/versions/2)
    parts = os.path.basename(filename).split('_')
    start_str = parts[4] # e.g., 01Dec14
    end_str = parts[5]   # e.g., 31Dec14
    
    start_dt = datetime.strptime(start_str, "%d%b%y")
    end_dt = datetime.strptime(end_str, "%d%b%y")
    mid_dt = start_dt + (end_dt - start_dt) / 2
    
    return np.datetime64(mid_dt), np.array([np.datetime64(start_dt), np.datetime64(end_dt)])

def preprocess_measures_winter(vv_file, master_x, master_y):
    """Loads MEaSUREs GeoTIFFs, calculates error, and interpolates to master grid."""
    # Deduce ex and ey filepaths
    ex_file = vv_file.replace('_vv_', '_ex_')
    ey_file = vv_file.replace('_vv_', '_ey_')
    
    # Extract times
    time_mid, time_bnds = parse_measures_winter_time(vv_file)
    
    # Load GeoTIFFs (squeeze removes the 'band' dimension)
    vv = rioxarray.open_rasterio(vv_file).squeeze('band', drop=True)
    ex = rioxarray.open_rasterio(ex_file).squeeze('band', drop=True)
    ey = rioxarray.open_rasterio(ey_file).squeeze('band', drop=True)
    
    # Mask out the -1 no-data values with NaN before interpolating
    vv = vv.where(vv != -1)
    ex = ex.where(ex != -1)
    ey = ey.where(ey != -1)
    
    # Interpolate to PROMICE (master) grid
    vv_interp = vv.interp(x=master_x, y=master_y, method="nearest")
    ex_interp = ex.interp(x=master_x, y=master_y, method="nearest")
    ey_interp = ey.interp(x=master_x, y=master_y, method="nearest")
    
    # Calculate hypotenuse for error
    err_interp = np.sqrt(ex_interp**2 + ey_interp**2)
    
    # Assemble into standard Dataset format
    ds = xr.Dataset({
        # We add 'time' as the first dimension, and use np.expand_dims to make the data 3D (1, y, x)
        'speed': (['time', 'y', 'x'], np.expand_dims(vv_interp.values, axis=0), {'units': 'm/year', 'grid_mapping': 'spatial_ref'}),
        'error': (['time', 'y', 'x'], np.expand_dims(err_interp.values, axis=0), {'units': 'm/year', 'grid_mapping': 'spatial_ref'}),
        'data_source': (['time'], np.array(["MEaSUREs_winter"], dtype="<U50"))
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
    
    # Replace FillValues (0) with NaN so they don't corrupt the interpolation
    vx = ds_raw['VX'].where(ds_raw['VX'] != 0)
    vy = ds_raw['VY'].where(ds_raw['VY'] != 0)
    
    # Calculate speed
    speed_raw = np.sqrt(vx**2 + vy**2)
    
    # Interpolate to master grid
    speed_interp = speed_raw.interp(x=master_x, y=master_y, method="nearest")
    
    # Calculate 5% error
    error_interp = speed_interp * 0.05
    
    # Ensure dimensions are ordered correctly (y, x) before expanding to 3D
    speed_vals = speed_interp.transpose('y', 'x').values
    error_vals = error_interp.transpose('y', 'x').values
    
    ds = xr.Dataset({
        'speed': (['time', 'y', 'x'], np.expand_dims(speed_vals, axis=0), {'units': 'm/year', 'grid_mapping': 'spatial_ref'}),
        'error': (['time', 'y', 'x'], np.expand_dims(error_vals, axis=0), {'units': 'm/year', 'grid_mapping': 'spatial_ref'}),
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
    v_error = ds_raw['v_error'].where(ds_raw['v_error'] != 32767)
    
    # Interpolate to master grid
    speed_interp = v.interp(x=master_x, y=master_y, method="nearest")
    error_interp = v_error.interp(x=master_x, y=master_y, method="nearest")
    
    # Ensure dimensions are ordered correctly (y, x) before expanding to 3D
    speed_vals = speed_interp.transpose('y', 'x').values
    error_vals = error_interp.transpose('y', 'x').values
    
    ds = xr.Dataset({
        'speed': (['time', 'y', 'x'], np.expand_dims(speed_vals, axis=0), {'units': 'm/year', 'grid_mapping': 'spatial_ref'}),
        'error': (['time', 'y', 'x'], np.expand_dims(error_vals, axis=0), {'units': 'm/year', 'grid_mapping': 'spatial_ref'}),
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
    
    vx = ds_slice['land_ice_surface_east_velocity']
    vy = ds_slice['land_ice_surface_north_velocity']
    
    speed_raw = np.sqrt(vx**2 + vy**2) * 365.25
    speed_interp = speed_raw.interp(x=master_x, y=master_y, method="nearest")
    error_interp = speed_interp * 0.05
    
    speed_vals = speed_interp.transpose('y', 'x').values
    error_vals = error_interp.transpose('y', 'x').values
    
    ds = xr.Dataset({
        'speed': (['time', 'y', 'x'], np.expand_dims(speed_vals, axis=0), {'units': 'm/year', 'grid_mapping': 'spatial_ref'}),
        'error': (['time', 'y', 'x'], np.expand_dims(error_vals, axis=0), {'units': 'm/year', 'grid_mapping': 'spatial_ref'}),
        'data_source': (['time'], np.array(["ESA_CCI_Sentinel-1"], dtype="<U50"))
    }, coords={
        'y': (['y'], master_y.values), 'x': (['x'], master_x.values),
    })
    return ds


# --- 6. ESA CCI Sentinel-2 Processing ---
def preprocess_esacci_s2(file_path, target_idx, master_x, master_y):
    ds_raw = xr.open_dataset(file_path, decode_times=True)
    ds_slice = ds_raw.isel(time=target_idx)
    
    vx = ds_slice['land_ice_surface_easting_velocity']
    vy = ds_slice['land_ice_surface_northing_velocity']
    
    speed_raw = np.sqrt(vx**2 + vy**2) * 365.25
    speed_interp = speed_raw.interp(x=master_x, y=master_y, method="nearest")
    error_interp = speed_interp * 0.05
    
    speed_vals = speed_interp.transpose('y', 'x').values
    error_vals = error_interp.transpose('y', 'x').values
    
    ds = xr.Dataset({
        'speed': (['time', 'y', 'x'], np.expand_dims(speed_vals, axis=0), {'units': 'm/year', 'grid_mapping': 'spatial_ref'}),
        'error': (['time', 'y', 'x'], np.expand_dims(error_vals, axis=0), {'units': 'm/year', 'grid_mapping': 'spatial_ref'}),
        'data_source': (['time'], np.array(["ESA_CCI_Sentinel-2"], dtype="<U50"))
    }, coords={
        'y': (['y'], master_y.values), 'x': (['x'], master_x.values),
    })
    return ds


# --- 7. ESA CCI CSK Processing ---
def preprocess_esacci_csk(file_path, target_idx, master_x, master_y):
    ds_raw = xr.open_dataset(file_path, decode_times=True)
    ds_slice = ds_raw.isel(time=target_idx)
    
    speed_raw = ds_slice['land_ice_surface_velocity_magnitude'] * 365.25
    error_raw = ds_slice['land_ice_surface_velocity_magnitude_std'] * 365.25
    
    speed_interp = speed_raw.interp(x=master_x, y=master_y, method="nearest")
    error_interp = error_raw.interp(x=master_x, y=master_y, method="nearest")
    
    speed_vals = speed_interp.transpose('y', 'x').values
    error_vals = error_interp.transpose('y', 'x').values
    
    ds = xr.Dataset({
        'speed': (['time', 'y', 'x'], np.expand_dims(speed_vals, axis=0), {'units': 'm/year', 'grid_mapping': 'spatial_ref'}),
        'error': (['time', 'y', 'x'], np.expand_dims(error_vals, axis=0), {'units': 'm/year', 'grid_mapping': 'spatial_ref'}),
        'data_source': (['time'], np.array(["ESA_CCI_CSK"], dtype="<U50"))
    }, coords={
        'y': (['y'], master_y.values), 'x': (['x'], master_x.values),
    })
    return ds


# --- 8. ESA CCI ERS1-2/Envisat, ERS2-95/96, PALSAR 2006-2011 & ERA1 (northern basins)  Processing ---
def preprocess_esacci_ers_env(file_path, target_idx, master_x, master_y, source_label="ESA_CCI_ERS1-2_Envisat"):
    ds_raw = xr.open_dataset(file_path, decode_times=True)
    ds_slice = ds_raw.isel(time=target_idx)
    
    # Robust Variable Checks
    if 'land_ice_surface_velocity_magnitude' in ds_slice:
        speed_raw = ds_slice['land_ice_surface_velocity_magnitude'] * 365.25
    else:
        if 'land_ice_surface_east_velocity' in ds_slice:
            vx = ds_slice['land_ice_surface_east_velocity']
            vy = ds_slice['land_ice_surface_north_velocity']
        elif 'land_ice_surface_easting_velocity' in ds_slice:
            vx = ds_slice['land_ice_surface_easting_velocity']
            vy = ds_slice['land_ice_surface_northing_velocity']
        else:
            raise KeyError(f"No valid speed or velocity component variables found in {file_path}")
        speed_raw = np.sqrt(vx**2 + vy**2) * 365.25
        
    if 'land_ice_surface_velocity_magnitude_std' in ds_slice:
        error_raw = ds_slice['land_ice_surface_velocity_magnitude_std'] * 365.25
    else:
        error_raw = speed_raw * 0.05
        
    speed_interp = speed_raw.interp(x=master_x, y=master_y, method="nearest")
    error_interp = error_raw.interp(x=master_x, y=master_y, method="nearest")
    
    speed_vals = speed_interp.transpose('y', 'x').values
    error_vals = error_interp.transpose('y', 'x').values
    
    ds = xr.Dataset({
        'speed': (['time', 'y', 'x'], np.expand_dims(speed_vals, axis=0), {'units': 'm/year', 'grid_mapping': 'spatial_ref'}),
        'error': (['time', 'y', 'x'], np.expand_dims(error_vals, axis=0), {'units': 'm/year', 'grid_mapping': 'spatial_ref'}),
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
    
    # Extract speed
    if 'land_ice_surface_velocity_magnitude' in ds_raw:
        speed_raw = ds_raw['land_ice_surface_velocity_magnitude'] * 365.25
    else:
        vx = ds_raw.get('land_ice_surface_easting_velocity', ds_raw.get('land_ice_surface_east_velocity'))
        vy = ds_raw.get('land_ice_surface_northing_velocity', ds_raw.get('land_ice_surface_north_velocity'))
        speed_raw = np.sqrt(vx**2 + vy**2) * 365.25
        
    # Extract speed error
    if 'land_ice_surface_velocity_stddev' in ds_raw:
        error_raw = ds_raw['land_ice_surface_velocity_stddev'] * 365.25
    elif 'land_ice_surface_velocity_magnitude_std' in ds_raw:
        error_raw = ds_raw['land_ice_surface_velocity_magnitude_std'] * 365.25
    elif 'land_ice_surface_velocity_magnuitude_std' in ds_raw:
        error_raw = ds_raw['land_ice_surface_velocity_magnuitude_std'] * 365.25
    else:
        std_x = ds_raw.get('land_ice_surface_easting_velocity_std', ds_raw.get('land_ice_surface_easting_stddev'))
        std_y = ds_raw.get('land_ice_surface_northing_velocity_std', ds_raw.get('land_ice_surface_northing_stddev'))
        if std_x is not None and std_y is not None:
            error_raw = np.sqrt(std_x**2 + std_y**2) * 365.25
        else:
            error_raw = speed_raw * 0.05
    
    speed_interp = speed_raw.interp(x=master_x, y=master_y, method="nearest")
    error_interp = error_raw.interp(x=master_x, y=master_y, method="nearest")
    
    speed_vals = speed_interp.transpose('y', 'x').values
    error_vals = error_interp.transpose('y', 'x').values
    
    ds = xr.Dataset({
        'speed': (['time', 'y', 'x'], np.expand_dims(speed_vals, axis=0), {'units': 'm/year', 'grid_mapping': 'spatial_ref'}),
        'error': (['time', 'y', 'x'], np.expand_dims(error_vals, axis=0), {'units': 'm/year', 'grid_mapping': 'spatial_ref'}),
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
    
    mag = rioxarray.open_rasterio(mag_file).squeeze('band', drop=True)
    std = rioxarray.open_rasterio(std_file).squeeze('band', drop=True)
    
    # Safely mask native NoData values if they exist
    if mag.rio.nodata is not None: mag = mag.where(mag != mag.rio.nodata)
    if std.rio.nodata is not None: std = std.where(std != std.rio.nodata)
        
    mag_interp = mag.interp(x=master_x, y=master_y, method="nearest")
    std_interp = std.interp(x=master_x, y=master_y, method="nearest")
    
    speed_vals = mag_interp.values * 365.25
    error_vals = std_interp.values * 365.25
    
    ds = xr.Dataset({
        'speed': (['time', 'y', 'x'], np.expand_dims(speed_vals, axis=0), {'units': 'm/year', 'grid_mapping': 'spatial_ref'}),
        'error': (['time', 'y', 'x'], np.expand_dims(error_vals, axis=0), {'units': 'm/year', 'grid_mapping': 'spatial_ref'}),
        'data_source': (['time'], np.array(["ENVEO_annual"], dtype="<U50"))
    }, coords={
        'y': (['y'], master_y.values), 'x': (['x'], master_x.values),
    })
    return ds

def preprocess_enveo_nc(file_path, master_x, master_y):
    ds_raw = xr.open_dataset(file_path)
    
    speed_raw = ds_raw['land_ice_surface_velocity_magnitude'] * 365.25
    std_x = ds_raw['land_ice_surface_easting_stddev']
    std_y = ds_raw['land_ice_surface_northing_stddev']
    error_raw = np.sqrt(std_x**2 + std_y**2) * 365.25
    
    speed_interp = speed_raw.interp(x=master_x, y=master_y, method="nearest")
    error_interp = error_raw.interp(x=master_x, y=master_y, method="nearest")
    
    speed_vals = speed_interp.transpose('y', 'x').values
    error_vals = error_interp.transpose('y', 'x').values
    
    ds = xr.Dataset({
        'speed': (['time', 'y', 'x'], np.expand_dims(speed_vals, axis=0), {'units': 'm/year', 'grid_mapping': 'spatial_ref'}),
        'error': (['time', 'y', 'x'], np.expand_dims(error_vals, axis=0), {'units': 'm/year', 'grid_mapping': 'spatial_ref'}),
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

def preprocess_shift(epoch_dir, master_x, master_y):
    date_str = os.path.basename(epoch_dir)
    speed_file = os.path.join(epoch_dir, f"S_{date_str}_200m_raw.tif")
    meta_dir = os.path.join(epoch_dir, "metadata")
    
    # 1. Load Speed (Already in m/year)
    speed = rioxarray.open_rasterio(speed_file).squeeze('band', drop=True)
    if speed.rio.nodata is not None: 
        speed = speed.where(speed != speed.rio.nodata)
        
    speed_interp = speed.interp(x=master_x, y=master_y, method="nearest")
    
    # 2. Extract Error Metadata
    rock_u = read_shift_med(os.path.join(meta_dir, f"rock_mask_U_metadata_200m_{date_str}.txt"))
    rock_v = read_shift_med(os.path.join(meta_dir, f"rock_mask_V_metadata_200m_{date_str}.txt"))
    
    error_scalar = np.nan
    
    if not (np.isnan(rock_u) or np.isnan(rock_v)):
        error_scalar = np.sqrt(rock_u**2 + rock_v**2)
    else:
        off_u = read_shift_med(os.path.join(meta_dir, f"off_ice_U_metadata_200m_{date_str}.txt"))
        off_v = read_shift_med(os.path.join(meta_dir, f"off_ice_V_metadata_200m_{date_str}.txt"))
        if not (np.isnan(off_u) or np.isnan(off_v)):
            error_scalar = np.sqrt(off_u**2 + off_v**2)

    # 3. Apply Error (Constant Scalar or 5% Fallback)
    if np.isnan(error_scalar):
        error_interp = speed_interp * 0.05
    else:
        # Create a spatial array matching the speed footprint, filled with the single scalar value
        error_interp = xr.full_like(speed_interp, error_scalar)
        error_interp = error_interp.where(speed_interp.notnull())

    speed_vals = speed_interp.values
    error_vals = error_interp.values
    
    ds = xr.Dataset({
        'speed': (['time', 'y', 'x'], np.expand_dims(speed_vals, axis=0), {'units': 'm/year', 'grid_mapping': 'spatial_ref'}),
        'error': (['time', 'y', 'x'], np.expand_dims(error_vals, axis=0), {'units': 'm/year', 'grid_mapping': 'spatial_ref'}),
        'data_source': (['time'], np.array(["SHIFT"], dtype="<U50"))
    }, coords={
        'y': (['y'], master_y.values), 'x': (['x'], master_x.values),
    })
    return ds


# --- HPC BUILDER LOGIC ---

# Setup Paths globally so all functions can see them
OUTPUT_ZARR = "/mnt/parscratch/users/gg1bjd/Data/Velocity/Greenland/multisource_zarr/Greenland_multisource_speed_spatial_200.zarr"
CATALOG_FILE = "/mnt/parscratch/users/gg1bjd/Data/Velocity/Greenland/multisource_zarr/master_epoch_catalog.pkl"

def build_catalog_and_skeleton():
    """Run ONCE by a single job to map files and create the Zarr structure."""
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
            t_n, tb_n = apply_noise(t, tb)
            epochs.append({'time': t_n, 'time_bnds': tb_n, 'source': 'PROMICE', 'path': f})
            
    # 2. MEaSUREs monthly
    for f in sorted(glob.glob(os.path.join(measures_monthly_dir, "*_vv_*.tif"))):
        t, tb = parse_measures_monthly_time(f)
        t_n, tb_n = apply_noise(t, tb)
        epochs.append({'time': t_n, 'time_bnds': tb_n, 'source': 'MEaSUREs_monthly', 'path': f})
        
    # 3. MEaSUREs quarterly
    for f in sorted(glob.glob(os.path.join(measures_quarterly_dir, "*_vv_*.tif"))):
        t, tb = parse_measures_quarterly_time(f)
        t_n, tb_n = apply_noise(t, tb)
        epochs.append({'time': t_n, 'time_bnds': tb_n, 'source': 'MEaSUREs_quarterly', 'path': f})
        
    # 4. MEaSUREs annual
    for f in sorted(glob.glob(os.path.join(measures_annual_dir, "*_vv_*.tif"))):
        t, tb = parse_measures_annual_time(f)
        t_n, tb_n = apply_noise(t, tb)
        epochs.append({'time': t_n, 'time_bnds': tb_n, 'source': 'MEaSUREs_annual', 'path': f})
        
    # 5. MEaSUREs winter
    for f in sorted(glob.glob(os.path.join(measures_winter_dir, "*_vv_*.tif"))):
        t, tb = parse_measures_winter_time(f)
        t_n, tb_n = apply_noise(t, tb)
        epochs.append({'time': t_n, 'time_bnds': tb_n, 'source': 'MEaSUREs_winter', 'path': f})
        
    # 6. Mouginot
    for f in sorted(glob.glob(os.path.join(mouginot_dir, "*.nc"))):
        t, tb = parse_mouginot_time(f)
        t_n, tb_n = apply_noise(t, tb)
        epochs.append({'time': t_n, 'time_bnds': tb_n, 'source': 'Mouginot_annual', 'path': f})
        
    # 7. ITS_LIVE
    for f in sorted(glob.glob(os.path.join(itslive_dir, "*.nc"))):
        t, tb = parse_itslive_time(f)
        t_n, tb_n = apply_noise(t, tb)
        epochs.append({'time': t_n, 'time_bnds': tb_n, 'source': 'ITS_LIVE_annual', 'path': f})
        
    # 8. ESA CCI Winter
    for f in get_highest_version_files(esacci_dir, "greenland_ice_velocity_map_winter_*", "*.nc"):
        t, tb = parse_cci_winter_time(f)
        t_n, tb_n = apply_noise(t, tb)
        epochs.append({'time': t_n, 'time_bnds': tb_n, 'source': 'ESA_CCI_winter', 'path': f})

    # 9. ENVEO
    for f in sorted(glob.glob(os.path.join(enveo_dir, "*", "*_mag.tif"))) + sorted(glob.glob(os.path.join(enveo_dir, "*_mag.tif"))):
        t, tb = parse_enveo_time(f)
        t_n, tb_n = apply_noise(t, tb)
        epochs.append({'time': t_n, 'time_bnds': tb_n, 'source': 'ENVEO_annual', 'path': f})
    for f in sorted(glob.glob(os.path.join(enveo_dir, "*", "C3S_GrIS_IV_250m_S1_*.nc"))) + sorted(glob.glob(os.path.join(enveo_dir, "C3S_GrIS_IV_250m_S1_*.nc"))):
        t, tb = parse_enveo_time(f)
        t_n, tb_n = apply_noise(t, tb)
        epochs.append({'time': t_n, 'time_bnds': tb_n, 'source': 'ENVEO_annual', 'path': f})

    # 10. SHIFT
    for d in sorted(glob.glob(os.path.join(shift_dir, "*_*"))):
        date_str = os.path.basename(d)
        if os.path.exists(os.path.join(d, f"S_{date_str}_200m_raw.tif")):
            t, tb = parse_shift_time(date_str)
            t_n, tb_n = apply_noise(t, tb)
            epochs.append({'time': t_n, 'time_bnds': tb_n, 'source': 'SHIFT', 'path': d})

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
                    t_n, tb_n = apply_noise(t, tb)
                    epochs.append({'time': t_n, 'time_bnds': tb_n, 'idx': idx, 'source': source_name, 'path': f})
        
    # Sort ALL chronologically
    epochs = sorted(epochs, key=lambda d: d['time'])
    total_epochs = len(epochs)
    print(f"Found {total_epochs} total epochs for the FULL build.")

    # Save to disk so workers know the master index map
    with open(CATALOG_FILE, 'wb') as f:
        pickle.dump(epochs, f)

    print("Extracting master grid from PROMICE...")
    first_promice = next(item['path'] for item in epochs if item['source'] == 'PROMICE')
    ds_master = preprocess_promice(first_promice)
    master_x, master_y = ds_master['x'], ds_master['y']
    
    times = [ep['time'] for ep in epochs]
    time_bnds = [ep['time_bnds'] for ep in epochs]
    
    # Chunk size for time is 1 to allow parallel worker writes
    chunk_def = (1, 1024, 1024) 
    
    empty_speed = da.empty((total_epochs, master_y.size, master_x.size), chunks=chunk_def, dtype=np.float32)
    empty_error = da.empty((total_epochs, master_y.size, master_x.size), chunks=chunk_def, dtype=np.float32)
    empty_source = da.full((total_epochs,), "", chunks=(1,), dtype="<U50")

    ds_skeleton = xr.Dataset({
        'speed': (['time', 'y', 'x'], empty_speed, ds_master['speed'].attrs),
        'error': (['time', 'y', 'x'], empty_error, ds_master['error'].attrs),
        'spatial_ref': ([], ds_master['spatial_ref'].values, ds_master['spatial_ref'].attrs),
        'data_source': (['time'], empty_source)
    }, coords={
        'time': (['time'], np.array(times), ds_master['time'].attrs),
        'time_bnds': (['time', 'bnds'], np.array(time_bnds), ds_master['time_bnds'].attrs),
        'y': (['y'], master_y.values, ds_master['y'].attrs),
        'x': (['x'], master_x.values, ds_master['x'].attrs),
    })

    for var in ['time', 'time_bnds']: ds_skeleton[var].encoding.clear()
    encoding = {'speed': {'chunks': chunk_def}, 'error': {'chunks': chunk_def}, 'data_source': {'dtype': '<U50'}}
    
    print("Writing skeleton to disk...")
    ds_skeleton.to_zarr(OUTPUT_ZARR, compute=False, encoding=encoding, mode='w')
    print("Skeleton initialized successfully!")


def process_worker(target_source):
    """Run by multiple parallel jobs. Loads catalog, filters by source, and inserts data."""
    print(f"Worker started for source: {target_source}")
    with open(CATALOG_FILE, 'rb') as f:
        epochs = pickle.load(f)
        
    # We need the master grid for interpolation
    first_promice = next(item['path'] for item in epochs if item['source'] == 'PROMICE')
    ds_master = xr.open_dataset(first_promice)
    master_x, master_y = ds_master['x'], ds_master['y']
    
    for i, ep in enumerate(epochs):
        if ep['source'] != target_source:
            continue # Skip files belonging to other sources
            
        print(f"  [{i}/{len(epochs)}] Processing {os.path.basename(ep['path'])}")
        
        # Dispatch to appropriate function
        if ep['source'] == 'PROMICE': ds_slice = preprocess_promice(ep['path'])
        elif ep['source'] == 'MEaSUREs_monthly': ds_slice = preprocess_measures_monthly(ep['path'], master_x, master_y)
        elif ep['source'] == 'MEaSUREs_quarterly': ds_slice = preprocess_measures_quarterly(ep['path'], master_x, master_y)
        elif ep['source'] == 'MEaSUREs_annual': ds_slice = preprocess_measures_annual(ep['path'], master_x, master_y)
        elif ep['source'] == 'MEaSUREs_winter': ds_slice = preprocess_measures_winter(ep['path'], master_x, master_y)
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
            
        ds_to_write = ds_slice.drop_vars(['x', 'y', 'spatial_ref', 'time', 'time_bnds'], errors='ignore')
        ds_to_write.to_zarr(OUTPUT_ZARR, region={'time': slice(i, i+1)})
        
    print(f"Worker for {target_source} completed!")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py [init | process SOURCE_NAME | consolidate]")
        sys.exit(1)
        
    command = sys.argv[1]
    
    if command == "init":
        build_catalog_and_skeleton()
    elif command == "process":
        if len(sys.argv) < 3:
            print("Please provide a data source name. (e.g. python script.py process PROMICE)")
            sys.exit(1)
        source_target = sys.argv[2]
        process_worker(source_target)
    elif command == "consolidate":
        zarr.consolidate_metadata(OUTPUT_ZARR)
        print("Zarr metadata consolidated successfully!")