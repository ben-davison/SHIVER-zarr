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
OUTPUT_ZARR = "/mnt/parscratch/users/gg1bjd/Data/Velocity/Greenland/multisource_zarr/greenland_multisource_velocity_spatial.zarr"
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
            
    # --- STEP A: Pre-process all new files into a single Level 0 batch ---
    batch_datasets = []
    
    for i, f in enumerate(new_files):
        print(f"  [{i+1}/{len(new_files)}] Pre-processing {os.path.basename(f)}")
        ds_slice = preprocess_promice(f)
        
        # Replicate unique noise logic
        t = ds_slice['time'].values[0]
        tb = ds_slice['time_bnds'].values
        if ds_slice['time_bnds'].dims == ('bnds', 'time'):
            tb = ds_slice['time_bnds'].transpose('time', 'bnds').values[0]
        else:
            tb = tb[0] if tb.ndim > 1 else tb
            
        t_n, tb_n = apply_noise(t, tb)
        
        # Prep the slice with new coordinates
        ds_slice = ds_slice.assign_coords(time=[t_n])
        ds_slice['time_bnds'].values = [tb_n] if ds_slice['time_bnds'].ndim == 2 else tb_n
        
        batch_datasets.append(ds_slice)
        
        # Track epoch history
        existing_epochs.append({
            'time': t_n, 
            'time_bnds': tb_n, 
            'source': 'PROMICE', 
            'path': f
        })
        
    # Combine all individual files into one single Xarray Dataset
    print(f"Concatenating {len(new_files)} files into a single batch for appending...", flush=True)
    ds_batch = xr.concat(batch_datasets, dim='time')
            
    
    # --- STEP B: Iterate through levels, coarsen the batch, and append once per level ---
    for level in existing_levels:
        print(f"Appending batch to Group '{level}'...", flush=True)
        
        # If we are past Level 0, coarsen the entire batch from the previous level
        if level > 0:
            ds_next = xr.Dataset()
            for var in ['speed', 'vx', 'vy', 'speed_error', 'vx_error', 'vy_error']:
                if var in ds_batch and 'y' in ds_batch[var].dims and 'x' in ds_batch[var].dims:
                    ds_next[var] = ds_batch[var].coarsen(x=2, y=2, boundary='pad').mean(keep_attrs=True)
                elif var in ds_batch:
                    ds_next[var] = ds_batch[var]
                    
            if 'data_source' in ds_batch: ds_next['data_source'] = ds_batch['data_source']
            if 'time_bnds' in ds_batch: ds_next['time_bnds'] = ds_batch['time_bnds']
            
            ds_next = ds_next.assign_coords({
                'x': ds_batch['x'].coarsen(x=2, boundary='pad').mean(keep_attrs=True),
                'y': ds_batch['y'].coarsen(y=2, boundary='pad').mean(keep_attrs=True)
            })
            ds_batch = ds_next  # Update the pointer for the next iteration
            
        # Drop fixed spatial variables so we don't overwrite/conflict with the target group
        ds_level_write = ds_batch.drop_vars(['x', 'y', 'spatial_ref'], errors='ignore')
        
        # Clear any lingering file encoding on the batch before writing
        for var in ds_level_write.variables:
            ds_level_write[var].encoding.clear()
        
        # Append the ENTIRE batch at once to the group
        ds_level_write.to_zarr(OUTPUT_ZARR, group=str(level), append_dim='time', mode='a')
        
        
    # --- STEP C: Re-consolidate 1D metadata arrays into single chunks (Zarr v3) ---
    print("Re-consolidating 1D metadata arrays into single chunks...", flush=True)
    z_root = zarr.open(OUTPUT_ZARR, mode='a')

    for level in existing_levels:
        grp = z_root[str(level)]
        
        for var_name in ['time', 'time_bnds', 'data_source']:
            if var_name in grp:
                arr = grp[var_name]
                
                # 1. Read data and preserve attributes
                full_data = arr[:]
                saved_attrs = dict(arr.attrs)
                
                # 2. Overwrite using the Zarr v3 create_array API
                grp.create_array(
                    name=var_name,
                    data=full_data,
                    chunks=full_data.shape,  # Forces a single chunk spanning full length
                    attributes=saved_attrs,
                    overwrite=True
                )
    
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