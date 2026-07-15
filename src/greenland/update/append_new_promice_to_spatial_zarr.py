import os
import glob
import pickle
import sys
import xarray as xr
import numpy as np
import zarr
import random

# --- 1. CONFIGURATION ---
PROMICE_DIR = "/mnt/parscratch/users/gg1bjd/Data/Velocity/Greenland/PROMICE_edition5"
OUTPUT_ZARR = "/mnt/parscratch/users/gg1bjd/Data/Velocity/Greenland/multisource_zarr/Greenland_multisource_speed_spatial.zarr"
CATALOG_FILE = "/mnt/parscratch/users/gg1bjd/Data/Velocity/Greenland/multisource_zarr/master_epoch_catalog_spatial.pkl"

# --- HELPERS ---
def apply_noise(t, tb):
    """Adds 1 to 86399 seconds of random noise to ensure strictly unique Zarr coordinates."""
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

# --- 3. IDENTIFY NEW FILES ---
def get_new_promice_files_from_pyramid():
    """Identifies new NetCDF files by checking Group 0 of the OME-Zarr store directly."""
    if not os.path.exists(OUTPUT_ZARR):
        print(f"Error: OME-Zarr store not found at {OUTPUT_ZARR}")
        sys.exit(1)
        
    # Open Group 0 (the full-resolution base layer) lazily
    ds_zarr = xr.open_zarr(OUTPUT_ZARR, group="0")
    
    promice_mask = ds_zarr['data_source'].values == 'PROMICE'
    zarr_promice_times = ds_zarr['time'].values[promice_mask]
    
    all_nc_files = sorted(glob.glob(os.path.join(PROMICE_DIR, "*.nc")))
    new_files = []
    tolerance = np.timedelta64(2, 'D')
    
    for f in all_nc_files:
        with xr.open_dataset(f, decode_times=True) as temp_ds:
            nc_time = temp_ds['time'].values[0]
            
        time_diffs = np.abs(zarr_promice_times - nc_time)
        if not np.any(time_diffs < tolerance):
            new_files.append(f)
            
    return new_files

# --- 4. MULTI-LEVEL APPEND LOOP ---
def append_new_data_to_pyramid(new_files):
    """Processes, downsamples, and appends new epochs to all pyramid levels."""
    if not new_files:
        print("No new PROMICE files detected for OME-Zarr. Gracefully exiting.")
        sys.exit(0)
        
    print(f"Detected {len(new_files)} new PROMICE files. Beginning OME-Zarr append...")
    
    # 1. Inspect the existing Zarr store to find exactly what levels exist
    z_store = zarr.open(OUTPUT_ZARR, mode='r')
    existing_levels = sorted([int(k) for k in z_store.group_keys() if k.isdigit()])
    print(f"Targeting existing Zarr pyramid levels: {existing_levels}")
    
    # Optional: Load the pyramid pickle catalog
    existing_epochs = []
    if os.path.exists(CATALOG_FILE):
        with open(CATALOG_FILE, 'rb') as f:
            existing_epochs = pickle.load(f)
            
    for i, f in enumerate(new_files):
        print(f"  [{i+1}/{len(new_files)}] Appending {os.path.basename(f)} across all pyramid tiers")
        
        # Base full-resolution slice for Level 0
        ds_slice = preprocess_promice(f)
        
        # Replicate unique noise logic
        t = ds_slice['time'].values[0]
        tb = ds_slice['time_bnds'].values
        if ds_slice['time_bnds'].dims == ('bnds', 'time'):
            tb = ds_slice['time_bnds'].transpose('time', 'bnds').values[0]
        else:
            tb = tb[0] if tb.ndim > 1 else tb
            
        t_n, tb_n = apply_noise(t, tb)
        
        # 2. Iterate strictly through the levels that actually exist on disk
        for level in existing_levels:
            
            # If we are past Level 0, coarsen the slice from the previous level
            if level > 0:
                ds_next = xr.Dataset()
                for var in ['speed', 'error']:
                    if 'y' in ds_slice[var].dims and 'x' in ds_slice[var].dims:
                        ds_next[var] = ds_slice[var].coarsen(x=2, y=2, boundary='pad').mean(keep_attrs=True)
                    else:
                        ds_next[var] = ds_slice[var]
                        
                ds_next['data_source'] = ds_slice['data_source']
                ds_next['time_bnds'] = ds_slice['time_bnds']
                ds_next = ds_next.assign_coords({
                    'x': ds_slice['x'].coarsen(x=2, boundary='pad').mean(keep_attrs=True),
                    'y': ds_slice['y'].coarsen(y=2, boundary='pad').mean(keep_attrs=True)
                })
                ds_slice = ds_next  # Update the pointer for the next iteration
            
            # Prep the current level slice for writing
            ds_level_write = ds_slice.assign_coords(time=[t_n])
            ds_level_write['time_bnds'].values = [tb_n] if ds_level_write['time_bnds'].ndim == 2 else tb_n
            
            # Drop fixed spatial variables so we don't overwrite/conflict with the target group
            ds_level_write = ds_level_write.drop_vars(['x', 'y', 'spatial_ref'], errors='ignore')
            
            # Append directly to the group
            ds_level_write.to_zarr(OUTPUT_ZARR, group=str(level), append_dim='time', mode='a')
            
        # Track epoch history
        existing_epochs.append({
            'time': t_n, 
            'time_bnds': tb_n, 
            'source': 'PROMICE', 
            'path': f
        })

    # Save the updated pickle catalog
    with open(CATALOG_FILE, 'wb') as f:
        pickle.dump(existing_epochs, f)
        
    # Consolidate hierarchical Zarr structural mappings
    zarr.consolidate_metadata(OUTPUT_ZARR)
    print("OME-Zarr hierarchy consolidated successfully!")
    print("Pyramid append process completed successfully!")

if __name__ == "__main__":
    new_files = get_new_promice_files_from_pyramid()
    append_new_data_to_pyramid(new_files)