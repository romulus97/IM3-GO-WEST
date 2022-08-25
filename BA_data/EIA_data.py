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

for a in abbr:
    
    #saving BA index and reading hourly demand, solar and wind data for 2019
    idx = abbr.index(a)
    filename = '../Raw_BA_files/' + a + '.xlsx'
    BA_dataset = pd.read_excel(filename,header=0,sheet_name='Published Hourly Data')
    
    solar = BA_dataset.loc[BA_dataset['Local time'].dt.year == 2019,'Adjusted SUN Gen'].copy()
    wind = BA_dataset.loc[BA_dataset['Local time'].dt.year == 2019,'Adjusted WND Gen'].copy()
    load = BA_dataset.loc[BA_dataset['Local time'].dt.year == 2019,'Adjusted D'].copy()
    
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
df_S.to_csv('BA_solar.csv')

df_W = pd.DataFrame(W_end, columns=abbr)
df_W[df_W < 0] = 0
df_W.to_csv('BA_wind.csv')

df_L = pd.DataFrame(L_end, columns=abbr)
df_L[df_L < 0] = 0
df_L.to_csv('BA_load.csv')




