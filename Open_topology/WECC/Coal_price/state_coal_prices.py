# -*- coding: utf-8 -*-
"""
Created on Mon Jul  5 14:40:23 2021

@author: kakdemi
"""

import pandas as pd

#reading data
coal_data = pd.read_excel('EIA923_Schedules_2_3_4_5_M_12_2019_Final_Revision.xlsx',\
                          sheet_name='Page 5 Fuel Receipts and Costs',header=4,\
                          usecols=['Plant State','FUEL_GROUP','FUEL_COST','MONTH'])
#dropping invalid data
coal_data.dropna(inplace=True)
coal_data = coal_data.loc[coal_data['FUEL_COST']!='.']

#defining states and creating empty dict to store coal prices
states = ['AZ','CA','CO','ID','MT','NM','NV','OR','TX','WA']

#creating empty lists and dictionaries to store data
for state in states:
    globals()[state] = []

state_coal_price = {}
daily_state_coal_price = {}

#calculating average monthly coal price for each state and saving those
for state in states:
    
    selected_data = coal_data.loc[(coal_data['Plant State']==state) & (coal_data['FUEL_GROUP']=='Coal')]
    
    for month in range(1,13):
        selected_month = selected_data.loc[selected_data['MONTH']==month]
        coal_price = selected_month['FUEL_COST'].mean()/100
        globals()[state].append(coal_price)
    
    state_coal_price[state] = globals()[state]

#filling missing states' data, and finding daily values of coal price
coal_price_final = pd.DataFrame(data=state_coal_price)
coal_price_final['WA'] = coal_price_final['OR'].copy()
coal_price_final['ID'] = coal_price_final['MT'].copy()
coal_price_final['CA'] = coal_price_final['AZ'].copy()

for state in states:
    globals()[state+'_daily'] = []
    globals()[state+'_daily'] += 31 * [coal_price_final.loc[0,state]]
    globals()[state+'_daily'] += 28 * [coal_price_final.loc[1,state]]
    globals()[state+'_daily'] += 31 * [coal_price_final.loc[2,state]]
    globals()[state+'_daily'] += 30 * [coal_price_final.loc[3,state]]
    globals()[state+'_daily'] += 31 * [coal_price_final.loc[4,state]]
    globals()[state+'_daily'] += 30 * [coal_price_final.loc[5,state]]
    globals()[state+'_daily'] += 31 * [coal_price_final.loc[6,state]]
    globals()[state+'_daily'] += 31 * [coal_price_final.loc[7,state]]
    globals()[state+'_daily'] += 30 * [coal_price_final.loc[8,state]]
    globals()[state+'_daily'] += 31 * [coal_price_final.loc[9,state]]
    globals()[state+'_daily'] += 30 * [coal_price_final.loc[10,state]]
    globals()[state+'_daily'] += 31 * [coal_price_final.loc[11,state]]

    daily_state_coal_price[state] = globals()[state+'_daily']

#saving coal prices as CSV file
coal_price_final_daily = pd.DataFrame(data=daily_state_coal_price)
coal_price_final_daily.to_csv('coal_prices_state.csv',index=False)




