# -*- coding: utf-8 -*-
"""
Created on Thu Nov 12 18:42:39 2020

@author: jkern
"""

import pandas as pd
import matplotlib.pyplot as plt
import descartes
import geopandas as gpd
from shapely.geometry import Point, Polygon
import numpy as np

#non CAISO 
df_WECC = pd.read_csv('eGRID_to_WECC_nonCAISO.csv',header=0)
df_AS = df_WECC.loc[:,:'State'].drop_duplicates()
df_AS = df_AS.reset_index(drop=True)
unique_buses = list(df_WECC['Bus_name'].unique())

# states
states = ['AZ','CA','CO','ID','MT','NM','NV','OR','UT','WA','WY']

WECC = {}

for i in range(0,len(df_AS)):
    
    buses = []
    
    area = df_AS.loc[i,'Area']
    state = df_AS.loc[i,'State']
    
    sample = df_WECC.loc[df_WECC['Area'] == area]
    sample = sample.loc[sample['State'] == state]
    sample = sample.drop_duplicates()
    sampe = sample.reset_index(drop=True)
    
    B = sample['Bus_name'].reset_index(drop=True)
    
    for j in range(0,len(sample)):
        
        buses.append(B[j])
    
    keys = tuple([str(area),str(state)])
    WECC[keys] = buses


for i in range(0,len(states)):
    
    filename = 'egrid_2016_gens_' + str(states[i]) + '.csv'
    df_eGRID = pd.read_csv(filename,header=0,index_col=0)
    
    if i < 1:
        
        df_combined = df_eGRID
    
    else:
        
        df_combined = pd.concat([df_combined,df_eGRID])
        
df_combined = df_combined.reset_index(drop=True)

eGRID_codes = {}
WECC_nodes = {}

for j in unique_buses:
    
    gens = []
    nodes = []

    for i in WECC:
        
        if len(WECC[i]) <= 1:
            # find generators that match
            area = i[0]
            state = i[1]
            bus = WECC[i][0]
            
            if bus == j:
                
                selected = df_combined[df_combined['state'] == state]
                selected = selected[selected['area'] == area]
                selected = selected.reset_index(drop=True)
    
                for k in range(0,len(selected)):
                    
                    code = selected.loc[k,'eGRID2016 Generator file sequence number']
                    gens.append(code)
                    nodes.append(bus)
               
    eGRID_codes[j] = gens
    WECC_nodes[j] = nodes
    
total_codes_found = []
corresponding_nodes = []
for j in eGRID_codes:
    gens = eGRID_codes[j]
    nodes = WECC_nodes[j]
    
    if len(gens) >= 1:
        total_codes_found = total_codes_found + gens
        corresponding_nodes = corresponding_nodes + nodes

df_found = df_combined.loc[df_combined['eGRID2016 Generator file sequence number'].isin(total_codes_found)]
df_found = df_found.reset_index(drop=True)
df_found['Bus'] = np.zeros((len(df_found),1))

for i in range(0,len(df_found)):
    code = df_found.loc[i,'eGRID2016 Generator file sequence number']
    idx = total_codes_found.index(code)
    df_found.loc[i,'Bus'] = corresponding_nodes[idx]

df_found.to_csv('intial_found_WECC.csv')
    
# Export excluded non-CAISO units and try to sort out
df_notfound = df_combined.loc[~df_combined['eGRID2016 Generator file sequence number'].isin(total_codes_found)]
df_notfound = df_notfound.reset_index(drop=True)
df_notfound['Bus'] = np.zeros((len(df_notfound),1))
df_notfound.to_csv('initial_not_found_WECC.csv')
 
# Incorporate non-CAISO units identified by hand
df_manual = pd.read_csv('manual_ID.csv',header=0)
IDs = list(df_manual['eGRID2016 Generator file sequence number'])

df_notfound.drop(df_notfound.loc[df_notfound['eGRID2016 Generator file sequence number'].isin(IDs)].index, inplace=True)

df_notfound.to_csv('update_notfound.csv')


