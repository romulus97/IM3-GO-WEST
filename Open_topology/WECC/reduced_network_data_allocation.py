# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import pandas as pd
import math
import numpy as np
import matplotlib.pyplot as plt
import descartes
import geopandas as gpd
from shapely.geometry import Point, Polygon


########################################
# LOAD ALLOCATION FROM BALANCING AUTHORITY to NODES
########################################

# read reduction algorithm summary and parse nodal operations
df_summary = pd.read_csv('Reduction_Summary_LOAD.csv',header=4)
nodes=0
merged = {}
N = []
for i in range(0,len(df_summary)):
    test = df_summary.iloc[i,0]
    res = [int(i) for i in test.split() if i.isdigit()] 
    if res[1] in N:
        pass
    else:
        N.append(res[1])
for n in N:
    k = []
    for i in range(0,len(df_summary)):
        test = df_summary.iloc[i,0]
        res = [int(i) for i in test.split() if i.isdigit()] 
        if res[1] == n:
            k.append(res[0])
        else:
            pass
    merged[n] = k

df_load = pd.read_csv('BA_load.csv',header=0,index_col=0)
df_BAs = pd.read_csv('BAs.csv',header=0)
BAs = list(df_BAs['Name'])

# calculate nodal weights within each BA

df = pd.read_csv('10k_load.csv',header=0)
crs = {'init':'epsg:4326'}
# crs = {"init": "epsg:2163"}
geometry = [Point(xy) for xy in zip(df['Substation Longitude'],df['Substation Latitude'])]
nodes_df = gpd.GeoDataFrame(df,crs=crs,geometry=geometry)
nodes_df = nodes_df.to_crs(epsg=2163)

BAs_gdf = gpd.read_file('WECC.shp')
BAs_gdf = BAs_gdf.to_crs(epsg=2163)

joined = gpd.sjoin(nodes_df,BAs_gdf,how='left',op='within')

buses = list(joined['Number'])
B = []
for b in buses:
    if b in B:
        pass
    else:
        B.append(b)
        
#Make sure every BA in EIA dataset is selected at least once
BAs_selected = []

#elimate redundant buses (overlapping BAs) 

for b in B:
    
    print(B.index(b))
    sample = joined[joined['Number'] == b]
    sample = sample.reset_index(drop=True)
    
    if len(sample) > 1:
        TELL_ok = []
        sample_BAs = []
        for i in range(0,len(sample)):
            if sample.loc[i,'NAME'] in BAs:
                TELL_ok.append(i)
                
        if len(TELL_ok)<1:
            print('Remove me, I might not exist')         
        
        else:
            for t in TELL_ok:
                
                if sample.loc[i,'NAME'] in BAs_selected:
                    s = 0
                else:
                    s = t
            selection = sample.loc[s,:]
            if sample.loc[s,'NAME'] in BAs_selected:
                BAs_selected.append(sample.loc[s,'NAME'])
                    
    else:
        selection = sample
        if sample.loc[0,'NAME'] in BAs_selected:
            BAs_selected.append(sample.loc[0,'NAME'])
        
    b_idx = B.index(b)
    # print(b_idx)
    
    if b_idx < 1:
        combined = selection
    
    else:  
        combined = combined.append(selection) 

combined = combined.reset_index(drop=True)

BA_totals = []
for b in BAs:
    sample = list(combined.loc[combined['NAME']==b,'Load MW'])
    corrected = [0 if math.isnan(x) else x for x in sample]
    BA_totals.append(sum(corrected))

BA_totals = np.column_stack((BAs,BA_totals))
df_BA_totals = pd.DataFrame(BA_totals)
df_BA_totals.columns = ['Name','Total']

weights = []
for i in range(0,len(combined)):
    area = combined.loc[i,'NAME']
    if str(area) == 'nan':
        weights.append(0)
    elif str(combined.loc[i,'Load MW']) == 'nan':
        weights.append(0)
    else:        
        X = float(df_BA_totals.loc[df_BA_totals['Name']==area,'Total'])
        W = combined.loc[i,'Load MW']/X
        weights.append(W)
combined['BA Load Weight'] = weights

# selected nodes
df_selected = pd.read_csv('remaining_buses.csv',header=0)
buses = list(df_selected['bus_i'])
BAs = list(df_BAs['Name'])

idx = 0
w= 0
T = np.zeros((8760,len(buses)))

for b in buses:
        
    #load for original node
    sample = combined.loc[combined['Number'] == b]
    sample = sample.reset_index(drop=True)
    name = sample['NAME'][0]
    
    if str(name) != 'nan':

        abbr = df_BAs.loc[df_BAs['Name']==name,'Abbreviation'].values[0]
        weight = sample['BA Load Weight'].values[0]
        T[:,idx] = T[:,idx] + np.reshape(df_load[abbr].values*weight,(8760,))
        w+=weight
    
    else:
        pass
              
    #add loads from merged nodes
    try:
        m_nodes = merged[b]
        
        for m in m_nodes:

            #load for original node
            sample = combined.loc[combined['Number'] == m]
            sample = sample.reset_index(drop=True)
            name = sample['NAME'][0]
            if str(name) == 'nan':
                pass
            else:
                abbr = df_BAs.loc[df_BAs['Name']==name,'Abbreviation'].values[0]
                weight = sample['BA Load Weight'].values[0]
                w+=weight
        
                T[:,idx] = T[:,idx] + np.reshape(df_load[abbr].values*weight,(8760,))

    except KeyError:
        # print (b)
        pass
    
    idx+=1

df_C = pd.DataFrame(T)
df_C.columns = buses
df_C.to_csv('nodal_load.csv')   

#############
# GENERATORS

df_wind = pd.read_csv('BA_wind.csv',header=0,index_col=0)
df_solar = pd.read_csv('BA_solar.csv',header=0,index_col=0)

# read reduction algorithm summary and parse nodal operations
df_summary = pd.read_csv('Reduction_Summary.csv',header=4)
nodes=0
merged = {}
N = []
for i in range(0,len(df_summary)):
    test = df_summary.iloc[i,0]
    res = [int(i) for i in test.split() if i.isdigit()] 
    if res[1] in N:
        pass
    else:
        N.append(res[1])
for n in N:
    k = []
    for i in range(0,len(df_summary)):
        test = df_summary.iloc[i,0]
        res = [int(i) for i in test.split() if i.isdigit()] 
        if res[1] == n:
            k.append(res[0])
        else:
            pass
    merged[n] = k

##################################
# WIND ALLOCATION FROM BA TO NODE

df_gen = pd.read_csv('10k_Gen.csv',header=0)
MWMax = []
fuel_type = []
nums = list(df_gen['BusNum'])

#add gen info to combined df
for i in range(0,len(combined)):
    bus = combined.loc[i,'Number']
    if bus in nums:
        MWMax.append(df_gen.loc[df_gen['BusNum']==bus,'MWMax'].values[0])
        fuel_type.append(df_gen.loc[df_gen['BusNum']==bus,'FuelType'].values[0])
    else:
        MWMax.append(0)
        fuel_type.append('none')

combined['MWMax'] = MWMax
combined['FuelType'] = fuel_type

BA_totals = []

for b in BAs:
    sample = list(combined.loc[(combined['NAME']==b) & (combined['FuelType'] == 'WND (Wind)'),'MWMax'])
    corrected = [0 if math.isnan(x) else x for x in sample]
    BA_totals.append(sum(corrected))

BA_totals = np.column_stack((BAs,BA_totals))
df_BA_totals = pd.DataFrame(BA_totals)
df_BA_totals.columns = ['Name','Total']

weights = []
for i in range(0,len(combined)):
    area = combined.loc[i,'NAME']
    if str(area) == 'nan':
        weights.append(0)
    elif str(combined.loc[i,'FuelType']) != 'WND (Wind)':
        weights.append(0)
    else:        
        X = float(df_BA_totals.loc[df_BA_totals['Name']==area,'Total'])
        W = combined.loc[i,'MWMax']/X
        weights.append(W)
combined['BA Wind Weight'] = weights

# selected nodes
df_selected = pd.read_csv('remaining_buses.csv',header=0)
buses = list(df_selected['bus_i'])

idx = 0
w= 0
T = np.zeros((8760,len(buses)))

for b in buses:
    
    #load for original node
    sample = combined.loc[combined['Number'] == b]
    sample = sample.reset_index(drop=True)
    name = sample['NAME'][0]
    
    if str(name) != 'nan':

        abbr = df_BAs.loc[df_BAs['Name']==name,'Abbreviation'].values[0]
        weight = sample['BA Wind Weight'].values[0]
        T[:,idx] = T[:,idx] + np.reshape(df_wind[abbr].values*weight,(8760,))
        w += weight 
        
    else:
        pass
              
    #add wind capacity from merged nodes
    try:
        m_nodes = merged[b]
        
        for m in m_nodes:
            #load for original node
            sample = combined.loc[combined['Number'] == m]
            sample = sample.reset_index(drop=True)
            name = sample['NAME'][0]
            if str(name) == 'nan':
                pass
            else:
                abbr = df_BAs.loc[df_BAs['Name']==name,'Abbreviation'].values[0]
                weight = sample['BA Wind Weight']
                w += weight        
                T[:,idx] = T[:,idx] + np.reshape(df_wind[abbr].values*weight.values[0],(8760,))

    except KeyError:
        # print (b)
        pass
    
    idx +=1

df_C = pd.DataFrame(T)
df_C.columns = buses
df_C.to_csv('nodal_wind.csv')   

##################################
# SOLAR ALLOCATION FROM BA TO NODE

MWMax = []
fuel_type = []
nums = list(df_gen['BusNum'])

#add gen info to combined df
for i in range(0,len(combined)):
    bus = combined.loc[i,'Number']
    if bus in nums:
        MWMax.append(df_gen.loc[df_gen['BusNum']==bus,'MWMax'].values[0])
        fuel_type.append(df_gen.loc[df_gen['BusNum']==bus,'FuelType'].values[0])
    else:
        MWMax.append(0)
        fuel_type.append('none')

combined['MWMax'] = MWMax
combined['FuelType'] = fuel_type

BA_totals = []

for b in BAs:
    sample = list(combined.loc[(combined['NAME']==b) & (combined['FuelType'] == 'SUN (Solar)'),'MWMax'])
    corrected = [0 if math.isnan(x) else x for x in sample]
    BA_totals.append(sum(corrected))

BA_totals = np.column_stack((BAs,BA_totals))
df_BA_totals = pd.DataFrame(BA_totals)
df_BA_totals.columns = ['Name','Total']

weights = []
for i in range(0,len(combined)):
    area = combined.loc[i,'NAME']
    if str(area) == 'nan':
        weights.append(0)
    elif str(combined.loc[i,'FuelType']) != 'SUN (Solar)':
        weights.append(0)
    else:        
        X = float(df_BA_totals.loc[df_BA_totals['Name']==area,'Total'])
        W = combined.loc[i,'MWMax']/X
        weights.append(W)
combined['BA Solar Weight'] = weights

# selected nodes
df_selected = pd.read_csv('remaining_buses.csv',header=0)
buses = list(df_selected['bus_i'])

idx = 0
w= 0
T = np.zeros((8760,len(buses)))

for b in buses:
    
    #load for original node
    sample = combined.loc[combined['Number'] == b]
    sample = sample.reset_index(drop=True)
    name = sample['NAME'][0]
    
    if str(name) != 'nan':

        abbr = df_BAs.loc[df_BAs['Name']==name,'Abbreviation'].values[0]
        weight = sample['BA Solar Weight'].values[0]
        T[:,idx] = T[:,idx] + np.reshape(df_solar[abbr].values*weight,(8760,))
        w += weight 
        
    else:
        pass
              
    #add solar capacity from merged nodes
    try:
        m_nodes = merged[b]
        
        for m in m_nodes:
            #load for original node
            sample = combined.loc[combined['Number'] == m]
            sample = sample.reset_index(drop=True)
            name = sample['NAME'][0]
            if str(name) == 'nan':
                pass
            else:
                abbr = df_BAs.loc[df_BAs['Name']==name,'Abbreviation'].values[0]
                weight = sample['BA Solar Weight']
                w += weight        
                T[:,idx] = T[:,idx] + np.reshape(df_solar[abbr].values*weight.values[0],(8760,))

    except KeyError:
        # print (b)
        pass
    
    idx +=1

df_C = pd.DataFrame(T)
df_C.columns = buses
df_C.to_csv('nodal_solar.csv') 

##############################
# THERMAL GENERATION

import re

df_gens = pd.read_csv('10k_Gen.csv',header=0)
old_bus_num =[]
new_bus_num = []
NB = []

for n in N:
    k = merged[n]
    for s in k:
        old_bus_num.append(s)
        new_bus_num.append(n)

for i in range(0,len(df_gens)):
    OB = df_gens.loc[i,'BusNum']
    if OB in old_bus_num:
        idx = old_bus_num.index(OB)
        NB.append(new_bus_num[idx])
    else:
        NB.append(OB)

df_gens['NewBusNum'] = NB
    
names = list(df_gens['BusName'])

# remove numbers and spaces
for n in names:
    i = names.index(n)
    corrected = re.sub(r'[^A-Z]',r'',n)
    names[i] = corrected

df_gens['PlantNames'] = names

NB = df_gens['NewBusNum'].unique()
plants = []
caps = []
mw_min = []
count = 2
nbs = []
marg = []
f = []
thermal = ['NG (Natural Gas)','NUC (Nuclear)','BIT (Bituminous Coal)']

for n in NB:
    sample = df_gens.loc[df_gens['NewBusNum'] == n]
    sublist = sample['PlantNames'].unique()
    for s in sublist:
        fuel = list(sample.loc[sample['PlantNames']==s,'FuelType'])
        if fuel[0] in thermal:
            c = sum(sample.loc[sample['PlantNames']==s,'MWMax'].values)
            mc = np.mean(sample.loc[sample['PlantNames']==s,'MargCostMW'].values)
            mn = sum(sample.loc[sample['PlantNames']==s,'MWMin'].values)
            mw_min.append(mn)
            caps.append(c)
            nbs.append(n)
            marg.append(mc)
            f.append(fuel[0])
            if s in plants:
                new = s + '_' + str(count)
                plants.append(new)
                count+=1
            else:
                plants.append(s)

C=np.column_stack((plants,nbs))
C=np.column_stack((C,f))
C=np.column_stack((C,caps))
C=np.column_stack((C,mw_min))
C=np.column_stack((C,marg))

df_C = pd.DataFrame(C)
df_C.columns = ['Name','Bus','Fuel','Max_Cap','Min_Cap','MarginalCost']
df_C.to_csv('Thermal_Gens.csv')
    

##############################
# TRANSMISSION PARAMETERS 


