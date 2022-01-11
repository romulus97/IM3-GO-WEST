# -*- coding: utf-8 -*-
"""
Created on Thu Nov 11 12:04:16 2021

@author: kakdemi
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import timedelta

#getting BA names and abbreviations
BA_name_data = pd.read_csv('../BA_data/BAs.csv',header=0)
BA_abb = list(BA_name_data['Abbreviation'])
BA_names = list(BA_name_data['Name'])

#defining hours of 2019 and excluded BAs
hours_2019 = pd.date_range(start='2019-01-01 00:00:00',end='2019-12-31 23:00:00',freq='H')
excluded_BAs = ['EPE', 'TEPC', 'CISO', 'BPAT']

for BA in BA_abb:
    
    #reading historical generation data
    idx = BA_abb.index(BA)
    hydro_data_all = pd.read_excel('../../Raw_Data/{}.xlsx'.format(BA), sheet_name='Published Hourly Data',header=0,parse_dates=True)
    hydro_data_all.set_index('UTC time',drop=True,inplace=True)
    hydro_data = hydro_data_all.loc[hours_2019,'Adjusted WAT Gen']
    
    #filtering negative values and writing 0 in place of those
    hydro_data[hydro_data < 0] = 0
    
    #writing 0 for all hours for the excluded BAs (they have either no data or will be defined from another dataset)
    if BA in excluded_BAs:
        
        hydro_data = np.repeat(0, 8760)
          
    else:
        
        missing_vals = hydro_data.isna().sum().sum()
        
        if missing_vals != 0:
            
            missing_hours_all = hydro_data[hydro_data.isnull()].index.tolist()
            
            for hour in missing_hours_all:
                
                hour_count = 0
                
                #trying to find a valid value within +-30 days of the missing value
                for i in range(1,30*24):

                    hour_count += i
                    
                    try:
                        hour_before = hour - timedelta(hours=hour_count)
                        new_val = hydro_data.loc[hour_before]
                        if pd.notnull(new_val) and hour_before not in missing_hours_all:
                            break
                        else:
                            new_val = np.nan
                            
                        
                    except KeyError:
                        try: 
                            hour_after = hour + timedelta(hours=hour_count)
                            new_val = hydro_data.loc[hour_after]
                            if pd.notnull(new_val) and hour_after not in missing_hours_all:
                                break
                            else:
                                new_val = np.nan
                                
                        except KeyError:
                            pass
                        
                if pd.isnull(new_val):
                    
                    years = int(len(hydro_data_all)/8760)
                    year_count = 0
                    
                    #trying to find a valid value from another years on the same day
                    for i in range(1,years):

                        year_count += i
                    
                        try:
                            year_before = hour - timedelta(years=year_count)
                            new_val = hydro_data_all.loc[year_before, 'Adjusted WAT Gen']
                            if pd.notnull(new_val):
                                break
                            
                        except KeyError:
                            try:
                                year_after = hour + timedelta(years=year_count)
                                new_val = hydro_data_all.loc[year_after, 'Adjusted WAT Gen']
                                if pd.notnull(new_val):
                                    break
                                
                            except KeyError:
                                pass
                                 
                hydro_data.loc[hour] = new_val
                
            remaining_missing = hydro_data.isna().sum().sum()
            
            #if no valid value is found even after two previous attempts, just doing a linear interpolation
            if remaining_missing != 0:
                hydro_data = hydro_data.interpolate(method ='linear', limit_direction ='both')
        
        else:
            pass
    
    #merging all data together 
    if idx < 1:
        hydro = hydro_data
    else:
        hydro = np.column_stack((hydro,hydro_data))

final_hydro_df = pd.DataFrame(hydro, columns=BA_abb)

#changing origin of CAISO hydro from another dataset
CISO_hydro = pd.read_excel('CAISO_hydro_2019.xlsx', sheet_name='Production',header=0,parse_dates=True)
CISO_hydro.set_index('Date',drop=True,inplace=True)
CISO_hydro = CISO_hydro.resample('H').mean()
final_hydro_df.loc[:,'CISO'] = CISO_hydro.loc[:,'Large Hydro'].values.astype(int)

#changing origin of BPA hydro from another dataset
BPA_hydro_1 = pd.read_excel('BPA_hydro_2019.xls', sheet_name='January-June',header=23,parse_dates=True)
BPA_hydro_1.set_index('Date/Time',drop=True,inplace=True)
BPA_hydro_1.index = pd.to_datetime(BPA_hydro_1.index)
BPA_hydro_1 = BPA_hydro_1.resample('H').mean()
BPA_hydro_2 = pd.read_excel('BPA_hydro_2019.xls', sheet_name='July-December',header=23,parse_dates=True)
BPA_hydro_2.set_index('Date/Time',drop=True,inplace=True)
BPA_hydro_2.index = pd.to_datetime(BPA_hydro_2.index)
BPA_hydro_2 = BPA_hydro_2.resample('H').mean()
BPA_hydro_all = pd.concat([BPA_hydro_1, BPA_hydro_2])
final_hydro_df.loc[:,'BPAT'] = BPA_hydro_all.loc[:,'TOTAL HYDRO GENERATION (MW; SCADA 79682)'].values.astype(int)

#filtering negative values and writing 0 in place of those
final_hydro_df[final_hydro_df < 0] = 0
final_hydro_df.index = hours_2019


BAs_extreme_low = ['BPAT','CISO','NWMT']
BAs_extreme_high = ['IID','PACE','PGE','PSCO','SRP','WACM']
   
#filtering out anomalies (really high values) by using percentiles
for BA in BAs_extreme_high:
        
    exteme_value_limit = np.percentile(final_hydro_df.loc[:,BA], 99)
    
    for time in hours_2019:
        
        val = final_hydro_df.loc[time,BA]
           
        if val > exteme_value_limit:
            
            day_count = 0
            new_val = 0
            
            for i in range(1,8):

                day_count += i
                try:
                    day_before = time - timedelta(days=day_count)
                    new_val = final_hydro_df.loc[day_before,BA]
                    if new_val <= exteme_value_limit:
                        break
                    
                except KeyError:
                    try: 
                        day_after = time + timedelta(days=day_count)
                        new_val = final_hydro_df.loc[day_after,BA]
                        if new_val <= exteme_value_limit:
                            break
                    except KeyError:
                        pass
                        
            final_hydro_df.loc[time,BA] = new_val
            
        else:
            pass


#filtering out anomalies (really low values) by using percentiles
for BA in BAs_extreme_low:
    
    if BA == 'NWMT':
        
        exteme_value_limit = np.percentile(final_hydro_df.loc[:,BA], 1)
        
    else:
                
        exteme_value_limit = np.percentile(final_hydro_df.loc[:,BA], 0.001)
    
    for time in hours_2019:
        
        val = final_hydro_df.loc[time,BA]
           
        if val < exteme_value_limit:
            
            day_count = 0
            new_val = 0
            
            for i in range(1,8):

                day_count += i
                try:
                    day_before = time - timedelta(days=day_count)
                    new_val = final_hydro_df.loc[day_before,BA]
                    if new_val >= exteme_value_limit:
                        break
                    
                except KeyError:
                    try: 
                        day_after = time + timedelta(days=day_count)
                        new_val = final_hydro_df.loc[day_after,BA]
                        if new_val >= exteme_value_limit:
                            break
                    except KeyError:
                        pass
                        
            final_hydro_df.loc[time,BA] = new_val
            
        else:
            pass

#exporting the data
final_hydro_df.reset_index(drop=True,inplace=True)
final_hydro_df.to_csv('BA_hydro.csv')











