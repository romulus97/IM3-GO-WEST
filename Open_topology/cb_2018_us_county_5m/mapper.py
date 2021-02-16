# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import descartes
import geopandas as gpd
from shapely.geometry import Point, Polygon
from matplotlib.colors import TwoSlopeNorm

df = pd.read_csv('Buses_EIA.csv',header=0)
crs = {'init':'epsg:4326'}
# crs = {"init": "epsg:2163"}
geometry = [Point(xy) for xy in zip(df['Substation Longitude'],df['Substation Latitude'])]
nodes_df = gpd.GeoDataFrame(df,crs=crs,geometry=geometry)
nodes_df = nodes_df.to_crs(epsg=2163)

counties_gdf = gpd.read_file('cb_2018_us_county_5m.shp')
counties_gdf = counties_gdf.to_crs(epsg=2163)

joined = gpd.sjoin(nodes_df,counties_gdf,how='left',op='within')

GEOID = list(joined['GEOID'].unique())

g = []
mw = []
n = []

for i in GEOID:
    if str(i) == 'nan':
        pass
    else:
        g.append(i)
        L = list(joined.loc[joined['GEOID'] == i,'Load MW'])
        
        X = 0
        for l in L:
            if str(l) != 'nan':
                X+=l
    
        names = list(joined.loc[joined['GEOID'] == i,'NAME'])
        n.append(names[0])
        mw.append(X)

C = np.column_stack((g,n))
C = np.column_stack((C,mw))
df_C = pd.DataFrame(C)
df_C.columns = ['GEOID','Name','MW']
df_C.to_csv('county_load_EIC.csv')
        

# buses = list(joined['Number'])
# B = []
# for b in buses:
#     if b in B:
#         pass
#     else:
#         B.append(b)
        
# #elimate redundant buses (overlapping BAs) based on peak load

# for b in B:
    
#     sample = joined[joined['Number'] == b]
    
#     if len(sample) > 1:
#         smallest = min(sample['PEAK_LOAD'])
#         selection = sample[sample['PEAK_LOAD']==smallest]
    
#     else:
        
#         selection = sample
        
#     b_idx = B.index(b)
#     # print(b_idx)
    
#     if b_idx < 1:
        
#         combined = selection
    
#     else:
        
#         combined = combined.append(selection) 
    

# combined.to_csv('nodes_to_BA_state.csv')

