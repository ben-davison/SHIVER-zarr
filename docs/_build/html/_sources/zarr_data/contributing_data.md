(contributing_data_top)=
# Contributing Datasets

Our ice sheet velocity Zarr stores contain ice velocity estimates that have been generated over years of effort by many research groups. 

(greenland_data)=
## Greenland Data

_There are 17 Contributing Datasets for Greenland, which are summarised in this table:_

**Table 1. Datasets contributing to the Greenland Ice Sheet unified dataset. _Valid as of 30th July 2026_**
| Source Dataset | Start Date | End Date | Epochs | Sep. (days) | Resolution (m) | Citation |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: |
| C3S annual | 01/10/2014 | 30/09/2020 | 6 | 364 | 250 | [1] |
| ESA CCI CSK | 02/06/2012 | 25/12/2014 | 13 | 4 | 250 | [2] |
| ESA CCI ERS1 1991-1992 | 29/12/1991 | 22/03/1992 | 1 | 84 | 500 | [3] |
| ESA CCI ERS1-2 Envisat | 01/08/1991 | 07/02/2011 | 1877 | 35 | 90 | [4-11] |
| ESA CCI ERS2 1995-1996 | 03/09/1995 | 29/03/1996 | 1 | 208 | 90 | [12] |
| ESA CCI PALSAR | 20/12/2006 | 17/03/2011 | 5 | 112 | 90 | [13] |
| ESA CCI Sentinel-1<sup>a</sup> | 10/10/2014 | 22/03/2017 | 1133 | 12 | 250 | [14-22] |
| ESA CCI Sentinel-2<sup>a</sup> | 01/05/2017 | 14/09/2017 | 28 | 14 | 50 | [23-31] |
| ESA CCI winter<sup>c</sup> | 21/01/2014 | 28/02/2018 | 5 | 62 | 500 | [32] |
| ITS LIVE annual | 01/01/1985 | 31/12/2024 | 40 | 364 | 120 | [33, 34] |
| MEaSUREs annual | 01/12/2014 | 30/11/2023 | 9 | 364 | 200 | [35-37] |
| MEaSUREs monthly | 01/12/2014 | 30/11/2024 | 120 | 30 | 200 | [36-38] |
| MEaSUREs qaurterly | 01/12/2014 | 30/11/2024 | 40 | 91 | 200 | [36, 37, 39] |
| MEaSUREs winter | 03/09/2000 | 31/05/2018 | 11 | 272 | 200 | [36, 37, 40] |
| Mouginot annual<sup>a</sup> | 01/07/1972 | 30/06/2017 | 38 | 364 | 90 | [41] |
| PROMICE | 05/01/2016 | 28/06/2026 | 317 | 24 | 200 | [42, 43] |
| SHIFT<sup>d</sup> | 11/10/2014 | 17/01/2026 | 1663 | 12 | 200 | [44, 45] |

<sup>a</sup> Error of all epochs and velocity components assumed to be 5% \
<sup>b</sup> Error for years 2017/2018, 2018/2019 and 2019/2020 provided. Velocity component errors for years 2014/2015, 2015/2016 and 2016/2017 calculated by scaling the velocity magnitude error by the proportional contribution of each velocity component to the velocity magnitude. \
<sup>c</sup> Error provided for all components in winters 2013/2014. All errors assumed to be 5% in winter 2014/2015. Only velocity magnitude error provided in winters 2015/2016, 2016/2017 and 2017/2018, so velocity component errors assumed to be 5%. \
<sup>d</sup> Error is provided as a scalar value defined as the standard deviation of apparent ice motion over bedrock areas. If provided error is NaN for a given epoch, the error is assumed to be 5%.

<em>Citations:</em> <strong>[1]</strong> Copernicus Climate Change Service, Climate Data Store (2020); <strong>[2, 4-11, 23-27, 32]</strong> ESA Greenland Ice Sheet CCI project team (2018a-o); <strong>[3, 12, 13]</strong> ESA Greenland Ice Sheet CCI project team (2016a-c); <strong>[14-22, 28-31]</strong> ESA Greenland Ice Sheet CCI project team (2019a-m); <strong>[33]</strong> Gardner et al. (2025); <strong>[34]</strong> Gardner et al. (2022); <strong>[35, 38, 39]</strong> Joughin (2023a-c); <strong>[36]</strong> Joughin et al. (2010); <strong>[37]</strong> Joughin et al. (2018); <strong>[40]</strong> Joughin et al. (2015); <strong>[41]</strong> Mouginot et al. (2017); <strong>[42, 43]</strong> Solgaard et al. (2021; 2026); <strong>[44]</strong> Davison et al. (2020); <strong>[45]</strong> Sole & Davison (2026).

The sections below provide a brief overview of each of these Contributing Datasets.

(greenland_shift)=
### SHIFT Greenland
The SHIFT data provide 12-day snapshots of ice speed in West Greenland derived from intensity tracking of Sentinel-1 image pairs from 2014 to 2026.

```{figure} ../_static/greenland/verification_maps_SHIFT.png
---
name: shift-greenland-overview-fig
alt: SHIFT Greenland data overview
---
Overview of the Greenland SHIFT data
```

> Sole, A. J. and Davison, B. J. 2026. SHeffield Ice Flow Tracker (SHIFT) velocity data: West Greenland ice surface velocity fields derived from intensity tracking of Sentinel-1 Synthetic Aperture Radar image pairs. [Online]. Available from: https://doi.org/10.15131/shef.data.33113009.v1.

> Davison, B.J., Sole, A.J., Cowton, T.R., Lea, J.M., Slater, D.A., Fahrner, D. and Nienow, P.W., 2020. Subglacial drainage evolution modulates seasonal ice flow variability of three tidewater glaciers in southwest Greenland. Journal of Geophysical Research: Earth Surface, 125(9), p.e2019JF005492. DOI: https://doi.org/10.1029/2019JF005492.

(greenland_promice)=
### PROMICE
The PROMICE data provide 24-day (two consecutive Sentinel-1 cycles) averages of ice speed over Greenland derived from intensity tracking of Sentinel-1 image pairs from 2016 to 2026, with new 24-day averages added every 12 days. We use Edition 5 of the PROMICE mosaics here; these mosaics can be downloaded from the [GEUS Dataverse repository](https://dataverse.geus.dk/dataset.xhtml?persistentId=doi%3A10.22008%2FFK2%2FK70OPK&version=&q=&fileTypeGroupFacet=&fileAccess=&fileSortField=name&fileSortOrder=desc). The PROMICE velocity processing pipeline is described in detail in [Solgaard et al. (2021)](https://essd.copernicus.org/articles/13/3491/2021/).

```{figure} ../_static/greenland/verification_maps_PROMICE.png
---
name: promice-greenland-overview-fig
alt: PROMICE Greenland data overview
---
Overview of the Greenland PROMICE data
```

> Solgaard, A., Kusk, A., Merryman Boncori, J.P., Dall, J., Mankoff, K.D., Ahlstrøm, A.P., Andersen, S.B., Citterio, M., Karlsson, N.B., Kjeldsen, K.K. and Korsgaard, N.J., 2021. Greenland ice velocity maps from the PROMICE project. Earth System Science Data, 13(7), pp.3491-3512. DOI: https://doi.org/10.5194/essd-13-3491-2021.

> Solgaard, Anne Munck; Kusk, Anders, 2026, "Greenland Ice Velocity from Sentinel-1 Edition 5", https://doi.org/10.22008/FK2/K70OPK, GEUS Dataverse, V6.

(greenland_measures_monthly)=
### MEaSUREs monthly

The MEaSUREs data provide monthly averages of ice speed over Greenland derived from a combination of Interferometric SAR (InSAR) and intensity tracking of Sentinel-1 image pairs from 2015 to 2024. The MEaSUREs velocity processing pipeline is described in detail in [Joughin et al. (2018)](https://nsidc.org/data/nsidc-0731/versions/1).

```{figure} ../_static/greenland/verification_maps_MEaSUREs_monthly.png
---
name: verification-maps-measures-monthly-fig
alt: MEaSUREs monthly data overview
---
Overview of the Greenland MEaSUREs monthly data.
```

> Joughin, I. (2023). MEaSUREs Greenland Monthly Ice Sheet Velocity Mosaics from SAR and Landsat. (NSIDC-0731, Version 5). [Data Set]. Boulder, Colorado USA. NASA National Snow and Ice Data Center Distributed Active Archive Center. https://doi.org/10.5067/EGKZX6FXXM4P. Date Accessed 04-21-2026.

> Joughin, I., B. Smith, I. Howat, T. Scambos, and T. Moon. 2010. Greenland flow variability from icesheet-wide velocity mapping, Journal of Glaciology. 56. 415-430. https://doi.org/10.3189/002214310792447734.

> Joughin, I., B. Smith, and I. Howat. 2018. Greenland Ice Mapping Project: ice flow velocity variation at sub-monthly to decadal timescales, The Cryosphere. 12. 2211-2227. https://doi.org/10.5194/tc-12-2211-2018.

(greenland_measures_quarterly)=
### MEaSUREs quarterly

The MEaSUREs data provide quarterly averages of ice speed over Greenland derived from a combination of Interferometric SAR (InSAR) and intensity tracking of Sentinel-1 and TerraSAR-X/TanDEM-X imagery, plus feature tracking of optical imagery acquired by Landsat 8 and Landsat 9. The data are available from 1st December 2014 to 30th November 2024. The MEaSUREs velocity processing pipeline is described in detail in [Joughin et al. (2023)](https://nsidc.org/data/nsidc-0727/versions/5).

```{figure} ../_static/greenland/verification_maps_MEaSUREs_quarterly.png
---
name: verification-maps-measures-quarterly-fig
alt: MEaSUREs quarterly data overview
---
Overview of the Greenland MEaSUREs quarterly data.
```

> Joughin, I. (2023). MEaSUREs Greenland Quarterly Ice Sheet Velocity Mosaics from SAR and Landsat. (NSIDC-0727, Version 5). [Data Set]. Boulder, Colorado USA. NASA National Snow and Ice Data Center Distributed Active Archive Center. https://doi.org/10.5067/V5KW64S63OSN. Date Accessed 04-21-2026.

> Joughin, I., B. Smith, I. Howat, T. Scambos, and T. Moon. 2010. Greenland flow variability from icesheet-wide velocity mapping, Journal of Glaciology. 56. 415-430. https://doi.org/10.3189/002214310792447734.

> Joughin, I., B. Smith, and I. Howat. 2018. Greenland Ice Mapping Project: ice flow velocity variation at sub-monthly to decadal timescales, The Cryosphere. 12. 2211-2227. https://doi.org/10.5194/tc-12-2211-2018.

(greenland_measures_winter)=
### MEaSUREs winter

The MEaSUREs data provide 'winter' averages of ice speed over Greenland derived from Interferometric SAR (InSAR) data obtained by RADARSAT-1, ALOS, TerraSAR-X/TanDEM-X and Sentinel-1A and Sentinel-1B. The data are available for the 2000/2001, 2005-2010, 2012/2013, and 2014-2018 winters. The MEaSUREs velocity processing pipeline is described in detail in [Joughin et al. (2015)](https://nsidc.org/data/nsidc-0478/versions/2).

```{figure} ../_static/greenland/verification_maps_MEaSUREs_winter.png
---
name: verification-maps-measures-winter-fig
alt: MEaSUREs winter data overview
---
Overview of the Greenland MEaSUREs winter data.
```

> Joughin, I., Smith, B., Howat, I. & Scambos, T. (2015). MEaSUREs Greenland Ice Sheet Velocity Map from InSAR Data. (NSIDC-0478, Version 2). [Data Set]. Boulder, Colorado USA. NASA National Snow and Ice Data Center Distributed Active Archive Center. https://doi.org/10.5067/OC7B04ZM9G6Q. Date Accessed 04-23-2026.

> Joughin, I., B. Smith, I. Howat, T. Scambos, and T. Moon. 2010. Greenland flow variability from icesheet-wide velocity mapping, Journal of Glaciology. 56. 415-430. https://doi.org/10.3189/002214310792447734.

> Joughin, I., B. Smith, and I. Howat. 2018. Greenland Ice Mapping Project: ice flow velocity variation at sub-monthly to decadal timescales, The Cryosphere. 12. 2211-2227. https://doi.org/10.5194/tc-12-2211-2018.


(greenland_measures_annual)=
### MEaSUREs annual

The MEaSUREs data provide annual averages of ice speed over Greenland derived from a combination of Interferometric SAR (InSAR) and intensity tracking of Sentinel-1 and TerraSAR-X/TanDEM-X imagery, plus feature tracking of optical imagery acquired by Landsat 8 and Landsat 9. The data are available from 1st December 2014 to 30th November 2023. The MEaSUREs velocity processing pipeline is described in detail in [Joughin et al. (2023)](https://nsidc.org/data/nsidc-0725/versions/5).

```{figure} ../_static/greenland/verification_maps_MEaSUREs_annual.png
---
name: verification-maps-measures-annual-fig
alt: MEaSUREs annual data overview
---
Overview of the Greenland MEaSUREs annual data.
```

> Joughin, I. (2023). MEaSUREs Greenland Annual Ice Sheet Velocity Mosaics from SAR and Landsat. (NSIDC-0725, Version 5). [Data Set]. Boulder, Colorado USA. NASA National Snow and Ice Data Center Distributed Active Archive Center. https://doi.org/10.5067/USBL3Z8KF9C3. Date Accessed 04-21-2026.

> Joughin, I., B. Smith, I. Howat, T. Scambos, and T. Moon. 2010. Greenland flow variability from icesheet-wide velocity mapping, Journal of Glaciology. 56. 415-430. https://doi.org/10.3189/002214310792447734.

> Joughin, I., B. Smith, and I. Howat. 2018. Greenland Ice Mapping Project: ice flow velocity variation at sub-monthly to decadal timescales, The Cryosphere. 12. 2211-2227. https://doi.org/10.5194/tc-12-2211-2018.


(greenland_itslive)=
### ITS_LIVE Annual

The ITS_LIVE annual data provide annual (calendar year) averages of ice speed over Greenland derived from feature tracking applied to a range of satellite missions from 1985 to 2024. The ITS_LIVE velocity processing pipeline is described in [Gardner et al. (2025)](https://tc.copernicus.org/articles/19/3517/2025/) and [Lei et al. (2022)](https://essd.copernicus.org/articles/14/5111/2022/) and the mosaics are available to download from [the ITS_LIVE website](https://nsidc.org/apps/itslive/).

```{figure} ../_static/greenland/verification_maps_ITS_LIVE_annual.png
---
name: verification-maps-its-live-annual-fig
alt: ITS_LIVE annual data overview
---
Overview of the Greenland ITS_LIVE annual data.
```

> Gardner, A.S., Greene, C.A., Kennedy, J.H., Fahnestock, M.A., Liukis, M., López L.A., Lei, Y., Scambos, T.A. and Dehecq, A., 2025. ITS_LIVE global glacier velocity data in near-real time. The Cryosphere, 19(9), pp.3517-3533. DOI: https://doi.org/10.5194/tc-19-3517-2025.

> Gardner, A. S., Fahnestock, M. & Scambos, T. (2022). MEaSUREs ITS_LIVE Regional Glacier and Ice Sheet Surface Velocities. (NSIDC-0776, Version 1). [Data Set]. Boulder, Colorado USA. NASA National Snow and Ice Data Center Distributed Active Archive Center. https://doi.org/10.5067/6II6VW8LLWJ7. Date Accessed 08-17-2026.

(greenland_mouginot_annual)=
### Mouginot Annual

The Mouginot annual data provide annual (July through June) averages of ice speed over Greenland derived from feature tracking applied to a range of satellite missions from 1972 to 2017. The velocity processing pipeline used to produce the mosaics is described in [Mouginot et al. (2017)](https://www.mdpi.com/2072-4292/9/4/364) and the mosaics can be accessed at: [1972-1990](https://datadryad.org/dataset/doi:10.7280/D1MM37), [1991-2000](https://datadryad.org/dataset/doi:10.7280/D1GW91), [2001-2010](https://datadryad.org/dataset/doi:10.7280/D1595V), and [2010-2017](https://datadryad.org/dataset/doi:10.7280/D11H3X).

```{figure} ../_static/greenland/verification_maps_Mouginot_annual.png
---
name: verification-maps-mouginot-annual-fig
alt: Mouginot annual data overview
---
Overview of the Greenland Mouginot annual data.
```

> Mouginot, J., Rignot, E., Scheuchl, B. and Millan, R., 2017. Comprehensive annual ice sheet velocity mapping using Landsat-8, Sentinel-1, and RADARSAT-2 data. Remote Sensing, 9(4), p.364. DOI: https://doi.org/10.3390/rs9040364.

(greenland_c3s_annual)=
### C3S Annual

The Copernicus Climate Change Service (C3S) annual data provide annual (October through September) averages of ice speed over Greenland derived from a combination of SAR interferometry and intensity and coherence tracking applied to Sentinel-1 image pairs acquired during 2014 to 2020. The velocity processing pipeline used to produce the mosaics is described in [Wuite et al. (2026)](https://www.sciencedirect.com/science/article/pii/S0034425725004961) and the mosaics can be accessed [here](https://cds.climate.copernicus.eu/datasets/satellite-greenland-ice-sheet-velocity?tab=download).

```{figure} ../_static/greenland/verification_maps_ENVEO_annual.png
---
name: verification-maps-enveo-annual-fig
alt: C3S annual data overview
---
Overview of the Greenland C3S annual data.
```

> Copernicus Climate Change Service, Climate Data Store (2020): Ice sheet velocity for Antarctica and Greenland derived from satellite observations. Copernicus Climate Change Service (C3S) Climate Data Store (CDS), DOI: 10.24381/cds.0b96b838 (Accessed on 26-Apr-2026).

(greenland_esa_winter)=
### ESA CCI Winter

The ESA CCI Winter data provide winter measurements (from varying months) of ice speed over Greenland derived from RADARSAT and Sentinel-1 image pairs acquired during 2013 to 2018. The mosaics can be accessed at: [2013-2014](https://catalogue.ceda.ac.uk/uuid/9bdeb99d91a743fe84623264587ad043/), [2014-2015](https://catalogue.ceda.ac.uk/uuid/82e4ede59fe746ba810009d9a30e0153/), [2015-2016](https://catalogue.ceda.ac.uk/uuid/302f379334e84664bd3409d08eca6565/), [2016-2017](https://catalogue.ceda.ac.uk/uuid/24dc5d5429434ccdb349db04a1a3233d/) and [2017-2018](https://catalogue.ceda.ac.uk/uuid/eaed9fba86c44e9c854dfbdec9d16b99/).

```{figure} ../_static/greenland/verification_maps_ESA_CCI_winter.png
---
name: verification-maps-esa-cci-winter-fig
alt: ESA CCI Winter data overview
---
Overview of the ESA CCI Winter data.
```

> ESA Greenland Ice Sheet CCI project team (2018): ESA Greenland Ice Sheet Climate Change Initiative (Greenland_Ice_Sheet_cci): Greenland Ice Velocity Map, Winter 2017-2018, v1.0. Centre for Environmental Data Analysis, 16/04/2026. https://catalogue.ceda.ac.uk/uuid/eaed9fba86c44e9c854dfbdec9d16b99

(greenland_esa_ers1_91)=
### ESA CCI ERS-1 (1991-1992)

The ESA CCI ERS-1 (1991-1992) data provide winter measurements of ice speed over Greenland's northern and northwest basins, derived from intensity tracking of ERS-1 Ice phase (3-day repeat) data acquired between 29th December 1991 and 22nd March 1992. The data can be accessed from [ESA Greenland Ice Sheet CCI project team (2016)](https://catalogue.ceda.ac.uk/uuid/e4f39152bc50466f8887bd2a343cac93/).

```{figure} ../_static/greenland/verification_maps_ESA_CCI_ERS1_1991-1992.png
---
name: verification-maps-esa-cci-ers1-1991-1992-fig
alt: ESA CCI ERS-1 (1991-1992) data overview
---
Overview of the ESA CCI ERS-1 (1991-1992) data.
```

> ESA Greenland Ice Sheet CCI project team (2016): ESA Greenland Ice Sheet Climate Change Initiative (Greenland_Ice_Sheet_cci): Ice Velocity data for the Greenland Northern Drainage basin from ERS-1 for winter 1991-1992, v1.1 (June 2016 release). Centre for Environmental Data Analysis, 16/04/2026. https://catalogue.ceda.ac.uk/uuid/e4f39152bc50466f8887bd2a343cac93

(greenland_esa_ers2_95)=
### ESA CCI ERS-2 (1995-1996)

The ESA CCI ERS-2 (1995-1996) data provide winter measurements of ice speed over Greenland's margin, derived from intensity tracking of ERS-2 data acquired between 3rd September 1995 and 29th March 1996. The data can be accessed from [ESA Greenland Ice Sheet CCI project team (2016)](https://catalogue.ceda.ac.uk/uuid/0b23b3c771db4fff8958196432d978cb/).

```{figure} ../_static/greenland/verification_maps_ESA_CCI_ERS2_1995-1996.png
---
name: verification-maps-esa-cci-ers2-1995-1996-fig
alt: ESA CCI ERS-2 (1995-1996) data overview
---
Overview of the ESA CCI ERS-2 (1995-1996) data.
```

> ESA Greenland Ice Sheet CCI project team (2016): ESA Greenland Ice Sheet Climate Change Initiative (Greenland_Ice_Sheet_cci): Ice Velocity data for the Greenland Margin from ERS-2 for winter 1995-1996, v1.1 (June 2016 release). Centre for Environmental Data Analysis, 16/04/2026. https://catalogue.ceda.ac.uk/uuid/0b23b3c771db4fff8958196432d978cb

(greenland_esa_palsar)=
### ESA CCI ALOS-PALSAR

The ESA CCI ALOS-PALSAR data provide winter measurements of ice speed over Greenland's margin, derived from intensity tracking of images acquired using the PALSAR instrument on the ALOS satellite between 20th December 2016 and 17th March 2011. The data can be accessed from [ESA Greenland Ice Sheet CCI project team (2016)](https://catalogue.ceda.ac.uk/uuid/84b5cf8380894d719b61deac5abf3bae/).

```{figure} ../_static/greenland/verification_maps_ESA_CCI_PALSAR.png
---
name: verification-maps-esa-cci-palsar-fig
alt: ESA CCI ALOS-PALSAR data overview
---
Overview of the ESA CCI ALOS-PALSAR data.
```

> ESA Greenland Ice Sheet CCI project team (2016): ESA Greenland Ice Sheet Climate Change Initiative (Greenland_Ice_Sheet_cci): Ice Velocity data for the Greenland Margin from the PALSAR instrument for 2006-2011, v1.1 (June 2016 version). Centre for Environmental Data Analysis, 16/04/2026. https://catalogue.ceda.ac.uk/uuid/84b5cf8380894d719b61deac5abf3bae

(greenland_esa_ers_env)=
### ESA CCI ERS-1/2 & Envisat

The ESA CCI ERS-1/2 & Envisat data provide measurements of ice speed for Hagen Brae, Helheim Glacier, Jakobshavn Isbrae, Kangerlussuaq Glacier, Petermann Glacier, Storstrommen, Upernavik Isstrom and Zachariae Isstrom/79 North Glacier. The measurements have been derived from intensity tracking of ERS-1, ERS-2 and Envisat data acquired between 1991 and 2010 (observation periods vary between glaciers). Upernavik Isstrom also contains velocity estimates derived from PALSAR imagery. The data for each basin can be accessed from: [Jakobshavn Isbrae](https://catalogue.ceda.ac.uk/uuid/a0d9764a3068439b997c42928ef739d2/), [Petermann Glacier](https://catalogue.ceda.ac.uk/uuid/22254b5608ab430fa360d0ff7e71c34e/), [Kangerlussuaq Glacier](https://catalogue.ceda.ac.uk/uuid/723067f77b8b43609079d721e3b4a3c7/), [Helheim Glacier](https://catalogue.ceda.ac.uk/uuid/17767027aa484505b7b732aee6619c74/), [Hagen Brae](https://catalogue.ceda.ac.uk/uuid/27fc79c6e65f4302a18ec9788605c246/), [Storstrommen Glacier](https://catalogue.ceda.ac.uk/uuid/8381d3f3998143fd9b53c7086b7061e3/), [Zachariae and 79 North Glacier](https://catalogue.ceda.ac.uk/uuid/2457272c747f4d6ca33cb40833bd9cc2/), and [Upernavik Isstrom](https://catalogue.ceda.ac.uk/uuid/8d475d7d92894765ad1ddda16de0e610/).

```{figure} ../_static/greenland/verification_maps_ESA_CCI_ERS1-2_Envisat.png
---
name: verification-maps-esa-cci-ers1-2-envisat-fig
alt: ESA CCI ERS-1/2 & Envisat data overview
---
Overview of the ESA CCI ERS-1/2 & Envisat data.
```

> ESA Greenland Ice Sheet CCI project team (2018): ESA Greenland Ice Sheet Climate Change Initiative (Greenland_Ice_Sheet_cci): Ice Velocity time series for the Jakobshavn glacier from ERS-1, ERS2 and ENVISAT data for 1992-2010, v1.2. Centre for Environmental Data Analysis, 16/04/2026. https://catalogue.ceda.ac.uk/uuid/a0d9764a3068439b997c42928ef739d2

> ESA Greenland Ice Sheet CCI project team (2018): ESA Greenland Ice Sheet Climate Change Initiative (Greenland_Ice_Sheet_cci): Ice Velocity time series for the Petermann glacier from ERS-1, ERS-2 and Envisat data for 1991-2010, v1.1. Centre for Environmental Data Analysis, 16/04/2026. https://catalogue.ceda.ac.uk/uuid/22254b5608ab430fa360d0ff7e71c34e

> ESA Greenland Ice Sheet CCI project team (2018): ESA Greenland Ice Sheet Climate Change Initiative (Greenland_Ice_Sheet_cci): Ice Velocity time series for the Kangerlussuaq glacier from ERS-1, ERS-2, Envisat for 1992-2008, v1.0. Centre for Environmental Data Analysis, 16/04/2026. https://catalogue.ceda.ac.uk/uuid/723067f77b8b43609079d721e3b4a3c7

> ESA Greenland Ice Sheet CCI project team (2018): ESA Greenland Ice Sheet Climate Change Initiative (Greenland_Ice_Sheet_cci): Ice Velocity time series for the Helheim glacier from ERS-1, ERS-2 and Envisat data for 1996-2010, v1.1. Centre for Environmental Data Analysis, 16/04/2026. https://catalogue.ceda.ac.uk/uuid/17767027aa484505b7b732aee6619c74

> ESA Greenland Ice Sheet CCI project team (2018): ESA Greenland Ice Sheet Climate Change Initiative (Greenland_Ice_Sheet_cci): Ice Velocity time series for the Hagen glacier from ERS-1, ERS-2 and Envisat data for 1991-2010, v1.1. Centre for Environmental Data Analysis, 16/04/2026. https://catalogue.ceda.ac.uk/uuid/27fc79c6e65f4302a18ec9788605c246

> ESA Greenland Ice Sheet CCI project team (2018): ESA Greenland Ice Sheet Climate Change Initiative (Greenland_Ice_Sheet_cci): Ice Velocity time series of the Storstrommen glacier from ERS-1, ERS-2 and Envisat data for 1991-2010, v1.1. Centre for Environmental Data Analysis, 16/04/2026. https://catalogue.ceda.ac.uk/uuid/8381d3f3998143fd9b53c7086b7061e3

> ESA Greenland Ice Sheet CCI project team (2018): ESA Greenland Ice Sheet Climate Change Initiative (Greenland_Ice_Sheet_cci): Ice Velocity time series for the Zachariae and 79Fjord area from ERS-1, ERS-2 and Envisat data for 1991-2011, v1.1. Centre for Environmental Data Analysis, 16/04/2026. https://catalogue.ceda.ac.uk/uuid/2457272c747f4d6ca33cb40833bd9cc2

> ESA Greenland Ice Sheet CCI project team (2018): ESA Greenland Ice Sheet Climate Change Initiative (Greenland_Ice_Sheet_cci): Ice Velocity time series for the Upernavik glacier from ERS-1, ERS-2, Envisat and PALSAR data for 1992-2010, v1.2. Centre for Environmental Data Analysis, 16/04/2026. https://catalogue.ceda.ac.uk/uuid/8d475d7d92894765ad1ddda16de0e610

(greenland_esa_csk)=
### ESA CCI CSK

The ESA CCI CSK data provide ice speed measurements of Jakobshavn Isbrae, derived from intensity tracking of 4-day repeat images acquired by COSMO-SkyMed between 2nd June 2012 and 25th December 2014. The data can be accessed from [ESA Greenland Ice Sheet CCI project team (2018)](https://catalogue.ceda.ac.uk/uuid/2e54b40f184b44c797db36e192d2b679/).

```{figure} ../_static/greenland/verification_maps_ESA_CCI_CSK.png
---
name: verification-maps-esa-cci-csk-fig
alt: ESA CCI CSK data overview
---
Overview of the ESA CCI CSK data.
```

> ESA Greenland Ice Sheet CCI project team (2018): ESA Greenland Ice Sheet Climate Change Initiative (Greenland_Ice_Sheet_cci): Ice Velocity time series for the Jakobshavn Glacier from COSMO-SkyMed for 2012-2014, v1.0. Centre for Environmental Data Analysis, 16/04/2026. https://catalogue.ceda.ac.uk/uuid/2e54b40f184b44c797db36e192d2b679

(greenland_esa_sentinel2)=
### ESA CCI Sentinel-2

The ESA CCI Sentinel-2 data provide ice speed measurements of 79 North Glacier, Docker Smith, Hagen Brae, Helheim Glacier, Jakobshavn Isbrae, Kangerlussuaq Glacier, Petermann Glacier, Upernavik Isstrom and Zachariae Isstrom. The measurements have been derived from intensity tracking of Sentinel-2 image pairs acquired in 2016 and 2017 (periods vary between glaciers). The data for each basin can be accessed from: [Petermann Glacier](https://catalogue.ceda.ac.uk/uuid/94f3670150de4bac90773806e26646f2/), [Kangerlussuaq Glacier](https://catalogue.ceda.ac.uk/uuid/aae643e1a7614c24b6b604dea82cad93/), [Jakobshavn Isbrae](https://catalogue.ceda.ac.uk/uuid/cfe3102659f34d33b123b2a0043e4068/), [Helehim Isbrae](https://catalogue.ceda.ac.uk/uuid/1e3fcdc14e2246c69fc54f0e1fe7a6ca/), [Zachariae Isstrom](https://catalogue.ceda.ac.uk/uuid/ada968fd392d49fbbb07ac84eeb23ac6/), [Hagen Brae](https://catalogue.ceda.ac.uk/uuid/e7fa45e785a64481960c3b140038c948/), [Docker Smith](https://catalogue.ceda.ac.uk/uuid/88d02eb5a6c14952aa88028894d8a69c/), [79 North Glacier](https://catalogue.ceda.ac.uk/uuid/f31e8e988c4144bebe13892b53d08e42/), and [Upernavik Isstrom](https://catalogue.ceda.ac.uk/uuid/84faf575c8e841a3a16476b05cbd657d/).

```{figure} ../_static/greenland/verification_maps_ESA_CCI_Sentinel-2.png
---
name: verification-maps-esa-cci-sentinel-2-fig
alt: ESA CCI Sentinel-2 data overview
---
Overview of the ESA CCI Sentinel-2 data.
```

> ESA Greenland Ice Sheet CCI project team (2019): ESA Greenland Ice Sheet Climate Change Initiative (Greenland_Ice_Sheet_cci): Optical ice velocity of the Petermann Glacier between 2017-05-01 and 2017-09-14, generated using Sentinel-2 data, v1.1. Centre for Environmental Data Analysis, 16/04/2026. https://catalogue.ceda.ac.uk/uuid/94f3670150de4bac90773806e26646f2

> ESA Greenland Ice Sheet CCI project team (2018): ESA Greenland Ice Sheet Climate Change Initiative (Greenland_Ice_Sheet_cci): Optical ice velocity of the Kangerlussuaq Glacier between 2017-07-21 and 2017-08-20, generated using Sentinel-2 data, v1.1. Centre for Environmental Data Analysis, 16/04/2026. https://catalogue.ceda.ac.uk/uuid/aae643e1a7614c24b6b604dea82cad93

> ESA Greenland Ice Sheet CCI project team (2018): ESA Greenland Ice Sheet Climate Change Initiative (Greenland_Ice_Sheet_cci): Optical ice velocity of the Jakobshavn Glacier between 2017-06-03 and 2017-09-08, generated using Sentinel-2 data, v1.1. Centre for Environmental Data Analysis, 16/04/2026. https://catalogue.ceda.ac.uk/uuid/cfe3102659f34d33b123b2a0043e4068

> ESA Greenland Ice Sheet CCI project team (2019): ESA Greenland Ice Sheet Climate Change Initiative (Greenland_Ice_Sheet_cci): Optical ice velocity of the Helheim Glacier between 2017-05-01 and 2017-08-29, generated using Sentinel-2 data, v1.1. Centre for Environmental Data Analysis, 16/04/2026. https://catalogue.ceda.ac.uk/uuid/1e3fcdc14e2246c69fc54f0e1fe7a6ca

> ESA Greenland Ice Sheet CCI project team (2019): ESA Greenland Ice Sheet Climate Change Initiative (Greenland_Ice_Sheet_cci): Optical ice velocity of the Zachariae Glacier between 2017-06-25 and 2017-08-10, generated using Sentinel-2 data, v1.1. Centre for Environmental Data Analysis, 16/04/2026. https://catalogue.ceda.ac.uk/uuid/ada968fd392d49fbbb07ac84eeb23ac6

> ESA Greenland Ice Sheet CCI project team (2018): ESA Greenland Ice Sheet Climate Change Initiative (Greenland_Ice_Sheet_cci): Optical ice velocity of the Hagen Glacier between 2017-06-30 and 2017-08-14, generated using Sentinel-2 data, v1.1. Centre for Environmental Data Analysis, 16/04/2026. https://catalogue.ceda.ac.uk/uuid/e7fa45e785a64481960c3b140038c948

> ESA Greenland Ice Sheet CCI project team (2019): ESA Greenland Ice Sheet Climate Change Initiative (Greenland_Ice_Sheet_cci): Optical ice velocity of the Døcker Smith Glacier between 2016-05-08 and 2016-05-18, generated using Sentinel-2 data, v1.0. Centre for Environmental Data Analysis, 16/04/2026. https://catalogue.ceda.ac.uk/uuid/88d02eb5a6c14952aa88028894d8a69c

> ESA Greenland Ice Sheet CCI project team (2018): ESA Greenland Ice Sheet Climate Change Initiative (Greenland_Ice_Sheet_cci): Optical ice velocity of the 79Fjord Glacier between 2017-06-25 and 2017-08-10, generated using Sentinel-2 data, v1.1. Centre for Environmental Data Analysis, 16/04/2026. https://catalogue.ceda.ac.uk/uuid/f31e8e988c4144bebe13892b53d08e42

> ESA Greenland Ice Sheet CCI project team (2018): ESA Greenland Ice Sheet Climate Change Initiative (Greenland_Ice_Sheet_cci): Optical ice velocity of the Upernavik Glacier between 2017-07-15 and 2017-08-14, generated using Sentinel-2 data, v1.1. Centre for Environmental Data Analysis, 16/04/2026. https://catalogue.ceda.ac.uk/uuid/84faf575c8e841a3a16476b05cbd657d

(greenland_esa_sentinel1)=
### ESA CCI Sentinel-1

The ESA CCI Sentinel-1 data provide ice speed measurements of 79 North Glacier, Storstrommen, Hagen Brae, Helheim Glacier, Jakobshavn Isbrae, Kangerlussuaq Glacier, Petermann Glacier, Upernavik Isstrom and Zachariae Isstrom. The measurements have been derived from intensity tracking of Sentinel-1 image pairs acquired in 2014 and 2017 (periods vary between glaciers). The data for each basin can be accessed from: [Petermann Glacier](https://catalogue.ceda.ac.uk/uuid/81332b9a10f14bda8a1a83b6463bb6de/), [Kangerlussuaq Glacier](https://catalogue.ceda.ac.uk/uuid/925e3f0e807243e2936cc492f5207af6/), [Jakobshavn Isbrae](https://catalogue.ceda.ac.uk/uuid/e1c0c34e0cc942898b3626efd1dcc095/), [Helehim Isbrae](https://catalogue.ceda.ac.uk/uuid/0e289294f2c141bca545cd9d7fcb62d0/), [Zachariae Isstrom](https://catalogue.ceda.ac.uk/uuid/e3dbdc32f7b6476e949d52d8d3990205/), [Hagen Brae](https://catalogue.ceda.ac.uk/uuid/5c9935b8b8854baeb7a256446293c03b/), [Storstrommen](https://catalogue.ceda.ac.uk/uuid/1dd4c30a78d84e628cd8097bae3148fd/), [79 North Glacier](https://catalogue.ceda.ac.uk/uuid/41e2300068b44fa190f24272dc08dcd0/), and [Upernavik Isstrom](https://catalogue.ceda.ac.uk/uuid/ef5c6596cae548c6aea9dea181c7624c/).

```{figure} ../_static/greenland/verification_maps_ESA_CCI_Sentinel-1.png
---
name: verification-maps-esa-cci-sentinel-1-fig
alt: ESA CCI Sentinel-1 data overview
---
Overview of the ESA CCI Sentinel-1 data.
```

> ESA Greenland Ice Sheet CCI project team (2019): ESA Greenland Ice Sheet Climate Change Initiative (Greenland_Ice_Sheet_cci): Ice Velocity time series for the Petermann Glacier for 2015-2017 from Sentinel-1 data, v1.1. Centre for Environmental Data Analysis, 16/04/2026. https://catalogue.ceda.ac.uk/uuid/81332b9a10f14bda8a1a83b6463bb6de

> ESA Greenland Ice Sheet CCI project team (2019): ESA Greenland Ice Sheet Climate Change Initiative (Greenland_Ice_Sheet_cci): Ice Velocity time series for the Kangerlussuaq Glacier for 2015-2017 from Sentinel-1, v1.1. Centre for Environmental Data Analysis, 16/04/2026. https://catalogue.ceda.ac.uk/uuid/925e3f0e807243e2936cc492f5207af6

> ESA Greenland Ice Sheet CCI project team (2019): ESA Greenland Ice Sheet Climate Change Initiative (Greenland_Ice_Sheet_cci): Ice Velocity time series for the Jakobshavn Glacier for 2014-2017 from Sentinel-1 data, v1.1. Centre for Environmental Data Analysis, 16/04/2026. https://catalogue.ceda.ac.uk/uuid/e1c0c34e0cc942898b3626efd1dcc095

> ESA Greenland Ice Sheet CCI project team (2019): ESA Greenland Ice Sheet Climate Change Initiative (Greenland_Ice_Sheet_cci): Ice Velocity time series for the Helheim Glacier for 2015-2017 from Sentinel-1 data, v1.1. Centre for Environmental Data Analysis, 16/04/2026. https://catalogue.ceda.ac.uk/uuid/0e289294f2c141bca545cd9d7fcb62d0

> ESA Greenland Ice Sheet CCI project team (2019): ESA Greenland Ice Sheet Climate Change Initiative (Greenland_Ice_Sheet_cci): Ice Velocity time series for the Zachariae Glacier for 2015-2017 from Sentinel-1 data, v1.1. Centre for Environmental Data Analysis, 16/04/2026. https://catalogue.ceda.ac.uk/uuid/e3dbdc32f7b6476e949d52d8d3990205

> ESA Greenland Ice Sheet CCI project team (2019): ESA Greenland Ice Sheet Climate Change Initiative (Greenland_Ice_Sheet_cci): Ice Velocity time series for the Hagen Glacier for 2015-2017 from Sentinel-1 data, v1.1. Centre for Environmental Data Analysis, 16/04/2026. https://catalogue.ceda.ac.uk/uuid/5c9935b8b8854baeb7a256446293c03b

> ESA Greenland Ice Sheet CCI project team (2019): ESA Greenland Ice Sheet Climate Change Initiative (Greenland_Ice_Sheet_cci): Ice Velocity time series for the Storstroemmen Glacier for 2015-2017 from Sentinel-1 data, v1.1. Centre for Environmental Data Analysis, 16/04/2026. https://catalogue.ceda.ac.uk/uuid/1dd4c30a78d84e628cd8097bae3148fd

> ESA Greenland Ice Sheet CCI project team (2019): ESA Greenland Ice Sheet Climate Change Initiative (Greenland_Ice_Sheet_cci): Ice Velocity time series for the 79-Fjord Glacier for 2015-2017 from Sentinel-1 data, v1.1. Centre for Environmental Data Analysis, 16/04/2026. https://catalogue.ceda.ac.uk/uuid/41e2300068b44fa190f24272dc08dcd0

> ESA Greenland Ice Sheet CCI project team (2019): ESA Greenland Ice Sheet Climate Change Initiative (Greenland_Ice_Sheet_cci): Ice Velocity time series for the Upernavik Glacier for 2014-2017 from Sentinel-1 data, v1.1. Centre for Environmental Data Analysis, 16/04/2026. https://catalogue.ceda.ac.uk/uuid/ef5c6596cae548c6aea9dea181c7624c


(antarctica_data)=
## Antarctica Data
_There are 17 Contributing Datasets for Antarctica, which are summarised in this table:_

**Table 2. Datasets contributing to the Antarctic Ice Sheet unified dataset. _Valid as of 30th July 2026_**
| Source Dataset | Start Date | End Date | Epochs | Sep. (days) | Resolution (m) | Citation |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: |
| ENVEO PALSAR<sup>a</sup> | 29/09/2009 | 17/02/2011 | 2 | 47 | 50 | [1] |
| ENVEO ERS<sup>a</sup> | 11/01/1992 | 10/11/1999 | 13 | 2 | 500 | [2, 3] |
| ENVEO Sentinel-1 PIG<sup>a</sup> | 10/10/2014 | 21/08/2019 | 402 | 13 | 200 | [4] |
| ENVEO TSX<sup>a</sup> | 26/06/2007 | 11/12/2016 | 125 | 12 | 50 | [1] |
| ENVEO TSX PALSAR<sup>a</sup> | 02/07/2010 | 09/03/2012 | 1 | 617 | 50 | [1] |
| ENVEO TSX Sentinel-1<sup>a</sup> | 31/10/2015 | 11/12/2016 | 1 | 408 | 50 | [1] |
| ENVEO monthly | 01/10/2014 | 31/12/2021 | 87 | 30 | 200 | [4] |
| C3S annual | 01/04/2021 | 31/03/2024 | 3 | 365 | 200 | [5] |
| ITS LIVE annual | 01/01/1985 | 31/12/2024 | 40 | 365 | 120 | [6, 7] |
| Joughin Sentinel-1<sup>a</sup> | 01/04/2015 | 29/09/2020 | 22 | 90 | 500 | [8] |
| Joughin TSX<sup>a</sup> | 06/02/2009 | 24/12/2015 | 13 | 106 | 500 | [8] |
| Li Totten<sup>a</sup> | 01/01/1963 | 31/12/1989 | 3 | 365 | 1000 | [8] |
| MEaSUREs ASE | 01/01/1996 | 31/12/2012 | 10 | 365 | 450 | [64], [10, 11] |
| MEaSUREs annual | 01/07/2000 | 30/06/2025 | 21 | 365 | 1000 | [12, 13] |
| MEaSUREs multiyear | 01/07/1995 | 30/06/2022 | 4 | 730 | 450 | [14, 15] |
| SHIFT<sup>c</sup> | 25/11/2014 | 20/01/2026 | 2033 | 13 | 200 | [16, 17] |
| SID annual<sup>d</sup> | 01/01/2015 | 31/12/2024 | 10 | 365 | 250 | [18, 19] |

<sup>a</sup> Error of all epochs and velocity components assumed to be 5% \
<sup>b</sup> Error calculated by scaling the velocity magnitude error by the proportional contribution of each velocity component to the velocity magnitude. \
<sup>c</sup> Error is provided as a scalar value defined as the standard deviation of apparent ice motion over bedrock areas. If provided error is NaN for a given epoch, the error is assumed to be 5%. \
<sup>d</sup> No velocity component data provided, so are assumed to be NaN.

Citations: <strong>[1]</strong> Rott et al.  (2018); <strong>[2]</strong> Rott et al. (2011); <strong>[3]</strong> Wuite et al. (2015); <strong>[4]</strong> Wuite et al. (2026); <strong>[5]</strong> Copernicus Climate Change Service, Climate Data Store (2020); <strong>[6]</strong> Gardner et al. (2025); <strong>[7]</strong> Gardner et al. (2022); <strong>[8]</strong> Joughin et al. (2021); <strong>[9]</strong> Li et al. (2023); <strong>[10]</strong> Rignot et al. (2014); <strong>[11]</strong> Mouginot et al. (2014); <strong>[12, 13]</strong> Mouginot et al. (2017a; 2017b); <strong>[14, 15]</strong> Rignot et al. (2022a; 2022b); <strong>[16]</strong> Davison et al. (2020); <strong>[17]</strong> Davison & Sole (2026); <strong>[18]</strong> Hogg et al. (2025); <strong>[19]</strong> Davison et al. (2023)

The sections below provide a brief overview of each of these Contributing Datasets.


(antarctica-shift)=
### SHIFT

The SHIFT data provide 6- and 12-day snapshots of ice speed over the Antarctic Peninsula derived from feature intensity of Sentinel-1 image pairs from 2014 to 2026. The SHIFT processing pipeline is described in detail in the [SHIFT Documentation Page](/documentation/shift).

```{figure} ../_static/antarctica/verification_maps_SHIFT.png
---
name: verification-maps-shift-fig
alt: SHIFT data overview
---
Overview of the Antarctic SHIFT data.
```

> Davison, B. J. and Sole, A. J. 2026. SHeffield Ice Flow Tracker (SHIFT) velocity data: Antarctic Peninsula ice surface velocity fields derived from intensity tracking of Sentinel-1 Synthetic Aperture Radar image pairs. [Online]. Available from: https://doi.org/10.15131/shef.data.33113111.v1

> Davison, B.J., Sole, A.J., Cowton, T.R., Lea, J.M., Slater, D.A., Fahrner, D. and Nienow, P.W., 2020. Subglacial drainage evolution modulates seasonal ice flow variability of three tidewater glaciers in southwest Greenland. Journal of Geophysical Research: Earth Surface, 125(9), p.e2019JF005492. DOI: https://doi.org/10.1029/2019JF005492.

(antarctica-enveo-monthly)=
### ENVEO monthly

The ENVEO monthly data provide monthly averages of ice speed over the Antarctic margin derived from intensity and coherence tracking of Sentinel-1 image pairs from 2014 to 2021. The ENVEO velocity processing pipeline is described in detail in [Wuite et al. (2026)](https://www.sciencedirect.com/science/article/pii/S0034425725004961), and the mosaics can be downloaded from [the ENVEO cryoportal](https://cryoportal.enveo.at/data/).

```{figure} ../_static/antarctica/verification_maps_ENVEO_monthly.png
---
name: verification-maps-enveo-monthly-fig
alt: ENVEO monthly data overview
---
Overview of the ENVEO monthly data.
```

> Wuite, J., Nagler, T., Hetzenecker, M. and Rott, H., 2026. Ten years of polar ice velocity mapping using Copernicus Sentinel-1. Remote Sensing of Environment, 332, p.115092. DOI: https://doi.org/10.1016/j.rse.2025.115092

(antarctica-enveo-pig)=
### ENVEO (Pine Island)

The ENVEO (Pine Island) data provide 6- and 12-day snapshots of ice speed over Pine Island Glacier derived from intensity and coherence tracking of Sentinel-1 image pairs from 2014 to 2019. The ENVEO velocity processing pipeline is described in detail in [Wuite et al. (2026)](https://www.sciencedirect.com/science/article/pii/S0034425725004961), and the image pair data can be downloaded from [the ENVEO cryoportal](https://cryoportal.enveo.at/data/).

```{figure} ../_static/antarctica/verification_maps_ENVEO_Sentinel-1_PIG.png
---
name: verification-maps-enveo-sentinel-1-pig-fig
alt: ENVEO Pine Island data overview
---
Overview of the ENVEO Pine Island data.
```

> Wuite, J., Nagler, T., Hetzenecker, M. and Rott, H., 2026. Ten years of polar ice velocity mapping using Copernicus Sentinel-1. Remote Sensing of Environment, 332, p.115092. DOI: https://doi.org/10.1016/j.rse.2025.115092

(antarctica-enveo-ers)=
### ENVEO ERS

The ENVEO ERS data provide estimates of ice speed covering the Larsen-B Embayment region, Ferrigno Ice Shelf area, Rutford Ice Stream and the Amundsen Sea Embayment region of Antarctica. The measurements are provided at a range of temporal resolutions - ranging from 8 days to 4 months during the period from 11th January 1992 to 11th November 1999. The measurements are derived from a combination of SAR interferometry and offset tracking of ERS-1 and ERS-2 imagery. The processing techniques used to derive these velocity estimates are described in [Rott et al. (2011)](https://tc.copernicus.org/articles/5/125/2011/), and [Wuite et al. (2015)](https://tc.copernicus.org/articles/9/957/2015/tc-9-957-2015.html) and the data can be downloaded from [the ENVEO cryoportal](https://cryoportal.enveo.at/data/).

```{figure} ../_static/antarctica/verification_maps_ENVEO_ERS.png
---
name: verification-maps-enveo-ers-fig
alt: ENVEO ERS data overview
---
Overview of the ENVEO ERS data.
```

> Rott, H., Müller, F., Nagler, T. and Floricioiu, D., 2011. The imbalance of glaciers after disintegration of Larsen-B ice shelf, Antarctic Peninsula. The Cryosphere, 5(1), pp.125-134. DOI: https://doi.org/10.5194/tc-5-125-2011.

> Wuite, J., Rott, H., Hetzenecker, M., Floricioiu, D., De Rydt, J., Gudmundsson, G.H., Nagler, T. and Kern, M., 2015. Evolution of surface velocities and ice discharge of Larsen B outlet glaciers from 1995 to 2013. The Cryosphere, 9(3), pp.957-969. DOI: https://doi.org/10.5194/tc-9-957-2015.

(antarctica-enveo-tsx)=
### ENVEO TSX

The ENVEO TSX data provide estimates of ice speed covering the Larsen-B Embayment region of the Antarctic Peninsula. The measurements are provided at a range of temporal resolutions - typically 11 or 22 days - during the period from 26th June 2007 to 12th December 2016. The measurements are derived from offset tracking of TerraSAR-X image pairs. The processing techniques used to derive these velocity estimates are described in [Rott et al. (2018)](https://tc.copernicus.org/articles/12/1273/2018/) and the data can be downloaded from [the ENVEO cryoportal](https://cryoportal.enveo.at/data/).

```{figure} ../_static/antarctica/verification_maps_ENVEO_TSX.png
---
name: verification-maps-enveo-tsx-fig
alt: ENVEO TSX data overview
---
Overview of the ENVEO TSX data.
```

> Rott, H., Abdel Jaber, W., Wuite, J., Scheiblauer, S., Floricioiu, D., Van Wessem, J.M., Nagler, T., Miranda, N. and Van Den Broeke, M.R., 2018. Changing pattern of ice flow and mass balance for glaciers discharging into the Larsen A and B embayments, Antarctic Peninsula, 2011 to 2016. The Cryosphere, 12(4), pp.1273-1291. DOI: https://doi.org/10.5194/tc-12-1273-2018.

(antarctica-enveo-alos)=
### ENVEO ALOS-PALSAR

The ENVEO ALOS-PALSAR data provide estimates of ice speed covering the Larsen-B Embayment region of the Antarctic Peninsula from the 29th September 2009 to 13th November 2009 and the 2nd January 2011 to 17th February 2011. The measurements are derived from offset tracking of a combination of ALOS-PALSAR image pairs. The data can be downloaded from [the ENVEO cryoportal](https://cryoportal.enveo.at/data/).

```{figure} ../_static/antarctica/verification_maps_ENVEO_ALOS.png
---
name: verification-maps-enveo-alos-fig
alt: ENVEO ALOS-PALSAR data overview
---
Overview of the ENVEO ALOS-PALSAR data.
```

(antarctica-enveo-tsx-s1)=
### ENVEO TSX & Sentinel-1

The ENVEO TSX & Sentinel-1 data provide estimates of ice speed covering the Larsen-B Embayment region of the Antarctic Peninsula from the 31st October 2015 to the 12th December 2016. The measurements are derived from offset tracking of TerraSAR-X image pairs with gaps filled using Sentinel-1 data. The processing techniques used to derive these velocity estimates are described in [Rott et al. (2018)](https://tc.copernicus.org/articles/12/1273/2018/) and the data can be downloaded from [the ENVEO cryoportal](https://cryoportal.enveo.at/data/).

```{figure} ../_static/antarctica/verification_maps_ENVEO_TSX_Sentinel-1.png
---
name: verification-maps-enveo-tsx-sentinel-1-fig
alt: ENVEO TSX & Sentinel-1 data overview
---
Overview of the ENVEO TSX & Sentinel-1 data.
```

> Rott, H., Abdel Jaber, W., Wuite, J., Scheiblauer, S., Floricioiu, D., Van Wessem, J.M., Nagler, T., Miranda, N. and Van Den Broeke, M.R., 2018. Changing pattern of ice flow and mass balance for glaciers discharging into the Larsen A and B embayments, Antarctic Peninsula, 2011 to 2016. The Cryosphere, 12(4), pp.1273-1291. DOI: https://doi.org/10.5194/tc-12-1273-2018.

(antarctica-enveo-tsx-palsar)=
### ENVEO TSX & ALOS-PALSAR

The ENVEO TSX & ALOS-PALSAR data provide estimates of ice speed covering the Larsen-B Embayment region of the Antarctic Peninsula from the 2nd July 2010 to the 10th March 2012. The measurements are derived from offset tracking of TerraSAR-X image pairs with gaps filled using ALOS-PALSAR data. The processing techniques used to derive these velocity estimates are described in [Rott et al. (2018)](https://tc.copernicus.org/articles/12/1273/2018/) and the data can be downloaded from [the ENVEO cryoportal](https://cryoportal.enveo.at/data/).

```{figure} ../_static/antarctica/verification_maps_ENVEO_TSX_PALSAR.png
---
name: verification-maps-enveo-tsx-palsar-fig
alt: ENVEO TSX & ALOS-PALSAR data overview
---
Overview of the ENVEO TSX & ALOS-PALSAR data.
```

> Rott, H., Abdel Jaber, W., Wuite, J., Scheiblauer, S., Floricioiu, D., Van Wessem, J.M., Nagler, T., Miranda, N. and Van Den Broeke, M.R., 2018. Changing pattern of ice flow and mass balance for glaciers discharging into the Larsen A and B embayments, Antarctic Peninsula, 2011 to 2016. The Cryosphere, 12(4), pp.1273-1291. DOI: https://doi.org/10.5194/tc-12-1273-2018.

(antarctica-measures-multiyear)=
### MEaSUREs multi-year

The MEaSUREs multi-year data provide estimates of ice speed for all of Antarctica from July through June of the following multi-year periods: 1995-2001, 2007-2009, 2014-2017 and 2020-2022. The measurements are derived by applying phase analysis and speckle tracking to SAR data and by feature tracking of optical imagery from Landsat 8. The processing techniques used to derive these velocity estimates are described in [Rignot et al. (2022)](https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2022GL100141) and the data can be downloaded from [NSIDC (0761)](https://nsidc.org/data/nsidc-0761/versions/1).

```{figure} ../_static/antarctica/verification_maps_MEaSUREs_multiyear.png
---
name: verification-maps-measures-multiyear-fig
alt: MEaSUREs multi-year data overview
---
Overview of the MEaSUREs multi-year data.
```

> Rignot, E., Mouginot, J., Scheuchl, B. and Jeong, S., 2022. Changes in Antarctic ice sheet motion derived from satellite radar interferometry between 1995 and 2022. Geophysical Research Letters, 49(23), p.e2022GL100141. DOI: https://doi.org/10.1029/2022GL100141.

> Rignot, E., Scheuchl, B., Mouginot, J. & Jeong, S. (2022). MEaSUREs Multi-year Reference Velocity Maps of the Antarctic Ice Sheet. (NSIDC-0761, Version 1). [Data Set]. Boulder, Colorado USA. NASA National Snow and Ice Data Center Distributed Active Archive Center. https://doi.org/10.5067/FB851ZIZYX5O. Date Accessed 04-16-2026.

(antarctica-measures-annual)=
### MEaSUREs annual

The MEaSUREs annual data provide estimates of ice speed for all of Antarctica from July through June of the following years: 2000, 2005-2025. The measurements are derived by applying phase analysis and speckle tracking to SAR data and by feature tracking of optical imagery from Landsat 8. The processing techniques used to derive these velocity estimates are described in [Mouginot et al. (2017)](https://www.mdpi.com/2072-4292/9/4/364) and the data can be downloaded from [NSIDC (0720)](https://nsidc.org/data/nsidc-0720/versions/1).

```{figure} ../_static/antarctica/verification_maps_MEaSUREs_annual.png
---
name: verification-maps-measures-annual-fig
alt: MEaSUREs annual data overview
---
Overview of the MEaSUREs annual data.
```

> Mouginot, J., Rignot, E., Scheuchl, B. and Millan, R., 2017. Comprehensive annual ice sheet velocity mapping using Landsat-8, Sentinel-1, and RADARSAT-2 data. Remote Sensing, 9(4), p.364. DOI: https://doi.org/10.3390/rs9040364.

> Mouginot, J., Scheuchl, B. & Rignot, E. (2017). MEaSUREs Annual Antarctic Ice Velocity Maps. (NSIDC-0720, Version 1). [Data Set]. Boulder, Colorado USA. NASA National Snow and Ice Data Center Distributed Active Archive Center. https://doi.org/10.5067/9T4EPQXTJYW9. Date Accessed 04-16-2026.

(antarctica-measures-ase)=
### MEaSUREs ASE

The MEaSUREs ASE data provide annual (calendar year) estimates of ice speed for the Amundsen Sea Embayment from 1996, 2000, 2002 and 2006 to 2012. The measurements are derived from SAR interferometry on a range of platforms. The processing techniques used to derive these velocity estimates are described in [Mouginot et al. (2014)](https://agupubs.onlinelibrary.wiley.com/doi/full/10.1002/2013GL059069) and the data can be downloaded from [NSIDC (0545)](https://nsidc.org/data/nsidc-0545/versions/1).

```{figure} ../_static/antarctica/verification_maps_MEaSUREs_ASE.png
---
name: verification-maps-measures-ase-fig
alt: MEaSUREs ASE data overview
---
Overview of the MEaSUREs ASE data.
```

> Mouginot, J., Rignot, E. and Scheuchl, B., 2014. Sustained increase in ice discharge from the Amundsen Sea Embayment, West Antarctica, from 1973 to 2013. Geophysical Research Letters, 41(5), pp.1576-1584. DOI: https://doi.org/10.1002/2013GL059069.

> Rignot, E., Mouginot, J. & Scheuchl, B. (2014). MEaSUREs InSAR-Based Ice Velocity of the Amundsen Sea Embayment, Antarctica. (NSIDC-0545, Version 1). [Data Set]. Boulder, Colorado USA. NASA National Snow and Ice Data Center Distributed Active Archive Center. https://doi.org/10.5067/MEASURES/CRYOSPHERE/nsidc-0545.001. Date Accessed 04-16-2026.

(antarctica-itslive-annual)=
### ITS_LIVE Annual

The ITS_LIVE annual data provide annual (calendar year) averages of ice speed over Antarctica derived from feature tracking applied to a range of satellite missions from 1985 to 2024. The ITS_LIVE velocity processing pipeline is described in [Gardner et al. (2025)](https://tc.copernicus.org/articles/19/3517/2025/) and [Lei et al. (2022)](https://essd.copernicus.org/articles/14/5111/2022/) and the mosaics are available to download from [the ITS_LIVE website](https://nsidc.org/apps/itslive/).

```{figure} ../_static/antarctica/verification_maps_ITS_LIVE_annual.png
---
name: verification-maps-its-live-annual-fig
alt: ITS_LIVE annual data overview
---
Overview of the Antarctica ITS_LIVE annual data.
```

> Gardner, A.S., Greene, C.A., Kennedy, J.H., Fahnestock, M.A., Liukis, M., López, L.A., Lei, Y., Scambos, T.A. and Dehecq, A., 2025. ITS_LIVE global glacier velocity data in near-real time. The Cryosphere, 19(9), pp.3517-3533. DOI: https://doi.org/10.5194/tc-19-3517-2025.

> Gardner, A. S., Fahnestock, M. & Scambos, T. (2022). MEaSUREs ITS_LIVE Regional Glacier and Ice Sheet Surface Velocities. (NSIDC-0776, Version 1). [Data Set]. Boulder, Colorado USA. NASA National Snow and Ice Data Center Distributed Active Archive Center. https://doi.org/10.5067/6II6VW8LLWJ7. Date Accessed 08-17-2026.

(antarctica-c3s-annual)=
### C3S Annual

The Copernicus Climate Change Service (C3S) Annual data provide annual (April through March) averages of ice speed over Antarctica derived from Sentinel-1 image pairs acquired during 2021 to 2024. The mosaics can be accessed through the [Copernicus Climate Data Store](https://cds.climate.copernicus.eu/datasets/satellite-greenland-ice-sheet-velocity?).

```{figure} ../_static/antarctica/verification_maps_ESA_CCI_annual.png
---
name: verification-maps-esa-cci-annual-fig
alt: C3S annual data overview
---
Overview of the C3S annual data.
```

> Copernicus Climate Change Service, Climate Data Store (2020): Ice sheet velocity for Antarctica and Greenland derived from satellite observations. Copernicus Climate Change Service (C3S) Climate Data Store (CDS), DOI: 10.24381/cds.0b96b838.

(antarctica-sid-annual)=
### SID Annual

The SID (Satellite Ice Dynamics) annual data provide annual (January through December) averages of ice speed over Antarctica derived from Sentinel-1 image pairs acquired during 2015 to 2025. The mosaics can be accessed through the [CEDA Archive](https://catalogue.ceda.ac.uk/uuid/c0b464b3da9845758cd33591e57c4abf/).

```{figure} ../_static/antarctica/verification_maps_SID_annual.png
---
name: verification-maps-sid-annual-fig
alt: SID annual data overview
---
Overview of the SID annual data.
```

> Hogg, A.E.; Davison, B.J.; Rigby, R.; Wallis, B.J.; Slater, R.A.W. (2025): EOCIS: Ice Sheet Velocity, V1. NERC EDS Centre for Environmental Data Analysis, 17 April 2025. doi:10.5285/c0b464b3da9845758cd33591e57c4abf. https://dx.doi.org/10.5285/c0b464b3da9845758cd33591e57c4abf

> Davison, B.J., Hogg, A.E., Rigby, R., Veldhuijsen, S., van Wessem, J.M., van den Broeke, M.R., Holland, P.R., Selley, H.L. and Dutrieux, P., 2023. Sea level rise from West Antarctic mass loss significantly modified by large snowfall anomalies. Nature Communications, 14(1), p.1479. DOI: https://doi.org/10.1038/s41467-023-36990-3.

(antarctica-joughin-s1)=
### Joughin Sentinel-1 (Pine Island)

The Sentinel-1 quarterly averages of Pine Island Glacier ice speed are available from 1st April 2015 to the 29th September 2020. These measurements are described in [Joughin et al. (2021)](https://www.science.org/doi/10.1126/sciadv.abg3080) and the data are available from the supplementary information of that paper.

```{figure} ../_static/antarctica/verification_maps_Joughin_Sentinel-1.png
---
name: verification-maps-joughin-sentinel-1-fig
alt: Joughin Sentinel-1 Pine Island data overview
---
Overview of the Joughin Sentinel-1 data over Pine Island Glacier.
```

> Joughin, I., Shapero, D., Smith, B., Dutrieux, P. and Barham, M., 2021. Ice-shelf retreat drives recent Pine Island Glacier speedup. Science Advances, 7(24), p.eabg3080. DOI: 10.1126/sciadv.abg3080.

(antarctica-joughin-tsx)=
### Joughin TSX (Pine Island)

The TerraSAR-X velocity estimates of Pine Island Glacier ice speed are available from 15th January 2009 to 15th January 2016 (dates are approximate). The time period over which the measurements were made was not provided with the data but described as a "range of several months", so we have assumed a 6-month range here. These measurements are described in [Joughin et al. (2021)](https://www.science.org/doi/10.1126/sciadv.abg3080) and the data are available from the supplementary information of that paper.

```{figure} ../_static/antarctica/verification_maps_Joughin_TSX.png
---
name: verification-maps-joughin-tsx-fig
alt: Joughin TerraSAR-X Pine Island data overview
---
Overview of the Joughin TerraSAR-X data over Pine Island Glacier.
```

> Joughin, I., Shapero, D., Smith, B., Dutrieux, P. and Barham, M., 2021. Ice-shelf retreat drives recent Pine Island Glacier speedup. Science Advances, 7(24), p.eabg3080. DOI: 10.1126/sciadv.abg3080.

(antarctica-li-totten)=
### Li (Totten)

These velocity estimates only cover Totten Glacier. The measurements were derived from feature tracking of ARGON and Landsat-1&4 imagery. The measurements are available for the periods 1963-1973, 1973-1989 and 1989. Dates were not provided with the data so we have assumed calendar years. These measurements are described in [Li et al. (2023)](https://www.nature.com/articles/s41467-023-39588-x). The link to the data provided in that paper did not work at the time of writing, but the authors shared the data on request.

```{figure} ../_static/antarctica/verification_maps_Li_Totten.png
---
name: verification-maps-li-totten-fig
alt: Li et al. Totten Glacier data overview
---
Overview of the Li et al. data over Totten Glacier.
```

> Li, R., Cheng, Y., Chang, T., Gwyther, D.E., Forbes, M., An, L., Xia, M., Yuan, X., Qiao, G., Tong, X. and Ye, W., 2023. Satellite record reveals 1960s acceleration of Totten ice shelf in East Antarctica. Nature Communications, 14(1), p.4061. DOI: https://doi.org/10.1038/s41467-023-39588-x.


(contributing_data_summary)=
## Summary

Combined, these sources offer an extensive historical record of ice motion. For Greenland, the measurements span from July 1972 to the present, with epoch resolutions ranging from four days to one year. For the Antarctic Ice Sheet, the temporal record extends from 1963 to January 2026, with epoch resolutions ranging from two days to multiple years.

The data infrastructure is designed to accommodate ongoing data generation. Currently, only one Contributing Dataset for Greenland (PROMICE (Solgaard et al. 2021)) receives predictable, operational updates; these new data are automatically ingested into the Unified Dataset and made accessible via SHIVER with a delay of three days following data publication by PROMICE. Irregular updates from other sources (e.g., MEaSUREs, ITS_LIVE), as well as the integration of entirely new ice velocity products, will be incorporated periodically into future versions of the Unified Dataset.