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
OUTPUT_ZARR = "/mnt/parscratch/users/gg1bjd/Data/Velocity/Greenland/multisource_zarr/greenland_multisource_velocity_spatial_200.zarr"
PKL_CATALOG = "/mnt/parscratch/users/gg1bjd/Data/Velocity/Greenland/multisource_zarr/master_epoch_catalog.pkl"
JSON_CATALOG = "/mnt/parscratch/users/gg1bjd/Data/Velocity/Greenland/multisource_zarr/greenland_multisource_velocity_catalog.json"

# --- HELPERS ---
def apply_noise(t, tb):
    """Adds 1 to 1000 milliseconds of random noise to ensure strictly unique Zarr coordinates."""
    noise = np.timedelta64(random.randint(1, 1000), 'ms')
    return np.datetime64(t) + noise, np.array(tb, dtype='datetime64[ns]') + noise

# --- 2. PROMICE Processing ---
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
    """Processes, applies noise, appends batch to Zarr, and updates catalogs."""
    if not new_files:
        print("No new PROMICE files detected. Gracefully exiting.")
        sys.exit(0)
        
    print(f"Detected {len(new_files)} new PROMICE files. Beginning batch append...")
    
    # Load catalog if it exists
    existing_epochs = []
    if os.path.exists(PKL_CATALOG):
        with open(PKL_CATALOG, 'rb') as f:
            existing_epochs = pickle.load(f)
            
    batch_datasets = []
    processed_epochs = []
    
    # --- STEP 1: Pre-process all files into a batch list ---
    for i, f in enumerate(new_files):
        print(f"  [{i+1}/{len(new_files)}] Pre-processing {os.path.basename(f)}")
        try:
            ds_new = preprocess_promice(f)
            
            t = ds_new['time'].values[0]
            tb = ds_new['time_bnds'].values
            if ds_new['time_bnds'].dims == ('bnds', 'time'):
                tb = ds_new['time_bnds'].transpose('time', 'bnds').values[0]
            else:
                tb = tb[0] if tb.ndim > 1 else tb
                
            t_n, tb_n = apply_noise(t, tb)
            
            # Format time coordinates
            ds_new = ds_new.assign_coords(time=[t_n])
            ds_new['time_bnds'].values = [tb_n] if ds_new['time_bnds'].ndim == 2 else tb_n
            
            batch_datasets.append(ds_new)
            processed_epochs.append({
                'time': t_n, 
                'time_bnds': tb_n, 
                'source': 'PROMICE', 
                'path': f
            })
            
        except Exception as e:
            print(f"Error pre-processing {f}: {e}")
            print("Halting batch processing to prevent further store corruption.")
            break

    if not batch_datasets:
        print("No valid datasets were prepared for appending. Exiting.")
        sys.exit(1)

    # --- STEP 2: Concatenate and append batch to Zarr ---
    print(f"Concatenating {len(batch_datasets)} files into a single batch dataset...", flush=True)
    ds_batch = xr.concat(batch_datasets, dim='time')
    
    # Drop fixed spatial variables so we don't conflict with target dataset
    ds_batch = ds_batch.drop_vars(['x', 'y', 'spatial_ref'], errors='ignore')
    
    # Clear lingering encodings from input NetCDF/GeoTIFF files
    for var in ds_batch.variables:
        ds_batch[var].encoding.clear()
        
    print("Writing batch append to Zarr store...", flush=True)
    ds_batch.to_zarr(OUTPUT_ZARR, append_dim='time', mode='a')
    
    # Update and save the catalog for successfully processed files
    existing_epochs.extend(processed_epochs)
    with open(PKL_CATALOG, 'wb') as pkl_file:
        pickle.dump(existing_epochs, pkl_file)

    # --- STEP 3: Re-consolidate 1D metadata arrays into single chunks (Zarr v3 API) ---
    print("Re-consolidating 1D metadata arrays into single chunks...", flush=True)
    z_root = zarr.open(OUTPUT_ZARR, mode='a')

    for var_name in ['time', 'time_bnds', 'data_source']:
        if var_name in z_root:
            arr = z_root[var_name]
            
            # Read full updated array into memory and preserve attributes
            full_data = arr[:]
            saved_attrs = dict(arr.attrs)
            
            # Overwrite array as a single chunk covering full length
            z_root.create_array(
                name=var_name,
                data=full_data,
                chunks=full_data.shape,
                attributes=saved_attrs,
                overwrite=True
            )

    # Consolidate the metadata
    zarr.consolidate_metadata(OUTPUT_ZARR)
    print("Zarr metadata consolidated.")
    
    # Update JSON catalog with whatever successfully appended
    build_json_catalog(OUTPUT_ZARR, "greenland")    
    
    print("Append process completed successfully!")

if __name__ == "__main__":
    new_files = get_new_promice_files_from_zarr()
    append_new_data(new_files)