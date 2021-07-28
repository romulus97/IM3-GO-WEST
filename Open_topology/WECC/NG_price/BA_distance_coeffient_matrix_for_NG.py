# -*- coding: utf-8 -*-
"""
Created on Fri Jul  9 21:34:14 2021

@author: kakdemi
"""

import pandas as pd
import numpy as np
import geopandas as gpd

#reading BAs shapefile
BAs_gdf = gpd.read_file('../WECC.shp')
BAs_gdf = BAs_gdf.to_crs(epsg=2163)

#reading BA names
BAs = pd.read_csv('../BAs.csv',header=0)
BA_names = list(BAs['Name'])

#filtering the shapefile with needed BAs and getting center of the BAs
BAs_filtered = BAs_gdf.loc[BAs_gdf['NAME'].isin(BA_names)].copy()
BAs_filtered_final = BAs_filtered[['NAME','geometry']].copy()
BAs_filtered_final['Center'] = BAs_filtered_final.geometry.centroid

#defining BAs that have and have not NG data
BAs_with_NG_data_abb = ['AZPS', 'CISO', 'IPCO', 'NEVP', 'PACE', 'PACW', 'PGE', 'PSEI']
BAs_with_NG_data_name = list(BAs.loc[BAs['Abbreviation'].isin(BAs_with_NG_data_abb)]['Name'])
BAs_without_NG_data_name = list(set(list(BAs_filtered_final['NAME'])) - set(BAs_with_NG_data_name))

#creating an empty dataframe to fill with distances between BAs
row_no = len(BAs_filtered_final) - len(BAs_with_NG_data_name)
column_no = len(BAs_with_NG_data_name)
BAs_distance_matrix = pd.DataFrame(np.zeros((row_no,column_no)), \
                                   columns=BAs_with_NG_data_name, index=BAs_without_NG_data_name)

#calculating distances between BAs and saving them
for i in BAs_without_NG_data_name:
    
    BA_point_1 = BAs_filtered_final.loc[BAs_filtered_final['NAME']==i,'Center'].values
    
    for j in BAs_with_NG_data_name:
        
        BA_point_2 = BAs_filtered_final.loc[BAs_filtered_final['NAME']==j,'Center'].values
        distance_B1_B2 = BA_point_1.distance(BA_point_2)
        BAs_distance_matrix.loc[i,j] = float(distance_B1_B2)
        
#creating an empty dataframe to fill with BA coefficients to estimate NG price
BAs_NG_dist_coeff_matrix = pd.DataFrame(np.zeros((row_no,column_no)), columns=BAs_with_NG_data_name,\
                                        index=BAs_without_NG_data_name)

#calculating and saving coeffients that are inversely proportional to distance between 
#BAs to estimate NG prices
for index,row in BAs_distance_matrix.iterrows():
    
    total_row = row.sum()
    new_row = 1/(row/total_row)
    new_total_row = new_row.sum()
    inverse_distance_coefficient = new_row/new_total_row
    BAs_NG_dist_coeff_matrix.loc[index,:] = inverse_distance_coefficient
    
BAs_NG_dist_coeff_matrix.to_csv('BA_NG_Price_Coeff_Matrix.csv')

