# -*- coding: utf-8 -*-
"""
Created on Tue Aug 30 14:22:31 2022

@author: kakdemi
"""

import pandas as pd

#Defining years
years = [2019,2020,2021]

#Reading and defining BAs
BAs = pd.read_csv('../../BA_data/BAs.csv',header=0)
BA_abss = [*BAs['Abbreviation']]
BA_names = [*BAs['Name']]
time_range = pd.date_range(start='1/1/2019', end='12/31/2019', freq='D')

#Bias correcting by looking at monthly average reported 
for year in years:
    
    #Reading estimated NG prices 
    NG_estimated = pd.read_csv('Estimated_NG_prices/Average_NG_prices_BAs_{}.csv'.format(year))
    del NG_estimated['Unnamed: 0']
    NG_estimated.index = time_range
    
    #Reading monthly BA NG data
    BA_NG_df = pd.read_excel('../EIA923_monthly_data/EIA_organized_data/{}_Fuel_Price_Data.xlsx'.format(year),sheet_name='BA_NG')
    EIA_BAs_NG = BA_NG_df.loc[:,BA_abss]
    
    #Defining BAs to exclude and BAs to include for bias correction
    excluded_BAs = ['AZPS', 'CISO', 'IPCO', 'NEVP', 'PACE', 'PACW', 'PGE', 'PSEI']
    included_BAs = list(set(BA_abss) - set(excluded_BAs))
    
    #Bias correction by comparing monthly average and adjusting accordingly
    for my_BA in included_BAs:
        
        my_BA_name = BAs.loc[BAs['Abbreviation']==my_BA]['Name'].values[0]
        
        for month in range(1,13):
                  
            monthly_data = NG_estimated.loc['2019-{}'.format(month),my_BA_name].copy()
            monthly_data_mean = monthly_data.mean()
            monthly_data_index = monthly_data.index
            
            EIA_data_monthly = EIA_BAs_NG.loc[month-1,my_BA]
            
            #Filtering cases where we have very high EIA dataset (probably errors in EIA dataset)
            if EIA_data_monthly >= 30:
                pass 
            
            else:
                monthly_difference = EIA_data_monthly - monthly_data_mean
                
                for date in monthly_data_index:
                    
                    altered_value = NG_estimated.loc[date,my_BA_name] + monthly_difference
                    
                    if altered_value <= 0:
                        pass
                    
                    else:
                        NG_estimated.loc[date,my_BA_name] = altered_value
                        
    #Saving the bias corrected data
    NG_estimated.to_csv('Bias_corrected_NG_prices/Average_NG_prices_BAs_{}.csv'.format(year),index=False)

        
        
        
        


