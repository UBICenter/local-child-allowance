#!/usr/bin/env python
# coding: utf-8

# NOTICE
## YOU WILL HAVE TO UNZIP THE SHAPEFILES WHERE THEY ARE CURRENTLY PLACED IN THE DIRECTORY FOR THIS TO WORK
## Upper and Lower legislative chamber shapefiles from https://www.census.gov/geographies/mapping-files/time-series/geo/cartographic-boundary.html
## PUMA Boundaries from https://usa.ipums.org/usa/volii/pumas10.shtml
import pandas as pd
import geopandas as gpd
from geopandas.tools import sjoin


##Lower Chamber for All 50 States

assembly = gpd.read_file(
    "data\original\cb_2019_us_sldl_500k\cb_2019_us_sldl_500k.shp", encoding="utf-8"
)

##Upper Chamber for All 50 States

senate = gpd.read_file(
    "data\original\cb_2019_us_sldu_500k\cb_2019_us_sldu_500k.shp", encoding="utf-8"
)

##Load PUMA Boundaries, limit to California (State FIP 06 represents CA)

 us_puma = gpd.read_file(
    "data\original\ipums_puma_2010\ipums_puma_2010.shp", encoding="utf-8"
 )

# ca_puma = us_puma.drop(us_puma[us_puma['STATEFIP'] != '06'].index, inplace = True)

## Ensure CRS is the same for all three maps

assembly = assembly.to_crs(us_puma.crs)

senate = senate.to_crs(us_puma.crs)

### find centroid coordinates

us_puma_pt = us_puma.copy()

us_puma_pt.geometry = us_puma_pt.centroid

## Point in polygon for puma coordinates within state assembly districts

pumas_by_assembly = gpd.sjoin(assembly, us_puma_pt, how="inner", op="contains")

pumas_by_assembly = pumas_by_assembly[
    ["NAME", "STATEFIP", "PUMA", "Name", "STATEFIP"]
].copy()

pumas_by_assembly = pumas_by_assembly.rename(
    columns={"NAME": "Assembly District Number", "Name": "PUMA Description"}
)

## Point-in-polygon for puma coordinates within state senate districts

pumas_by_senate = gpd.sjoin(senate, us_puma_pt, how="inner", op="contains")

pumas_by_senate = pumas_by_senate[["NAME", "STATEFIP", "PUMA", "Name"]].copy()

pumas_by_senate = pumas_by_senate.rename(
    columns={"NAME": "Senate District Number", "Name": "PUMA Description"}
)


puma_to_state_legis_mapping = pd.merge(pumas_by_senate, pumas_by_assembly, on="PUMA")


puma_to_state_legis_mapping.to_csv("data\\puma_to_state_legis_mapping.csv", index=False)

