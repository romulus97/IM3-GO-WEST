# -*- coding: utf-8 -*-
"""
Created on Thu Jun 17 11:30:26 2021

@author: kakdemi
"""

import pandas as pd
import numpy as np

#reading data and dropping plants with no weekly generation values (nan)
hydro_name_id = pd.read_csv('EIA_317_WECC_hydro_plants_to_10kbus_v2.csv',header=0\
                            ,usecols=['EIA_ID','plant','state','bal_auth','bus'])
    
hydro_cap = pd.read_csv('p_mean_max_min_MW_WECC_317plants_2009water_weekly.csv',header=0\
                            ,usecols=['EIA_ID','plant','state','bal_auth','nameplate_EIA'])
    
hydro_weekly_gen = pd.read_csv('targets_WECC_ERCOT_hydro_epiweek_mean_MW.csv',header=0)
hydro_weekly_gen = hydro_weekly_gen.loc[hydro_weekly_gen['1'].notna()]

#saving plant nameplate capacities and adding to the dataset
plant_caps = []

for ind,row in hydro_name_id.iterrows():

    selected_plant = hydro_cap.loc[(hydro_cap['EIA_ID']==row['EIA_ID']) & \
                                   (hydro_cap['state']==row['state'])]
    capacity = selected_plant['nameplate_EIA'].values[0]
    plant_caps.append(capacity)

hydro_name_id['capacity'] = plant_caps

#creating lists for week numbers
week_nums = list(range(1,53))
week_nums_str = [str(a) for a in week_nums]

#determining lost plants due to lack of data and dropping them
plant_ids_not_found = list(set(hydro_name_id['EIA_ID']) - set(hydro_weekly_gen['EIA_ID']))
hydro_name_id_updated = hydro_name_id[~hydro_name_id['EIA_ID'].isin(plant_ids_not_found)]

#checking for exactly same named plants and fixing their names
plant_names_EIA = []
plant_names_gen_file = []

for ind,row in hydro_name_id_updated.iterrows():
    if row['plant'] not in plant_names_EIA:
        plant_names_EIA.append(row['plant'])
    else:
        plant_names_EIA.append(row['plant']+'_'+row['state'])

hydro_name_id_updated.loc[:,'plant'] = plant_names_EIA
        
for ind,row in hydro_weekly_gen.iterrows():
    if row['plant'] not in plant_names_gen_file:
        plant_names_gen_file.append(row['plant'])
    else:
        plant_names_gen_file.append(row['plant']+'_'+row['state'])
        
hydro_weekly_gen.loc[:,'plant'] = plant_names_gen_file
 
#saving hydro plant information
hydro_name_id_updated.to_csv('EIA_302_WECC_hydro_plants.csv', index=False)
hydro_name_id_updated.reset_index(drop=True, inplace=True)

#creating empty dataframe to store results
weekly_gen_final = pd.DataFrame(data=np.zeros((len(hydro_name_id_updated)*52, 8)), \
                          columns=['EIA_ID','plant','state','bal_auth','week', \
                                   'mean','max','min'])

#copying relevant generator data to the empty dataframe
for i in range(len(hydro_name_id_updated)):
    
    weekly_gen_final.loc[i*52:i*52+51,'EIA_ID'] = hydro_name_id_updated.loc[i,'EIA_ID']
    weekly_gen_final.loc[i*52:i*52+51,'plant'] = hydro_name_id_updated.loc[i,'plant']
    weekly_gen_final.loc[i*52:i*52+51,'state'] = hydro_name_id_updated.loc[i,'state']
    weekly_gen_final.loc[i*52:i*52+51,'bal_auth'] = hydro_name_id_updated.loc[i,'bal_auth'] 
    weekly_gen_final.loc[i*52:i*52+51,'week'] = week_nums
    weekly_gen_final.loc[i*52:i*52+51,'max'] = hydro_name_id_updated.loc[i,'capacity']
    weekly_gen_final.loc[i*52:i*52+51,'min'] = 0
    
    mean_val = hydro_weekly_gen.loc[hydro_weekly_gen['EIA_ID']==hydro_name_id_updated.loc[i,'EIA_ID']]
    weekly_gen_final.loc[i*52:i*52+51,'mean'] = mean_val[week_nums_str].values.reshape(52,1)
    
#saving hydro plant generation information
weekly_gen_final.to_csv('p_mean_max_min_MW_WECC_302plants_weekly_2019.csv',index=False)
    
