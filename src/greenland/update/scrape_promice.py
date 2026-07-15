import os
import sys
import json
import requests
import shutil
import glob
from pathlib import Path

# --- CONFIGURATION ---
DATAVERSE_URL = "https://dataverse.geus.dk"
DATASET_DOI = "doi:10.22008/FK2/K70OPK"  # The Persistent ID (DOI) for PROMICE Ice Velocity Edition 5
STAGING_DIR = "/mnt/parscratch/users/gg1bjd/Data/Velocity/Greenland/PROMICE_scratch_new"
MAIN_DIR = "/mnt/parscratch/users/gg1bjd/Data/Velocity/Greenland/PROMICE_edition5"
HISTORY_LOG = "/mnt/parscratch/users/gg1bjd/Data/Velocity/Greenland/ingested_promice_files.json"

def load_ingested_history():
    """Loads the list of downloaded files, or rebuilds it from disk if missing."""
    if os.path.exists(HISTORY_LOG):
        with open(HISTORY_LOG, 'r') as f:
            return set(json.load(f))
            
    # Self-healing fallback: if no history file exists, check the actual directory
    print(f"History log not found. Rebuilding from existing files in {MAIN_DIR}...")
    existing_files = set()
    
    if os.path.exists(MAIN_DIR):
        for file_path in glob.glob(os.path.join(MAIN_DIR, "*.nc")):
            existing_files.add(os.path.basename(file_path))
            
    # Save this newly built list to the JSON file immediately
    update_ingested_history(existing_files)
    print(f"Rebuilt history log with {len(existing_files)} existing files.")
    
    return existing_files

def update_ingested_history(history_set):
    """Saves the updated list of ingested files."""
    with open(HISTORY_LOG, 'w') as f:
        json.dump(list(history_set), f, indent=4)

def fetch_dataverse_metadata():
    """Queries the Dataverse API for the latest dataset files."""
    api_endpoint = f"{DATAVERSE_URL}/api/datasets/:persistentId/?persistentId={DATASET_DOI}"
    
    print(f"Pinging GEUS Dataverse API: {api_endpoint}")
    response = requests.get(api_endpoint)
    
    if response.status_code != 200:
        print(f"CRITICAL ERROR: Failed to reach Dataverse API. Status {response.status_code}")
        sys.exit(1)
        
    return response.json()

def download_file(file_id, filename):
    """Streams the download safely to a staging area, then moves to production."""
    download_url = f"{DATAVERSE_URL}/api/access/datafile/{file_id}"
    staging_path = os.path.join(STAGING_DIR, filename)
    final_path = os.path.join(MAIN_DIR, filename)
    
    print(f"  -> Downloading: {filename} to staging area...")
    
    # 1. Download to the temporary staging directory
    with requests.get(download_url, stream=True) as r:
        r.raise_for_status()
        with open(staging_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192): 
                f.write(chunk)
                
    # 2. Move to the main directory ONLY if download finishes without errors
    shutil.move(staging_path, final_path)
    print(f"  -> Successfully verified and moved to {final_path}")

def run_scraper():
    # Ensure both directories exist
    Path(STAGING_DIR).mkdir(parents=True, exist_ok=True)
    Path(MAIN_DIR).mkdir(parents=True, exist_ok=True)
    
    ingested_files = load_ingested_history()
    dataset_metadata = fetch_dataverse_metadata()
    
    # Drill down into the JSON response to find the file list
    try:
        files_data = dataset_metadata['data']['latestVersion']['files']
    except KeyError:
        print("CRITICAL ERROR: Dataverse API response structure changed.")
        sys.exit(1)
        
    # Filter for NetCDF files and check against our history
    new_files_detected = False
    
    for item in files_data:
        file_info = item.get('dataFile', {})
        filename = file_info.get('filename', '')
        file_id = file_info.get('id')
        
        # We only want .nc files that we haven't seen before
        if filename.endswith('.nc') and filename not in ingested_files:
            new_files_detected = True
            print(f"\n[NEW DATA DETECTED] Found unpublished epoch: {filename}")
            
            try:
                download_file(file_id, filename)
                # Once safely downloaded, add to history so we don't grab it again
                ingested_files.add(filename)
                update_ingested_history(ingested_files)
            except Exception as e:
                print(f"Error downloading {filename}: {e}")
                # We do NOT add it to the history log so it tries again next time
                sys.exit(1)
                
    if not new_files_detected:
        print("No new PROMICE files found on GEUS Dataverse. Pipeline gracefully exiting.")

if __name__ == "__main__":
    run_scraper()