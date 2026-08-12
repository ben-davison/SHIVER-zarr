# Contributing Datasets

Our ice sheet velocity Zarr stores contain ice velocity estimates that have been generated over years of effort by many research groups. 

## Greenland Data

_There are 17 Contributing Datasets for Greenland, which are summarised in this table:_

**Table 1. Datasets contributing to the Greenland Ice Sheet unified dataset. _Valid as of 30th July 2026_**
| Source Dataset | Start Date | End Date | Epochs | Sep. (days) | Resolution (m) | Citation |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: |
| ENVEO annual | 01/10/2014 | 30/09/2020 | 6 | 364 | 250 | [1] |
| ESA CCI CSK | 02/06/2012 | 25/12/2014 | 13 | 4 | 250 | [2] |
| ESA CCI ERS1 1991-1992 | 29/12/1991 | 22/03/1992 | 1 | 84 | 500 | [11] |
| ESA CCI ERS1-2 Envisat | 01/08/1991 | 07/02/2011 | 1877 | 35 | 90 | [3-10] |
| ESA CCI ERS2 1995-1996 | 03/09/1995 | 29/03/1996 | 1 | 208 | 90 | [12] |
| ESA CCI PALSAR | 20/12/2006 | 17/03/2011 | 5 | 112 | 90 | [13] |
| ESA CCI Sentinel-1<sup>a</sup> | 10/10/2014 | 22/03/2017 | 1133 | 12 | 250 | [14-22] |
| ESA CCI Sentinel-2<sup>a</sup> | 01/05/2017 | 14/09/2017 | 28 | 14 | 50 | [23-31] |
| ESA CCI winter<sup>c</sup> | 21/01/2014 | 28/02/2018 | 5 | 62 | 500 | [32] |
| ITS LIVE annual | 01/01/1985 | 31/12/2024 | 40 | 364 | 120 | [33] |
| MEaSUREs annual | 01/12/2014 | 30/11/2023 | 9 | 364 | 200 | [34-36] |
| MEaSUREs monthly | 01/12/2014 | 30/11/2024 | 120 | 30 | 200 | [37-39] |
| MEaSUREs qaurterly | 01/12/2014 | 30/11/2024 | 40 | 91 | 200 | [40-42] |
| MEaSUREs winter | 03/09/2000 | 31/05/2018 | 11 | 272 | 200 | [43-45] |
| Mouginot annual<sup>a</sup> | 01/07/1972 | 30/06/2017 | 38 | 364 | 90 | [46] |
| PROMICE | 05/01/2016 | 28/06/2026 | 317 | 24 | 200 | [47], [48] |
| SHIFT<sup>d</sup> | 11/10/2014 | 17/01/2026 | 1663 | 12 | 200 | [49], [50] |

<sup>a</sup> Error of all epochs and velocity components assumed to be 5% \
<sup>b</sup> Error for years 2017/2018, 2018/2019 and 2019/2020 provided. Velocity component errors for years 2014/2015, 2015/2016 and 2016/2017 calculated by scaling the velocity magnitude error by the proportional contribution of each velocity component to the velocity magnitude. \
<sup>c</sup> Error provided for all components in winters 2013/2014. All errors assumed to be 5% in winter 2014/2015. Only velocity magnitude error provided in winters 2015/2016, 2016/2017 and 2017/2018, so velocity component errors assumed to be 5%. \
<sup>d</sup> Error is provided as a scalar value defined as the standard deviation of apparent ice motion over bedrock areas. If provided error is NaN for a given epoch, the error is assumed to be 5%.

## Antarctica Data
_There are 17 Contributing Datasets for Antarctica, which are summarised in this table:_

**Table 2. Datasets contributing to the Antarctic Ice Sheet unified dataset. _Valid as of 30th July 2026_**
| Source Dataset | Start Date | End Date | Epochs | Sep. (days) | Resolution (m) | Citation |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: |
| ENVEO ALOS<sup>a</sup> | 29/09/2009 | 17/02/2011 | 2 | 47 | 50 | [51] |
| ENVEO ERS<sup>a</sup> | 11/01/1992 | 10/11/1999 | 13 | 2 | 500 | [52], [53] |
| ENVEO Sentinel-1 PIG<sup>a</sup> | 10/10/2014 | 21/08/2019 | 402 | 13 | 200 | [54] |
| ENVEO TSX<sup>a</sup> | 26/06/2007 | 11/12/2016 | 125 | 12 | 50 | [55] |
| ENVEO TSX PALSAR<sup>a</sup> | 02/07/2010 | 09/03/2012 | 1 | 617 | 50 | [56] |
| ENVEO TSX Sentinel-1<sup>a</sup> | 31/10/2015 | 11/12/2016 | 1 | 408 | 50 | [57] |
| ENVEO monthly | 01/10/2014 | 31/12/2021 | 87 | 30 | 200 | [58] |
| ESA CCI annual | 01/04/2021 | 31/03/2024 | 3 | 365 | 200 | [59] |
| ITS LIVE annual | 01/01/1985 | 31/12/2024 | 40 | 365 | 120 | [60] |
| Joughin Sentinel-1<sup>a</sup> | 01/04/2015 | 29/09/2020 | 22 | 90 | 500 | [61] |
| Joughin TSX<sup>a</sup> | 06/02/2009 | 24/12/2015 | 13 | 106 | 500 | [62] |
| Li Totten<sup>a</sup> | 01/01/1963 | 31/12/1989 | 3 | 365 | 1000 | [63] |
| MEaSUREs ASE | 01/01/1996 | 31/12/2012 | 10 | 365 | 450 | [64], [65] |
| MEaSUREs annual | 01/07/2000 | 30/06/2025 | 21 | 365 | 1000 | [66], [67] |
| MEaSUREs multiyear | 01/07/1995 | 30/06/2022 | 4 | 730 | 450 | [68], [69] |
| SHIFT<sup>c</sup> | 25/11/2014 | 20/01/2026 | 2033 | 13 | 200 | [70], [71] |
| SID annual<sup>d</sup> | 01/01/2015 | 31/12/2024 | 10 | 365 | 250 | [72], [73] |

<sup>a</sup> Error of all epochs and velocity components assumed to be 5% \
<sup>b</sup> Error calculated by scaling the velocity magnitude error by the proportional contribution of each velocity component to the velocity magnitude. \
<sup>c</sup> Error is provided as a scalar value defined as the standard deviation of apparent ice motion over bedrock areas. If provided error is NaN for a given epoch, the error is assumed to be 5%. \
<sup>d</sup> No velocity component data provided, so are assumed to be NaN.


## Summary

Combined, these sources offer an extensive historical record of ice motion. For Greenland, the measurements span from July 1972 to the present, with epoch resolutions ranging from four days to one year. For the Antarctic Ice Sheet, the temporal record extends from 1963 to January 2026, with epoch resolutions ranging from two days to multiple years.

The data infrastructure is designed to accommodate ongoing data generation. Currently, only one Contributing Dataset for Greenland (PROMICE (Solgaard et al. 2021)) receives predictable, operational updates; these new data are automatically ingested into the Unified Dataset and made accessible via SHIVER with a delay of three days following data publication by PROMICE. Irregular updates from other sources (e.g., MEaSUREs, ITS_LIVE), as well as the integration of entirely new ice velocity products, will be incorporated periodically into future versions of the Unified Dataset.