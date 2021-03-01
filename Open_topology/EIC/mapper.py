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

df = pd.read_csv('EIA.csv',header=0)
crs = {'init':'epsg:4326'}
# crs = {"init": "epsg:2163"}
geometry = [Point(xy) for xy in zip(df['Substation Longitude'],df['Substation Latitude'])]
nodes_df = gpd.GeoDataFrame(df,crs=crs,geometry=geometry)
nodes_df = nodes_df.to_crs(epsg=2163)

BAs_gdf = gpd.read_file('Control_Areas.shp')
BAs_gdf = BAs_gdf.to_crs(epsg=2163)

states_gdf = gpd.read_file('geo_export_9ef76f60-e019-451c-be6b-5a879a5e7c07.shp')
states_gdf = states_gdf.to_crs(epsg=2163)


# joined = gpd.sjoin(nodes_df,BAs_gdf,how='left',op='within')
# joined2 = gpd.sjoin(nodes_df,states_gdf,how='left',op='within')
# joined['State'] = joined2['state_name']

# buses = list(joined['Number'])
# B = []
# for b in buses:
#     if b in B:
#         pass
#     else:
#         B.append(b)
        
#elimate redundant buses (overlapping BAs) based on peak load

# for b in B:
    
#     sample = joined[joined['Number'] == b]
    
#     if len(sample) > 1:
#         smallest = min(sample['PEAK_LOAD'])
#         selection = sample[sample['PEAK_LOAD']==smallest]
    
#     else:
        
#         selection = sample
        
#     b_idx = B.index(b)
#     print(b_idx)
    
#     if b_idx < 1:
        
#         combined = selection
    
#     else:
        
#         combined = combined.append(selection) 
    

# combined.to_csv('nodes_to_BA_state.csv')


##################################################################
# Need to manually fill in missing BAs with 'NAN' before next part
##################################################################

##############################
#  Generators
##############################

import re
from itertools import compress
import copy

df_BA_states = pd.read_csv('nodes_to_BA_state.csv',index_col=0)

assigned = df_BA_states[df_BA_states['NAME']!='NAN']
assigned = assigned.reset_index(drop=True)

lats = np.array(assigned['Substation Latitude'])
lats_idx = np.column_stack((lats,range(0,len(lats))))

longs = np.array(assigned['Substation Longitude'])
longs_idx = np.column_stack((longs,range(0,len(longs))))

unassigned = df_BA_states[df_BA_states['NAME'] == 'NAN']
unassigned = unassigned.reset_index(drop=True)

for i in range(0,len(unassigned)):
    
    sample_lat = unassigned.loc[i,'Substation Latitude']
    sample_long = unassigned.loc[i,'Substation Longitude']
    
    a = copy.deepcopy(lats_idx)
    b = copy.deepcopy(longs_idx)
    a[:,0] = np.abs(a[:,0] - sample_lat)
    b[:,0] = np.abs(b[:,0] - sample_long)

    c = a[:,0] + b[:,0]
    c_list = list(c)
    M = min(c_list)
    idx = c_list.index(M)
    
    bus = unassigned.loc[i,'Number']
    df_BA_states.loc[df_BA_states['Number'] == bus,'NAME'] = assigned.loc[idx,'NAME']
    df_BA_states.loc[df_BA_states['Number'] == bus,'State'] = assigned.loc[idx,'State']
    
df_gens = pd.read_csv('Generators_EIA.csv')

names = list(df_gens['BusName'])
BAs = []
c = list(df_BA_states.columns)
nx = c.index('NAME')

# remove numbers and spaces
for n in names:
    i = names.index(n)
    corrected = re.sub(r'[^A-Z]',r'',n)
    names[i] = corrected
    BA = df_BA_states[df_BA_states['Number'] == df_gens.loc[i,'BusNum']]
    BAs.append(BA.iloc[0,nx])
    
df_gens['BusName'] = names
df_gens['BA'] = BAs

#select a single bus for each plant/BA combination (generators with the same name)

leftover = []
reduced_gen_buses = []
unique_bus_names = []
caps = []

for n in names:
    if n in unique_bus_names:
        pass
    else:
        unique_bus_names.append(n)

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

df_load = pd.read_csv('Buses_EIA.csv')

#pull all nodes with >0 load
non_zero = list(df_load.loc[df_load['LoadMW']>0,'Number'])
unique_non_zero = []
for i in non_zero:
    if i in reduced_gen_buses:
        pass
    else:
        unique_non_zero.append(i)

#pull all nodes with voltage >= 500kV
major_V = list(df_load.loc[df_load['NomkV']>=500,'Number'])
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
    l = df_load.loc[df_load['Number']==i,'LoadMW'].values
    
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
N = 1000
g_N = 400 #generation nodes
l_N = 400 #demand nodes
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
    load_ranks[idx,1] = df_load.loc[df_load['Number']==i,'LoadMW'].values
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
    load_ranks[idx,1] = df_load.loc[df_load['Number']==i,'LoadMW'].values
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
ax.set_xlim(-800000,2700000)
ax.set_ylim([-2000000,800000])
plt.axis('off')
plt.savefig('draft_topology.jpg',dpi=330)


#CACKALACKY
fig,ax = plt.subplots()
states_gdf.plot(ax=ax,color='white',edgecolor='black',linewidth=0.5)
nodes_df.plot(ax=ax,color = 'lightgray',alpha=1)
M=18

G_NODES.plot(ax=ax,color = 'deepskyblue',markersize=M,alpha=1,edgecolor='black',linewidth=0.3)
D_NODES.plot(ax=ax,color = 'deeppink',markersize=M,alpha=1,edgecolor='black',linewidth=0.3)
T_NODES.plot(ax=ax,color = 'limegreen',markersize=M,alpha=1,edgecolor='black',linewidth=0.3)   

ax.set_box_aspect(1)
ax.set_xlim(1200000,2300000)
ax.set_ylim([-1200000,-500000])
plt.axis('off')
plt.savefig('CACKALACKY_topology.jpg',dpi=330)


# #DALLAS
# fig,ax = plt.subplots()
# states_gdf.plot(ax=ax,color='white',edgecolor='black',linewidth=0.5)
# nodes_df.plot(ax=ax,color = 'lightgray',alpha=1)
# M=18

# G_NODES.plot(ax=ax,color = 'deepskyblue',markersize=M,alpha=1,edgecolor='black',linewidth=0.3)
# D_NODES.plot(ax=ax,color = 'deeppink',markersize=M,alpha=1,edgecolor='black',linewidth=0.3)
# T_NODES.plot(ax=ax,color = 'limegreen',markersize=M,alpha=1,edgecolor='black',linewidth=0.3)   

# ax.set_box_aspect(1)
# ax.set_xlim(200000,350000)
# ax.set_ylim([-1400000,-1275000])
# plt.axis('off')
# plt.savefig('DALLAS_topology.jpg',dpi=330)


selected_nodes = demand_nodes_selected + gen_nodes_selected + trans_nodes_selected
full = list(df_BA_states['Number'])

excluded = [i for i in full if i not in selected_nodes]

df_excluded_nodes = pd.DataFrame(excluded)
df_excluded_nodes.columns = ['ExcludedNodes']
df_excluded_nodes.to_csv('excluded_nodes.csv')

df_selected_nodes = pd.DataFrame(selected_nodes)
df_selected_nodes.columns = ['SelectedNodes']
df_selected_nodes.to_csv('selected_nodes.csv')
