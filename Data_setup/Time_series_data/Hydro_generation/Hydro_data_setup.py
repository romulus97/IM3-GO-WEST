# -*- coding: utf-8 -*-
"""
Created on Fri Aug 26 15:22:28 2022

@author: kakdemi
"""

import pandas as pd 
import numpy as np 

#Reading WECC hydropower plants data
WECC_plants = pd.read_csv('EIA_302_WECC_hydro_plants.csv',header=0)

#Reading raw hydropower data
Hydro_2019 = pd.read_csv('Hydropower_raw_data/hydro923plus_WEEKLY_2019.csv',header=0)
Hydro_2020 = pd.read_csv('Hydropower_raw_data/hydro923plus_WEEKLY_2020.csv',header=0)
Hydro_2021 = pd.read_csv('Hydropower_raw_data/hydro923plus_WEEKLY_2021.csv',header=0)

#Omitting 53rd weeks
Hydro_2019_filter = Hydro_2019.loc[Hydro_2019['epiweek']!=53].copy()
Hydro_2020_filter = Hydro_2020.loc[Hydro_2020['epiweek']!=53].copy()
Hydro_2021_filter = Hydro_2021.loc[Hydro_2021['epiweek']!=53].copy()

#Organizing the data for every year
years = [2019,2020,2021]

for year in years:
    
    All_EIA_IDs = []
    All_Plants = []
    All_States = []
    All_BAs = []
    All_Weeks = []
    All_Means = []
    All_Maxs = []
    All_Mins = []
    
    for my_ID in [*WECC_plants['EIA_ID']]:
        
        All_EIA_IDs.extend([my_ID]*52)
        
        my_plant = WECC_plants.loc[WECC_plants['EIA_ID']==my_ID]['plant'].values[0]
        All_Plants.extend([my_plant]*52)
        
        my_state = WECC_plants.loc[WECC_plants['EIA_ID']==my_ID]['state'].values[0]
        All_States.extend([my_state]*52)
        
        my_BA = WECC_plants.loc[WECC_plants['EIA_ID']==my_ID]['bal_auth'].values[0]
        All_BAs.extend([my_BA]*52)
        
        All_Weeks.extend([*range(1,53)])
        
        my_mean = globals()['Hydro_{}_filter'.format(year)].loc[globals()['Hydro_{}_filter'.format(year)]['EIA_ID']==my_ID]['p_avg'].values
        All_Means.extend([*my_mean])
        
        my_max = WECC_plants.loc[WECC_plants['EIA_ID']==my_ID]['capacity'].values[0]
        All_Maxs.extend([my_max]*52)
        
        my_min = globals()['Hydro_{}_filter'.format(year)].loc[globals()['Hydro_{}_filter'.format(year)]['EIA_ID']==my_ID]['p_min'].values
        All_Mins.extend([*my_min])
    
    #Saving and exporting organized dataset for every year
    Hydro_data_organized = pd.DataFrame(list(zip(All_EIA_IDs,All_Plants,All_States,All_BAs,All_Weeks,All_Means,All_Maxs,All_Mins)),
                                        columns=['EIA_ID','plant','state','bal_auth','week','mean','max','min'])
    
    Hydro_data_organized.to_csv('Hydropower_organized_data/p_mean_max_min_MW_WECC_302plants_weekly_{}.csv'.format(year),index=False)
        
        
        
        






