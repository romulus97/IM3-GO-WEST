# -*- coding: utf-8 -*-
"""
Created on Mon Sep  6 16:47:27 2021

@author: kakdemi
"""

import pandas as pd

#define function to remove outliers 
# def remove_outlier_IQR(df):
#     Q1=df.quantile(0.25)
#     Q3=df.quantile(0.75)
#     IQR=Q3-Q1
#     df_final=df[~((df<(Q1-1.5*IQR)) | (df>(Q3+1.5*IQR)))]
#     return df_final

#reading BA names and creating a date range for 2019
BA_name_data = pd.read_csv('BA_data/BAs.csv',header=0)
BA_abb = BA_name_data['Abbreviation']
BA_names = BA_name_data['Name']
days_2019 = pd.date_range(start='2019-01-01',end='2019-12-31',freq='D')
hours_2019 = pd.date_range(start='2019-01-01 00:00:00',end='2019-12-31 23:00:00',freq='H')

all_BA_to_BA_combinations_hist = []
all_BA_to_BA_limits = []

#organizing historical tranmission data and getting max transmission recorded for each BA to BA combination
for BA in BA_abb:
    
    #reading historical interchange and filling empty values with 0
    globals()[BA] = pd.read_excel('../Raw_Data/{}.xlsx'.format(BA), sheet_name='Published Hourly Data',header=0,parse_dates=True)
    globals()[BA].fillna(0,inplace=True)
    
    #filtering tranmission values, getting all BA to BA tranmission data by checking if we have that BA in our model
    index = [*globals()[BA].columns].index('NG: UNK')
    globals()[BA] = globals()[BA].iloc[:,index+1:]
    intersecting_BAs = list(set(globals()[BA].columns) & set(BA_abb))
    globals()[BA+'_hist_hourly'] = globals()[BA].loc[:,intersecting_BAs]
    globals()[BA+'_connected_BAs'] = list(globals()[BA+'_hist_hourly'].columns)
    globals()[BA+'_connected_BAs'].sort()
    
    for con_BA in globals()[BA+'_connected_BAs']:
        hist_comb = BA+'_'+con_BA
        all_BA_to_BA_combinations_hist.append(hist_comb)
            
        globals()['{}_{}_hist_hourly'.format(BA,con_BA)] = globals()[BA+'_hist_hourly'][con_BA]
        globals()['{}_{}_hist_hourly'.format(BA,con_BA)] = globals()['{}_{}_hist_hourly'.format(BA,con_BA)].loc[globals()['{}_{}_hist_hourly'.format(BA,con_BA)]>=0]
        # globals()['{}_{}_hist_hourly'.format(BA,con_BA)] = remove_outlier_IQR(globals()['{}_{}_hist_hourly'.format(BA,con_BA)])
        all_BA_to_BA_limits.append(globals()['{}_{}_hist_hourly'.format(BA,con_BA)].max())
            
#exporting transmission limit data
BA_to_BA_limit_df = pd.DataFrame(list(zip(all_BA_to_BA_combinations_hist, all_BA_to_BA_limits)), columns=['BA_to_BA', 'Limit_MW'])
BA_to_BA_limit_df.set_index('BA_to_BA',inplace=True)
#correcting the errors
BA_to_BA_limit_df.loc['BANC_CISO','Limit_MW'] = 3391
BA_to_BA_limit_df.loc['BANC_TIDC','Limit_MW'] = 2233
BA_to_BA_limit_df.loc['LDWP_CISO','Limit_MW'] = 4734
BA_to_BA_limit_df.loc['WAUW_NWMT','Limit_MW'] = 212
BA_to_BA_limit_df.loc['SCL_BPAT','Limit_MW'] = 995
# BA_to_BA_limit_df.loc['WACM_PSCO','Limit_MW'] = 1871
# BA_to_BA_limit_df.loc['DOPD_BPAT','Limit_MW'] = 983

BA_to_BA_limit_df.to_csv('BA_to_BA_transmission_limits.csv')
    

    
    
    
    
    
    