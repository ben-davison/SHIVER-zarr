import xarray as xr
import numpy as np
import dask.array as da
import glob
import os
import sys
import zarr
import rioxarray
import pickle
from datetime import datetime, timedelta
import random
import re

# --- Paths ---
ENVEO_DIR = "/mnt/parscratch/users/gg1bjd/Data/Velocity/Antarctica/ENVEO_monthly"
ITSLIVE_DIR = "/mnt/parscratch/users/gg1bjd/Data/Velocity/Antarctica/ITS_LIVE_annual"
MEASURES_DIR = "/mnt/parscratch/users/gg1bjd/Data/Velocity/Antarctica/MEaSUREs/annual"
MEASURES_MULTI_DIR = "/mnt/parscratch/users/gg1bjd/Data/Velocity/Antarctica/MEaSUREs/multiyear"
MEASURES_ASE_DIR = "/mnt/parscratch/users/gg1bjd/Data/Velocity/Antarctica/MEaSUREs/ASE"
SID_ANNUAL_DIR = "/mnt/parscratch/users/gg1bjd/Data/Velocity/Antarctica/SID/annual"
ESA_CCI_ANNUAL_DIR = "/mnt/parscratch/users/gg1bjd/Data/Velocity/Antarctica/ESA_CCI/annual"
JOUGHIN_DIR = "/mnt/parscratch/users/gg1bjd/Data/Velocity/Antarctica/Joughin/pine_island/RWArchive/velocityTimeSeries"
LI_TOTTEN_DIR = "/mnt/parscratch/users/gg1bjd/Data/Velocity/Antarctica/Totten"
ENVEO_S1_PIG_DIR = "/mnt/parscratch/users/gg1bjd/Data/Velocity/Antarctica/ENVEO_selected/pine_island/ais_cci_iv_PIG_S1t065_20141010_20190821_v1_1/mag"
ENVEO_OTHERS_DIR = "/mnt/parscratch/users/gg1bjd/Data/Velocity/Antarctica/ENVEO_selected/others"
SHIFT_DIR = "/mnt/parscratch/users/gg1bjd/SCADI/output/Sentinel1/Antarctica/mosaic/subregions/peninsula/date_pairs"

OUTPUT_DIR = "/mnt/parscratch/users/gg1bjd/Data/Velocity/Antarctica/multisource_zarr"
OUTPUT_ZARR = os.path.join(OUTPUT_DIR, "Antarctica_multisource_speed_spatial.zarr")
CATALOG_FILE = os.path.join(OUTPUT_DIR, "master_epoch_catalog_spatial.pkl")

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- Helpers ---
def apply_noise(t, tb):
    """Adds 1 to 86399 seconds of random noise to ensure strictly unique Zarr coordinates."""
    noise = np.timedelta64(random.randint(1, 1000), 'ms')
    return np.datetime64(t) + noise, np.array(tb, dtype='datetime64[ns]') + noise

# --- 1. ENVEO Monthly Processing ---
def parse_enveo_monthly_time(file_path):
    with xr.open_dataset(file_path) as ds:
        start_str = ds.attrs.get('time_coverage_start')[:10]
        end_str = ds.attrs.get('time_coverage_end')[:10]
    start_dt = datetime.strptime(start_str, "%Y-%m-%d")
    end_dt = datetime.strptime(end_str, "%Y-%m-%d")
    mid_dt = start_dt + (end_dt - start_dt) / 2
    return np.datetime64(mid_dt), np.array([np.datetime64(start_dt), np.datetime64(end_dt)])

def preprocess_enveo_monthly(file_path, master_x=None, master_y=None):
    ds_raw = xr.open_dataset(file_path)
    speed_raw = ds_raw['land_ice_surface_velocity_magnitude'] * 365.25
    std_x = ds_raw['land_ice_surface_easting_stddev']
    std_y = ds_raw['land_ice_surface_northing_stddev']
    error_raw = np.sqrt(std_x**2 + std_y**2) * 365.25
    if master_x is not None and master_y is not None:
        speed_interp = speed_raw.interp(x=master_x, y=master_y, method="nearest")
        error_interp = error_raw.interp(x=master_x, y=master_y, method="nearest")
        out_x, out_y = master_x.values, master_y.values
    else:
        speed_interp = speed_raw
        error_interp = error_raw
        out_x, out_y = ds_raw['x'].values, ds_raw['y'].values
    speed_vals = speed_interp.squeeze().values
    error_vals = error_interp.squeeze().values
    crs_val = ds_raw['crs'].values if 'crs' in ds_raw else 0
    crs_attrs = ds_raw['crs'].attrs if 'crs' in ds_raw else {}
    ds = xr.Dataset({
        'speed': (['time', 'y', 'x'], np.expand_dims(speed_vals, axis=0), {'units': 'm/year', 'grid_mapping': 'spatial_ref'}),
        'error': (['time', 'y', 'x'], np.expand_dims(error_vals, axis=0), {'units': 'm/year', 'grid_mapping': 'spatial_ref'}),
        'spatial_ref': ([], crs_val, crs_attrs),
        'data_source': (['time'], np.array(["ENVEO_monthly"], dtype="<U50"))
    }, coords={'y': (['y'], out_y), 'x': (['x'], out_x)})
    return ds

# --- 2. ITS_LIVE Annual Processing ---
def parse_itslive_annual_time(file_path):
    match = re.search(r'_(\d{4})_', os.path.basename(file_path))
    year = int(match.group(1))
    start_dt = datetime(year, 1, 1)
    end_dt = datetime(year, 12, 31, 23, 59, 59)
    mid_dt = start_dt + (end_dt - start_dt) / 2
    return np.datetime64(mid_dt), np.array([np.datetime64(start_dt), np.datetime64(end_dt)])

def preprocess_itslive_annual(file_path, master_x, master_y):
    ds_raw = xr.open_dataset(file_path)
    speed_raw = ds_raw['v']
    error_raw = ds_raw['v_error']
    valid_mask = (speed_raw >= 0) & (speed_raw != 32767) & (error_raw >= 0) & (error_raw != 32767)
    speed_masked = speed_raw.where(valid_mask, np.nan)
    error_masked = error_raw.where(valid_mask, np.nan)
    speed_interp = speed_masked.interp(x=master_x, y=master_y, method="nearest")
    error_interp = error_masked.interp(x=master_x, y=master_y, method="nearest")
    ds = xr.Dataset({
        'speed': (['time', 'y', 'x'], np.expand_dims(speed_interp.squeeze().values, axis=0), {'units': 'm/year'}),
        'error': (['time', 'y', 'x'], np.expand_dims(error_interp.squeeze().values, axis=0), {'units': 'm/year'}),
        'data_source': (['time'], np.array(["ITS_LIVE_annual"], dtype="<U50"))
    }, coords={'y': (['y'], master_y.values), 'x': (['x'], master_x.values)})
    return ds

# --- 3. MEaSUREs Annual Processing ---
def parse_measures_annual_time(file_path):
    match = re.search(r'_(\d{4})_(\d{4})_', os.path.basename(file_path))
    start_dt = datetime(int(match.group(1)), 7, 1)
    end_dt = datetime(int(match.group(2)), 6, 30, 23, 59, 59)
    mid_dt = start_dt + (end_dt - start_dt) / 2
    return np.datetime64(mid_dt), np.array([np.datetime64(start_dt), np.datetime64(end_dt)])

def preprocess_measures_annual(file_path, master_x, master_y):
    ds_raw = xr.open_dataset(file_path)
    speed_raw = np.sqrt(ds_raw['VX']**2 + ds_raw['VY']**2)
    error_raw = np.sqrt(ds_raw['ERRX']**2 + ds_raw['ERRY']**2)
    valid_mask = (speed_raw != 0)
    speed_masked = speed_raw.where(valid_mask, np.nan)
    error_masked = error_raw.where(valid_mask, np.nan)
    speed_interp = speed_masked.interp(x=master_x, y=master_y, method="nearest")
    error_interp = error_masked.interp(x=master_x, y=master_y, method="nearest")
    ds = xr.Dataset({
        'speed': (['time', 'y', 'x'], np.expand_dims(speed_interp.squeeze().values, axis=0), {'units': 'm/year'}),
        'error': (['time', 'y', 'x'], np.expand_dims(error_interp.squeeze().values, axis=0), {'units': 'm/year'}),
        'data_source': (['time'], np.array(["MEaSUREs_annual"], dtype="<U50"))
    }, coords={'y': (['y'], master_y.values), 'x': (['x'], master_x.values)})
    return ds

# --- 4. MEaSUREs Multiyear Processing ---
def parse_measures_multiyear_time(file_path):
    match = re.search(r'_(\d{4})-(\d{4})_', os.path.basename(file_path))
    start_dt = datetime(int(match.group(1)), 7, 1)
    end_dt = datetime(int(match.group(2)), 6, 30, 23, 59, 59)
    mid_dt = start_dt + (end_dt - start_dt) / 2
    return np.datetime64(mid_dt), np.array([np.datetime64(start_dt), np.datetime64(end_dt)])

def preprocess_measures_multiyear(file_path, master_x, master_y):
    ds_raw = xr.open_dataset(file_path)
    speed_raw = np.sqrt(ds_raw['VX']**2 + ds_raw['VY']**2)
    error_raw = np.sqrt(ds_raw['ERRX']**2 + ds_raw['ERRY']**2)
    valid_mask = (speed_raw != 0)
    speed_masked = speed_raw.where(valid_mask, np.nan)
    error_masked = error_raw.where(valid_mask, np.nan)
    speed_interp = speed_masked.interp(x=master_x, y=master_y, method="nearest")
    error_interp = error_masked.interp(x=master_x, y=master_y, method="nearest")
    ds = xr.Dataset({
        'speed': (['time', 'y', 'x'], np.expand_dims(speed_interp.squeeze().values, axis=0), {'units': 'm/year'}),
        'error': (['time', 'y', 'x'], np.expand_dims(error_interp.squeeze().values, axis=0), {'units': 'm/year'}),
        'data_source': (['time'], np.array(["MEaSUREs_multiyear"], dtype="<U50"))
    }, coords={'y': (['y'], master_y.values), 'x': (['x'], master_x.values)})
    return ds

# --- 5. MEaSUREs ASE Processing ---
def catalog_measures_ase(file_path):
    epochs = []
    with xr.open_dataset(file_path) as ds:
        years = [int(var[2:]) for var in ds.data_vars if re.match(r'^vx\d{4}$', var)]
    for year in sorted(years):
        start_dt = datetime(year, 1, 1)
        end_dt = datetime(year, 12, 31, 23, 59, 59)
        mid_dt = start_dt + (end_dt - start_dt) / 2
        t_n, tb_n = apply_noise(np.datetime64(mid_dt), np.array([np.datetime64(start_dt), np.datetime64(end_dt)]))
        epochs.append({'time': t_n, 'time_bnds': tb_n, 'source': 'MEaSUREs_ASE', 'path': file_path, 'year': year})
    return epochs

def preprocess_measures_ase(file_path, year, master_x, master_y):
    ds_raw = xr.open_dataset(file_path)
    ds_renamed = ds_raw.assign_coords(x=ds_raw['xaxis'], y=ds_raw['yaxis']).swap_dims({'nx': 'x', 'ny': 'y'})
    vx, vy, err = ds_renamed[f'vx{year}'], ds_renamed[f'vy{year}'], ds_renamed[f'err{year}']
    speed_raw = np.sqrt(vx**2 + vy**2)
    valid_mask = (speed_raw > 0) & (err > 0)
    speed_masked = speed_raw.where(valid_mask, np.nan)
    error_masked = err.where(valid_mask, np.nan)
    speed_interp = speed_masked.interp(x=master_x, y=master_y, method="nearest")
    error_interp = error_masked.interp(x=master_x, y=master_y, method="nearest")
    ds = xr.Dataset({
        'speed': (['time', 'y', 'x'], np.expand_dims(speed_interp.squeeze().values, axis=0), {'units': 'm/year'}),
        'error': (['time', 'y', 'x'], np.expand_dims(error_interp.squeeze().values, axis=0), {'units': 'm/year'}),
        'data_source': (['time'], np.array(["MEaSUREs_ASE"], dtype="<U50"))
    }, coords={'y': (['y'], master_y.values), 'x': (['x'], master_x.values)})
    return ds

# --- 6. SID Annual Processing ---
def parse_sid_annual_time(file_path):
    match = re.search(r'-(\d{4})-fv', os.path.basename(file_path))
    year = int(match.group(1))
    start_dt = datetime(year, 1, 1)
    end_dt = datetime(year, 12, 31, 23, 59, 59)
    mid_dt = start_dt + (end_dt - start_dt) / 2
    return np.datetime64(mid_dt), np.array([np.datetime64(start_dt), np.datetime64(end_dt)])

def preprocess_sid_annual(file_path, master_x, master_y):
    ds_raw = xr.open_dataset(file_path)
    speed_raw = ds_raw['ice_speed'].squeeze()
    error_raw = ds_raw['ice_speed_uncertainty'].squeeze()
    valid_mask = (speed_raw > 0) & (error_raw > 0)
    speed_masked = speed_raw.where(valid_mask, np.nan)
    error_masked = error_raw.where(valid_mask, np.nan)
    speed_interp = speed_masked.interp(x=master_x, y=master_y, method="nearest")
    error_interp = error_masked.interp(x=master_x, y=master_y, method="nearest")
    ds = xr.Dataset({
        'speed': (['time', 'y', 'x'], np.expand_dims(speed_interp.values, axis=0), {'units': 'm/year'}),
        'error': (['time', 'y', 'x'], np.expand_dims(error_interp.values, axis=0), {'units': 'm/year'}),
        'data_source': (['time'], np.array(["SID_annual"], dtype="<U50"))
    }, coords={'y': (['y'], master_y.values), 'x': (['x'], master_x.values)})
    return ds

# --- 7. ESA CCI Annual Processing ---
def parse_esacci_annual_time(file_path):
    match = re.search(r'_(\d{8})_(\d{8})_', os.path.basename(file_path))
    start_dt = datetime.strptime(match.group(1), "%Y%m%d")
    end_dt = datetime.strptime(match.group(2), "%Y%m%d").replace(hour=23, minute=59, second=59)
    mid_dt = start_dt + (end_dt - start_dt) / 2
    return np.datetime64(mid_dt), np.array([np.datetime64(start_dt), np.datetime64(end_dt)])

def preprocess_esacci_annual(file_path, master_x, master_y):
    ds_raw = xr.open_dataset(file_path)
    speed_raw = ds_raw['land_ice_surface_velocity_magnitude'] * 365.25
    error_raw = np.sqrt(ds_raw['land_ice_surface_easting_stddev']**2 + ds_raw['land_ice_surface_northing_stddev']**2) * 365.25
    valid_mask = (speed_raw > 0) & (error_raw > 0)
    speed_masked = speed_raw.where(valid_mask, np.nan)
    error_masked = error_raw.where(valid_mask, np.nan)
    speed_interp = speed_masked.interp(x=master_x, y=master_y, method="nearest")
    error_interp = error_masked.interp(x=master_x, y=master_y, method="nearest")
    ds = xr.Dataset({
        'speed': (['time', 'y', 'x'], np.expand_dims(speed_interp.squeeze().values, axis=0), {'units': 'm/year'}),
        'error': (['time', 'y', 'x'], np.expand_dims(error_interp.squeeze().values, axis=0), {'units': 'm/year'}),
        'data_source': (['time'], np.array(["ESA_CCI_annual"], dtype="<U50"))
    }, coords={'y': (['y'], master_y.values), 'x': (['x'], master_x.values)})
    return ds

# --- 8. Joughin Sentinel-1 Processing ---
def parse_joughin_s1_time(file_path):
    match = re.search(r'S1Quarterly\.(\d{4}-\d{2}-\d{2})\.', os.path.basename(file_path))
    mid_dt = datetime.strptime(match.group(1), "%Y-%m-%d")
    start_dt = mid_dt - timedelta(days=45)
    end_dt = mid_dt + timedelta(days=45)
    return np.datetime64(mid_dt), np.array([np.datetime64(start_dt), np.datetime64(end_dt)])

def preprocess_joughin_s1(vx_path, master_x, master_y):
    vy_path = vx_path.replace('.vx.tif', '.vy.tif')
    vx_da = rioxarray.open_rasterio(vx_path).squeeze(drop=True)
    vy_da = rioxarray.open_rasterio(vy_path).squeeze(drop=True)
    speed_raw = np.sqrt(vx_da**2 + vy_da**2)
    valid_mask = (vx_da > -200000) & (vx_da < 200000) & (vy_da > -200000) & (vy_da < 200000)
    speed_masked = speed_raw.where(valid_mask, np.nan)
    error_masked = speed_masked * 0.05
    speed_interp = speed_masked.interp(x=master_x, y=master_y, method="nearest")
    error_interp = error_masked.interp(x=master_x, y=master_y, method="nearest")
    ds = xr.Dataset({
        'speed': (['time', 'y', 'x'], np.expand_dims(speed_interp.values, axis=0), {'units': 'm/year'}),
        'error': (['time', 'y', 'x'], np.expand_dims(error_interp.values, axis=0), {'units': 'm/year'}),
        'data_source': (['time'], np.array(["Joughin_Sentinel-1"], dtype="<U50"))
    }, coords={'y': (['y'], master_y.values), 'x': (['x'], master_x.values)})
    return ds

# --- 9. Joughin TSX Processing ---
def parse_joughin_tsx_time(file_path):
    match = re.search(r'TSX\.(\d{4}-\d{2}-\d{2})\.', os.path.basename(file_path))
    mid_dt = datetime.strptime(match.group(1), "%Y-%m-%d")
    start_dt = mid_dt - timedelta(days=75)
    end_dt = mid_dt + timedelta(days=75)
    return np.datetime64(mid_dt), np.array([np.datetime64(start_dt), np.datetime64(end_dt)])

def preprocess_joughin_tsx(vx_path, master_x, master_y):
    vy_path = vx_path.replace('.vx.tif', '.vy.tif')
    vx_da = rioxarray.open_rasterio(vx_path).squeeze(drop=True)
    vy_da = rioxarray.open_rasterio(vy_path).squeeze(drop=True)
    speed_raw = np.sqrt(vx_da**2 + vy_da**2)
    valid_mask = (vx_da > -200000) & (vx_da < 200000) & (vy_da > -200000) & (vy_da < 200000)
    speed_masked = speed_raw.where(valid_mask, np.nan)
    error_masked = speed_masked * 0.05
    speed_interp = speed_masked.interp(x=master_x, y=master_y, method="nearest")
    error_interp = error_masked.interp(x=master_x, y=master_y, method="nearest")
    ds = xr.Dataset({
        'speed': (['time', 'y', 'x'], np.expand_dims(speed_interp.values, axis=0), {'units': 'm/year'}),
        'error': (['time', 'y', 'x'], np.expand_dims(error_interp.values, axis=0), {'units': 'm/year'}),
        'data_source': (['time'], np.array(["Joughin_TSX"], dtype="<U50"))
    }, coords={'y': (['y'], master_y.values), 'x': (['x'], master_x.values)})
    return ds

# --- 10. Li Totten Processing ---
def parse_li_totten_time(file_path):
    filename = os.path.basename(file_path)
    match = re.search(r'^(\d{4})(?:_(\d{4}))?_v\.tif$', filename)
    start_year = int(match.group(1))
    end_year = int(match.group(2)) if match.group(2) else start_year
    start_dt = datetime(start_year, 1, 1)
    end_dt = datetime(end_year, 12, 31, 23, 59, 59)
    mid_dt = start_dt + (end_dt - start_dt) / 2
    return np.datetime64(mid_dt), np.array([np.datetime64(start_dt), np.datetime64(end_dt)])

def preprocess_li_totten(file_path, master_x, master_y):
    speed_raw = rioxarray.open_rasterio(file_path).squeeze(drop=True)
    valid_mask = (speed_raw > -200000) & (speed_raw < 200000)
    speed_masked = speed_raw.where(valid_mask, np.nan)
    error_masked = speed_masked * 0.05
    speed_interp = speed_masked.interp(x=master_x, y=master_y, method="nearest")
    error_interp = error_masked.interp(x=master_x, y=master_y, method="nearest")
    ds = xr.Dataset({
        'speed': (['time', 'y', 'x'], np.expand_dims(speed_interp.values, axis=0), {'units': 'm/year'}),
        'error': (['time', 'y', 'x'], np.expand_dims(error_interp.values, axis=0), {'units': 'm/year'}),
        'data_source': (['time'], np.array(["Li_Totten"], dtype="<U50"))
    }, coords={'y': (['y'], master_y.values), 'x': (['x'], master_x.values)})
    return ds

# --- 11. ENVEO Sentinel-1 PIG Processing ---
def parse_enveo_s1_pig_time(file_path):
    match = re.search(r'_(\d{8})_(\d{8})_', os.path.basename(file_path))
    start_dt = datetime.strptime(match.group(1), "%Y%m%d")
    end_dt = datetime.strptime(match.group(2), "%Y%m%d").replace(hour=23, minute=59, second=59)
    mid_dt = start_dt + (end_dt - start_dt) / 2
    return np.datetime64(mid_dt), np.array([np.datetime64(start_dt), np.datetime64(end_dt)])

def preprocess_enveo_s1_pig(file_path, master_x, master_y):
    speed_raw = rioxarray.open_rasterio(file_path).squeeze(drop=True)
    speed_yr = speed_raw * 365.25
    valid_mask = (speed_yr >= 0) & (speed_yr <= 200000)
    speed_masked = speed_yr.where(valid_mask, np.nan)
    error_masked = speed_masked * 0.05
    speed_interp = speed_masked.interp(x=master_x, y=master_y, method="nearest")
    error_interp = error_masked.interp(x=master_x, y=master_y, method="nearest")
    ds = xr.Dataset({
        'speed': (['time', 'y', 'x'], np.expand_dims(speed_interp.values, axis=0), {'units': 'm/year'}),
        'error': (['time', 'y', 'x'], np.expand_dims(error_interp.values, axis=0), {'units': 'm/year'}),
        'data_source': (['time'], np.array(["ENVEO_Sentinel-1_PIG"], dtype="<U50"))
    }, coords={'y': (['y'], master_y.values), 'x': (['x'], master_x.values)})
    return ds

# --- 12. ENVEO ERS Processing ---
def catalog_enveo_ers(base_dir):
    epochs = []
    child_dirs = glob.glob(os.path.join(base_dir, "*_ERS_*"))
    for cdir in child_dirs:
        match = re.search(r's(\d{8})_e(\d{8})', os.path.basename(cdir))
        if not match: continue
        start_dt = datetime.strptime(match.group(1), "%Y%m%d")
        end_dt = datetime.strptime(match.group(2), "%Y%m%d").replace(hour=23, minute=59, second=59)
        mid_dt = start_dt + (end_dt - start_dt) / 2
        
        tifs = [t for t in glob.glob(os.path.join(cdir, "*.tif")) if "_mag" not in os.path.basename(t)]
        for tif in tifs:
            t_n, tb_n = apply_noise(np.datetime64(mid_dt), np.array([np.datetime64(start_dt), np.datetime64(end_dt)]))
            epochs.append({'time': t_n, 'time_bnds': tb_n, 'source': 'ENVEO_ERS', 'path': tif})
    return epochs

def preprocess_enveo_ers(file_path, master_x, master_y):
    da_raw = rioxarray.open_rasterio(file_path)
    vx = da_raw.sel(band=1)
    vy = da_raw.sel(band=2)
    speed_yr = np.sqrt(vx**2 + vy**2) * 365.25
    valid_mask = (speed_yr >= 0) & (speed_yr <= 200000)
    speed_masked = speed_yr.where(valid_mask, np.nan)
    error_masked = speed_masked * 0.05
    speed_masked = speed_masked.drop_vars('band', errors='ignore')
    error_masked = error_masked.drop_vars('band', errors='ignore')
    speed_interp = speed_masked.interp(x=master_x, y=master_y, method="nearest")
    error_interp = error_masked.interp(x=master_x, y=master_y, method="nearest")
    ds = xr.Dataset({
        'speed': (['time', 'y', 'x'], np.expand_dims(speed_interp.values, axis=0), {'units': 'm/year'}),
        'error': (['time', 'y', 'x'], np.expand_dims(error_interp.values, axis=0), {'units': 'm/year'}),
        'data_source': (['time'], np.array(["ENVEO_ERS"], dtype="<U50"))
    }, coords={'y': (['y'], master_y.values), 'x': (['x'], master_x.values)})
    return ds

# --- 13. ENVEO TSX Processing ---
def catalog_enveo_tsx(base_dir):
    epochs = []
    child_dirs = glob.glob(os.path.join(base_dir, "*_TSX_*"))
    for cdir in child_dirs:
        tifs = [t for t in glob.glob(os.path.join(cdir, "*.tif")) if "mag" not in os.path.basename(t).lower()]
        for tif in tifs:
            match = re.search(r'_(\d{8})_(\d{8})_', os.path.basename(tif))
            if not match: continue
            start_dt = datetime.strptime(match.group(1), "%Y%m%d")
            end_dt = datetime.strptime(match.group(2), "%Y%m%d").replace(hour=23, minute=59, second=59)
            mid_dt = start_dt + (end_dt - start_dt) / 2
            t_n, tb_n = apply_noise(np.datetime64(mid_dt), np.array([np.datetime64(start_dt), np.datetime64(end_dt)]))
            epochs.append({'time': t_n, 'time_bnds': tb_n, 'source': 'ENVEO_TSX', 'path': tif})
    return epochs

def preprocess_enveo_tsx(file_path, master_x, master_y):
    da_raw = rioxarray.open_rasterio(file_path)
    vx = da_raw.sel(band=1)
    vy = da_raw.sel(band=2)
    speed_yr = np.sqrt(vx**2 + vy**2) * 365.25
    valid_mask = (speed_yr >= 0) & (speed_yr <= 200000)
    speed_masked = speed_yr.where(valid_mask, np.nan)
    error_masked = speed_masked * 0.05
    speed_masked = speed_masked.drop_vars('band', errors='ignore')
    error_masked = error_masked.drop_vars('band', errors='ignore')
    speed_interp = speed_masked.interp(x=master_x, y=master_y, method="nearest")
    error_interp = error_masked.interp(x=master_x, y=master_y, method="nearest")
    ds = xr.Dataset({
        'speed': (['time', 'y', 'x'], np.expand_dims(speed_interp.values, axis=0), {'units': 'm/year'}),
        'error': (['time', 'y', 'x'], np.expand_dims(error_interp.values, axis=0), {'units': 'm/year'}),
        'data_source': (['time'], np.array(["ENVEO_TSX"], dtype="<U50"))
    }, coords={'y': (['y'], master_y.values), 'x': (['x'], master_x.values)})
    return ds

# --- 14. ENVEO ALOS Processing ---
def catalog_enveo_alos(base_dir):
    epochs = []
    child_dirs = glob.glob(os.path.join(base_dir, "*_ALOS_*"))
    for cdir in child_dirs:
        tifs = [t for t in glob.glob(os.path.join(cdir, "*.tif")) if "mag" not in os.path.basename(t).lower()]
        for tif in tifs:
            match = re.search(r'_(\d{8})_(\d{8})_', os.path.basename(tif))
            if not match: continue
            start_dt = datetime.strptime(match.group(1), "%Y%m%d")
            end_dt = datetime.strptime(match.group(2), "%Y%m%d").replace(hour=23, minute=59, second=59)
            mid_dt = start_dt + (end_dt - start_dt) / 2
            t_n, tb_n = apply_noise(np.datetime64(mid_dt), np.array([np.datetime64(start_dt), np.datetime64(end_dt)]))
            epochs.append({'time': t_n, 'time_bnds': tb_n, 'source': 'ENVEO_ALOS', 'path': tif})
    return epochs

def preprocess_enveo_alos(file_path, master_x, master_y):
    da_raw = rioxarray.open_rasterio(file_path)
    vx = da_raw.sel(band=1)
    vy = da_raw.sel(band=2)
    speed_yr = np.sqrt(vx**2 + vy**2) * 365.25
    valid_mask = (speed_yr >= 0) & (speed_yr <= 200000)
    speed_masked = speed_yr.where(valid_mask, np.nan)
    error_masked = speed_masked * 0.05
    speed_masked = speed_masked.drop_vars('band', errors='ignore')
    error_masked = error_masked.drop_vars('band', errors='ignore')
    speed_interp = speed_masked.interp(x=master_x, y=master_y, method="nearest")
    error_interp = error_masked.interp(x=master_x, y=master_y, method="nearest")
    ds = xr.Dataset({
        'speed': (['time', 'y', 'x'], np.expand_dims(speed_interp.values, axis=0), {'units': 'm/year'}),
        'error': (['time', 'y', 'x'], np.expand_dims(error_interp.values, axis=0), {'units': 'm/year'}),
        'data_source': (['time'], np.array(["ENVEO_ALOS"], dtype="<U50"))
    }, coords={'y': (['y'], master_y.values), 'x': (['x'], master_x.values)})
    return ds

# --- 15. ENVEO TSX-S1 Processing ---
def catalog_enveo_tsx_s1(base_dir):
    epochs = []
    child_dirs = glob.glob(os.path.join(base_dir, "*_TSX-S1_*"))
    for cdir in child_dirs:
        tifs = glob.glob(os.path.join(cdir, "*_mag.tif"))
        for tif in tifs:
            start_dt = datetime(2015, 10, 31)
            end_dt = datetime(2016, 12, 11, 23, 59, 59)
            mid_dt = start_dt + (end_dt - start_dt) / 2
            t_n, tb_n = apply_noise(np.datetime64(mid_dt), np.array([np.datetime64(start_dt), np.datetime64(end_dt)]))
            epochs.append({'time': t_n, 'time_bnds': tb_n, 'source': 'ENVEO_TSX_Sentinel-1', 'path': tif})
    return epochs

def preprocess_enveo_tsx_s1(file_path, master_x, master_y):
    speed_raw = rioxarray.open_rasterio(file_path).squeeze(drop=True)
    speed_yr = speed_raw * 365.25
    valid_mask = (speed_yr > -200000) & (speed_yr < 200000)
    speed_masked = speed_yr.where(valid_mask, np.nan)
    error_masked = speed_masked * 0.05
    speed_interp = speed_masked.interp(x=master_x, y=master_y, method="nearest")
    error_interp = error_masked.interp(x=master_x, y=master_y, method="nearest")
    ds = xr.Dataset({
        'speed': (['time', 'y', 'x'], np.expand_dims(speed_interp.values, axis=0), {'units': 'm/year'}),
        'error': (['time', 'y', 'x'], np.expand_dims(error_interp.values, axis=0), {'units': 'm/year'}),
        'data_source': (['time'], np.array(["ENVEO_TSX_Sentinel-1"], dtype="<U50"))
    }, coords={'y': (['y'], master_y.values), 'x': (['x'], master_x.values)})
    return ds

# --- 16. ENVEO TSX-PALSAR Processing ---
def catalog_enveo_tsx_palsar(base_dir):
    epochs = []
    child_dirs = glob.glob(os.path.join(base_dir, "*_TSX-PALSAR_*"))
    for cdir in child_dirs:
        tifs = glob.glob(os.path.join(cdir, "*_mag.tif"))
        for tif in tifs:
            start_dt = datetime(2010, 7, 2)
            end_dt = datetime(2012, 3, 9, 23, 59, 59)
            mid_dt = start_dt + (end_dt - start_dt) / 2
            t_n, tb_n = apply_noise(np.datetime64(mid_dt), np.array([np.datetime64(start_dt), np.datetime64(end_dt)]))
            epochs.append({'time': t_n, 'time_bnds': tb_n, 'source': 'ENVEO_TSX_PALSAR', 'path': tif})
    return epochs

def preprocess_enveo_tsx_palsar(file_path, master_x, master_y):
    speed_raw = rioxarray.open_rasterio(file_path).squeeze(drop=True)
    speed_yr = speed_raw * 365.25
    valid_mask = (speed_yr > -200000) & (speed_yr < 200000)
    speed_masked = speed_yr.where(valid_mask, np.nan)
    error_masked = speed_masked * 0.05
    speed_interp = speed_masked.interp(x=master_x, y=master_y, method="nearest")
    error_interp = error_masked.interp(x=master_x, y=master_y, method="nearest")
    ds = xr.Dataset({
        'speed': (['time', 'y', 'x'], np.expand_dims(speed_interp.values, axis=0), {'units': 'm/year'}),
        'error': (['time', 'y', 'x'], np.expand_dims(error_interp.values, axis=0), {'units': 'm/year'}),
        'data_source': (['time'], np.array(["ENVEO_TSX_PALSAR"], dtype="<U50"))
    }, coords={'y': (['y'], master_y.values), 'x': (['x'], master_x.values)})
    return ds

# --- 17. SHIFT Processing ---
def parse_shift_time(date_str):
    start_str, end_str = date_str.split('_')
    start_dt = datetime.strptime(start_str, "%Y%m%d")
    end_dt = datetime.strptime(end_str, "%Y%m%d").replace(hour=23, minute=59, second=59)
    mid_dt = start_dt + (end_dt - start_dt) / 2
    return np.datetime64(mid_dt), np.array([np.datetime64(start_dt), np.datetime64(end_dt)])

def read_shift_med(filepath):
    if not os.path.exists(filepath):
        return np.nan
    try:
        with open(filepath, 'r') as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
        if len(lines) < 2: return np.nan
        headers = [h.lower() for h in lines[0].split()]
        values = lines[1].split()
        med_idx = -1
        if 'med' in headers:
            med_idx = headers.index('med')
        elif len(values) >= 6:
            med_idx = 5
        if med_idx != -1 and med_idx < len(values):
            val_str = values[med_idx].lower()
            if val_str in ['nan', 'none', 'null', 'n/a', '-9999', '-1', '-9999.0', '-1.0']:
                return np.nan
            val = float(values[med_idx])
            if np.isnan(val) or val == -9999 or val == -1:
                return np.nan
            return val
    except Exception as e:
        print(f"Warning: Failed to parse error from {filepath}: {e}")
        pass
    return np.nan

def catalog_shift(base_dir):
    epochs = []
    if not os.path.exists(base_dir):
        print(f"Warning: SHIFT base directory not found: {base_dir}")
        return epochs
    for d in os.listdir(base_dir):
        if re.match(r'^\d{8}_\d{8}$', d):
            cdir = os.path.join(base_dir, d)
            if not os.path.isdir(cdir): continue
            date_str = d
            try:
                t, tb = parse_shift_time(date_str)
            except ValueError: continue
            speed_file = os.path.join(cdir, f"S_{date_str}_200m_raw.tif")
            if not os.path.exists(speed_file):
                tifs = [f for f in os.listdir(cdir) if f.startswith('S_') and 'raw.tif' in f.lower()]
                if tifs: speed_file = os.path.join(cdir, tifs[0])
                else: continue
            t_n, tb_n = apply_noise(t, tb)
            epochs.append({
                'time': t_n, 'time_bnds': tb_n, 
                'source': 'SHIFT', 'path': speed_file,
                'epoch_dir': cdir, 'date_str': date_str
            })
    return epochs

def preprocess_shift(file_path, epoch_dir, date_str, master_x, master_y):
    meta_dir = os.path.join(epoch_dir, "metadata")
    speed = rioxarray.open_rasterio(file_path).squeeze('band', drop=True)
    valid_mask = (speed > -200000) & (speed < 200000)
    if speed.rio.nodata is not None: 
        valid_mask = valid_mask & (speed != speed.rio.nodata)
    speed_masked = speed.where(valid_mask, np.nan)
    speed_interp = speed_masked.interp(x=master_x, y=master_y, method="nearest")
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
    if np.isnan(error_scalar):
        error_interp = speed_interp * 0.05
    else:
        error_interp = xr.full_like(speed_interp, error_scalar)
        error_interp = error_interp.where(speed_interp.notnull())
    speed_vals = speed_interp.values
    error_vals = error_interp.values
    ds = xr.Dataset({
        'speed': (['time', 'y', 'x'], np.expand_dims(speed_vals, axis=0), {'units': 'm/year', 'grid_mapping': 'spatial_ref'}),
        'error': (['time', 'y', 'x'], np.expand_dims(error_vals, axis=0), {'units': 'm/year', 'grid_mapping': 'spatial_ref'}),
        'data_source': (['time'], np.array(["SHIFT"], dtype="<U50"))
    }, coords={'y': (['y'], master_y.values), 'x': (['x'], master_x.values)})
    return ds


# --- HPC BUILDER LOGIC ---

def build_catalog_and_skeleton():
    """Run ONCE by a single job to map files and create the multi-scale Zarr skeleton structure."""
    print("Cataloging files and generating noisy unique times...", flush=True)
    epochs = []
    
    # 1. ENVEO
    for f in sorted(glob.glob(os.path.join(ENVEO_DIR, "*.nc"))):
        t, tb = parse_enveo_monthly_time(f)
        t_n, tb_n = apply_noise(t, tb)
        epochs.append({'time': t_n, 'time_bnds': tb_n, 'source': 'ENVEO_monthly', 'path': f})
    # 2. ITS_LIVE
    for f in sorted(glob.glob(os.path.join(ITSLIVE_DIR, "*.nc"))):
        t, tb = parse_itslive_annual_time(f)
        t_n, tb_n = apply_noise(t, tb)
        epochs.append({'time': t_n, 'time_bnds': tb_n, 'source': 'ITS_LIVE_annual', 'path': f})
    # 3. MEaSUREs Annual
    for f in sorted(glob.glob(os.path.join(MEASURES_DIR, "*_1km_v*.nc"))):
        t, tb = parse_measures_annual_time(f)
        t_n, tb_n = apply_noise(t, tb)
        epochs.append({'time': t_n, 'time_bnds': tb_n, 'source': 'MEaSUREs_annual', 'path': f})
    # 4. MEaSUREs Multiyear
    for f in sorted(glob.glob(os.path.join(MEASURES_MULTI_DIR, "*.nc"))):
        t, tb = parse_measures_multiyear_time(f)
        t_n, tb_n = apply_noise(t, tb)
        epochs.append({'time': t_n, 'time_bnds': tb_n, 'source': 'MEaSUREs_multiyear', 'path': f})
    # 5. MEaSUREs ASE
    for f in sorted(glob.glob(os.path.join(MEASURES_ASE_DIR, "*.nc"))):
        epochs.extend(catalog_measures_ase(f))
    # 6. SID Annual
    for f in sorted(glob.glob(os.path.join(SID_ANNUAL_DIR, "*.nc"))):
        t, tb = parse_sid_annual_time(f)
        t_n, tb_n = apply_noise(t, tb)
        epochs.append({'time': t_n, 'time_bnds': tb_n, 'source': 'SID_annual', 'path': f})
    # 7. ESA CCI Annual
    for f in sorted(glob.glob(os.path.join(ESA_CCI_ANNUAL_DIR, "*.nc"))):
        t, tb = parse_esacci_annual_time(f)
        t_n, tb_n = apply_noise(t, tb)
        epochs.append({'time': t_n, 'time_bnds': tb_n, 'source': 'ESA_CCI_annual', 'path': f})
    # 8. Joughin Sentinel-1
    for f in sorted(glob.glob(os.path.join(JOUGHIN_DIR, "VelPIG.S1Quarterly.*.vx.tif"))):
        t, tb = parse_joughin_s1_time(f)
        t_n, tb_n = apply_noise(t, tb)
        epochs.append({'time': t_n, 'time_bnds': tb_n, 'source': 'Joughin_Sentinel-1', 'path': f})
    # 9. Joughin TSX
    for f in sorted(glob.glob(os.path.join(JOUGHIN_DIR, "VelPIG.TSX.*.vx.tif"))):
        t, tb = parse_joughin_tsx_time(f)
        t_n, tb_n = apply_noise(t, tb)
        epochs.append({'time': t_n, 'time_bnds': tb_n, 'source': 'Joughin_TSX', 'path': f})
    # 10. Li Totten
    li_totten_targets = ["1963_1973_v.tif", "1973_1989_v.tif", "1989_v.tif"]
    for filename in li_totten_targets:
        file_path = os.path.join(LI_TOTTEN_DIR, filename)
        if os.path.exists(file_path):
            t, tb = parse_li_totten_time(file_path)
            t_n, tb_n = apply_noise(t, tb)
            epochs.append({'time': t_n, 'time_bnds': tb_n, 'source': 'Li_Totten', 'path': file_path})
    # 11. ENVEO Sentinel-1 PIG
    for f in sorted(glob.glob(os.path.join(ENVEO_S1_PIG_DIR, "*_vv.tif"))):
        t, tb = parse_enveo_s1_pig_time(f)
        t_n, tb_n = apply_noise(t, tb)
        epochs.append({'time': t_n, 'time_bnds': tb_n, 'source': 'ENVEO_Sentinel-1_PIG', 'path': f})
    # 12-16. ENVEO Specials
    epochs.extend(catalog_enveo_ers(ENVEO_OTHERS_DIR))
    epochs.extend(catalog_enveo_tsx(ENVEO_OTHERS_DIR))
    epochs.extend(catalog_enveo_alos(ENVEO_OTHERS_DIR))
    epochs.extend(catalog_enveo_tsx_s1(ENVEO_OTHERS_DIR))
    epochs.extend(catalog_enveo_tsx_palsar(ENVEO_OTHERS_DIR))
    # 17. SHIFT
    epochs.extend(catalog_shift(SHIFT_DIR))
        
    epochs = sorted(epochs, key=lambda d: d['time'])
    total_epochs = len(epochs)
    print(f"Found {total_epochs} total epochs for the FULL build.", flush=True)

    with open(CATALOG_FILE, 'wb') as f:
        pickle.dump(epochs, f)

    print("Extracting master grid from the first ENVEO file...", flush=True)
    first_enveo = next(item['path'] for item in epochs if item['source'] == 'ENVEO_monthly')
    ds_master = preprocess_enveo_monthly(first_enveo)
    
    times = [ep['time'] for ep in epochs]
    time_bnds = [ep['time_bnds'] for ep in epochs]
    
    # Generate multi-scale group skeletons recursively
    current_ds_master = ds_master
    level = 0
    
    while True:
        master_x = current_ds_master['x']
        master_y = current_ds_master['y']
        
        print(f"Initializing skeleton for Group '{level}' | Shape: ({total_epochs}, {master_y.size}, {master_x.size})", flush=True)
        
        # Ensure block boundary adjustments if spatial dims fall below 1024
        ch_y = min(1024, master_y.size)
        ch_x = min(1024, master_x.size)
        level_chunk_def = (1, ch_y, ch_x)
        
        empty_speed = da.empty((total_epochs, master_y.size, master_x.size), chunks=level_chunk_def, dtype=np.float32)
        empty_error = da.empty((total_epochs, master_y.size, master_x.size), chunks=level_chunk_def, dtype=np.float32)
        empty_source = da.full((total_epochs,), "", chunks=(1,), dtype="<U50")

        ds_skeleton = xr.Dataset({
            'speed': (['time', 'y', 'x'], empty_speed, ds_master['speed'].attrs),
            'error': (['time', 'y', 'x'], empty_error, ds_master['error'].attrs),
            'spatial_ref': ([], ds_master['spatial_ref'].values, ds_master['spatial_ref'].attrs),
            'data_source': (['time'], empty_source)
        }, coords={
            'time': (['time'], np.array(times)),
            'time_bnds': (['time', 'bnds'], np.array(time_bnds)),
            'y': (['y'], master_y.values, ds_master['y'].attrs),
            'x': (['x'], master_x.values, ds_master['x'].attrs),
        })

        for var in ['time', 'time_bnds']: ds_skeleton[var].encoding.clear()
        encoding = {'speed': {'chunks': level_chunk_def}, 'error': {'chunks': level_chunk_def}, 'data_source': {'dtype': '<U50'}}
        
        ds_skeleton.to_zarr(OUTPUT_ZARR, group=str(level), compute=False, encoding=encoding, mode='w')
        
        # Termination condition: dataset fits entirely in a single 1024x1024 chunk
        if master_x.size <= 1024 and master_y.size <= 1024:
            print(f"Pyramid architecture target reached at Group '{level}'.", flush=True)
            break
            
        # Coarsen coordinates & layout boundaries by a factor of 2 for next group loop
        current_ds_master = current_ds_master.coarsen(x=2, y=2, boundary='trim').mean(keep_attrs=True)
        level += 1

    # Write explicit OME-Zarr multiscales metadata wrapper onto the Root Group store
    print("Writing root-level OME-Zarr multiscale attributes...", flush=True)
    root_store = zarr.open(OUTPUT_ZARR, mode='a')
    multiscales_metadata = [{
        "version": "0.4",
        "name": "antarctica_ice_velocity_speed",
        "datasets": [{"path": str(lvl)} for lvl in range(level + 1)],
        "type": "local-mean",
        "metadata": {"description": "Multi-source downsampled spatial pyramid levels"}
    }]
    root_store.attrs["multiscales"] = multiscales_metadata
    print("Multi-scale structural skeletons successfully built!", flush=True)


def process_worker(target_source):
    """Run by multiple parallel jobs. Loads catalog, filters by source, and downsamples into array slots."""
    print(f"Worker started for source: {target_source}", flush=True)
    with open(CATALOG_FILE, 'rb') as f:
        epochs = pickle.load(f)
        
    first_enveo = next(item['path'] for item in epochs if item['source'] == 'ENVEO_monthly')
    ds_master = preprocess_enveo_monthly(first_enveo)
    master_x, master_y = ds_master['x'], ds_master['y']
    
    for i, ep in enumerate(epochs):
        if ep['source'] != target_source:
            continue
            
        display_name = f"{os.path.basename(ep['path'])} ({ep.get('year', '')})" if 'year' in ep else os.path.basename(ep['path'])
        print(f"  [{i}/{len(epochs)}] Processing {ep['source']}: {display_name}", flush=True)
        
        # Dispatch to extract level-0 (full resolution) representation 
        if ep['source'] == 'ENVEO_monthly': ds_slice = preprocess_enveo_monthly(ep['path'], master_x, master_y)
        elif ep['source'] == 'ITS_LIVE_annual': ds_slice = preprocess_itslive_annual(ep['path'], master_x, master_y)
        elif ep['source'] == 'MEaSUREs_annual': ds_slice = preprocess_measures_annual(ep['path'], master_x, master_y)
        elif ep['source'] == 'MEaSUREs_multiyear': ds_slice = preprocess_measures_multiyear(ep['path'], master_x, master_y)
        elif ep['source'] == 'MEaSUREs_ASE': ds_slice = preprocess_measures_ase(ep['path'], ep['year'], master_x, master_y)
        elif ep['source'] == 'SID_annual': ds_slice = preprocess_sid_annual(ep['path'], master_x, master_y)
        elif ep['source'] == 'ESA_CCI_annual': ds_slice = preprocess_esacci_annual(ep['path'], master_x, master_y)
        elif ep['source'] == 'Joughin_Sentinel-1': ds_slice = preprocess_joughin_s1(ep['path'], master_x, master_y)
        elif ep['source'] == 'Joughin_TSX': ds_slice = preprocess_joughin_tsx(ep['path'], master_x, master_y)
        elif ep['source'] == 'Li_Totten': ds_slice = preprocess_li_totten(ep['path'], master_x, master_y)
        elif ep['source'] == 'ENVEO_Sentinel-1_PIG': ds_slice = preprocess_enveo_s1_pig(ep['path'], master_x, master_y)
        elif ep['source'] == 'ENVEO_ERS': ds_slice = preprocess_enveo_ers(ep['path'], master_x, master_y)
        elif ep['source'] == 'ENVEO_TSX': ds_slice = preprocess_enveo_tsx(ep['path'], master_x, master_y)
        elif ep['source'] == 'ENVEO_ALOS': ds_slice = preprocess_enveo_alos(ep['path'], master_x, master_y)
        elif ep['source'] == 'ENVEO_TSX_Sentinel-1': ds_slice = preprocess_enveo_tsx_s1(ep['path'], master_x, master_y)
        elif ep['source'] == 'ENVEO_TSX_PALSAR': ds_slice = preprocess_enveo_tsx_palsar(ep['path'], master_x, master_y)
        elif ep['source'] == 'SHIFT': ds_slice = preprocess_shift(ep['path'], ep['epoch_dir'], ep['date_str'], master_x, master_y)
            
        # Push single epoch values sequentially across all initialized resolution tiers
        level = 0
        while True:
            # Isolate 2D raster payload data arrays matching structural shapes 
            ds_to_write = ds_slice.drop_vars(['x', 'y', 'spatial_ref', 'time', 'time_bnds'], errors='ignore')
            ds_to_write.to_zarr(OUTPUT_ZARR, group=str(level), region={'time': slice(i, i+1)})
            
            # Break loop if current layout scale matches the single-chunk threshold condition
            if ds_slice['x'].size <= 1024 and ds_slice['y'].size <= 1024:
                break
                
            # Construct subsequent structural slice downsampled grid properties
            ds_next = xr.Dataset()
            for var in ['speed', 'error']:
                ds_next[var] = ds_slice[var].coarsen(x=2, y=2, boundary='trim').mean(keep_attrs=True)
                
            # Reassign metadata array fields not bound to standard grid definitions
            ds_next['data_source'] = ds_slice['data_source']
            ds_next = ds_next.assign_coords({
                'x': ds_slice['x'].coarsen(x=2, boundary='trim').mean(keep_attrs=True),
                'y': ds_slice['y'].coarsen(y=2, boundary='trim').mean(keep_attrs=True)
            })
            
            ds_slice = ds_next
            level += 1
        
    print(f"Worker for {target_source} completed successfully across all levels!", flush=True)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py [init | process SOURCE_NAME | consolidate]")
        sys.exit(1)
        
    command = sys.argv[1]
    
    if command == "init":
        build_catalog_and_skeleton()
    elif command == "process":
        if len(sys.argv) < 3:
            print("Please provide a data source name. (e.g. python script.py process ENVEO_monthly)")
            sys.exit(1)
        source_target = sys.argv[2]
        process_worker(source_target)
    elif command == "consolidate":
        # Consolidate metadata structures across the store to optimize reads
        zarr.consolidate_metadata(OUTPUT_ZARR)
        print("Zarr metadata consolidated successfully!", flush=True)