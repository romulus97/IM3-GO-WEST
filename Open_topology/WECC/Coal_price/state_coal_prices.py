# -*- coding: utf-8 -*-
"""
Created on Mon Jul  5 14:40:23 2021

@author: kakdemi
"""

import pandas as pd

#reading data
coal_data = pd.read_excel('EIA923_Schedules_2_3_4_5_M_12_2019_Final_Revision.xlsx',\
                          sheet_name='Page 5 Fuel Receipts and Costs',header=4,\
                          usecols=['Plant State','FUEL_GROUP','FUEL_COST'])
#dropping invalid data
coal_data.dropna(inplace=True)
coal_data = coal_data.loc[coal_data['FUEL_COST']!='.']

#defining states and creating empty dict to store coal prices
states = ['AZ','CA','CO','ID','MT','NM','NV','OR','TX','WA']
state_coal_price = {}

#calculating average coal price for each state and saving those
for state in states:
    
    selected_data = coal_data.loc[(coal_data['Plant State']==state) & (coal_data['FUEL_GROUP']=='Coal')]
    coal_price = selected_data['FUEL_COST'].mean()/100
    state_coal_price[state] = coal_price
    
coal_price_final = pd.DataFrame(data=state_coal_price, index=[0])
coal_price_final.loc[0,'WA'] = coal_price_final.loc[0,'OR']
coal_price_final.loc[0,'ID'] = coal_price_final.loc[0,'MT']
coal_price_final.loc[0,'CA'] = coal_price_final.loc[0,'AZ']
coal_price_final.to_csv('coal_prices.csv',index=False)
