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

df = pd.read_csv('gridkit_north_america-highvoltage-vertices.csv',header=0)
crs = {'init':'epsg:4326'}
# crs = {"init": "epsg:2163"}
geometry = [Point(xy) for xy in zip(df['lon'],df['lat'])]
nodes_df = gpd.GeoDataFrame(df,crs=crs,geometry=geometry)
nodes_df = nodes_df.to_crs(epsg=2163)

states_gdf = gpd.read_file('geo_export_9ef76f60-e019-451c-be6b-5a879a5e7c07.shp')
states_gdf = states_gdf.to_crs(epsg=2163)


fig,ax = plt.subplots()
states_gdf.plot(ax=ax,color='white',edgecolor='black',linewidth=0.5)
nodes_df.plot(ax=ax,color = 'red',alpha=1)
M=12

ax.set_box_aspect(1)
# ax.set_xlim(-2000000,-1500000)
# ax.set_ylim([-750000,0])
# plt.axis('off')
