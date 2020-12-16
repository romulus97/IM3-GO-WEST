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

df = pd.read_csv('found_WECC.csv',header=0)
crs = {'init':'epsg:4326'}
# crs = {"init": "epsg:2163"}
geometry = [Point(xy) for xy in zip(df['longitude'],df['latitude'])]
geo_df = gpd.GeoDataFrame(df,crs=crs,geometry=geometry)
geo_df = geo_df.to_crs(epsg=2163)

state_map = gpd.read_file('geo_export_9ef76f60-e019-451c-be6b-5a879a5e7c07.shp')
state_map = state_map.to_crs(epsg=2163)


fig,ax = plt.subplots()
state_map.plot(ax=ax,color='gray',alpha=0.6,edgecolor='white',linewidth=0.5)
ax.set_box_aspect(1)
ax.set_xlim(-2100000,10000)
ax.set_ylim([-1500000,750000])
plt.axis('off')

df_not = pd.read_csv('update_notfound_notCA.csv',header=0)
crs = {'init':'epsg:4326'}
# crs = {"init": "epsg:2163"}
geometry = [Point(xy) for xy in zip(df_not['longitude'],df_not['latitude'])]
geo_df_not = gpd.GeoDataFrame(df_not,crs=crs,geometry=geometry)
geo_df_not = geo_df_not.to_crs(epsg=2163)
geo_df_not.plot(ax=ax,markersize=0.3,color='black',marker='o')

df_CA = pd.read_csv('update_notfound_CA.csv',header=0)
crs = {'init':'epsg:4326'}
# crs = {"init": "epsg:2163"}
geometry = [Point(xy) for xy in zip(df_CA['longitude'],df_CA['latitude'])]
geo_df_CA = gpd.GeoDataFrame(df_CA,crs=crs,geometry=geometry)
geo_df_CA = geo_df_CA.to_crs(epsg=2163)
geo_df_CA.plot(ax=ax,markersize=0.3,color='white',marker='o')
buses = list(geo_df['Bus'].unique())
markers = ['o','P','^','*','D','d','s']
idx=0

for i in buses:
    if idx > 6:
        idx = 0
    r = np.random.random()
    b = np.random.random()
    g = np.random.random()
    geo_df[geo_df['Bus'] == i].plot(ax=ax,markersize=16,color=(r,g,b),marker=markers[idx],edgecolor='black',linewidth=0.1,label=i)
    idx += 1
    
    
plt.legend(loc = 'upper right',fontsize=4,framealpha=1)

plt.savefig('found.tiff',dpi=500)


# def Diff(li1, li2):
#     li_dif = [i for i in li1 + li2 if i not in li1 or i not in li2]
#     return li_dif

# D = Diff(buses,unique_buses)