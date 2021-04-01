# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import pandas as pd
import math
import numpy as np
import matplotlib.pyplot as plt
# import descartes
import geopandas as gpd
from shapely.geometry import Point, Polygon

########################################
# LOAD ALLOCATION FROM BALANCING AUTHORITY to NODES
########################################

df_load = pd.read_csv('BA_load.csv',header=0)
df_BAs = pd.read_csv('BAs.csv',header=0)
BAs = list(df_BAs['Name'])

df_full = pd.read_csv('nodes_to_BA_state.csv',header=0,index_col=0)

# selected nodes
df_selected = pd.read_csv('reduced_buses.csv',header=0)
buses = list(df_selected['bus_i'])

# pull selected nodes out of 
selected_BAs = []
for b in buses:
    BA = df_full.loc[df_full['Number']==b,'NAME']
    BA = BA.reset_index(drop=True)
    selected_BAs.append(BA[0])

df_selected['BA'] = selected_BAs
    
# calculate nodal weights within each BA

BA_totals = []
for b in BAs:
    sample = list(df_selected.loc[df_selected['BA']==b,'Pd'])
    corrected = [0 if x<0 else x for x in sample]
    BA_totals.append(sum(corrected))

BA_totals = np.column_stack((BAs,BA_totals))
df_BA_totals = pd.DataFrame(BA_totals)
df_BA_totals.columns = ['Name','Total']

weights = []
for i in range(0,len(df_selected)):
    area = df_selected.loc[i,'BA']
    if df_selected.loc[i,'Pd'] <0:
        weights.append(0)
    else:        
        X = float(df_BA_totals.loc[df_BA_totals['Name']==area,'Total'])
        W = df_selected.loc[i,'Pd']/X
        weights.append(W)
df_selected['BA Load Weight'] = weights

idx = 0
w= 0
T = np.zeros((8760,len(buses)))

for i in range(0,len(df_selected)):
        
    #load for original node
    name = df_selected.loc[i,'BA']
    
    abbr = df_BAs.loc[df_BAs['Name']==name,'Abbreviation'].values[0]
    weight = df_selected.loc[i,'BA Load Weight']
    T[:,i] = T[:,i] + np.reshape(df_load[abbr].values*weight,(8760,))
  
    
df_C = pd.DataFrame(T)
df_C.columns = buses
df_C.to_csv('nodal_load.csv',index=None)   

#############
# GENERATORS

df_wind = pd.read_csv('BA_wind.csv',header=0,index_col=0)
df_solar = pd.read_csv('BA_solar.csv',header=0,index_col=0)

#get rid of NaNs
a = df_wind.values
m=np.where(np.isnan(a))
r,c=np.shape(m)
for i in range(0,c):
    df_wind.iloc[m[0][i],m[1][i]] = 0
a = df_solar.values
m=np.where(np.isnan(a))
r,c=np.shape(m)
for i in range(0,c):
    df_solar.iloc[m[0][i],m[1][i]] = 0    

# read reduction algorithm summary and parse nodal operations
df_summary = pd.read_csv('Reduction_Summary.csv',header=4)
df_summary = df_summary.drop([len(df_summary)-1])
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

#### NOTE: TAMU DATASET DOES NOT INCLUDE ANY WIND IN: LADWP OR PSCO; EIA VALUES
# FOR THESE BAs WERE MANUALLY ADDED TO CAISO AND WACM IN THE BA_wind.csv FILE.

df_gen = pd.read_csv('10k_Gen.csv',header=0)
MWMax = []
fuel_type = []
nums = list(df_gen['BusNum'])

#add gen info to df
for i in range(0,len(df_full)):
    bus = df_full.loc[i,'Number']
    if bus in nums:
        MWMax.append(df_gen.loc[df_gen['BusNum']==bus,'MWMax'].values[0])
        fuel_type.append(df_gen.loc[df_gen['BusNum']==bus,'FuelType'].values[0])
    else:
        MWMax.append(0)
        fuel_type.append('none')

df_full['MWMax'] = MWMax
df_full['FuelType'] = fuel_type

BA_totals = []

for b in BAs:
    sample = list(df_full.loc[(df_full['NAME']==b) & (df_full['FuelType'] == 'WND (Wind)'),'MWMax'])
    # corrected = [0 if math.isnan(x) else x for x in sample]
    BA_totals.append(sum(sample))

BA_totals = np.column_stack((BAs,BA_totals))
df_BA_totals = pd.DataFrame(BA_totals)
df_BA_totals.columns = ['Name','Total']

weights = []
for i in range(0,len(df_full)):
    area = df_full.loc[i,'NAME']
    if str(area) == 'nan':
        weights.append(0)
    elif str(df_full.loc[i,'FuelType']) != 'WND (Wind)':
        weights.append(0)
    else:        
        X = float(df_BA_totals.loc[df_BA_totals['Name']==area,'Total'])
        W = df_full.loc[i,'MWMax']/X
        weights.append(W)
df_full['BA Wind Weight'] = weights

sums = []
for i in BAs:
    s = sum(df_full.loc[df_full['NAME']==i,'BA Wind Weight'])
    sums.append(s)

# selected nodes
# df_selected = pd.read_csv('reduced_buses.csv',header=0)
buses = list(df_selected['bus_i'])

idx = 0
w= 0
T = np.zeros((8760,len(buses)))

BA_sums = np.zeros((28,1))

for b in buses:
    
    #load for original node
    sample = df_full.loc[df_full['Number'] == b]
    sample = sample.reset_index(drop=True)
    name = sample['NAME'][0]

    
    if str(name) != 'nan':

        abbr = df_BAs.loc[df_BAs['Name']==name,'Abbreviation'].values[0]
        weight = sample['BA Wind Weight'].values[0]
        T[:,idx] = T[:,idx] + np.reshape(df_wind[abbr].values*weight,(8760,))
        w += weight
        dx = BAs.index(name)
        BA_sums[dx] = BA_sums[dx] + weight
        
    else:
        pass
              
    #add wind capacity from merged nodes
    try:
        m_nodes = merged[b]
        
        for m in m_nodes:
            #load for original node
            sample = df_full.loc[df_full['Number'] == m]
            sample = sample.reset_index(drop=True)
            name = sample['NAME'][0]
            if str(name) == 'nan':
                pass
            else:
                abbr = df_BAs.loc[df_BAs['Name']==name,'Abbreviation'].values[0]
                weight = sample['BA Wind Weight']
                w += weight  
                dx = BAs.index(name)
                BA_sums[dx] = BA_sums[dx] + weight
                T[:,idx] = T[:,idx] + np.reshape(df_wind[abbr].values*weight.values[0],(8760,))

    except KeyError:
        # print (b)
        pass
    
    idx +=1

df_C = pd.DataFrame(T)
df_C.columns = buses
df_C.to_csv('nodal_wind.csv',index=None)   

##################################
# SOLAR ALLOCATION FROM BA TO NODE

#### NOTE: TAMU DATASET DOES NOT INCLUDE ANY WIND IN: BANC, LADWP OR PSCO; EIA VALUES
# FOR THESE BAs WERE MANUALLY ADDED TO CAISO AND WACM IN THE BA_wind.csv FILE.

BA_totals = []

for b in BAs:
    sample = list(df_full.loc[(df_full['NAME']==b) & (df_full['FuelType'] == 'SUN (Solar)'),'MWMax'])
    # corrected = [0 if math.isnan(x) else x for x in sample]
    BA_totals.append(sum(sample))

BA_totals = np.column_stack((BAs,BA_totals))
df_BA_totals = pd.DataFrame(BA_totals)
df_BA_totals.columns = ['Name','Total']

weights = []
for i in range(0,len(df_full)):
    area = df_full.loc[i,'NAME']
    if str(area) == 'nan':
        weights.append(0)
    elif str(df_full.loc[i,'FuelType']) != 'SUN (Solar)':
        weights.append(0)
    else:        
        X = float(df_BA_totals.loc[df_BA_totals['Name']==area,'Total'])
        W = df_full.loc[i,'MWMax']/X
        weights.append(W)
df_full['BA Solar Weight'] = weights

sums = []
for i in BAs:
    s = sum(df_full.loc[df_full['NAME']==i,'BA Solar Weight'])
    sums.append(s)

# selected nodes
# df_selected = pd.read_csv('reduced_buses.csv',header=0)
buses = list(df_selected['bus_i'])

idx = 0
w= 0
T = np.zeros((8760,len(buses)))

BA_sums = np.zeros((28,1))

for b in buses:
    
    #load for original node
    sample = df_full.loc[df_full['Number'] == b]
    sample = sample.reset_index(drop=True)
    name = sample['NAME'][0]

    
    if str(name) != 'nan':

        abbr = df_BAs.loc[df_BAs['Name']==name,'Abbreviation'].values[0]
        weight = sample['BA Solar Weight'].values[0]
        T[:,idx] = T[:,idx] + np.reshape(df_solar[abbr].values*weight,(8760,))
        w += weight
        dx = BAs.index(name)
        BA_sums[dx] = BA_sums[dx] + weight
        
    else:
        pass
              
    #add solar capacity from merged nodes
    try:
        m_nodes = merged[b]
        
        for m in m_nodes:
            #load for original node
            sample = df_full.loc[df_full['Number'] == m]
            sample = sample.reset_index(drop=True)
            name = sample['NAME'][0]
            if str(name) == 'nan':
                pass
            else:
                abbr = df_BAs.loc[df_BAs['Name']==name,'Abbreviation'].values[0]
                weight = sample['BA Solar Weight']
                w += weight  
                dx = BAs.index(name)
                BA_sums[dx] = BA_sums[dx] + weight
                T[:,idx] = T[:,idx] + np.reshape(df_solar[abbr].values*weight.values[0],(8760,))

    except KeyError:
        # print (b)
        pass
    
    idx +=1

df_C = pd.DataFrame(T)
df_C.columns = buses
df_C.to_csv('nodal_solar.csv',index=None)   


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
thermal = ['NG (Natural Gas)','NUC (Nuclear)','BIT (Bituminous Coal)','NUC (Nuclear)']

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
df_C.to_csv('thermal_gens.csv',index=None)
    

##############################
# HYDROPOWER

#EIA plants
df_hydro = pd.read_csv('EIA_317_WECC_hydro_plants_to_10kbus_v2.csv',header=0)
df_hydro_ts = pd.read_csv('p_mean_max_min_MW_WECC_317plants_2009water_weekly.csv',header=0)
new_hydro_nodes = []

for i in range(0,len(df_hydro)):
    
    name = df_hydro.loc[i,'plant']
    new_name = re.sub(r'[^A-Z]',r'',name)
    bus = df_hydro.loc[i,'bus']
    
    if bus in old_bus_num:
        idx = old_bus_num.index(bus)
        new_hydro_nodes.append(new_bus_num[idx])
        pass
    elif bus in buses:
        new_hydro_nodes.append(bus)
    else:
        print(name+ ' Not found')

# add mean/min/max by node
H_min = np.zeros((52,len(buses)))
H_max = np.zeros((52,len(buses)))
H_mu = np.zeros((52,len(buses)))

for i in range(0,len(df_hydro)):
    b = new_hydro_nodes[i]
    idx = buses.index(b)
    plant = df_hydro.loc[i,'plant']
    
    ts = df_hydro_ts[df_hydro_ts['plant']==plant]
    
    H_min[:,idx] += ts['min']
    H_max[:,idx] += ts['max']
    H_mu[:,idx] += ts['mean']
    
# create daily time series by node
H_min_hourly = np.zeros((365,len(buses)))
H_max_hourly = np.zeros((365,len(buses)))
H_mu_hourly = np.zeros((365,len(buses)))

for i in range(0,len(H_min)):
    for j in range(0,len(buses)):
        H_min_hourly[i*7:i*7+7,j] = H_min[i,j]
        H_max_hourly[i*7:i*7+7,j] = H_max[i,j]
        H_mu_hourly[i*7:i*7+7,j] = H_mu[i,j]*24
        
H_min_hourly[364,:] = H_min_hourly[363,:]
H_max_hourly[364,:] = H_max_hourly[363,:]
H_mu_hourly[364,:] = H_mu_hourly[363,:] 

H_min_df = pd.DataFrame(H_min_hourly)
H_min_df.columns = buses
H_max_df = pd.DataFrame(H_max_hourly)
H_max_df.columns = buses
H_mu_df = pd.DataFrame(H_mu_hourly) 
H_mu_df.columns = buses       

H_min_df.to_csv('Hydro_min.csv',index=None)
H_max_df.to_csv('Hydro_max.csv',index=None)
H_mu_df.to_csv('Hydro_mu.csv',index=None)


#####################################
# TRANSMISSION

df = pd.read_csv('branches.csv',header=0)

names = []
caps = []
xs = []
repeats = {}

count = 0

for i in range(0,len(df)):
    
    a = df.loc[i,'fbus']
    b = df.loc[i,'tbus']
    x = df.loc[i,'x']
    c = df.loc[i,'rateA']
    
    name = str(a) + '_' + str(b)
    
    if name in names:
        name = name + '_' + str(count)
        count += 1
        
    names.append(name)
    xs.append(x)
    caps.append(c)

df_T = pd.DataFrame()
df_T['line'] = names
df_T['reactance'] = xs
df_T['limit'] = caps

df_T.to_csv('line_params.csv')
    

#########################################
# Generator file setup

df_G = pd.read_csv('Thermal_Gens.csv',header=0)

names = []
typs = []
nodes = []
maxcaps = []
mincaps = []
marginal_costs = []
var_oms = []
no_loads = []
st_costs = []
ramps = []
minups = []
mindns = []

must_nodes = []
must_caps = []

for i in range(0,len(df_G)):
    
    name = df_G.loc[i,'Name']
    t = df_G.loc[i,'Fuel']
    if t == 'NG (Natural Gas)':
        typ = 'ngcc'
    elif t == 'BIT (Bituminous Coal)':
        typ = 'coal'
    else:
        typ = 'nuclear'
    node = df_G.loc[i,'Bus']
    maxcap = df_G.loc[i,'Max_Cap']
    mincap = df_G.loc[i,'Min_Cap']
    mc = df_G.loc[i,'MarginalCost']
    
    if typ == 'ngcc':
        var_om = 3
        minup = 4
        mindn = 4
        ramp = maxcap
    else:
        var_om = 4
        minup = 12
        mindn = 12
        ramp = 0.33*maxcap
    
    st_cost = 70*maxcap
    no_load = 3*maxcap
    
    if typ != 'nuclear':
        
        names.append(name)
        typs.append(typ)
        nodes.append(node)
        maxcaps.append(maxcap)
        mincaps.append(mincap)
        var_oms.append(var_om)
        no_loads.append(no_load)
        st_costs.append(st_cost)
        ramps.append(ramp)
        minups.append(minup)
        mindns.append(mindn)
        marginal_costs.append(mc)
        
    else:
        
        must_nodes.append(node)
        must_caps.append(maxcap)
    

# wind

df_W = pd.read_csv('nodal_wind.csv',header=0)
buses = list(df_W.columns)
for n in buses:
    
    if sum(df_W[n]) > 0:
        name = n + '_WIND'
        maxcap = 100000
        names.append(name)
        typs.append('wind')
        nodes.append(n)
        maxcaps.append(maxcap)
        mincaps.append(0)
        var_oms.append(0)
        no_loads.append(0)
        st_costs.append(0)
        ramps.append(0)
        minups.append(0)
        mindns.append(0) 
        marginal_costs.append(0)

# solar

df_S = pd.read_csv('nodal_solar.csv',header=0)
buses = list(df_S.columns)
for n in buses:
    if sum(df_S[n]) > 0:
        name = n + '_SOLAR'
        maxcap = 100000
        names.append(name)
        typs.append('solar')
        nodes.append(n)
        maxcaps.append(maxcap)
        mincaps.append(0)
        var_oms.append(0)
        no_loads.append(0)
        st_costs.append(0)
        ramps.append(0)
        minups.append(0)
        mindns.append(0)   
        marginal_costs.append(0)

# hydro

df_H = pd.read_csv('Hydro_max.csv',header=0)
buses = list(df_H.columns)
for n in buses:
    if sum(df_H[n]) > 0:
        name = n + '_HYDRO'
        maxcap = max(df_H[n])
        names.append(name)
        typs.append('hydro')
        nodes.append(n)
        maxcaps.append(maxcap)
        mincaps.append(0)
        var_oms.append(1)
        no_loads.append(1)
        st_costs.append(1)
        ramps.append(maxcap)
        minups.append(0)
        mindns.append(0)   
        marginal_costs.append(0)

df_genparams = pd.DataFrame()
df_genparams['name'] = names
df_genparams['typ'] = typs
df_genparams['node'] = nodes
df_genparams['maxcap'] = maxcaps
df_genparams['marginal_cost'] = marginal_costs
df_genparams['mincap'] = mincaps
df_genparams['var_om'] = var_oms
df_genparams['no_load'] = no_loads
df_genparams['st_cost'] = st_costs
df_genparams['ramp'] = ramps
df_genparams['minup'] = minups
df_genparams['mindn'] = mindns

df_genparams.to_csv('data_genparams.csv',index=None)

df_must = pd.DataFrame()
for i in range(0,len(must_nodes)):
    df_must[must_nodes[i]] = must_caps[i]
df_must.to_csv('must_run.csv',index=None)



