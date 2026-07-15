import os
import glob
import pickle
import sys
import json
import xarray as xr
import numpy as np
import pandas as pd
import zarr
import random

try:
    from citations import CITATIONS_CONFIG
except ImportError:
    print("Warning: Could not import citations. Make sure your PYTHONPATH is set correctly.")
    sys.exit(1)

# --- 1. CONFIGURATION ---
PROMICE_DIR = "/mnt/parscratch/users/gg1bjd/Data/Velocity/Greenland/PROMICE_edition5"
OUTPUT_ZARR = "/mnt/parscratch/users/gg1bjd/Data/Velocity/Greenland/multisource_zarr/Greenland_multisource_speed_spatial_200.zarr"
PKL_CATALOG = "/mnt/parscratch/users/gg1bjd/Data/Velocity/Greenland/multisource_zarr/master_epoch_catalog.pkl"
JSON_CATALOG = "/mnt/parscratch/users/gg1bjd/Data/Velocity/Greenland/multisource_zarr/Greenland_multisource_speed_catalog.json"

# --- HELPERS ---
def apply_noise(t, tb):
    """Adds 1 to 1000 milliseconds of random noise to ensure strictly unique Zarr coordinates."""
    noise = np.timedelta64(random.randint(1, 1000), 'ms')
    return np.datetime64(t) + noise, np.array(tb, dtype='datetime64[ns]') + noise

# --- 2. PROMICE Processing ---
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
    
    ds['speed'] = ds['speed'] * 365.25
    ds['error'] = ds['error'] * 365.25
    
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

# --- 3. IDENTIFY NEW FILES ---
def get_new_promice_files_from_zarr():
    """Identifies new NetCDF files by checking the Zarr store directly."""
    ds_zarr = xr.open_zarr(OUTPUT_ZARR)
    
    promice_mask = ds_zarr['data_source'].values == 'PROMICE'
    zarr_promice_times = ds_zarr['time'].values[promice_mask]
    
    all_nc_files = sorted(glob.glob(os.path.join(PROMICE_DIR, "*.nc")))
    new_files = []
    tolerance = np.timedelta64(2, 's')
    
    for f in all_nc_files:
        with xr.open_dataset(f, decode_times=True) as temp_ds:
            nc_time = temp_ds['time'].values[0]
            
        time_diffs = np.abs(zarr_promice_times - nc_time)
        if not np.any(time_diffs < tolerance):
            new_files.append(f)
            
    return new_files

# --- 4. UPDATE METADATA CATALOGS ---
def build_json_catalog(zarr_path, region):
    print(f"Generating JSON metadata catalog for {zarr_path} (Region: {region})...")
    
    if not os.path.exists(zarr_path):
        print(f"Error: Zarr store not found at {zarr_path}")
        sys.exit(1)

    # 1. Open the fully compiled zarr
    ds = xr.open_zarr(zarr_path, consolidated=True)
    
    # 2. Extract Global Spatial Bounds
    x, y = ds['x'].values, ds['y'].values
    
    # Base catalog structure
    catalog = {
        "dataset_name": f"SHIVER Multi-Source {region.capitalize()} Ice Velocity",
        "spatial_extent": {
            "xmin": float(x.min()),
            "xmax": float(x.max()),
            "ymin": float(y.min()),
            "ymax": float(y.max()),
            "crs": "EPSG:3413"
        },
        "global_citations": CITATIONS_CONFIG.get("common", {}).get("SHIVER", []),
        "sources": {}
    }

    # 3. Clean and isolate unique sources
    sources = ds['data_source'].values
    time_bnds = ds['time_bnds'].values
    
    unique_vals = np.unique(sources)
    actual_sources = [
        str(s) for s in unique_vals 
        if pd.notna(s) and str(s).lower() not in ['nan', 'none', 'unknown', '']
    ]

    region_key = region.lower()
    region_citations = CITATIONS_CONFIG.get(region_key, {})

    # 4. Calculate Stats per Source
    for src in actual_sources:
        # Get boolean mask for this specific source
        idx = (sources == src)
        src_bnds = time_bnds[idx]
        
        # Calculate Epochs
        epochs = int(np.sum(idx))
        
        # Calculate Start and End Date
        start_date = pd.to_datetime(src_bnds[:, 0].min()).strftime('%Y-%m-%d')
        end_date = pd.to_datetime(src_bnds[:, 1].max()).strftime('%Y-%m-%d')
        
        # Calculate Mode Time Separation (dt) in days
        deltas = pd.to_timedelta(src_bnds[:, 1] - src_bnds[:, 0])
        days = np.round(deltas.total_seconds() / 86400.0).astype(int)
        
        mode_val = None
        if len(days) > 0:
            mode_vals = pd.Series(days).mode()
            if not mode_vals.empty:
                mode_val = int(mode_vals.iloc[0])

        # Fetch citation list for this source
        src_citations = region_citations.get(src, [])
        if isinstance(src_citations, str):
            src_citations = [src_citations]

        # Add to catalog
        catalog["sources"][src] = {
            "start_date": start_date,
            "end_date": end_date,
            "epochs": epochs,
            "mode_time_separation_days": mode_val,
            "citations": src_citations
        }

    # 5. Save to Disk
    catalog_out_path = zarr_path.replace('.zarr', '_catalog.json')
    if catalog_out_path == zarr_path:
        catalog_out_path += "_catalog.json"
        
    with open(catalog_out_path, 'w') as f:
        json.dump(catalog, f, indent=4)
        
    print(f"Catalog successfully saved to {catalog_out_path}")

# --- 5. APPEND AND UPDATE ---
def append_new_data(new_files):
    """Processes, applies noise, appends to Zarr, and updates catalogs."""
    if not new_files:
        print("No new PROMICE files detected. Gracefully exiting.")
        sys.exit(0)
        
    print(f"Detected {len(new_files)} new PROMICE files. Beginning append...")
    
    # Load the pickle file if it exists (Optional, for downstream compatibility)
    existing_epochs = []
    if os.path.exists(PKL_CATALOG):
        with open(PKL_CATALOG, 'rb') as f:
            existing_epochs = pickle.load(f)
    
    for i, f in enumerate(new_files):
        print(f"  [{i+1}/{len(new_files)}] Appending {os.path.basename(f)}")
        
        try:
            ds_new = preprocess_promice(f)
            
            t = ds_new['time'].values[0]
            tb = ds_new['time_bnds'].values
            if ds_new['time_bnds'].dims == ('bnds', 'time'):
                tb = ds_new['time_bnds'].transpose('time', 'bnds').values[0]
            else:
                tb = tb[0] if tb.ndim > 1 else tb
                
            t_n, tb_n = apply_noise(t, tb)
            
            ds_new = ds_new.assign_coords(time=[t_n])
            ds_new['time_bnds'].values = [tb_n] if ds_new['time_bnds'].ndim == 2 else tb_n
            
            ds_to_write = ds_new.drop_vars(['x', 'y', 'spatial_ref'], errors='ignore')
            ds_to_write.to_zarr(OUTPUT_ZARR, append_dim='time', mode='a')
            
            existing_epochs.append({
                'time': t_n, 
                'time_bnds': tb_n, 
                'source': 'PROMICE', 
                'path': f
            })
            
            # Save the pickle catalog iteratively to maintain sync
            with open(PKL_CATALOG, 'wb') as pkl_file:
                pickle.dump(existing_epochs, pkl_file)
                
        except Exception as e:
            print(f"Error appending {f}: {e}")
            print("Stopping execution to prevent further corruption.")
            break # Exit the loop, but proceed to rebuild JSON metadata with what succeeded

    # Consolidate the metadata
    zarr.consolidate_metadata(OUTPUT_ZARR)
    print("Zarr metadata consolidated.")
    
    # Update JSON catalog with whatever successfully appended
    build_json_catalog(OUTPUT_ZARR, "greenland")    
    
    print("Append process completed successfully!")

if __name__ == "__main__":
    new_files = get_new_promice_files_from_zarr()
    append_new_data(new_files)