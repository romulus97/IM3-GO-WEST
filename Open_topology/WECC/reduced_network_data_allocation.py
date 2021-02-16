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
# from matplotlib.colors import TwoSlopeNorm

# read reduction algorithm summary and parse nodal operations
df_summary = pd.read_csv('Reduction_Summary.csv',header=4)
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

########################################
# LOAD ALLOCATION BY BALANCING AUTHORITY
########################################

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
        
#elimate redundant buses (overlapping BAs) 

for b in B:
    
    print(B.index(b))
    sample = joined[joined['Number'] == b]
    sample = sample.reset_index(drop=True)
    
    if len(sample) > 1:
        TELL_ok = []
        for i in range(0,len(sample)):
            if sample.loc[i,'NAME'] in BAs:
                TELL_ok.append(i)
        if len(TELL_ok)<1:
            print('Remove me, I might not exist')
        else:
            smallest = 100000000
            #assign BA with smallest peak load
            for t in TELL_ok:
                if sample.loc[i,'PEAK_LOAD'] < smallest:
                    smallest = sample.loc[i,'PEAK_LOAD']
                    selection = sample.loc[t,:]
    
    else:
        
        selection = sample
        
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
        T = float(df_BA_totals.loc[df_BA_totals['Name']==area,'Total'])
        W = combined.loc[i,'Load MW']/T
        weights.append(W)
combined['BA Load Weight'] = weights

START HERE -- FOR EACH SELECTED NODE, TAKE ITS LOAD, PLUS THE LOAD OF MERGED NODES AND ADD TOGETHER FOR A 
SINGLE TIME SERIES, PRINT TO CSV
    

##############################
#  Generators
##############################

import re
from itertools import compress

df_BA_states = pd.read_csv('nodes_to_BA_state.csv',index_col=0)
df_gens = pd.read_csv('10k_Gen.csv')

names = list(df_gens['BusName'])
BAs = []
c = list(df_BA_states.columns)
nx = int(c.index('NAME'))

# remove numbers and spaces
for n in names:
    i = names.index(n)
    corrected = re.sub(r'[^A-Z]',r'',n)
    names[i] = corrected
    BA = df_BA_states[df_BA_states['Number'] == df_gens.loc[i,'BusNum']]
    BAs.append(BA.iloc[0,nx])
    
df_gens['BusName'] = names
df_gens['BA'] = BAs
types = list(df_gens['FuelType'])

#select a single bus for each plant/BA combination (generators with the same name)

leftover = []
reduced_gen_buses = []
unique_bus_names = []
unique_bus_types = []
caps = []

for n in names:
    idx = names.index(n)
    if n in unique_bus_names:
        pass
    else:
        unique_bus_names.append(n)
        unique_bus_types.append(types[idx])
        
df_T = pd.DataFrame(unique_bus_types)
df_T.columns = ['Type']
df_T.to_csv('reduced_types.csv')

for n in unique_bus_names:
    sample_ba = list(df_gens.loc[df_gens['BusName'] == n,'BA'].values)
    sample_bus_number = list(df_gens.loc[df_gens['BusName'] == n,'BusNum'].values)
    sample_bus_cap = list(df_gens.loc[df_gens['BusName'] == n,'MWMax'].values)
    
    s = []
    s_n = []
    s_c = []
    
    # record each BA for this plant
    for i in sample_ba:
        if i in s:
            pass
        else:
            s.append(i)
            
            #find max cap generator at this plant/BA combination
            idx = [ True if x == i else False for x in sample_ba]
            s_bn = list(compress(sample_bus_number,idx))
            s_cp = list(compress(sample_bus_cap,idx))
            mx = np.max(s_cp)
            total = np.sum(s_cp)
            idx2 = s_cp.index(mx)
            s_n.append(s_bn[idx2])
            s_c.append(total)
            
    if len(s)>1:
        if n in leftover:
            pass
        else:
            leftover.append(n)
        for j in range(0,len(s)):
            reduced_gen_buses.append(s_n[j])
            caps.append(s_c[j])
    else:
        reduced_gen_buses.append(s_n[0])
        caps.append(s_c[0])

##################################
#LOAD
##################################

df_load = pd.read_csv('10k_Load.csv')

#pull all nodes with >0 load
non_zero = list(df_load.loc[df_load['Load MW']>0,'Number'])
unique_non_zero = []
for i in non_zero:
    if i in reduced_gen_buses:
        pass
    else:
        unique_non_zero.append(i)

#pull all nodes with voltage > 500kV
major_V = list(df_load.loc[df_load['Nom kV']>500,'Number'])
unique_major_V = []
for i in major_V:
    if i in reduced_gen_buses:
        pass
    elif i in unique_non_zero:
        pass
    else:
        unique_major_V.append(i)
        
#Calculate load weights for State/BA combinations
states = list(df_BA_states['State'].unique())
BAs = list(df_BA_states['NAME'].unique())


keys=[]
loads=[]
max_loads = []

for i in non_zero:
    
    area = df_BA_states.loc[df_BA_states['Number']==i,'NAME'].values
    state = df_BA_states.loc[df_BA_states['Number']==i,'State'].values
    l = df_load.loc[df_load['Number']==i,'Load MW'].values
    
    t = tuple([str(area),str(state)])
    
    if t in keys:
        idx=keys.index(t)
        loads[idx] += l    
        if max_loads[idx] < l:
            max_loads[idx] = i
    else:
        keys.append(t)
        loads.append(l)
        max_loads.append(i)

load_weights = loads/sum(loads)

#Create analogous generation weights

gens = []
gen_keys = []

for i in reduced_gen_buses:
    
    x = reduced_gen_buses.index(i)
    
    area = df_BA_states.loc[df_BA_states['Number']==i,'NAME'].values
    state = df_BA_states.loc[df_BA_states['Number']==i,'State'].values
    
    t = tuple([str(area),str(state)])
    
    if t in gen_keys:
        idx=gen_keys.index(t)
        gens[idx] += caps[x]
        
    else:
        gen_keys.append(t)
        gens.append(caps[x])
        
gen_weights = gens/sum(gens)

##############################
#Nodal reduction
##############################

#specify number of nodes 
N = 300
g_N = 100 #generation nodes
l_N = 150 #demand nodes
t_N = N - g_N - l_N

#1 - put one demand node in each state/BA pairing (max node in each)
demand_nodes_selected = []
for k in keys:
    idx = keys.index(k)
    demand_nodes_selected.append(max_loads[idx])
    l_N += -1

#2 - allocate remaining demand nodes based on MW ranking of individual nodes
unallocated = [i for i in non_zero if i not in demand_nodes_selected]
load_ranks = np.zeros((len(unallocated),2))

for i in unallocated:
    idx = unallocated.index(i)
    load_ranks[idx,0] = i
    load_ranks[idx,1] = df_load.loc[df_load['Number']==i,'Load MW'].values
df_load_ranks = pd.DataFrame(load_ranks)
df_load_ranks.columns = ['BusName','MW']
df_load_ranks = df_load_ranks.sort_values(by='MW',ascending=False)
df_load_ranks = df_load_ranks.reset_index(drop=True)

added = 0
while l_N > 0:
    demand_nodes_selected.append(int(df_load_ranks.loc[added,'BusName']))
    added += 1  
    l_N += -1

#3 - allocate generation based on reduced gens (screen for overlap)

gen_nodes_selected = []
unallocated_gens = [i for i in reduced_gen_buses if i not in demand_nodes_selected]
unallocated_caps = []
for i in unallocated_gens:
    idx = reduced_gen_buses.index(i)
    unallocated_caps.append(caps[idx])

df_gen_ranks = pd.DataFrame()
df_gen_ranks['BusName'] = unallocated_gens
df_gen_ranks['MW'] = unallocated_caps

df_gen_ranks = df_gen_ranks.sort_values(by='MW',ascending=False)
df_gen_ranks = df_gen_ranks.reset_index(drop=True)

added = 0
while g_N > 0:
    gen_nodes_selected.append(int(df_gen_ranks.loc[added,'BusName']))
    added += 1  
    g_N += -1

#4 - allocate transmission nodes based on load as well (screen for overlap, make sure list is for >=345kV)
trans_nodes_selected = []
unallocated_trans = [i for i in non_zero if i not in demand_nodes_selected]
unallocated_trans = [i for i in unallocated_trans if i not in gen_nodes_selected]

load_ranks = np.zeros((len(unallocated_trans),2))

for i in unallocated_trans:
    idx = unallocated_trans.index(i)
    load_ranks[idx,0] = i
    load_ranks[idx,1] = df_load.loc[df_load['Number']==i,'Load MW'].values
df_load_ranks = pd.DataFrame(load_ranks)
df_load_ranks.columns = ['BusName','MW']
df_load_ranks = df_load_ranks.sort_values(by='MW',ascending=False)
df_load_ranks = df_load_ranks.reset_index(drop=True)

added = 0
while t_N > 0:
    trans_nodes_selected.append(int(df_load_ranks.loc[added,'BusName']))
    added += 1  
    t_N += -1


# plot (unique colors, and combos)

fig,ax = plt.subplots()
states_gdf.plot(ax=ax,color='white',edgecolor='black',linewidth=0.5)
nodes_df.plot(ax=ax,color = 'lightgray',alpha=1)
M=18

G_NODES = nodes_df[nodes_df['Number'].isin(gen_nodes_selected)]
G_NODES.plot(ax=ax,color = 'deepskyblue',markersize=M,alpha=1,edgecolor='black',linewidth=0.3)

D_NODES = nodes_df[nodes_df['Number'].isin(demand_nodes_selected)]
D_NODES.plot(ax=ax,color = 'deeppink',markersize=M,alpha=1,edgecolor='black',linewidth=0.3)

T_NODES = nodes_df[nodes_df['Number'].isin(trans_nodes_selected)]
T_NODES.plot(ax=ax,color = 'limegreen',markersize=M,alpha=1,edgecolor='black',linewidth=0.3)   

ax.set_box_aspect(1)
ax.set_xlim(-2000000,0)
ax.set_ylim([-1750000,750000])
plt.axis('off')
plt.savefig('draft_topology.jpg',dpi=330)


#SO-CAL
fig,ax = plt.subplots()
states_gdf.plot(ax=ax,color='white',edgecolor='black',linewidth=0.5)
nodes_df.plot(ax=ax,color = 'lightgray',alpha=1)
M=18

G_NODES.plot(ax=ax,color = 'deepskyblue',markersize=M,alpha=1,edgecolor='black',linewidth=0.3)
D_NODES.plot(ax=ax,color = 'deeppink',markersize=M,alpha=1,edgecolor='black',linewidth=0.3)
T_NODES.plot(ax=ax,color = 'limegreen',markersize=M,alpha=1,edgecolor='black',linewidth=0.3)   

ax.set_box_aspect(1)
ax.set_xlim(-1800000,-1100000)
ax.set_ylim([-1400000,-700000])
plt.axis('off')
plt.savefig('SOCAL_topology.jpg',dpi=330)


#Mid-C
fig,ax = plt.subplots()
states_gdf.plot(ax=ax,color='white',edgecolor='black',linewidth=0.5)
nodes_df.plot(ax=ax,color = 'lightgray',alpha=1)
M=18

G_NODES.plot(ax=ax,color = 'deepskyblue',markersize=M,alpha=1,edgecolor='black',linewidth=0.3)
D_NODES.plot(ax=ax,color = 'deeppink',markersize=M,alpha=1,edgecolor='black',linewidth=0.3)
T_NODES.plot(ax=ax,color = 'limegreen',markersize=M,alpha=1,edgecolor='black',linewidth=0.3)   

ax.set_box_aspect(1)
ax.set_xlim(-2000000,-1000000)
ax.set_ylim([0,750000])
plt.axis('off')
plt.savefig('MIDC_topology.jpg',dpi=330)


#SF Bay Area
fig,ax = plt.subplots()
states_gdf.plot(ax=ax,color='white',edgecolor='black',linewidth=0.5)
nodes_df.plot(ax=ax,color = 'lightgray',alpha=1)
M=18

G_NODES.plot(ax=ax,color = 'deepskyblue',markersize=M,alpha=1,edgecolor='black',linewidth=0.3)
D_NODES.plot(ax=ax,color = 'deeppink',markersize=M,alpha=1,edgecolor='black',linewidth=0.3)
T_NODES.plot(ax=ax,color = 'limegreen',markersize=M,alpha=1,edgecolor='black',linewidth=0.3)   

ax.set_box_aspect(1)
ax.set_xlim(-2000000,-1500000)
ax.set_ylim([-750000,0])
plt.axis('off')
plt.savefig('SF_topology.jpg',dpi=330)

selected_nodes = demand_nodes_selected + gen_nodes_selected + trans_nodes_selected
full = list(df_BA_states['Number'])

excluded = [i for i in full if i not in selected_nodes]

df_excluded_nodes = pd.DataFrame(excluded)
df_excluded_nodes.columns = ['ExcludedNodes']
df_excluded_nodes.to_csv('excluded_nodes.csv')

df_selected_nodes = pd.DataFrame(selected_nodes)
df_selected_nodes.columns = ['SelectedNodes']
df_selected_nodes.to_csv('selected_nodes.csv')
