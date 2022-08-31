# -*- coding: utf-8 -*-
"""
Created on Thu Feb 11 22:24:48 2021

@author: jkern
"""
import pandas as pd
import numpy as np

#read BA name data and save BA abbreviations
df_BAs = pd.read_csv('BAs.csv',header=0)
abbr = list(df_BAs['Abbreviation'])
years = [2019,2020,2021]

for year in years:

    for a in abbr:
        
        #saving BA index and reading hourly demand, solar and wind data for the year
        idx = abbr.index(a)
        
        if (a == 'PSEI') and (year == 2020):
            filename = 'EIA_datasets/EIA930_raw_timeseries/PSEI_2020.xlsx'
            
        else:
            filename = 'EIA_datasets/EIA930_raw_timeseries/' + a + '.xlsx'
        
        BA_dataset = pd.read_excel(filename,header=0,sheet_name='Published Hourly Data')
        
        solar = BA_dataset.loc[BA_dataset['Local time'].dt.year == year,'Adjusted SUN Gen'].copy()
        wind = BA_dataset.loc[BA_dataset['Local time'].dt.year == year,'Adjusted WND Gen'].copy()
        load = BA_dataset.loc[BA_dataset['Local time'].dt.year == year,'Adjusted D'].copy()
        
        #saving the time zone
        tz = BA_dataset.loc[0,'Time zone']
        
        #checking the time zone of the BA and shifting load, solar and wind timeseries accordingly 
        #(Pacific time zone is selected as standard time zone)
        
        if tz == 'Pacific':
            #copying relevant timeseries as is if time zone is Pacific
            S = np.array(solar)
            W = np.array(wind)
            L = np.array(load)
        
        elif tz == 'Mountain' or tz == 'Arizona':
            #shifting revelant timeseries for 1 hour if time zone is Mountain or Arizona
            renewable_ind = [*solar.index]
            fixed_renewable_ind = [c+1 for c in renewable_ind]
            solar = BA_dataset.loc[fixed_renewable_ind,'Adjusted SUN Gen'].copy()
            wind = BA_dataset.loc[fixed_renewable_ind,'Adjusted WND Gen'].copy()
            load = BA_dataset.loc[fixed_renewable_ind,'Adjusted D'].copy()
            S = np.array(solar)
            W = np.array(wind)
            L = np.array(load)
            
        else:
            #if timezone is any of the above, show the BA and time zone
            print([abbr,tz])
            
        #copying all BA level data side by side
        if idx < 1:
            S_end = S
            W_end = W
            L_end = L
            
        else:
            S_end = np.column_stack((S_end,S))
            W_end = np.column_stack((W_end,W))
            L_end = np.column_stack((L_end,L))
        
    #Turning timeseries into dataframe, changing negative values to 0 and saving the timeseries
    df_S = pd.DataFrame(S_end, columns=abbr)
    df_S[df_S < 0] = 0
    df_S.to_csv('BA_raw_data/BA_solar_{}_init.csv'.format(year))
    
    df_W = pd.DataFrame(W_end, columns=abbr)
    df_W[df_W < 0] = 0
    df_W.to_csv('BA_raw_data/BA_wind_{}_init.csv'.format(year))
    
    df_L = pd.DataFrame(L_end, columns=abbr)
    df_L[df_L < 0] = 0
    df_L.to_csv('BA_raw_data/BA_load_{}_init.csv'.format(year))




