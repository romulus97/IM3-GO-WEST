# -*- coding: utf-8 -*-
"""
Created on Wed Aug 18 12:16:00 2021

@author: kakdemi
"""

import pandas as pd
from datetime import timedelta

#importing BA load data
load_data = pd.read_csv('BA_load.csv',header=0)
del load_data['Unnamed: 0']

#reindexing BA load data getting the BA names
hours_2019 = pd.date_range(start='1-1-2019 00:00:00',end='12-31-2019 23:00:00', freq='H')
load_data.index = hours_2019
BAs = list(load_data.columns)

#searching for a valid demand value by looking at 1 day before and after. If not available, the algorithm continues to look for a valid value up to 30 days before or after
for BA in BAs:
    
    for time in hours_2019:
        
        load_val = load_data.loc[time,BA]
        
        if load_val <= 0:
            
            day_count = 0
            new_val = 0
            
            for i in range(1,31):

                day_count += i
                try:
                    day_before = time - timedelta(days=day_count)
                    new_val = load_data.loc[day_before,BA]
                    if new_val > 0:
                        break
                    
                except KeyError:
                    try: 
                        day_after = time + timedelta(days=day_count)
                        new_val = load_data.loc[day_after,BA]
                        if new_val > 0:
                            break
                    except KeyError:
                        pass
                        
            load_data.loc[time,BA] = new_val
            
load_data.reset_index(drop=True,inplace=True)

#checking whether there are still zero demand values or nor
if 0 in load_data.values:
    print('There are still invalid values.')
else:
    print('Data is filled successfully.')

#exporting corrected data
load_data.to_csv('BA_load_corrected.csv')



            
            
            
         

