# Cite

The recommended approach to citing these data in your work is:

> "Ice velocity data were extracted using the Sheffield Ice Velocity ExploreR (SHIVER; Davison, 2026a,b; Davison et al., 2026) and included the data products detailed in Table X."

Where Davison et al. 2026 is a dataset description paper for SHIVER (in preparation). The citation for that paper will be something like:

> Davison, B. J. et al. (in prep). The SHeffield Ice Velocity ExploreR (SHIVER): an online tool for low latency exploration, analysis and sub-setting of unified satellite-derived ice velocity data for Earth's ice sheets. [specify journal]. https://doi.org/10.xxxx/XXXXXXX

And Davison (2026a) is the citation for the dataset itself:

> Davison, B. J. (2026a). The SHeffield Ice Velocity ExploreR (SHIVER): A unified satellite-derived ice velocity dataset for Earth's ice sheets (Version v[specify version number]) [Data set]. Zenodo. https://doi.org/10.5281/zenodo.21375859

Davison (2026b) should only be cited if your outputs relied on the SHIVER interactive application:

> Davison, B. J. (2026b). The SHeffield Ice Velocity ExploreR (SHIVER): an online tool for low latency exploration, analysis and sub-setting of unified satellite-derived ice velocity data for Earth's ice sheets (Version v[specify version number]) [Computer software]. Zenodo. https://doi.org/10.5281/zenodo.21378057

The SHIVER dataset is a compilation of many published velocity datasets and so would not have been possible without those. Therefore, those contributing datasets should also be cited. Specifically, you should cite all contributing datasets that your specific query intersected. If you are extracting data programmatically, please see our notebook describing how you can generate the correct citations for your query. 

If instead you are using the SHIVER application, all exports will contain citation details for the relevant contributing datasets. This will include a table (<strong>citations_summary.csv</strong>) summarising the required citations and a text file (<strong>citations_and_usage.txt</strong>) with descriptive details. 

<em>Note: The ESA_CCI_Sentinel-1, ESA_CCI_Sentinel-2 and ESA_CCI_ERS1-2_Envisat over selected glacier sites in Greenland require separate citations for each glacier site. Our dataset compilation method combines all of those glacier sites into one datasource. Our automated citation generator will therefore provide the citation information for all glacier sites even if only one is intersected. You should remove the unnecessary citations when incorporating them into your work.</em>


