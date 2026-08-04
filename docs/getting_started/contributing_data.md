# Contributing Datasets

## Greenland

The Unified Dataset for the Greenland Ice Sheet integrates 17 distinct ice velocity Contributing Datasets. The Greenland Ice Sheet data are summarised in Table 1 and Figure 1.

```{figure} ../_static/greenland_data_overview.png
---
name: greenland-overview-fig
alt: Greenland data overview
---
Summary of the Greenland Ice Sheet unified dataset. (a) Time-average mean speed, (b) mean error, (c) total number of valid (non-NaN) measurements, (d) the date of the first valid measurement and (e) date of the last valid measurement across all contributing datasets. (f) Timeline of all contributing datasets, where each black dot represents the mid-date of each measurement epoch and the width of each coloured bar represents the duration of each measurement epoch. The number of epochs is listed on the right. *Contributing dataset name has been shortened for display – full names are in Table 1. 
```

![Greenland Data Table](../_static/greenland_data_table.png)

## Antarctica

The Unified Dataset for the Antarctic Ice Sheet integrates 17 distinct ice velocity Contributing Datasets. The Antarctic Ice Sheet data are summarised in Table 2 and Figure 2.


```{figure} ../_static/antarctica_data_overview.png
---
name: antarctic-overview-fig
alt: Antarctic data overview
---
Summary of Antarctic Ice Sheet unified dataset. (a) Time-average mean speed, (b) mean error, (c) total number of valid (non-NaN) measurements, (d) the date of the first valid measurement and (e) date of the last valid measurement across all contributing datasets. (f) Timeline of all contributing datasets, where each black dot represents the mid-date of each measurement epoch and the width of each coloured bar represents the duration of each measurement epoch. The number of epochs is listed on the right. *Contributing dataset name has been shortened for display – full names are in Table 2. 
```

![Antarctica Data Table](../_static/antarctica_data_table.png)

## Summary

Combined, these sources offer an extensive historical record of ice motion. For Greenland, the measurements span from July 1972 to the present, with epoch resolutions ranging from four days to one year. For the Antarctic Ice Sheet, the temporal record extends from 1963 to January 2026, with epoch resolutions ranging from two days to multiple years.

The data infrastructure is designed to accommodate ongoing data generation. Currently, only one Contributing Dataset for Greenland (PROMICE (Solgaard et al. 2021)) receives predictable, operational updates; these new data are automatically ingested into the Unified Dataset and made accessible via SHIVER (Section 4) with a delay of one day following data publication by PROMICE. Irregular updates from other sources (e.g., MEaSUREs, ITS_LIVE), as well as the integration of entirely new ice velocity products, will be incorporated periodically into future versions of the Unified Dataset.