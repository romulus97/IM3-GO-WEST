# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import pandas as pd
import math
import numpy as np
import os
from shutil import copy
from pathlib import Path

########################################
# LOAD ALLOCATION FROM BALANCING AUTHORITY to NODES
########################################

df_load = pd.read_csv('BA_data/BA_load.csv',header=0)
df_BAs = pd.read_csv('BA_data/BAs.csv',header=0)
BAs = list(df_BAs['Name'])

df_wind = pd.read_csv('BA_data/BA_wind.csv',header=0,index_col=0)
df_solar = pd.read_csv('BA_data/BA_solar.csv',header=0,index_col=0)
df_solar_wind_cap_EIA = pd.read_csv('BA_data/BA_solar_wind_capacity_EIA.csv',header=0,index_col=0)

df_gen = pd.read_csv('10k_topology_files/10k_Gen.csv',header=0)
df_full = pd.read_csv('10k_topology_files/nodes_to_BA_state.csv',header=0,index_col=0)

BA_to_BA_hurdle_data = pd.read_csv('BA_to_BA_hurdle.csv',header=0)
all_BA_BA_connections = list(BA_to_BA_hurdle_data['BA_to_BA'])

# NODE_NUMBER = [75,100,125,150,175,200,225,250,275,300]
NODE_NUMBER = [100]

# UC_TREATMENTS = ['_simple','_coal']
UC_TREATMENTS = ['_simple']

# line_limit_MW_scaling = [25,50,75,100]
line_limit_MW_scaling = [900]

# BA_hurdle_scaling = list(range(0,1050,100))
BA_hurdle_scaling = [0]

for NN in NODE_NUMBER:
    
    for UC in UC_TREATMENTS:
        
        for T_p in line_limit_MW_scaling:
            
            for BA_hurd in BA_hurdle_scaling:
    
                path=str(Path.cwd()) + str(Path('/Simulation_folders/Exp' + str(NN) + UC + '_' + str(T_p) + '_' + str(BA_hurd)))
                os.makedirs(path,exist_ok=True)
                
                T_p_new = T_p
                BA_hurd_new = BA_hurd/100
                
                FN = 'Selected_nodes/Results_Excluded_Nodes_' + str(NN) + '.xlsx'
             
                # selected nodes
                df_selected = pd.read_excel(FN,sheet_name = 'Bus', header=0)
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
                        W = (df_selected.loc[i,'Pd']/X)
                        weights.append(W)
                df_selected['BA Load Weight'] = weights
                
                idx = 0
                w= 0
                T = np.zeros((8760,len(buses)))
                
                for i in range(0,len(df_selected)):
                    
                    #load for original node
                    name = df_selected.loc[i,'BA']
                    
                    if float(df_BA_totals.loc[df_BA_totals['Name']==str(name),'Total'].values[0]) < 1:
                        pass
                    else: 
                        
                        abbr = df_BAs.loc[df_BAs['Name']==name,'Abbreviation'].values[0]
                        weight = df_selected.loc[i,'BA Load Weight']
                        
                        if max(df_load[abbr]) < 1:
                            T[:,i] = T[:,i] + np.reshape(df_load[abbr].values,(8760,))                    
                        else:                    
                            T[:,i] = T[:,i] + np.reshape(df_load[abbr].values*weight,(8760,)) 
            
                for i in range(0,len(buses)):
                    buses[i] = 'bus_' + str(buses[i])
                
                df_C = pd.DataFrame(T)
                df_C.columns = buses
                df_C.to_csv('nodal_load.csv',index=None)   
                
                copy('nodal_load.csv',path)
                
                #############
                # GENERATORS  
                
                # read reduction algorithm summary and parse nodal operations
                df_summary = pd.read_excel(FN,sheet_name='Summary',header=5)
                # df_summary = df_summary.drop([len(df_summary)-1])
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
                    if area in BAs:
                        if str(df_full.loc[i,'FuelType']) != 'WND (Wind)':
                            weights.append(0)
                        else:        
                            X = float(df_BA_totals.loc[df_BA_totals['Name']==area,'Total'])
                            W = df_full.loc[i,'MWMax']/X
                            weights.append(W)
                    else:
                        weights.append(0)
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
                
                BA_sums = np.zeros((len(BAs),1))
            
                #finding how many nodes in each BA
                selected_nodes = df_full.loc[df_full['Number'].isin(buses)]
                node_count_BA = selected_nodes['NAME'].value_counts()
                
                for b in buses:
                    
                    #load for original node
                    sample = df_full.loc[df_full['Number'] == b]
                    sample = sample.reset_index(drop=True)
                    name = sample['NAME'][0]
                
                    
                    if name in BAs:
                    
                        if float(df_BA_totals.loc[df_BA_totals['Name']==name,'Total'].values[0]) < 1:
                            
                            if df_solar_wind_cap_EIA.loc[name,'Wind'] < 1:
                                pass
                            else:
                                node_count_BA_sp = node_count_BA[name]
                                abbr = df_BAs.loc[df_BAs['Name']==name,'Abbreviation'].values[0]
                                T[:,idx] = T[:,idx] + np.reshape(df_wind[abbr].values/node_count_BA_sp,(8760,))
                                                
                        else:
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
                            if name in BAs:
                            
                                if float(df_BA_totals.loc[df_BA_totals['Name']==str(name),'Total'].values[0]) < 1:
                                    pass
                                else:
                                    abbr = df_BAs.loc[df_BAs['Name']==name,'Abbreviation'].values[0]
                                    weight = sample['BA Wind Weight']
                                    w += weight  
                                    dx = BAs.index(name)
                                    BA_sums[dx] = BA_sums[dx] + weight
                                    T[:,idx] = T[:,idx] + np.reshape(df_wind[abbr].values*weight.values[0],(8760,))
                            else:
                                pass
                        
                    except KeyError:
                        # print (b)
                        pass
                    
                    idx +=1
                
                w_buses = []
                for i in range(0,len(buses)):
                    w_buses.append('bus_' + str(buses[i]))
                
                df_C = pd.DataFrame(T)
                df_C.columns = w_buses
                df_C.to_csv('nodal_wind.csv',index=None)   
                copy('nodal_wind.csv',path)
                
                
                ##################################
                # SOLAR ALLOCATION FROM BA TO NODE

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
                    if area in BAs:
                        if str(df_full.loc[i,'FuelType']) != 'SUN (Solar)':
                            weights.append(0)
                        else:
                            X = float(df_BA_totals.loc[df_BA_totals['Name']==area,'Total'])
                            W = df_full.loc[i,'MWMax']/X
                            weights.append(W)
                    else:  
                        weights.append(0)
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
                
                BA_sums = np.zeros((len(BAs),1))
            
                #finding how many nodes in each BA
                selected_nodes = df_full.loc[df_full['Number'].isin(buses)]
                node_count_BA = selected_nodes['NAME'].value_counts()
                    
                for b in buses:
                    
                    #load for original node
                    sample = df_full.loc[df_full['Number'] == b]
                    sample = sample.reset_index(drop=True)
                    name = sample['NAME'][0]
                
                    
                    if name in BAs:
                    
                        if float(df_BA_totals.loc[df_BA_totals['Name']==name,'Total'].values[0]) < 1:
                            
                            if df_solar_wind_cap_EIA.loc[name,'Solar'] < 1:
                                pass
                            
                            else:
                                node_count_BA_sp = node_count_BA[name]
                                abbr = df_BAs.loc[df_BAs['Name']==name,'Abbreviation'].values[0]
                                T[:,idx] = T[:,idx] + np.reshape(df_solar[abbr].values/node_count_BA_sp,(8760,))
                        
                        else:
                
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
                            if name in BAs:
                            
                                if float(df_BA_totals.loc[df_BA_totals['Name']==str(name),'Total'].values[0]) < 1:
                                    pass
                                
                                else:
                                    abbr = df_BAs.loc[df_BAs['Name']==name,'Abbreviation'].values[0]
                                    weight = sample['BA Solar Weight']
                                    w += weight  
                                    dx = BAs.index(name)
                                    BA_sums[dx] = BA_sums[dx] + weight
                                    T[:,idx] = T[:,idx] + np.reshape(df_solar[abbr].values*weight.values[0],(8760,))
                            
                            else:
                                pass
                        
                    except KeyError:
                        # print (b)
                        pass
                    
                    idx +=1
                    
                
                s_buses = []
                for i in range(0,len(buses)):
                    s_buses.append('bus_' + str(buses[i]))
                
                df_C = pd.DataFrame(T)
                df_C.columns = s_buses
                df_C.to_csv('nodal_solar.csv',index=None)  
                copy('nodal_solar.csv',path)
                
                
                ##############################
                # THERMAL GENERATION
                
                import re
                
                df_gens = pd.read_csv('10k_topology_files/10k_Gen.csv',header=0)
                df_gens = df_gens.replace('', np.nan, regex=True)
                df_gens_heat_rate = pd.read_excel('NG_Coal_heat_rates.xlsx',header=0)
                old_bus_num =[]
                new_bus_num = []
                NB = []
                
                old_bus_num_hr =[]
                new_bus_num_hr = []
                NB_hr = []
                
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
                
                for i in range(0,len(df_gens_heat_rate)):
                    OB = df_gens_heat_rate.loc[i,'BusNum']
                    if OB in old_bus_num:
                        idx = old_bus_num.index(OB)
                        NB_hr.append(new_bus_num[idx])
                    else:
                        NB_hr.append(OB)
                
                df_gens_heat_rate['NewBusNum'] = NB_hr
        
                names = list(df_gens['BusName'])
                names_hr = list(df_gens_heat_rate['BusName'])
                
                # remove numbers and spaces
                for n in names:
                    i = names.index(n)
                    corrected = re.sub(r'[^A-Z]',r'',n)
                    names[i] = corrected
                    
                for n in names_hr:
                    i = names_hr.index(n)
                    corrected = re.sub(r'[^A-Z]',r'',n)
                    names_hr[i] = corrected
                
                df_gens['PlantNames'] = names
                df_gens_heat_rate['PlantNames'] = names_hr
                
                NB = df_gens['NewBusNum'].unique()
                plants = []
                caps = []
                mw_min = []
                count = 2
                nbs = []
                heat_rate = []
                f = []
                thermal = ['NG (Natural Gas)','NUC (Nuclear)','BIT (Bituminous Coal)','NUC (Nuclear)']
                
                for n in NB:
                    sample = df_gens.loc[df_gens['NewBusNum'] == n]
                    sample_hr = df_gens_heat_rate.loc[df_gens_heat_rate['NewBusNum'] == n]
                    sublist = sample['PlantNames'].unique()
                    for s in sublist:
                        fuel = list(sample.loc[sample['PlantNames']==s,'FuelType'])
                        if fuel[0] in thermal:
                            c = sum(sample.loc[sample['PlantNames']==s,'MWMax'].values)
                            hr = np.nanmean(sample.loc[sample['PlantNames']==s,'Heat Rate MBTU/MWh'].values)
                            if hr == np.nan or hr == 0 or hr == 'nan' or hr == '':
                                hr = np.nanmean(sample_hr.loc[sample_hr['PlantNames']==s,'Heat Rate MBTU/MWh'].values)
                            else:
                                pass
                            mn = sum(sample.loc[sample['PlantNames']==s,'MWMin'].values)
                            mw_min.append(mn)
                            caps.append(c)
                            nbs.append(n)
                            heat_rate.append(hr)
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
                C=np.column_stack((C,heat_rate))
                
                df_C = pd.DataFrame(C)
                df_C.columns = ['Name','Bus','Fuel','Max_Cap','Min_Cap','Heat_Rate']
                df_C.to_csv('Thermal_gens.csv',index=None)
                copy('Thermal_gens.csv',path)
                    
                
                ##############################
                # HYDROPOWER
                
                #EIA plants
                df_hydro = pd.read_csv('Hydro_gen_setup/EIA_302_WECC_hydro_plants.csv',header=0)
                df_hydro_ts = pd.read_csv('Hydro_gen_setup/p_mean_max_min_MW_WECC_302plants_weekly_2019.csv',header=0)
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
                        print(name + ' Not found')
                
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
                
                h_buses = []
                for i in range(0,len(buses)):
                    h_buses.append('bus_' + str(buses[i]))
                
                H_min_df = pd.DataFrame(H_min_hourly)
                H_min_df.columns = h_buses
                H_max_df = pd.DataFrame(H_max_hourly)
                H_max_df.columns = h_buses
                H_mu_df = pd.DataFrame(H_mu_hourly) 
                H_mu_df.columns = h_buses       
                
                H_min_df.to_csv('Hydro_min.csv',index=None)
                H_max_df.to_csv('Hydro_max.csv',index=None)
                H_mu_df.to_csv('Hydro_total.csv',index=None)
                
                copy('Hydro_min.csv',path)
                copy('Hydro_max.csv',path)
                copy('Hydro_total.csv',path)
                
                    
                
                #########################################
                # Generator file setup
                
                df_G = pd.read_csv('Thermal_Gens.csv',header=0)
                
                names = []
                typs = []
                nodes = []
                maxcaps = []
                mincaps = []
                heat_rates = []
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
                    node = 'bus_' + str(df_G.loc[i,'Bus'])
                    maxcap = df_G.loc[i,'Max_Cap']
                    mincap = df_G.loc[i,'Min_Cap']
                    hr_2 = df_G.loc[i,'Heat_Rate']
                    
                    if typ == 'ngcc':
                        var_om = 3
                        minup = 4
                        mindn = 4
                        ramp = maxcap
                        hr_2 = hr_2*2.098
                    else:
                        var_om = 4
                        minup = 12
                        mindn = 12
                        ramp = 0.33*maxcap
                        hr_2 = hr_2*1.310
                    
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
                        heat_rates.append(hr_2)
                        
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
                        heat_rates.append(0)
                
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
                        heat_rates.append(0)
                
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
                        heat_rates.append(0)
                
                df_genparams = pd.DataFrame()
                df_genparams['name'] = names
                df_genparams['typ'] = typs
                df_genparams['node'] = nodes
                df_genparams['maxcap'] = maxcaps
                df_genparams['heat_rate'] = heat_rates
                df_genparams['mincap'] = mincaps
                df_genparams['var_om'] = var_oms
                df_genparams['no_load'] = no_loads
                df_genparams['st_cost'] = st_costs
                df_genparams['ramp'] = ramps
                df_genparams['minup'] = minups
                df_genparams['mindn'] = mindns
                
                df_genparams.to_csv('data_genparams.csv',index=None)
                copy('data_genparams.csv',path)
                
                df_must = pd.DataFrame()
                for i in range(0,len(must_nodes)):
                    n = must_nodes[i]
                    df_must[n] = [must_caps[i]]
                df_must.to_csv('must_run.csv',index=None)
                copy('must_run.csv',path)
                
                
                
                ######
                # create gen-to-bus matrix
                
                df = pd.read_csv('data_genparams.csv',header=0)
                gens = list(df.loc[:,'name'])
                
                df_nodes = pd.read_excel(FN, sheet_name = 'Bus', header=0)
                all_nodes = list(df_nodes['bus_i'])
                for i in range(0,len(all_nodes)):
                    all_nodes[i] = 'bus_' + str(all_nodes[i])
                
                A = np.zeros((len(gens),len(all_nodes)))
                
                df_A = pd.DataFrame(A)
                df_A.columns = all_nodes
                df_A['name'] = gens
                df_A.set_index('name',inplace=True)
                
                for i in range(0,len(gens)):
                    node = df.loc[i,'node']
                    g = gens[i]
                    df_A.loc[g,node] = 1
                
                df_A.to_csv('gen_mat.csv')
                copy('gen_mat.csv',path)
                
                #####################################
                # TRANSMISSION
                
                df = pd.read_excel(FN,sheet_name = 'Branch',header=0)
                
                # eliminate repeats
                lines = []
                repeats = []
                index = []
                for i in range(0,len(df)):
                    
                    t=tuple((df.loc[i,'fbus'],df.loc[i,'tbus']))
                    
                    if t in lines:
                        df = df.drop([i])
                        repeats.append(t)
                        r = lines.index(t)
                        i = index[r]
                        df.loc[i,'rateA'] += df.loc[i,'rateA']
                    else:
                        lines.append(t)
                        index.append(i)
                
                df = df.reset_index(drop=True)
                    
                sources = df.loc[:,'fbus']
                sinks = df.loc[:,'tbus']
                combined = np.append(sources, sinks)
                df_combined = pd.DataFrame(combined,columns=['node'])
                unique_nodes = df_combined['node'].unique()
                unique_nodes.sort()
                
                A = np.zeros((len(df),len(unique_nodes)))
                
                df_line_to_bus = pd.DataFrame(A)
                df_line_to_bus.columns = unique_nodes
                
                negative = []
                positive = []
                lines = []
                ref_node = 0
                reactance = []
                limit = []
                
                for i in range(0,len(df)):
                    s = df.loc[i,'fbus']
                    k = df.loc[i,'tbus']
                    line = str(s) + '_' + str(k)
                    if s == df.loc[0,'fbus']: 
                        lines.append(line)
                        positive.append(s)
                        negative.append(k)
                        df_line_to_bus.loc[ref_node,s] = 1
                        df_line_to_bus.loc[ref_node,k] = -1
                        reactance.append(df.loc[i,'x'])
                        MW = ((1/df.loc[i,'x'])*100)+T_p_new
                        limit.append(MW)
                        ref_node += 1
                    elif k == df.loc[0,'fbus']:      
                        lines.append(line)
                        positive.append(k)
                        negative.append(s)
                        df_line_to_bus.loc[ref_node,k] = 1
                        df_line_to_bus.loc[ref_node,s] = -1
                        reactance.append(df.loc[i,'x'])
                        MW = ((1/df.loc[i,'x'])*100)+T_p_new
                        limit.append(MW)
                        ref_node += 1
                        
                for i in range(0,len(df)):
                    s = df.loc[i,'fbus']
                    k = df.loc[i,'tbus']
                    line = str(s) + '_' + str(k)
                    if s != df.loc[0,'fbus']:
                        if k != df.loc[0,'fbus']:
                            lines.append(line)
                            
                            if s in positive and k in negative:
                                df_line_to_bus.loc[ref_node,s] = 1
                                df_line_to_bus.loc[ref_node,k] = -1
                            
                            elif k in positive and s in negative:
                                df_line_to_bus.loc[ref_node,k] = 1
                                df_line_to_bus.loc[ref_node,s] = -1
                                
                            elif s in positive and k in positive:
                                df_line_to_bus.loc[ref_node,s] = 1
                                df_line_to_bus.loc[ref_node,k] = -1
                            
                            elif s in negative and k in negative:   
                                df_line_to_bus.loc[ref_node,s] = 1
                                df_line_to_bus.loc[ref_node,k] = -1
                                
                            elif s in positive:
                                df_line_to_bus.loc[ref_node,s] = 1
                                df_line_to_bus.loc[ref_node,k] = -1
                                negative.append(k)
                            elif s in negative:
                                df_line_to_bus.loc[ref_node,k] = 1
                                df_line_to_bus.loc[ref_node,s] = -1   
                                positive.append(k)
                            elif k in positive:
                                df_line_to_bus.loc[ref_node,k] = 1
                                df_line_to_bus.loc[ref_node,s] = -1  
                                negative.append(s)
                            elif k in negative:
                                df_line_to_bus.loc[ref_node,s] = 1
                                df_line_to_bus.loc[ref_node,k] = -1 
                                positive.append(s)
                            else:
                                positive.append(s)
                                negative.append(k)
                                df_line_to_bus.loc[ref_node,s] = 1
                                df_line_to_bus.loc[ref_node,k] = -1
                
                            reactance.append(df.loc[i,'x'])
                            MW = ((1/df.loc[i,'x'])*100)+T_p_new
                            limit.append(MW)
                            ref_node += 1
                
                unique_nodes = list(unique_nodes)
                for i in range(0,len(unique_nodes)):
                    unique_nodes[i] = 'bus_' + str(unique_nodes[i])
                df_line_to_bus.columns = unique_nodes
                
                for i in range(0,len(lines)):
                    lines[i] = 'line_' + lines[i]
                    
                df_line_to_bus['line'] = lines
                df_line_to_bus.set_index('line',inplace=True)
                df_line_to_bus.to_csv('line_to_bus.csv')
                copy('line_to_bus.csv',path)
                
                
                df_line_params = pd.DataFrame()
                df_line_params['line'] = lines
                df_line_params['reactance'] = reactance
                df_line_params['limit'] = limit 
                df_line_params.to_csv('line_params.csv',index=None)
                copy('line_params.csv',path)
                
                #Creating BA to BA transmission matrix for individual lines
                exchange_columns = ['Exchange'] + lines
                BA_to_BA_exhange_matrix = pd.DataFrame(np.zeros((len(all_BA_BA_connections),len(exchange_columns))),columns=exchange_columns,index=all_BA_BA_connections)
                BA_to_BA_exhange_matrix.loc[:,'Exchange'] = all_BA_BA_connections
                
                for i in all_BA_BA_connections:
                    
                    weight_count = 0
                    line_count = 0
                    
                    splitted_str = i.split('_')
                    first_BA = splitted_str[0]
                    second_BA = splitted_str[1]
                    
                    for j in lines:
                                            
                        splitted_line = j.split('_')
                        BA_first_line = df_selected.loc[df_selected['bus_i']==int(splitted_line[1])]['BA'].values[0]
                        first_BA_abb = df_BAs.loc[df_BAs['Name']==BA_first_line]['Abbreviation'].values[0]
                        
                        a_bus = df_line_to_bus.loc[j,'bus_' + splitted_line[1]]
                        
                        BA_second_line = df_selected.loc[df_selected['bus_i']==int(splitted_line[2])]['BA'].values[0]
                        second_BA_abb = df_BAs.loc[df_BAs['Name']==BA_second_line]['Abbreviation'].values[0]
                        
                        b_bus = df_line_to_bus.loc[j,'bus_' + splitted_line[2]]
                        
                        # print(a_bus + b_bus)
                        
                        #if flow on that line means flow from first BA to second BA, write 1, if vice versa write -1
                        if first_BA_abb == first_BA and second_BA_abb == second_BA:
                            line_count += 1
                            BA_to_BA_exhange_matrix.loc[i,j] = int(b_bus)
                        elif first_BA_abb == second_BA and second_BA_abb == first_BA:
                            BA_to_BA_exhange_matrix.loc[i,j] = int(a_bus)
                            line_count += 1
                        else:
                            pass
                        
                        weight_count += int(BA_to_BA_exhange_matrix.loc[i,j])
                        
                
                BA_to_BA_hurdle_data_new = BA_to_BA_hurdle_data.copy()
                BA_to_BA_hurdle_data_new['Hurdle_$/MWh'] = BA_to_BA_hurdle_data_new['Hurdle_$/MWh']*(1+BA_hurd_new)
                BA_to_BA_hurdle_data_new.to_csv('BA_to_BA_hurdle_scaled.csv', index=False)
                copy('BA_to_BA_hurdle_scaled.csv',path)
                
                BA_to_BA_exhange_matrix.to_csv('BA_to_BA_transmission_matrix.csv', index=False)
                copy('BA_to_BA_transmission_matrix.csv',path)
                
                #####################################
                # FUEL PRICES
                
                # Natural gas prices
                NG_price = pd.read_csv('NG_price/Average_NG_prices_BAs.csv', header=0)
                buses = list(df_selected['bus_i'])
                for bus in buses:
                    
                    selected_node_BA = df_full.loc[df_full['Number']==bus,'NAME'].values[0]
                    specific_node_NG_price = NG_price.loc[:,selected_node_BA].copy()
                    
                    if buses.index(bus) == 0:
                        NG_prices_all = specific_node_NG_price.copy()
                    else:
                        NG_prices_all = pd.concat([NG_prices_all,specific_node_NG_price], axis=1)
                
                Fuel_buses = []
                for i in range(0,len(buses)):
                    Fuel_buses.append('bus_' + str(buses[i]))
                
                NG_prices_all.columns = Fuel_buses
                
                # Coal prices
                Coal_price = pd.read_csv('Coal_price/coal_prices_state.csv', header=0)
        
                for bus in buses:
                    
                    selected_node_state = df_full.loc[df_full['Number']==bus,'STATE'].values[0]
                    specific_node_coal_price = Coal_price.loc[:,selected_node_state].copy()
                    
                    if buses.index(bus) == 0:
                        Coal_prices_all = specific_node_coal_price.copy()
                    else:
                        Coal_prices_all = pd.concat([Coal_prices_all,specific_node_coal_price], axis=1)
                
                Coal_prices_all.columns = Fuel_buses
                
                # getting generator based fuel prices
                
                thermal_gens_info = df_genparams.loc[(df_genparams['typ']=='ngcc') | (df_genparams['typ']=='coal')].copy()
                thermal_gens_names = [*thermal_gens_info['name']]
                
                for ind, row in thermal_gens_info.iterrows():
                    
                    if row['typ'] == 'ngcc':
                        gen_fuel_price = NG_prices_all.loc[:, row['node']].copy() 
                    elif row['typ'] == 'coal':
                        gen_fuel_price = Coal_prices_all.loc[:, row['node']].copy() 
                    else:
                        pass
                    
                    if thermal_gens_names.index(row['name']) == 0:
                        Fuel_prices_all = gen_fuel_price.copy()
                    else:
                        Fuel_prices_all = pd.concat([Fuel_prices_all,gen_fuel_price], axis=1)
                        
                Fuel_prices_all.columns = thermal_gens_names
                
                Fuel_prices_all.to_csv('Fuel_prices.csv',index=None)
                copy('Fuel_prices.csv',path)       
    
                #copy other files
                w = 'wrapper' + UC + '.py'
                milp = 'WECC_MILP' + UC + '.py'
                lp = 'WECC_LP' + UC + '.py'
                
                copy(w,path)
                copy('WECCDataSetup.py',path)
                
                if UC == '_simple':
                    copy('WECC' + UC + '.py',path)
                else:          
                    copy(milp,path)
                    copy(lp,path)
                
            

    
