# -*- coding: utf-8 -*-
"""
Created on Thu Nov 11 12:04:16 2021

@author: kakdemi
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib as mpl
import re
from datetime import timedelta

#getting BA names and abbreviations
BA_name_data = pd.read_csv('../BA_data/BAs.csv',header=0)
BA_abb = list(BA_name_data['Abbreviation'])
BA_names = list(BA_name_data['Name'])

#defining hours of 2019
hours_2019 = pd.date_range(start='2019-01-01 00:00:00',end='2019-12-31 23:00:00',freq='H')

for BA in BA_abb:
    
    #reading historical generation data
    idx = BA_abb.index(BA)
    
    hydro_data_all = pd.read_excel('../../Raw_Data/{}.xlsx'.format(BA), sheet_name='Published Hourly Data',header=0,parse_dates=True)

    hydro_data_all.set_index('UTC time',drop=True,inplace=True)
    hydro_data = hydro_data_all.loc[hours_2019,'Adjusted WAT Gen']
    hydro_data[hydro_data < 0] = 0
    
    if BA=='EPE' or BA=='TEPC' or 'CISO' or 'BPAT':
        
        hydro_data = np.repeat(0, 8760)
      
    else:
        
        missing_vals = hydro_data.isna().sum().sum()
        
        if missing_vals != 0:
            
            missing_hours_all = hydro_data[hydro_data.isnull()].index.tolist()
            
            for hour in missing_hours_all:
                
                hour_count = 0
                
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
            
            if remaining_missing != 0:
                hydro_data = hydro_data.interpolate(method ='linear', limit_direction ='both')
        
        else:
            pass
                      
    if idx < 1:
        hydro = hydro_data
    else:
        hydro = np.column_stack((hydro,hydro_data))

final_hydro_df = pd.DataFrame(hydro, columns=BA_abb)

#changing origin of CAISO hydro
CISO_hydro = pd.read_excel('CAISO_hydro_2019.xlsx', sheet_name='Production',header=0,parse_dates=True)
CISO_hydro.set_index('Date',drop=True,inplace=True)
CISO_hydro = CISO_hydro.resample('H').mean()
final_hydro_df.loc[:,'CISO'] = CISO_hydro.loc[:,'Large Hydro'].values.astype(int)

#changing origin of BPA hydro
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

final_hydro_df[final_hydro_df < 0] = 0


# final_hydro_df.isna().sum().sum()

# for BA in BA_abb:

#     df = final_hydro_df.loc[:,BA].copy()
    
#     Q1=df.quantile(0.25)
#     Q3=df.quantile(0.75)
#     IQR=Q3-Q1
#     max_val = Q3+1.5*IQR
#     min_val = Q1-1.5*IQR
    
#     df[df < min_val] = min_val
#     df[df > max_val] = max_val
#     fig, ax = plt.subplots(2,1,sharex=True)
    
#     ax[0].plot(range(len(df)), df)
#     ax[0].set_title(BA+'after')
#     ax[1].plot(range(len(df)), final_hydro_df.loc[:,BA])
#     # ax[2].title(BA)
#     plt.show()
#     plt.clf()


for BA in BA_abb:
    
    plt.plot(range(len(final_hydro_df)), final_hydro_df.loc[:,BA])
    plt.title(BA)
    plt.show()
    plt.clf()


# def remove_outlier_IQR(df):
#     Q1=df.quantile(0.25)
#     Q3=df.quantile(0.75)
#     IQR=Q3-Q1
#     df_final=df[~((df<(Q1-1.5*IQR)) | (df>(Q3+1.5*IQR)))]
#     return df_final

















