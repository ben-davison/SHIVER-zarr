# Code to generate Unified Dataset from: "The Sheffield Ice Velocity ExploreR (SHIVER): an online tool for low latency exploration, analysis and sub-setting of unified satellite-derived ice velocity data for Earth's ice sheets"

[![DOI](https://zenodo.org/badge/1301557133.svg)](https://doi.org/10.5281/zenodo.21375859)

**NOTE:** This code and the associated manuscript are in preparation and may be subject to change.

## Overview
This repository contains the scripts used to generate the dataset described in the manuscript in preparation: *"The Sheffield Ice Velocity ExploreR (SHIVER): an online tool for low latency exploration, analysis and sub-setting of unified satellite-derived ice velocity data for Earth's ice sheets"*. 

**Note:** This repository only contains the code to generate the dataset. The resulting dataset is hosted by Source Cooperative at https://source.coop/uos-shiver.

## Directory Structure
* `src/` : Contains the Python scripts used to generate the unified dataset.
	* `citations.py` : Provides formatted citation records for each contributing dataset. 
	* `greenland/` 
		* `build_multisource_zarr.py` : Compiles a Zarr store (*spatial_200.zarr) from all contributing datasets for Greenland. The chunk definition is 1024 x 1024 x 1 (x, y, t) and the resolution is 200 x 200 m.
		* `build_multisource_omezarr.py` : Compiles an OME-Zarr store (*spatial.zarr) from all contributing datasets for Greenland. The chunk definition is 1024 x 1024 x 1 (x, y, t) and the resolution is telescopes from 200 m to 3200 m.
		* `rechunk_zarr_safe.py` : Rechunks the *spatial_200.zarr Zarr store to either a time-series optimised (chunk def: 64 x 64 x -1) Zarr or general-purpose Zarr (chunk def: 256 x 256 x 300). 
		* `update/` 
			* `scrape_promice.py` : Download only new PROMICE (edition 5) files.
			* `append_new_promice_to_spatial_200_zarr.py` : Appends new PROMICE files to the spatial_200 Zarr store.
			* `append_new_promice_to_spatial_zarr.py` : Appends new PROMICE files to the spatial OME-Zarr store.
	* `antartica/` 
		* `build_multisource_zarr.py` : Compiles a Zarr store (*spatial_200.zarr) from all contributing datasets for Antarctica. The chunk definition is 1024 x 1024 x 1 (x, y, t) and the resolution is 200 x 200 m.
		* `build_multisource_omezarr.py` : Compiles an OME-Zarr store (*spatial.zarr) from all contributing datasets for Antarctica. The chunk definition is 1024 x 1024 x 1 (x, y, t) and the resolution is telescopes from 200 m to 6400 m.
		* `rechunk_zarr_safe.py` : Rechunks the *spatial_200.zarr Zarr store to either a time-series optimised (chunk def: 64 x 64 x -1) Zarr or general-purpose Zarr (chunk def: 256 x 256 x 300). 
* `requirements.txt` : List of required Python packages.

## Requirements
This code was run using Python 3.11.14. To install the necessary dependencies, you can use conda:
`conda install --file requirements.txt`

## Usage
To reproduce the dataset creation:
1. Download the raw data from the sources given in citations.py.
2. Update the directory paths in each script.
3. Run the scripts. Note the build*.py scripts are designed to run on a HPC, where each contributing dataset is submitted as a separate batch job.

## License
This code is licensed under the GPL-3.0 License - see the [LICENSE](LICENSE) file for details.