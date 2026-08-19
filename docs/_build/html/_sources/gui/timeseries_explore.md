(shiver-timeseries)=
# Timeseries Explorer

(timeseries-basic-usage)=
### Basic Usage

The SHIVER Timeseries Explorer lets you quickly and easily visualize and export ice velocity timeseries anywhere on the Greenland and Antarctic ice sheets. Just navigate to your glacier of interest and click on the map to create a chart showing how ice flow has changed over time in that location. 

After selecting a point, you can click-and-drag it to modify the position, or you can manually modify the coordinates in the site list. Alternatively, you can upload a shapefile containing a point or points to view time-series of ice velocity in those locations. You can select up to ten points to compare different locations.

SHIVER allows you to examine ice flow changes in Greenland or Antarctica. You can navigate to your preferred ice sheet by clicking the Greenland button ({{ greenlandIcon }}) or the Antarctica button ({{ antarcticaIcon }}).

**The timeseries chart:** After creating a chart you can click-and-drag in the chart area to zoom in on a particular section of the chart. Double click on the chart to reset the axes. Or use the zoom, pan and reset buttons in the top right of the chart to navigate. You can click the {{ paletteIcon }} icon to colour the data points either by site number or by data source.

(timseries-file-upload)=
### Uploading Files {{ uploadIcon }}

You can upload a file by clicking the {{ uploadIcon }} symbol.

**Requirements:**
* **Format:** KMZ, KML, GeoJSON or a zipped shapefile (containing .shp, .shx, .dbf, and .prj files).
* **Projection:** Must be in WGS84 (EPSG:4326).
* **Type:** Point or Multipoint geometries only. Maximum of ten points.

**Optional:**
* **Buffer:** Include 'buffer' as a field name, containing integer buffer values in metres for each point.
* **Point names:** Include 'name' as a field name to give your outputs a custom name.

(timeseries-advanced-options)=
### Advanced Options {{ advancedIcon }}

You can access the advanced options by clicking the {{ advancedIcon }} symbol.

The advanced options allow you to control which variables and contributing datasets and variables are extracted from our data centre and how they are filtered before being displayed in the chart. See the [Greenland Data](/documentation/greenland) and [Antarctic Data](/documentation/antarctic) documentation pages for details of each data source.

You can modify the parameters used during the ice velocity extraction and filtering. You can adjust the 'buffer' placed around your selection point - larger buffers extract data from larger squares around your selection point. You can also adjust the timeseries smoothing parameters, such as the size of data gaps to fill and the size of the window used in the time-series smoothing.

When you modify anything in the advanced options, your choices will be applied to all subsequent extraction locations. If you want to apply your advanced options to existing extraction locations, then click "Update All Timeseries".

**Buffer distance (m):** When you click a location on the map, data are extracted from a small square centred on your chosen point. The size of that square is controlled by the buffer distance text box. The default value is 500 m, which produces a 1000 x 1000 m box (since we buffer outwards by 500 m from the chosen location). If you want to modify the buffer distance for all of the points, just change the value and click "Update All Timeseries". If you want to modify the buffer distance for just one point, then change the value in the Site List table below the map.

**Variables:**
* **speed:** Extract horizontal ice surface velocity magnitude.
* **vx:** Extract horizontal ice surface easting velocity. Values are positive towards polar stereographic east.
* **vy:** Extract horizontal ice surface northing velocity. Values are positive towards polar stereographic north.

**Smoothing parameters:** 
All time-series extracted with SHIVER are smoothed using a Savitzky-Golay filter. Use the slide bars to modify how much smoothing is applied.
* **Max gap fill length days:** Small gaps in the point data are filled using linear interpolation. Use this option to control the maximum length of gap that is filled.
* **Window size days (Points):** Set the size of the moving window used to smooth the point data displayed on the time-series chart. A larger window increases smoothing.
* **Window size days (Line):** Set the size of the moving window used to smooth the line data displayed on the time-series chart. A larger window increases smoothing.
* **Polynomial order:** Set the degree of the local polynomial fitted to the data within each moving window. A lower order increases smoothing but may distort rapid changes; a higher order better preserved high-frequences features but reduces smoothing.

(timeseries-map-interpret)=
### Navigating & Interpreting the Map

When you first access the SHIVER Timeseries Explorer, you will see a map of Greenland with a long-term average ice speed estimate overlain. You can switch to a map of Antarctica by clicking the Antarctica button ({{ antarcticaIcon }}) in the top-right of the map, or switch back to Greenland by clicking the Greenland button ({{ greenlandIcon }}).

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
* *Ice Margins:* This uses simplified versions of the PROMICE 2022 ice mask ([Luetzenburg et al., 2025](https://essd.copernicus.org/articles/18/411/2026/essd-18-411-2026.html)) for Greenland, the ADD SCAR medium resolution Antarctic coastline ([Gerrish et al., 2025](https://data.bas.ac.uk/items/f2792d06-1e9d-4e00-a5c6-37d43bee5297/)) and the grounding line of [Wallis et al. (2024)](https://tc.copernicus.org/articles/18/4723/2024/)
* *Basin Outlines:* For Greenland, the basin options are the [IMBIE](https://imbie.org/) basins ([Mouginot et al., 2019](https://datadryad.org/dataset/doi:10.7280/D1WT11)), the glacier catchments within each IMBIE basin ([Mouginot et al., 2019](https://datadryad.org/dataset/doi:10.7280/D1WT11)) or individual glacier basins ([Mankoff et al., 2020](https://essd.copernicus.org/articles/12/2811/2020/); [Mankoff, 2020](https://dataverse.geus.dk/dataset.xhtml?persistentId=doi:10.22008/FK2/XKQVL7)). For Antarctica, the basin options are those used in IMBIE ([Mouginot et al., 2017](https://nsidc.org/data/nsidc-0709/versions/2)), the glacier catchments within each IMBIE basin ([Mouginot et al., 2017](https://nsidc.org/data/nsidc-0709/versions/2)) or individual glacier basins on the Peninsula ([Cook et al., 2014](https://doi.org/10.1017/S0954102014000200)). If you zoom in sufficiently on the Antarctic Peninsula, glacier names from the [British Antarctic Territory gazetteer](https://apc.antarctica.ac.uk/gazetteers/go-to-gazetteers/) will be displayed. Note that all basins have been simplified for performance, so the outlines displayed are different to those available in the cited datasets.

**Analysis layers**

The analysis layers panel allows you to display and compare all ice sheet-wide maps of ice flow in our multi-source dataset. This allows you to explore maps of ice motion from any time period, as well as the long-term average maps available in the "Overview" panel. The panel also allows you to calculate and display the change in ice speed between any two maps of ice motion, so you can examine how Greenland and Antarctica have sped up and slowed down in different locations over time. The slider at the bottom of the panel allows you to adjust the colour scale, to maximise the visibility of patterns in your area of interest. 

* *Variable:* Choose "Speed", "Speed Trend" or "Measurement Count".
* *Data Source:* Select which data source to analyse. See the [Greenland Data](/documentation/greenland) and [Antarctic Data](/documentation/antarctic) documentation pages for details of each data source.
* *Measurement Epoch:* If analysing "Speed" you can choose to display a map of speed from any measurement epoch, or the long-term average from your selected data source.
* *Calculate Speed Change:* If analysing "Speed" you can optionally calculate and display a map of speed change compared to any other map of speed. Red areas correspond to speed-up and blue areas correspond to slow-down.

When you click a point on the map an icon will appear showing the extraction location or region. The icon will usually be a square with a point in the centre: the point shows where you clicked and the square shows the region in which data were extracted. The size of this square is controlled by the Advanced Options ({{ advancedIcon }}) "Buffer" setting. The colour of the square corresponds to the site number and will change dynamically depending on the number of points selected.

(timeseries-chart-interpret)=
### Interpreting the Chart

The retrieved data are displayed as both points and a line. Each point represents the average velocity in the selected location over a 6- or 12-day period centred on that time. The corresponding error in that velocity estimate is displayed on the point as a vertical line (indicating the range of potential velocity estimates at that time). The error is defined as the median velocity over bedrock regions at the time. A smoothed, daily velocity time-series is also plotted - this is linearly interpolated from the point data and then smoothed using a Savitzky-Golay filter. 

You can optionally add a linear trend line to each of the selected time-series by clicking the {{ trendIcon }} button below the chart. This will add a dashed line to the chart and the retrieved trends and their significance level will be displayed in the legend. You can use the text boxes to adjust the time period over which the linear trend is calculated. Four levels of trend significance may be displayed in the legend:

* **ns** Not significant.
* **\*** Significant at the 0.05 level (i.e. p<0.05).
* **\*\*** Significant at the 0.01 level (i.e. p<0.01).
* **\*\*\*** Significant at the 0.001 level (i.e. p<0.001).

Use the text boxes below the chart to adjust the x- and y-axis limits. This will also change the .png image exports, however the .xslx will always contain the full time-series.

(timeseries-output)=
### Output

Clicking the map will produce a timeseries showing point data and a smoothed line. The point data provide the measurements taken directly from our ice velocity dataset. The line provides a smoothed representation of those measurements.

{{ graphIcon }} **Download the graph:** 
You can download the graph showing your data by clicking the {{ graphIcon }} button. This will download a .zip containing .png of the graph (or graphs is multiple variables are selected), along with a .txt file and a .csv detailing how to cite the data presented in the graph(s). 

{{ excelIcon }} **Download the data:**
You can also download your data to an excel spreadsheet by clicking the {{ excelIcon }} button. This will download a .zip containing one excel file per location along with a geojson of your point location(s). The .zip will also contain .txt file and a .csv detailing how to cite the data.

**XLSX naming convention:** 
`SiteName_Buffer_Lat_Lon_SmoothingParams.xslx`
e.g., `Site_1_500m_67.123_-48.567_gf24_wr25_wd25_p2.xslx`
*where: gf24 means gap_fill=24 days, wr25 means raw window smoothing length of 25 days, wd25 means a daily window smoothing length of 25 days, and p2 means a second order polynomial in the savitzky-golay smoother was used.*

Each .xlsx file will contain three sheets:
* **Point Data:** A timeseries of each velocity variable, velocity error, image pair time separation (days) and the number of finite values within the extraction area at each epoch. These form the points and whiskers plotted on the chart.
* **Daily Data:** A timeseries of each velocity variable interpolated to daily values. This forms the smooth line on the chart.
* **Metadata:** A table containing the site details.

**Point data output variables:**
*Note: Only "Date", "speed_m_yr", "speed_error_m_yr", "time_separation_days", "pixel_count", and "data_source" are exported by default. Other variables can be enabled for download within the Advanced Options menu, depending on the variables selected.*

* **Date:** The central date of the two images used to estimate ice speed.
* **speed_error_m_yr:** An estimate of the global uncertainty in ice speed at this time period. Defined as the standard deviation of speed over bedrock regions at that time.
* **vx_error_m_yr:** An estimate of the global uncertainty in easting ice velocity at this time period. Defined as the standard deviation of easting ice velocity over bedrock regions at that time.
* **vy_error_m_yr:** An estimate of the global uncertainty in northing ice velocity at this time period. Defined as the standard deviation of northing ice velocity over bedrock regions at that time.
* **time_separation_days:** The number of days between the two images used to estimate ice speed. So the first image was acquired on Date-Time_separation_days/2, and the second image on Date+Time_separation_days/2.
* **pixel_count:** The number of valid speed estimates in the extraction location. This will be 1 if buffer=0. Pixel resolution is 200 metres, so the maximum value for e.g. a 500 m buffer is 25 (1000 x 1000 metre region = 5 x 5 pixel region).
* **speed_m_yr:** Horizontal ice surface velocity magnitude in metres per year. If a buffer is used, the median speed within the resulted area is used.
* **vx_m_yr:** Horizontal ice surface easting velocity in metres per year (positive in the polar stereographic eastwards direction). If a buffer is used, the median velocity within the resulted area is used.
* **vy_m_yr:** Horizontal ice surface northing velocity in metres per year (positive in the polar stereographic northwards direction). If a buffer is used, the median velocity within the resulted area is used.
* **data_source:** The data source label corresponding to every measurement epoch.

**Daily data output variables:**
*Note: Only "Date" and "s_filt" are exported by default. Other variables can be enabled for download within the Advanced Options menu.*

* **Date:** The date of the interpolated velocity.
* **speed_m_ye:** Horizontal ice surface velocity magnitude in metres per year. If a buffer is used, the median speed within the resulted area is used.
* **vx_m_yr:** Horizontal ice surface easting velocity in metres per year (positive in the polar stereographic eastwards direction). If a buffer is used, the median velocity within the resulted area is used.
* **vy_m_yr:** Horizontal ice surface northing velocity in metres per year (positive in the polar stereographic northwards direction). If a buffer is used, the median velocity within the resulted area is used.

(timeseries-references)=
### References

> Luetzenburg, Gregor; Korsgaard, Niels J.; Deichmann, Anna K.; Socher, Tobias; Gleie, Karin; Scharffenberger, Thomas; Fahrner, Dominik; Nielsen, Eva B.; How, Penelope; Bjork, Anders A.; Kjeldsen, Kristian K.; Ahlstrom, Andreas P.; Fausto, Robert S., 2025, "PROMICE-2022 Ice Mask", https://doi.org/10.22008/FK2/O8CLRE, GEUS Dataverse, V3.

> Gerrish, L., Ireland, L., Fretwell, P., Cooper, P., & Skachkova, A. (2025). Medium resolution vector polylines of the Antarctic coastline (Version 7.11) [Data set]. NERC EDS UK Polar Data Centre. https://doi.org/10.5285/333065a9-633d-4005-ae41-fb7ae5ae7a91.

> Wallis, B.J., Hogg, A.E., Zhu, Y. and Hooper, A., 2024. Change in grounding line location on the Antarctic Peninsula measured using a tidal motion offset correlation method. The Cryosphere, 18(10), pp.4723-4742. https://doi.org/10.5194/tc-18-4723-2024.

> Howat, Ian, et al., 2022, The Reference Elevation Model of Antarctica - Mosaics, Version 2, https://doi.org/10.7910/DVN/EBW8UC, Harvard Dataverse, V1, [16/02/2026].

> Howat, I., Negrete, A. & Smith, B. (2015). MEaSUREs Greenland Ice Mapping Project (GIMP) Digital Elevation Model. (NSIDC-0645, Version 1). [Data Set]. Boulder, Colorado USA. NASA National Snow and Ice Data Center Distributed Active Archive Center. https://doi.org/10.5067/NV34YUIXLP9W. Date Accessed 02-16-2026.

> Cook AJ, Vaughan DG, Luckman AJ, Murray T. A new Antarctic Peninsula glacier basin inventory and observed area changes since the 1940s. Antarctic Science. 2014;26(6):614-624. doi:10.1017/S0954102014000200

> Mouginot J, Rignot E (2019). Glacier catchments/basins for the Greenland Ice Sheet [Dataset]. Dryad. DOI: 10.7280/D1WT11

> Mankoff, K.D., Noël, B., Fettweis, X., Ahlstrøm, A.P., Colgan, W., Kondo, K., Langley, K., Sugiyama, S., Van As, D. and Fausto, R.S., 2020. Greenland liquid water discharge from 1958 through 2019. Earth System Science Data, 12(4), pp.2811-2841. DOI: https://doi.org/10.5194/essd-12-2811-2020.

> Mankoff, K. D.: Freshwater runoff, GEUS Dataverse, https://doi.org/10.22008/promice/freshwater, 2020.


