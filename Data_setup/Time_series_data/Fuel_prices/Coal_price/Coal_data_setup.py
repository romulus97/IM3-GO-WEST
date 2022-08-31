# -*- coding: utf-8 -*-
"""
Created on Mon Jul  5 14:40:23 2021

@author: kakdemi
"""

import pandas as pd

#Defining years and BAs
years = [2019,2020,2021]
BAs = pd.read_csv('../../BA_data/BAs.csv',header=0)
BA_abss = [*BAs['Abbreviation']]
BA_names = [*BAs['Name']]

for year in years:
    
    #Reading monthly BA coal data
    BA_coal_df = pd.read_excel('../EIA923_monthly_data/EIA_organized_data/{}_Fuel_Price_Data.xlsx'.format(year),sheet_name='BA_coal')
    WECC_BAs_coal = BA_coal_df.loc[:,BA_abss]
    
    #Creating a dictionary to store data
    daily_BA_coal_price = {}
    
    for my_BA in BA_abss:
        globals()[my_BA+'_daily'] = []
        globals()[my_BA+'_daily'] += 31 * [WECC_BAs_coal.loc[0,my_BA]]
        globals()[my_BA+'_daily'] += 28 * [WECC_BAs_coal.loc[1,my_BA]]
        globals()[my_BA+'_daily'] += 31 * [WECC_BAs_coal.loc[2,my_BA]]
        globals()[my_BA+'_daily'] += 30 * [WECC_BAs_coal.loc[3,my_BA]]
        globals()[my_BA+'_daily'] += 31 * [WECC_BAs_coal.loc[4,my_BA]]
        globals()[my_BA+'_daily'] += 30 * [WECC_BAs_coal.loc[5,my_BA]]
        globals()[my_BA+'_daily'] += 31 * [WECC_BAs_coal.loc[6,my_BA]]
        globals()[my_BA+'_daily'] += 31 * [WECC_BAs_coal.loc[7,my_BA]]
        globals()[my_BA+'_daily'] += 30 * [WECC_BAs_coal.loc[8,my_BA]]
        globals()[my_BA+'_daily'] += 31 * [WECC_BAs_coal.loc[9,my_BA]]
        globals()[my_BA+'_daily'] += 30 * [WECC_BAs_coal.loc[10,my_BA]]
        globals()[my_BA+'_daily'] += 31 * [WECC_BAs_coal.loc[11,my_BA]]

        daily_BA_coal_price[my_BA] = globals()[my_BA+'_daily']
    
    #saving coal prices as CSV file
    coal_price_final_daily = pd.DataFrame(data=daily_BA_coal_price)
    coal_price_final_daily.to_csv('Coal_organized_prices/BA_coal_prices_{}.csv'.format(year),index=False)



