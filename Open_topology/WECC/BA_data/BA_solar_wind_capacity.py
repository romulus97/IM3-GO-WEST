# -*- coding: utf-8 -*-
"""
Created on Mon Mar 28 12:18:12 2022

@author: kakdemi
"""

import pandas as pd
import numpy as np

#Reading EIA plant data which has plant names and BA data
plants = pd.read_excel('Plant_EIA860.xlsx',header=1)

#Reading EIA solar and wind data
solar = pd.read_excel('Solar_EIA860.xlsx',sheet_name='Operable',header=1)
wind = pd.read_excel('Wind_EIA860.xlsx',sheet_name='Operable',header=1)

#Reading BA names 
BAs_data = pd.read_csv('BAs.csv',header=0)
BAs_abb = list(BAs_data['Abbreviation'])

#Creating a dataframe to store data
solar_wind_df = pd.DataFrame(np.zeros((len(BAs_data),2)),columns=['Solar','Wind'],index=list(BAs_data['Name']))

#summing solar generation capacity for each BA
for ind,row in solar.iterrows():
    
    code = row['Plant Code']
    solar_BA_abb = plants.loc[plants['Plant Code']==code]['Balancing Authority Code'].values[0]
    solar_BA_cap = row['Nameplate Capacity (MW)']
    
    if solar_BA_abb in BAs_abb:
        
        solar_BA_name = BAs_data.loc[BAs_data['Abbreviation']==solar_BA_abb]['Name'].values[0]
        solar_wind_df.loc[solar_BA_name,'Solar'] = solar_wind_df.loc[solar_BA_name,'Solar'] + solar_BA_cap
       
    else:
        pass
    
#summing wind generation capacity for each BA
for ind,row in wind.iterrows():
    
    code = row['Plant Code']
    wind_BA_abb = plants.loc[plants['Plant Code']==code]['Balancing Authority Code'].values[0]
    wind_BA_cap = row['Nameplate Capacity (MW)']
    
    if wind_BA_abb in BAs_abb:
        
        wind_BA_name = BAs_data.loc[BAs_data['Abbreviation']==wind_BA_abb]['Name'].values[0]
        solar_wind_df.loc[wind_BA_name,'Wind'] = solar_wind_df.loc[wind_BA_name,'Wind'] + wind_BA_cap
       
    else:
        pass

#Exporting results
solar_wind_df.to_csv('BA_solar_wind_capacity_EIA.csv')





