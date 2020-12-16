# -*- coding: utf-8 -*-
"""
Created on Thu Nov 12 18:42:39 2020

@author: jkern
"""

import pandas as pd
import numpy as np

# eGRID plant data
df_plants = pd.read_excel('egrid2016_data.xlsx',sheet_name = 'PLNT16',header = 0)
df_gens = pd.read_excel('egrid2016_data.xlsx',sheet_name = 'GEN16',header = 0)

# screen for operational plants/units
df_op_gens = df_gens.loc[df_gens['Generator status'] == 'OP']

# extract plants in WECC
WECC_plants = df_plants.loc[df_plants['NERC region acronym'] == 'WECC']

states = ['AZ','CA','CO','ID','MT','NM','NV','OR','UT','WA','WY']

for s in states:
    
    filename = 'egrid_2016_gens_' + s + '.csv'
    
    state_plants = WECC_plants.loc[WECC_plants['Plant state abbreviation'] == s]
    plant_codes = list(state_plants['DOE/EIA ORIS plant or facility code'])
    state_gens = df_op_gens.loc[df_op_gens['Plant state abbreviation'] == s]
    state_gens = state_gens.reset_index(drop=True)
    gen_codes = list(state_gens['DOE/EIA ORIS plant or facility code'])
         
    for i in range(0,len(state_gens)):
        
        g = gen_codes[i]
        
        if g in plant_codes:
            
            df_select = state_gens.loc[i,:]       
            
            if i < 1:
            
                df_total = state_gens.copy(deep=True)
            
            else:
            
                df_total.append(df_select)
    
    df_total = df_total.reset_index(drop=True)         
    gen_fuels = list(df_total['Generator primary fuel'].unique())
    gen_movers = list(df_total['Generator prime mover type'].unique())
    plant_types = ['NGCC','NGCT','Coal','Oil','Wind','SolarPV','SolarCSP','Hydro','Nuclear','Other']
    plant_caps = np.zeros((len(df_total),len(plant_types)))
    areas = []
    utilities = []
    lats = []
    lons = []
    
    for i in range(0,len(df_total)):
        
        code = df_total.loc[i,'DOE/EIA ORIS plant or facility code']
        area = state_plants.loc[state_plants['DOE/EIA ORIS plant or facility code'] == code,'Balancing Authority Code']
        area = area.reset_index(drop=True)
        if len(area) >= 1:
            area = area[0]
            
        utility = state_plants.loc[state_plants['DOE/EIA ORIS plant or facility code'] == code,'Plant operator name']
        utility = utility.reset_index(drop=True)
        
        lat = state_plants.loc[state_plants['DOE/EIA ORIS plant or facility code'] == code,'Plant latitude']
        lat = lat.reset_index(drop=True)
        
        lon = state_plants.loc[state_plants['DOE/EIA ORIS plant or facility code'] == code,'Plant longitude']
        lon = lon.reset_index(drop=True)
        
        
        if len(utility) >= 1:
            utility = utility[0]
            lat = lat[0]
            lon = lon[0]
        elif len(utility) < 1:
            utility = 'blank'
            lat = 'blank'
            lon = 'blank'
            
        utilities.append(utility)
        lats.append(lat)
        lons.append(lon)
        
        if utility == 'Sierra Pacific Power Co':       
            areas.append('SPPC')
        else:
            areas.append(area)
        

        

        if df_total.loc[i,'Generator primary fuel'] == 'NG':
            if df_total.loc[i,'Generator prime mover type'] == 'ST' or df_total.loc[i,'Generator prime mover type'] == 'CA' or df_total.loc[i,'Generator prime mover type'] == 'CT':
                plant_caps[i,0] = df_total.loc[i,'Generator nameplate capacity (MW)']
            else:
                plant_caps[i,1] = df_total.loc[i,'Generator nameplate capacity (MW)']
        elif df_total.loc[i,'Generator primary fuel'] == 'SUB':
            plant_caps[i,2] = df_total.loc[i,'Generator nameplate capacity (MW)']
        elif df_total.loc[i,'Generator primary fuel'] == 'DFO':
            plant_caps[i,3] = df_total.loc[i,'Generator nameplate capacity (MW)']
        elif df_total.loc[i,'Generator primary fuel'] == 'WND':
            plant_caps[i,4] = df_total.loc[i,'Generator nameplate capacity (MW)']
        elif df_total.loc[i,'Generator primary fuel'] == 'SUN':
            if df_total.loc[i,'Generator prime mover type'] == 'ST':
                plant_caps[i,6] = df_total.loc[i,'Generator nameplate capacity (MW)']
            else:
                plant_caps[i,5] = df_total.loc[i,'Generator nameplate capacity (MW)']
        elif df_total.loc[i,'Generator primary fuel'] == 'WAT':
            plant_caps[i,7] = df_total.loc[i,'Generator nameplate capacity (MW)']
        elif df_total.loc[i,'Generator primary fuel'] == 'NUC':
            plant_caps[i,8] = df_total.loc[i,'Generator nameplate capacity (MW)']
        else:
            plant_caps[i,9] = df_total.loc[i,'Generator nameplate capacity (MW)']
    
    df_total['area'] = areas
    df_total['utility'] = utilities
    df_total['latitude'] = lats
    df_total['longitude'] = lons
    
    if s == 'AZ':
        df_total['state'] = 'Arizona'
    elif s == 'CA':
        df_total['state'] = 'California'
    elif s == 'CO':
        df_total['state'] = 'Colorado'
    elif s == 'ID':
        df_total['state'] = 'Idaho'
    elif s == 'MT':
        df_total['state'] = 'Montana'
    elif s == 'NM':
        df_total['state'] = 'New Mexico'
    elif s == 'NV':
        df_total['state'] = 'Nevada'
    elif s == 'OR':
        df_total['state'] = 'Oregon'
    elif s == 'UT':
        df_total['state'] = 'Utah'
    elif s == 'WA':
        df_total['state'] = 'Washington'
    elif s == 'WY':
        df_total['state'] = 'Wyoming'
    
    for i in plant_types:
        idx = plant_types.index(i)
        df_total[i] = plant_caps[:,idx]

    df_total.to_csv(filename)
        
        