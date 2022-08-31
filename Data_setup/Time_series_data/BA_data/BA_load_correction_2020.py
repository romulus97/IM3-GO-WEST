# -*- coding: utf-8 -*-
"""
Created on Wed Aug 18 12:16:00 2021

@author: kakdemi
"""

import pandas as pd
from datetime import timedelta

#importing BA load data
load_data = pd.read_csv('BA_raw_data/BA_load_2020_init.csv',header=0)
del load_data['Unnamed: 0']
load_data = load_data.fillna(0)

#reindexing BA load data and getting the BA names
hours_2020 = pd.date_range(start='1-1-2020 00:00:00',end='12-31-2020 23:00:00', freq='H')
feb_29_hours = pd.date_range(start='2-29-2020 00:00:00',end='2-29-2020 23:00:00', freq='H')
load_data.index = hours_2020
BAs = list(load_data.columns)

#searching for a valid demand value by looking at 1 day before and after if demand is 0 or negative. If not available, the algorithm continues to look for a valid value up to 90 days before or after
for BA in BAs:
    
    for time in hours_2020:
        
        load_val = load_data.loc[time,BA]
        
        if load_val <= 0:
            
            new_val = 0
            
            for i in range(1,91):

                try:
                    day_before = time - timedelta(days=i)
                    new_val = load_data.loc[day_before,BA]
                    if new_val > 0:
                        break
                    
                except KeyError:
                    try: 
                        day_after = time + timedelta(days=i)
                        new_val = load_data.loc[day_after,BA]
                        if new_val > 0:
                            break
                    except KeyError:
                        pass
                        
            load_data.loc[time,BA] = new_val
            

#checking whether there are still zero demand values or invalid values
if 0 in load_data.values or load_data.isna().sum().sum() != 0:
    print('There are still missing values.')
else:
    print('Load data is fixed successfully. There are no 0 or negative values.')

#selecting which BAs to include    
load_BAs = ['BANC','BPAT','PGE','PNM','PSCO','WACM','WAUW']
#filtering out anomalies (really high and low values) from the data, replacing them with values from a different day but at the same hour
for BA in load_BAs:
    
    for time in hours_2020:
        
        load_val = load_data.loc[time,BA]
        
        time_before = time - timedelta(days=7)
        time_after = time - timedelta(days=7)
        max_load_before = load_data.loc[time_before:time - timedelta(hours=1),BA].max()
        max_load_after = load_data.loc[time + timedelta(hours=1):time_after,BA].max()
        
        min_load_before = load_data.loc[time_before:time - timedelta(hours=1),BA].min()
        min_load_after = load_data.loc[time + timedelta(hours=1):time_after,BA].min()
        
        if load_val > 1.2*max_load_before or load_val > 1.2*max_load_after:
            
            new_val = 0
            
            for i in range(1,8):

                try:
                    day_before = time - timedelta(days=i)
                    new_val = load_data.loc[day_before,BA]
                    if new_val <= max_load_before or new_val <= max_load_after:
                        break
                    
                except KeyError:
                    try: 
                        day_after = time + timedelta(days=i)
                        new_val = load_data.loc[day_after,BA]
                        if new_val <= max_load_before or new_val <= max_load_after:
                            break
                    except KeyError:
                        pass
                        
            load_data.loc[time,BA] = new_val
            
        elif load_val < 0.8*min_load_before or load_val < 0.8*min_load_after:
            
            new_val = 0
            
            for i in range(1,8):

                try:
                    day_before = time - timedelta(days=i)
                    new_val = load_data.loc[day_before,BA]
                    if new_val >= min_load_before or new_val >= min_load_after:
                        break
                    
                except KeyError:
                    try: 
                        day_after = time + timedelta(days=i)
                        new_val = load_data.loc[day_after,BA]
                        if new_val >= min_load_before or new_val >= min_load_after:
                            break
                    except KeyError:
                        pass
                        
            load_data.loc[time,BA] = new_val
            
        else:
            pass
        

#exporting corrected data
load_data.drop(feb_29_hours,inplace=True)
load_data.reset_index(drop=True,inplace=True)
load_data.to_csv('BA_organized_data/BA_load_2020.csv')

# #Checking load profiles
# import matplotlib.pyplot as plt
# for BA in BAs:
#     plt.plot(load_data[BA])
#     plt.title(BA)
#     plt.show()
#     plt.clf()









