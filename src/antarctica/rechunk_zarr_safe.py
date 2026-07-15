import xarray as xr
import dask
from dask.distributed import Client, LocalCluster
import os
import shutil
import argparse

def safe_p2p_rechunk(mode):
    # --- 1. SLURM & CLUSTER SETUP ---
    slurm_cpus = int(os.environ.get('SLURM_CPUS_PER_TASK', 8))
    slurm_mem_mb = int(os.environ.get('SLURM_MEM_PER_NODE', 128000))
    
    # 1 thread per worker is safest for heavy I/O
    cluster = LocalCluster(
        n_workers=slurm_cpus, 
        threads_per_worker=1,
        memory_limit=f"{int(slurm_mem_mb / slurm_cpus)}MB"
    )
    client = Client(cluster)
    
    # CRITICAL: Enable Dask's P2P shuffling for constant-memory rechunking
    dask.config.set({"array.rechunk.method": "p2p"})
    
    print(f"Dask cluster started with {slurm_cpus} workers.")
    print(f"P2P Shuffling Enabled. Dashboard: {client.dashboard_link}")

    # --- 2. PATH DEFINITIONS ---
    base_dir = "/mnt/parscratch/users/gg1bjd/Data/Velocity/Antarctica/multisource_zarr"
    source_path = os.path.join(base_dir, "Antarctica_multisource_speed_spatial_200.zarr")
    
    if mode == "cubed":
        final_path = os.path.join(base_dir, "Antarctica_multisource_speed_cubed.zarr")
    elif mode == "timeseries":
        final_path = os.path.join(base_dir, "Antarctica_multisource_speed_timeseries.zarr")
    else:
        raise ValueError(f"Unknown mode: {mode}")

    temp_target_path = final_path.replace(".zarr", "_temp.zarr")
    backup_path = final_path.replace(".zarr", "_backup.zarr")

    # Clean up orphaned temp directories from previously failed runs
    if os.path.exists(temp_target_path):
        print(f"Cleaning up orphaned temp directory: {temp_target_path}")
        shutil.rmtree(temp_target_path)

    # --- 3. DYNAMIC CHUNK DEFINITIONS ---
    print("Opening source Zarr...")
    # Xarray handles Zarr V3 natively
    ds = xr.open_zarr(source_path)

    # Clear old chunk encodings so Xarray doesn't force the original shapes
    for var in ds.variables:
        if 'chunks' in ds[var].encoding:
            del ds[var].encoding['chunks']

    time_len = ds.sizes['time']
    
    if mode == "cubed":
        chunk_dict = {'time': 300, 'y': 256, 'x': 256}
    elif mode == "timeseries":
        chunk_dict = {'time': time_len, 'y': 64, 'x': 64}

    print(f"Target Chunking -> {chunk_dict}")

    # --- 4. EXECUTE P2P RECHUNK ---
    print("Applying chunk definitions and writing to temporary store...")
    ds_rechunked = ds.chunk(chunk_dict)
    
    # Write to a temporary path to ensure crash-safety
    # Explicitly set zarr_format=3 if you want to ensure the output is V3
    ds_rechunked.to_zarr(temp_target_path, zarr_format=3)

    # --- 5. ATOMIC SWAP ---
    print("Rechunking complete! Performing safe swap...")
    
    if os.path.exists(final_path):
        if os.path.exists(backup_path):
            shutil.rmtree(backup_path) 
        os.rename(final_path, backup_path)
        
    os.rename(temp_target_path, final_path)
    
    if os.path.exists(backup_path):
        shutil.rmtree(backup_path)

    print(f"Success! '{mode.capitalize()}' Zarr is fully updated and ready at: {final_path}")
    client.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Safely rechunk the spatially optimized Zarr store using Dask P2P.")
    parser.add_argument(
        "--mode", 
        type=str, 
        choices=["cubed", "timeseries"], 
        required=True,
        help="Choose the chunking schema: 'cubed' or 'timeseries'"
    )
    
    args = parser.parse_args()
    safe_p2p_rechunk(args.mode)