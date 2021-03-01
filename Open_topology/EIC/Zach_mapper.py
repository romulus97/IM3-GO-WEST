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

df = pd.read_csv('Persimmon Creek Lat_Long_Nodes.csv',header=0)
crs = {'init':'epsg:4326'}
# crs = {"init": "epsg:2163"}
geometry = [Point(xy) for xy in zip(df['Longitude'],df['Latitude'])]
nodes_df = gpd.GeoDataFrame(df,crs=crs,geometry=geometry)
nodes_df = nodes_df.to_crs(epsg=2163)

BAs_gdf = gpd.read_file('Planning_Areas.shp')
BAs_gdf = BAs_gdf.to_crs(epsg=2163)

states_gdf = gpd.read_file('geo_export_9ef76f60-e019-451c-be6b-5a879a5e7c07.shp')
states_gdf = states_gdf.to_crs(epsg=2163)


M=18

SPP = BAs_gdf[BAs_gdf['NAME']=='SOUTHWEST POWER POOL']

#plot
fig,ax = plt.subplots()
states_gdf.plot(ax=ax,color='white',edgecolor='black',linewidth=0.5)
SPP.plot(ax=ax,color='salmon',edgecolor='red',linewidth=0.5)
nodes_df.plot(ax=ax,color = 'black',markersize=M,alpha=1,linewidth=0.3)

ax.set_box_aspect(1)
ax.set_xlim(-1000000,1000000)
ax.set_ylim([-1600000,600000])
plt.axis('off')
plt.savefig('SPP.jpg',dpi=400)

#plot
fig,ax = plt.subplots()
states_gdf.plot(ax=ax,color='black',edgecolor = 'black',linewidth=0.5)
SPP.plot(ax=ax,color='salmon',edgecolor='red',linewidth=0.5)

ax.set_box_aspect(1)
ax.set_xlim(-2200000,2600000)
ax.set_ylim([-2200000,1000000])
plt.axis('off')
plt.savefig('SPP2.jpg',dpi=400)

#plot
fig,ax = plt.subplots()
states_gdf.plot(ax=ax,color='white',edgecolor='black',linewidth=0.5)
SPP.plot(ax=ax,color='salmon',edgecolor='red',linewidth=0.5)
nodes_df.plot(ax=ax,color = 'black',markersize=32,alpha=1,linewidth=0.3)

ax.set_box_aspect(1)
ax.set_xlim(0,110000)
ax.set_ylim([-1000000,-920000])
plt.axis('off')
plt.savefig('SPP4.jpg',dpi=400)