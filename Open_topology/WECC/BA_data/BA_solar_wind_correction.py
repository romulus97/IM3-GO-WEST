# -*- coding: utf-8 -*-
"""
Created on Mon Aug 23 22:05:54 2021

@author: kakdemi
"""

import pandas as pd
import numpy as np
from datetime import timedelta
from sklearn import linear_model

#reading the solar and wind time series
BA_solar = pd.read_csv('BA_solar.csv',header=0)
del BA_solar['Unnamed: 0']

BA_wind = pd.read_csv('BA_wind.csv',header=0)
del BA_wind['Unnamed: 0']

#reindexing BA renewables data and getting the BA names
hours_2019 = pd.date_range(start='1-1-2019 00:00:00',end='12-31-2019 23:00:00', freq='H')
days_2019 = pd.date_range(start='1-1-2019',end='12-31-2019', freq='D')
hours_2020 = pd.date_range(start='1-1-2020 00:00:00',end='12-31-2020 23:00:00', freq='H')
days_2020 = pd.date_range(start='1-1-2020',end='12-31-2020', freq='D')
BA_solar.index = hours_2019
BA_wind.index = hours_2019
BAs = list(BA_solar.columns)

#defining months and night hours
summer_night_hours = [20,21,22,23,0,1,2,3,4,5,6]
winter_night_hours = [18,19,20,21,22,23,0,1,2,3,4,5,6,7]
summer_months = [3,4,5,6,7,8,9]
winter_months = [1,2,10,11,12]

#if there are negative values for solar and wind, changing them with 0
BA_solar[BA_solar < 0] = 0
BA_wind[BA_wind < 0] = 0

#filling 100 days missing solar data in PACE
#reading data
PACE_data_daily = pd.read_excel('../Raw_BA_files/PACE.xlsx', sheet_name='Published Daily Data',header=0,parse_dates=True)
PACE_data_daily.set_index('Local date', inplace=True, drop=True)
PACE_data_hourly = pd.read_excel('../Raw_BA_files/PACE.xlsx', sheet_name='Published Hourly Data',header=0,parse_dates=True)
PACE_data_hourly.set_index('Local time', inplace=True, drop=True)

PACE_2019_hourly = PACE_data_hourly.loc['2019','Adjusted SUN Gen']
PACE_2019_hourly.index = hours_2019
PACE_2020_hourly = PACE_data_hourly.loc['2020','Adjusted SUN Gen']
PACE_2020_hourly.index = hours_2020

#saving days with no data at all for both years
PACE_daily_2019 = PACE_data_daily.loc['2019','NG: SUN']
PACE_daily_2019.index = days_2019
missing_days_PACE_2019 = PACE_daily_2019[PACE_daily_2019[:].isnull()].index.tolist()
PACE_daily_2019_drop = PACE_daily_2019.drop(index=missing_days_PACE_2019)
PACE_daily_2020 = PACE_data_daily.loc['2020','NG: SUN']
PACE_daily_2020.index = days_2020
missing_days_PACE_2020 = [date + timedelta(days=366) for date in missing_days_PACE_2019]
PACE_daily_2020_drop = PACE_daily_2020.drop(index=missing_days_PACE_2020)
PACE_daily_2020_drop = PACE_daily_2020_drop.drop(index=pd.to_datetime('2020-02-29'))

#building a linear regression to predict daily solar generation for missing days in 2019
daily_reg = linear_model.LinearRegression().fit(PACE_daily_2020_drop.values.reshape(-1, 1), PACE_daily_2019_drop.values.reshape(-1, 1))
predicted_daily_2019 = daily_reg.predict(PACE_daily_2020.loc[missing_days_PACE_2020].values.reshape(-1, 1))

#building hourly profiles for missing days by using 2020 data
missing_day_profiles = []

for date in missing_days_PACE_2020:
    
    selected_day = '{}-{}-{}'.format(date.year, date.month, date.day)
    selected_day_data = list(PACE_2020_hourly.loc[selected_day])
    day_profile = [val/sum(selected_day_data) for val in selected_day_data]
    missing_day_profiles.append(day_profile)
    
missing_day_profiles = np.array(missing_day_profiles, dtype=object) 
   
#multiplying daily 2019 values with hourly profiles and filling hour missing data in 2019 
for date in missing_days_PACE_2019:
    
    ind = missing_days_PACE_2019.index(date)
    selected_day = '{}-{}-{}'.format(date.year, date.month, date.day)
    hourly_gen = predicted_daily_2019[ind]*missing_day_profiles[ind]
    selected_day_hourly_ind = PACE_2019_hourly[selected_day].index
    PACE_2019_hourly = PACE_2019_hourly.drop(index=selected_day_hourly_ind)
    hourly_generated_data = pd.Series(data=hourly_gen, index=selected_day_hourly_ind)
    PACE_2019_hourly = PACE_2019_hourly.append(hourly_generated_data)

#sorting the data and changing the whole solar time series for PACE
PACE_2019_hourly.sort_index(inplace=True)  
BA_solar['PACE'] = PACE_2019_hourly


#checking if there are missing data in solar and filling those 
missing_value_count_solar = BA_solar.isna().sum().sum()

if missing_value_count_solar > 0:
    print('Solar time series includes {} missing values, trying to fill those...'.format(missing_value_count_solar))
    
    for BA in BAs:
        
        BA_sp_solar = BA_solar.loc[:,BA].copy()
        missing_value_number = BA_sp_solar.isnull().sum()
        
        if missing_value_number == 8760:
            BA_solar[BA] = np.repeat(0,8760)
            continue
        
        else:
            missing_times = BA_sp_solar[BA_sp_solar[:].isnull()].index.tolist()
        
            for time in hours_2019:
            
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
solar_BAs = ['AZPS','BANC','PACE','PACW']

#filtering out anomalies (really high values) from solar data, replacing them with values from a different day but at the same hour
for BA in solar_BAs:
    
    for time in hours_2019:
        
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
        
        if missing_value_number == 8760:
            BA_wind[BA] = np.repeat(0,8760)
            continue
        
        else:
            missing_times = BA_sp_wind[BA_sp_wind[:].isnull()].index.tolist()
    
            for time in hours_2019:
            
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
wind_BAs = ['CHPD','PACE','PACW','WACM']

#filtering out anomalies (really high values) from wind data by using percentiles
for BA in wind_BAs:
    
    if BA == 'CHPD' or BA == 'WACM':
    
        exteme_value_limit = np.percentile(BA_wind.loc[:,BA], 99.9)
    
    elif BA == 'PACE' or BA == 'PACW':
    
        exteme_value_limit = np.percentile(BA_wind.loc[:,BA], 99.95)
    
    for time in hours_2019:
        
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
BA_wind.to_csv('BA_wind_corrected.csv')

BA_solar.reset_index(drop=True,inplace=True)
BA_solar.to_csv('BA_solar_corrected.csv')           
        



