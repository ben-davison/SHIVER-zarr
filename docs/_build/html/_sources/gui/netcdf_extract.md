(shiver-netcdf-extract)=
# NetCDF Extractor

(netcdf-basic-usage)=
## Basic Usage

The SHIVER Data Cube Extractor lets you quickly and easily extract a 'data cube' of ice velocity measurements for any time period and location on the Greenland and Antarctic ice sheets. Just navigate to your glacier of interest and draw a polygon or upload a shapefile and select your time period and variables/data sources of interest then initiate the download. 

Your download request will be sent to the server and you will be emailed with a download link once the data cube extraction is complete.

SHIVER allows you to extract ice velocity data cubes in Greenland or Antarctica. You can navigate to your preferred ice sheet by clicking the Greenland button ({{ greenlandIcon }}) or the Antarctica button ({{ antarcticaIcon }}).

**Data Cube limits:** To reduce the load on our server, we limit individual data cube extraction volumes to a maximum of 15,000 kilometres squared and one year. If you require a larger data cube, then split your download into multiple requests or contact the SHIVER team via email (shiver@sheffield.ac.uk) with your request.

(netcdf-file-upload)=
## Uploading Files {{ uploadIcon }}

You can upload a file by clicking the {{ uploadIcon }} symbol.

**Requirements:**
* **Format:** KMZ, KML, GeoJSON or a zipped shapefile (containing .shp, .shx, .dbf, and .prj files).
* **Projection:** Must be in WGS84 (EPSG:4326).
* **Type:** Point or Multipoint geometries only. Maximum of ten points.

(netcdf-map-interpret)=
## Navigating & Interpreting the Map

When you first access the SHIVER Data Cube Extractor, you will see a map of Greenland with a long-term average ice speed estimate overlain. You can switch to a map of Antarctica by clicking the Antarctica button ({{ antarcticaIcon }}) in the top-right of the map, or switch back to Greenland by clicking the Greenland button ({{ greenlandIcon }}).

You can navigate the map by using your mouse scroller and by clicking and dragging the cursor to move around. 

**Data overlays:** A long-term average ice speed estimate is shown on the map by default. You can remove that layer and display other overlays by clicking the "Map Layers & Analysis" button ({{ layersIcon }}). There are two modes of layers: "Overview" layers and "Analysis" layers. 

**Overview layers**

The overview layers panel allows you to control the basemap and long-term average overlays of certain variables, as well as display contextual information like glacier basin outlines.

* *Satellite basemap:* A 20 m resolution image mosaic created from true-colour Sentinel-2 imagery acquired during June 1st to August 31st in 2023, 2024 and 2025. This is only available for Greenland.
* *Topography basemap:* A hillshaded digital elevation model of each ice sheet (Howat et al., [2015](https://nsidc.org/data/nsidc-0645/versions/1), [2022](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/EBW8UC)).
* *Speed overlay:* The average ice speed from all available datasets, in metres per year.
* *Measurement Count overlay:* The number of valid speed measurements available in each location.
* *Speed Trend overlay:* The linear trend in speed through all available measurements, in metres per year per year.
* *Measurement Range overlay:* The median spread of speed estimates between data sources during common time periods.
* *Flow direction:* The long term average flow direction of each ice sheet displayed using vector arrows.
* *Ice Margins:* This uses simplified versions of the PROMICE 2022 ice mask ([Luetzenburg et al., 2025](https://essd.copernicus.org/articles/18/411/2026/essd-18-411-2026.html)) for Greenland, the ADD SCAR medium resolution Antarctic coastline ([Gerrish et al., 2025](https://data.bas.ac.uk/items/f2792d06-1e9d-4e00-a5c6-37d43bee5297/)) and the grounding line of [Wallis et al. (2024)](https://tc.copernicus.org/articles/18/4723/2024/).
* *Basin Outlines:* For Greenland, the basin options are the [IMBIE](https://imbie.org/) basins ([Mouginot et al., 2019](https://datadryad.org/dataset/doi:10.7280/D1WT11)), the glacier catchments within each IMBIE basin ([Mouginot et al., 2019](https://datadryad.org/dataset/doi:10.7280/D1WT11)) or individual glacier basins ([Mankoff et al., 2020](https://essd.copernicus.org/articles/12/2811/2020/); [Mankoff, 2020](https://dataverse.geus.dk/dataset.xhtml?persistentId=doi:10.22008/FK2/XKQVL7)). For Antarctica, the basin options are those used in IMBIE ([Mouginot et al., 2017](https://nsidc.org/data/nsidc-0709/versions/2)), the glacier catchments within each IMBIE basin ([Mouginot et al., 2017](https://nsidc.org/data/nsidc-0709/versions/2)) or individual glacier basins on the Peninsula ([Cook et al., 2014](https://doi.org/10.1017/S0954102014000200)). If you zoom in sufficiently on the Antarctic Peninsula, glacier names from the [British Antarctic Territory gazetteer](https://apc.antarctica.ac.uk/gazetteers/go-to-gazetteers/) will be displayed. Note that all basins have been simplified for performance, so the outlines displayed are different to those available in the cited datasets.

**Analysis layers**

The analysis layers panel allows you to display and compare all ice sheet-wide maps of ice flow in our multi-source dataset. This allows you to explore maps of ice motion from any time period, as well as the long-term average maps available in the "Overview" panel. The panel also allows you to calculate and display the change in ice speed between any two maps of ice motion, so you can examine how Greenland and Antarctica have sped up and slowed down in different locations over time. The slider at the bottom of the panel allows you to adjust the colour scale, to maximise the visibility of patterns in your area of interest. 

* *Variable:* Choose "Speed", "Speed Trend" or "Measurement Count".
* *Data Source:* Select which data source to analyse. See the [Greenland Data](/documentation/greenland) and [Antarctic Data](/documentation/antarctic) documentation pages for details of each data source.
* *Measurement Epoch:* If analysing "Speed" you can choose to display a map of speed from any measurement epoch, or the long-term average from your selected data source.
* *Calculate Speed Change:* If analysing "Speed" you can optionally calculate and display a map of speed change compared to any other map of speed. Red areas correspond to speed-up and blue areas correspond to slow-down.

When you click a point on the map an icon will appear showing the extraction location or region. The icon will usually be a square with a point in the centre: the point shows where you clicked and the square shows the region in which data were extracted. The size of this square is controlled by the Advanced Options ({{ advancedIcon }}) "Buffer" setting. The colour of the square corresponds to the site number and will change dynamically depending on the number of points selected.

(netcdf-output)=
## Output

The retrieved data cubes will be in NetCDF format. 

**NetCDF naming convention:**
* IceSheet_multisource_StartTime_EndTime_RANDOM.nc e.g., `Greenland_native_2018-01-01_2018-03-31_6j48egb.nc`. Is a data cube for Greenland from the 1st of January 2018 to the 31st of March 2018.

**Each NetCDF file contains:**  
*Note: Only "x", "y", and "time" are exported by default. Other exported variables depend on the selected options.*

* **x:** The easting coordinates of the grid, in the local projection.
* **y:** The northing coordinates of the grid, in the local projection.
* **time:** The date of the measurement. This represents the mid-date of the measurement epoch.
* **speed:** Horizontal ice surface velocity magnitude in metres per year.
* **vx:** Horizontal ice surface easting velocity in metres per year (positive in the polar stereographic eastwards direction).
* **vy:** Horizontal ice surface northing velocity in metres per year (positive in the polar stereographic northwards direction).
* **speed_error:** Horizontal ice surface velocity magnitude error in metres per year. This is as provided with each of the underlying data sources or 5% of the speed if no error is provided.
* **vx_error:** Horizontal ice surface easting velocity error in metres per year. This is as provided with each of the underlying data sources or 5% of the absolute easting velocity if no error is provided.
* **vy_error:** Horizontal ice surface northing velocity error in metres per year. This is as provided with each of the underlying data sources or 5% of the absolute northing velocity if no error is provided.
* **data_source:** The name of the data source corresponding to each row in 'time' i.e. each measurement epoch in 'speed'.
* **time_separation:** The number of days between the two images used to estimate ice speed. So the first image was acquired on `time-time_separation/2`, and the second image on `time+time_separation/2`.

(netcdf-references)=
## References

> Luetzenburg, Gregor; Korsgaard, Niels J.; Deichmann, Anna K.; Socher, Tobias; Gleie, Karin; Scharffenberger, Thomas; Fahrner, Dominik; Nielsen, Eva B.; How, Penelope; Bjork, Anders A.; Kjeldsen, Kristian K.; Ahlstrom, Andreas P.; Fausto, Robert S., 2025, "PROMICE-2022 Ice Mask", https://doi.org/10.22008/FK2/O8CLRE, GEUS Dataverse, V3.

> Gerrish, L., Ireland, L., Fretwell, P., Cooper, P., & Skachkova, A. (2025). Medium resolution vector polylines of the Antarctic coastline (Version 7.11) [Data set]. NERC EDS UK Polar Data Centre. https://doi.org/10.5285/333065a9-633d-4005-ae41-fb7ae5ae7a91.

> Wallis, B.J., Hogg, A.E., Zhu, Y. and Hooper, A., 2024. Change in grounding line location on the Antarctic Peninsula measured using a tidal motion offset correlation method. The Cryosphere, 18(10), pp.4723-4742. https://doi.org/10.5194/tc-18-4723-2024.

> Howat, Ian, et al., 2022, The Reference Elevation Model of Antarctica - Mosaics, Version 2, https://doi.org/10.7910/DVN/EBW8UC, Harvard Dataverse, V1, [16/02/2026].

> Howat, I., Negrete, A. & Smith, B. (2015). MEaSUREs Greenland Ice Mapping Project (GIMP) Digital Elevation Model. (NSIDC-0645, Version 1). [Data Set]. Boulder, Colorado USA. NASA National Snow and Ice Data Center Distributed Active Archive Center. https://doi.org/10.5067/NV34YUIXLP9W. [describe subset used if applicable]. Date Accessed 02-16-2026.

> Cook AJ, Vaughan DG, Luckman AJ, Murray T. A new Antarctic Peninsula glacier basin inventory and observed area changes since the 1940s. Antarctic Science. 2014;26(6):614-624. doi:10.1017/S0954102014000200

> Mouginot J, Rignot E (2019). Glacier catchments/basins for the Greenland Ice Sheet [Dataset]. Dryad. DOI: 10.7280/D1WT11

> Mankoff, K.D., Noël, B., Fettweis, X., Ahlstrøm, A.P., Colgan, W., Kondo, K., Langley, K., Sugiyama, S., Van As, D. and Fausto, R.S., 2020. Greenland liquid water discharge from 1958 through 2019. Earth System Science Data, 12(4), pp.2811-2841. DOI: https://doi.org/10.5194/essd-12-2811-2020.

> Mankoff, K. D.: Freshwater runoff, GEUS Dataverse, https://doi.org/10.22008/promice/freshwater, 2020.