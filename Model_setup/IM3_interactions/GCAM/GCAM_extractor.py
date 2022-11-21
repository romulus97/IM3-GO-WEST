# -*- coding: utf-8 -*-
"""
Created on Sun Nov  6 11:58:38 2022

@author: kakdemi
"""

import pandas as pd
import numpy as np
import os
from shutil import copy
from pathlib import Path
import sys

def GCAM_extract(NN,UC,T_p,BA_hurd,YY,Hydro_year,GCAM_year,CS):
    
    #Correcting the directory
    cwd = os.getcwd()
    os.chdir("{}\\GCAM".format(cwd[:-4]))
    
    #Read GCAM outputs
    GCAM_outputs_df = pd.read_csv('GCAM_outputs/dataGCAM_go.csv',header=0)
    
    #Reading generator params file
    datagenparams_df = pd.read_csv('../Altered_simulation_folders/Exp{}{}_{}_{}_{}_{}/Inputs/data_genparams.csv'.format(NN,UC,T_p,BA_hurd,GCAM_year,CS))
    
    #Reading CERF generators file for location information
    if GCAM_year == 2015:
        CERF_generators = pd.read_csv('../CERF/CERF_outputs/power_plant_initialization_{}.csv'.format(GCAM_year),header=0)
    else:
        CERF_generators = pd.read_csv('../CERF/CERF_outputs/cerf_for_go_{}_{}.csv'.format(CS,GCAM_year),header=0)
    
    #Filtering for fuel cost and and climate scenario
    GCAM_initial_filter = GCAM_outputs_df.loc[(GCAM_outputs_df['scenario']==CS) & (GCAM_outputs_df['param']=='elec_fuel_price_2015USDperMBTU')].copy()
    GCAM_year_filter = GCAM_initial_filter.loc[(GCAM_initial_filter['vintage']=='Vint_{}'.format(GCAM_year)) & (GCAM_initial_filter['x']==GCAM_year)].copy()
    
    #Filtering for thermal generators to find fuel costs
    thermal_gen_list = ['coal', 'oil', 'ngcc', 'biomass','geothermal']
    datagenparams_filter = datagenparams_df.loc[datagenparams_df['typ'].isin(thermal_gen_list)].copy()
    datagenparams_filter.reset_index(drop=True,inplace=True)
    
    states_dict = {'alabama':'AL','alaska':'AK','arizona':'AZ','arkansas':'AR','california':'CA','colorado':'CO',\
                   'connecticut':'CT','district_of_columbia':'DC','delaware':'DE','florida':'FL','georgia':'GA',\
                   'hawaii':'HI','iowa':'IA','idaho':'ID','illinois':'IL','indiana':'IN','kansas':'KS',\
                   'kentucky':'KY','louisiana':'LA','massachusetts':'MA','maryland':'MD','maine':'ME','michigan':'MI',\
                   'minnesota':'MN','missouri':'MO','mississippi':'MS','montana':'MT','north_carolina':'NC','north_dakota':'ND',\
                   'nebraska':'NE','new_hampshire':'NH','new_jersey':'NJ','new_mexico':'NM','nevada':'NV','new_york':'NY',\
                   'ohio':'OH','oklahoma':'OK','oregon':'OR','pennsylvania':'PA','rhode_island':'RI','south_carolina':'SC',\
                   'south_dakota':'SD','tennessee':'TN','texas':'TX','utah':'UT','virginia':'VA','vermont':'VT','washington':'WA',\
                   'wisconsin':'WI','west_virginia':'WV','wyoming':'WY'}
        
    #Creating dataframe to store fuel prices
    fuel_prices_df = pd.DataFrame(np.zeros((365,len(datagenparams_filter))),columns=[*datagenparams_filter['name']])
    
    #Saving relevant fuel prices for each generator (fuel price stays the same for 365 days)
    for i in range(0,len(datagenparams_filter)):
        
        CERF_gen_name = datagenparams_filter.loc[i,'name']
        CERF_gen_type = datagenparams_filter.loc[i,'typ']
        CERF_gen_state = CERF_generators.loc[CERF_generators['plant_id']==CERF_gen_name[3:]]['region_name'].values[0]
        GCAM_gen_state = states_dict[CERF_gen_state]
        
        GCAM_state_filter = GCAM_year_filter.loc[GCAM_year_filter['subRegion']==GCAM_gen_state].copy()
        
        if CERF_gen_type == 'coal':
            GCAM_fuel_price = GCAM_state_filter.loc[GCAM_state_filter['class1']=='regional coal']['value'].values[0]
        elif CERF_gen_type == 'oil':
            GCAM_fuel_price = GCAM_state_filter.loc[GCAM_state_filter['class1']=='refined liquids industrial']['value'].values[0]
        elif CERF_gen_type == 'ngcc':
            GCAM_fuel_price = GCAM_state_filter.loc[GCAM_state_filter['class1']=='wholesale gas']['value'].values[0]
        elif CERF_gen_type == 'biomass':
            GCAM_fuel_price = GCAM_state_filter.loc[GCAM_state_filter['class1']=='regional biomass']['value'].values[0]
        elif CERF_gen_type == 'geothermal':
            GCAM_fuel_price = 0.001 #Fuel price of geothermal assumed to be negligible
        else:
            pass
        
        fuel_prices_df.loc[:,CERF_gen_name] = [GCAM_fuel_price]*365
        
    #Exporting fuel prices
    fuel_prices_df.to_csv('../Altered_simulation_folders/Exp{}{}_{}_{}_{}_{}/Inputs/Fuel_prices.csv'.format(NN,UC,T_p,BA_hurd,GCAM_year,CS),index=None)
        
    return None
    
    
    
    