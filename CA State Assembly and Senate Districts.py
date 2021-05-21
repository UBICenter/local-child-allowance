#!/usr/bin/env python
# coding: utf-8

# In[1]:


import geopandas as gpd
from geopandas.tools import sjoin
import matplotlib as plt
import microdf as mdf
import pandas as pd
import numpy as np
import us


# In[2]:


# All shapefiles from https://www.census.gov/geographies/mapping-files/time-series/geo/cartographic-boundary.html

##Lower Chamber for All 50 States

assembly = gpd.read_file('C:\CA_MAP\cb_2019_us_sldl_500k\cb_2019_us_sldl_500k.shp')

##Upper Chamber for All 50 States

senate = gpd.read_file('C:\CA_MAP\cb_2019_us_sldu_500k\cb_2019_us_sldu_500k.shp')

##Load PUMA Boundaries, limit to California (State FIP 06 represents CA)

US_PUMA = gpd.read_file('C:\CA_MAP\ipums_puma_2010\ipums_puma_2010.shp')

#ca_puma = US_PUMA.drop(US_PUMA[US_PUMA['STATEFIP'] != '06'].index, inplace = True)


# In[3]:


#US_PUMA.plot()
#ca_puma.plot()


# In[4]:


## Ensure CRS is the same for all three maps

assembly = assembly.to_crs(US_PUMA.crs)

senate = senate.to_crs(US_PUMA.crs)

### find centroid coordinates

US_PUMA_pt = US_PUMA.copy()

US_PUMA_pt.geometry = US_PUMA_pt.centroid


# In[39]:


## note that Nebraska, smack dab in the middle of the country, has a unicameral body
#assembly.plot()
#senate.plot()


# In[40]:


##Lower Chamber Visualization

base = assembly.plot(color = 'white', edgecolor = 'black')

test = US_PUMA_pt.plot(ax = base, marker = 'o', color = 'red', markersize = 1)


# In[7]:


##Upper Chamber Visualization

#base1 = senate.plot(color = 'white', edgecolor = 'black')

#test1 = US_PUMA_pt.plot(ax = base1, marker = 'o', color = 'red', markersize = 1)


# In[8]:


#STATEFIP FROM US_PUMA
#STATEFP FROM ASSEMBLY


# In[31]:


## Point in polygon for puma coordinates within state assembly districts

pumas_by_assembly = gpd.sjoin(assembly, US_PUMA_pt, how = 'inner', op = 'contains')

pumas_by_assembly = pumas_by_assembly[['NAME', 'STATEFIP', 'PUMA', 'Name','STATEFIP']].copy()

pumas_by_assembly = pumas_by_assembly.rename(columns = {'NAME' : 'Assembly District Number', 'Name' : 'PUMA Description'})


### FOUR ASSEMBLY DISTRICTS HAVE NOT MATCHED, LIKELY COASTAL


# In[36]:


## Point-in-polygon for puma coordinates within state senate districts

pumas_by_senate = gpd.sjoin(senate, US_PUMA_pt, how = 'inner', op = 'contains')

pumas_by_senate = pumas_by_senate[['NAME', 'STATEFIP', 'PUMA', 'Name']].copy() 

pumas_by_senate = pumas_by_senate.rename(columns = {'NAME' : 'Senate District Number', 'Name' : 'PUMA Description'})


## TODO: 
## Figure out state code mapping
#pumas_by_senate['STATE_CODE'] = us.states.mapping(fips = pumas_by_senate['STATE_CODE'])
                                                 
### FOUR SENATE DISTRICTS HAVE NOT MATCHED, LIKELY COASTAL


# In[37]:


##Export and notes

#PUMA codes are non-unique between states - need to use FIPS/state code to 

pumas_by_assembly.to_csv('Mapping1.csv', index=False)

#Issues may be caused by the inclusion of CA islands, may have to drop those

