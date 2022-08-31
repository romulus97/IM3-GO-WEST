# -*- coding: utf-8 -*-
"""
Created on Mon Aug 23 22:05:54 2021

@author: kakdemi
"""

import pandas as pd
import numpy as np
from datetime import timedelta
# from sklearn import linear_model

#reading the solar and wind time series
BA_solar = pd.read_csv('BA_raw_data/BA_solar_2021_init.csv',header=0)
del BA_solar['Unnamed: 0']

BA_wind = pd.read_csv('BA_raw_data/BA_wind_2021_init.csv',header=0)
del BA_wind['Unnamed: 0']

#Filling out missing data in AZPS and TEPC
BA_wind.loc[0:959,'AZPS'] = BA_wind.loc[960:1919,'AZPS'].values
BA_wind.loc[1152:1524,'TEPC'] = BA_wind.loc[779:1151,'TEPC'].values
BA_wind.loc[1525:1895,'TEPC'] = BA_wind.loc[1896:2266,'TEPC'].values
BA_solar.loc[1145:1523,'TEPC'] = BA_solar.loc[766:1144,'TEPC'].values
BA_solar.loc[1524:1901,'TEPC'] = BA_solar.loc[1902:2279,'TEPC'].values

#reindexing BA renewables data and getting the BA names
hours_2021 = pd.date_range(start='1-1-2021 00:00:00',end='12-31-2021 23:00:00', freq='H')
# days_2021 = pd.date_range(start='1-1-2021',end='12-31-2021', freq='D')
# hours_2020 = pd.date_range(start='1-1-2020 00:00:00',end='12-31-2020 23:00:00', freq='H')
# days_2020 = pd.date_range(start='1-1-2020',end='12-31-2020', freq='D')
BA_solar.index = hours_2021
BA_wind.index = hours_2021
BAs = list(BA_solar.columns)

#defining months and night hours
summer_night_hours = [20,21,22,23,0,1,2,3,4,5,6]
winter_night_hours = [18,19,20,21,22,23,0,1,2,3,4,5,6,7]
summer_months = [3,4,5,6,7,8,9]
winter_months = [1,2,10,11,12]

#if there are negative values for solar and wind, changing them with 0
BA_solar[BA_solar < 0] = 0
BA_wind[BA_wind < 0] = 0

#checking if there are missing data in solar and filling those 
missing_value_count_solar = BA_solar.isna().sum().sum()

if missing_value_count_solar > 0:
    print('Solar time series includes {} missing values, trying to fill those...'.format(missing_value_count_solar))
    
    for BA in BAs:
        
        BA_sp_solar = BA_solar.loc[:,BA].copy()
        missing_value_number = BA_sp_solar.isnull().sum()
        
        if missing_value_number > len(hours_2021)-100:
            BA_solar[BA] = np.repeat(0,len(hours_2021))
            continue
        
        else:
            missing_times = BA_sp_solar[BA_sp_solar[:].isnull()].index.tolist()
        
            for time in hours_2021:
            
                solar_val = BA_solar.loc[time,BA]
                
                #correcting nightime generation issue           
                if time.month in winter_months:
                    if time.hour in winter_night_hours:
                        BA_solar.loc[time,BA] = 0
                    else:
                        pass
                
                elif time.month in summer_months:
                    if time.hour in summer_night_hours:
                        BA_solar.loc[time,BA] = 0
                    else:
                        pass
            
                else:
                    pass
                
                #searching for a valid demand value by looking at 1 day before and after. If not available, the algorithm continues to look for a valid value up to 90 days before or after           
                if pd.isnull(solar_val):
                    
                    new_val = 0
                    
                    for i in range(1,91):
        
                        try:
                            day_before = time - timedelta(days=i)
                            new_val = BA_solar.loc[day_before,BA]
                            if pd.notnull(new_val) and day_before not in missing_times:
                                break
                            else:
                                new_val = 0
                            
                        except KeyError:
                            try: 
                                day_after = time + timedelta(days=i)
                                new_val = BA_solar.loc[day_after,BA]
                                if pd.notnull(new_val) and day_after not in missing_times:
                                    break
                                else:
                                    new_val = 0
                            except KeyError:
                                pass
                                
                    BA_solar.loc[time,BA] = new_val
    
    if BA_solar.isna().sum().sum() == 0:
        print('Solar time series is filled successfully.')
    else:
        print('Filling failed. There are still invalid values.')
    
else:
    print('Solar time series does not include missing data.')

#selecting which BAs to include
solar_BAs = ['AZPS','BANC','PACE','PACW','WACM','WALC']

#filtering out anomalies (really high values) from solar data, replacing them with values from a different day but at the same hour
for BA in solar_BAs:
    
    for time in hours_2021:
        
        solar_val = BA_solar.loc[time,BA]
        
        time_before = time - timedelta(days=10)
        time_after = time + timedelta(days=10)
        max_gen_before = BA_solar.loc[time_before:time - timedelta(hours=1),BA].max()
        max_gen_after = BA_solar.loc[time + timedelta(hours=1):time_after,BA].max()
        
        min_gen_before = BA_solar.loc[time_before:time - timedelta(hours=1),BA].min()
        min_gen_after = BA_solar.loc[time + timedelta(hours=1):time_after,BA].min()
        
        if solar_val > 1.25*max_gen_before or solar_val > 1.25*max_gen_after:
            
            new_val = 0
            
            for i in range(1,8):

                try:
                    day_before = time - timedelta(days=i)
                    new_val = BA_solar.loc[day_before,BA]
                    if new_val <= max_gen_before or new_val <= max_gen_after:
                        break
                    
                except KeyError:
                    try: 
                        day_after = time + timedelta(days=i)
                        new_val = BA_solar.loc[day_after,BA]
                        if new_val <= max_gen_before or new_val <= max_gen_after:
                            break
                    except KeyError:
                        pass
                        
            BA_solar.loc[time,BA] = new_val
               
        else:
            pass



#checking if there are any missing values in wind data
missing_value_count_wind = BA_wind.isna().sum().sum()

if missing_value_count_wind > 0:
    print('Wind time series includes {} missing values, trying to fill those...'.format(missing_value_count_wind))
    
    for BA in BAs:
        
        BA_sp_wind = BA_wind.loc[:,BA].copy()
        missing_value_number = BA_sp_wind.isnull().sum()
        
        if missing_value_number > len(hours_2021)-100:
            BA_wind[BA] = np.repeat(0,len(hours_2021))
            continue
        
        else:
            missing_times = BA_sp_wind[BA_sp_wind[:].isnull()].index.tolist()
    
            for time in hours_2021:
            
                wind_val = BA_wind.loc[time,BA]
                
                
                
                #searching for a valid demand value by looking at 1 day before and after. If not available, the algorithm continues to look for a valid value up to 90 days before or after           
                if pd.isnull(wind_val):
                    
                    new_val = 0
                    
                    for i in range(1,91):
        
                        try:
                            day_before = time - timedelta(days=i)
                            new_val = BA_wind.loc[day_before,BA]
                            if pd.notnull(new_val) and day_before not in missing_times:
                                break
                            else:
                                new_val = 0
                            
                        except KeyError:
                            try: 
                                day_after = time + timedelta(days=i)
                                new_val = BA_wind.loc[day_after,BA]
                                if pd.notnull(new_val) and day_after not in missing_times:
                                    break
                                else:
                                    new_val = 0
                            except KeyError:
                                pass
                                
                    BA_wind.loc[time,BA] = new_val
    
    if BA_wind.isna().sum().sum() == 0:
        print('Wind time series is filled successfully.')
    else:
        print('Filling failed. There are still invalid values.')
    
else:
    print('Wind time series does not include missing data.')


#selecting which BAs to include
wind_BAs = ['PACW','WACM']

#filtering out anomalies (really high values) from wind data by using percentiles
for BA in wind_BAs:
    
    if BA == 'WACM':
    
        exteme_value_limit = np.percentile(BA_wind.loc[:,BA], 99.9)
    
    elif BA == 'PACW':
    
        exteme_value_limit = np.percentile(BA_wind.loc[:,BA], 99.95)
    
    for time in hours_2021:
        
        wind_val = BA_wind.loc[time,BA]
           
        if wind_val > exteme_value_limit:
            
            new_val = 0
            
            for i in range(1,6):

                try:
                    day_before = time - timedelta(days=i)
                    new_val = BA_wind.loc[day_before,BA]
                    if new_val <= exteme_value_limit:
                        break
                    
                except KeyError:
                    try: 
                        day_after = time + timedelta(days=i)
                        new_val = BA_wind.loc[day_after,BA]
                        if new_val <= exteme_value_limit:
                            break
                    except KeyError:
                        pass
                        
            BA_wind.loc[time,BA] = new_val
            
        else:
            pass


#exporting the data
BA_wind.reset_index(drop=True,inplace=True)
BA_wind.to_csv('BA_organized_data/BA_wind_2021.csv')

BA_solar.reset_index(drop=True,inplace=True)
BA_solar.to_csv('BA_organized_data/BA_solar_2021.csv')           

  
# #Checking solar and wind profiles
# import matplotlib.pyplot as plt
# for BA in BAs:
#     plt.plot(BA_wind[BA])
#     plt.title(BA+'_wind')
#     plt.show()
#     plt.clf()
    
#     plt.plot(BA_solar[BA])
#     plt.title(BA+'_solar')
#     plt.show()
#     plt.clf()


