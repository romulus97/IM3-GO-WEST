# -*- coding: utf-8 -*-
"""
Created on Mon Aug 22 15:05:01 2022

@author: kakdemi
"""

import pandas as pd 
import numpy as np 

#Listing years, months and fuels
years = [2019,2020,2021]
months = [*range(1,13)]
fuels = ['coal','NG','oil']

#Reading WECC BAs
BAs_df = pd.read_csv('BAs.csv',header=0)
WECC_BAs = [*BAs_df['Abbreviation']]

#Reading and finding states of WECC BAs
nodes_to_BA_state = pd.read_csv('nodes_to_BA_state.csv',header=0)
nodes_to_BA_state.dropna(subset=['State','NAME'], inplace=True)
nodes_to_BA_state.reset_index(inplace=True,drop=True)

WECC_state_abbs = {'Washington':'WA','Oregon':'OR','Idaho':'ID','California':'CA','Nevada':'NV','Arizona':'AZ','Utah':'UT',
                   'New Mexico':'NM','Wyoming':'WY','Texas':'TX','Colorado':'CO','Montana':'MT'}

#Finding which WECC BA located in which states
for i in range(0,len(nodes_to_BA_state)):
    sp_state = nodes_to_BA_state.loc[i,'State']
    sp_state_abb = WECC_state_abbs[sp_state]
    
    sp_BA = nodes_to_BA_state.loc[i,'NAME']
    sp_BA_abb = BAs_df.loc[BAs_df['Name']==sp_BA]['Abbreviation'].values[0]
    
    nodes_to_BA_state.loc[i,'State'] = sp_state_abb
    nodes_to_BA_state.loc[i,'NAME'] = sp_BA_abb    

WECC_BA_state_dic = {}

for i in WECC_BAs:
    
    filtered_df = nodes_to_BA_state.loc[nodes_to_BA_state['NAME']==i]
    uniq_states = [*filtered_df['State'].unique()]
    WECC_BA_state_dic[i] = uniq_states

for year in years:
    
    #Reading data
    EIA_923 = pd.read_excel('EIA923_{}.xlsx'.format(year),sheet_name='Page 5 Fuel Receipts and Costs',header=4)
    
    #Drop rows where we don't have BA and fuel price information
    EIA_923.dropna(subset=['Balancing\nAuthority Code','FUEL_COST','Plant State'], inplace=True)
    EIA_923 = EIA_923.loc[EIA_923['FUEL_COST'] != '.']
    EIA_923['FUEL_COST'] = pd.to_numeric(EIA_923['FUEL_COST'])
    EIA_923['FUEL_COST'] = EIA_923['FUEL_COST']/100
    
    #Finding all BAs and states
    all_BAs = [*EIA_923['Balancing\nAuthority Code'].unique()]
    all_states = [*EIA_923['Plant State'].unique()]
    
    #Finding which BA located in which states in EIA data
    EIA_exclusive_BAs = [a for a in all_BAs if a not in WECC_BAs]
    EIA_BA_state_dic = {}
    
    for i in EIA_exclusive_BAs:
        
        filtered_df = EIA_923.loc[EIA_923['Balancing\nAuthority Code']==i]
        uniq_states = [*filtered_df['Plant State'].unique()]
        EIA_BA_state_dic[i] = uniq_states
    
    #Creating empty array to store data
    BA_coal_prices = pd.DataFrame(np.zeros((12,len(all_BAs))),columns=all_BAs)
    BA_NG_prices = pd.DataFrame(np.zeros((12,len(all_BAs))),columns=all_BAs)
    BA_oil_prices = pd.DataFrame(np.zeros((12,len(all_BAs))),columns=all_BAs)
    
    State_coal_prices = pd.DataFrame(np.zeros((12,len(all_states))),columns=all_states)
    State_NG_prices = pd.DataFrame(np.zeros((12,len(all_states))),columns=all_states)
    State_oil_prices = pd.DataFrame(np.zeros((12,len(all_states))),columns=all_states)
    
    #Finding monthly average fuel price info for each state and saving it 
    for my_state in all_states:
        
        idx = all_states.index(my_state)
        State_plants = EIA_923.loc[EIA_923['Plant State']==my_state].copy()
        
        ##STATE COAL###
        State_coal_plants = State_plants.loc[State_plants['FUEL_GROUP']=='Coal'].copy()
        if len(State_coal_plants) == 0: 
            State_coal_prices.loc[:,my_state] = ['']*12
            
        else:
            coal_values = State_coal_plants.groupby('MONTH').mean()['FUEL_COST']
            
            if len(coal_values) == 12:
                State_coal_prices.loc[:,my_state] = coal_values.values
                
            else:
                
                for i in months:
                    try:  
                        State_coal_prices.loc[i-1,my_state] = coal_values[i]
            
                    except KeyError:
                        State_coal_prices.loc[i-1,my_state] = ''
                        
        ##STATE NG###            
        State_NG_plants = State_plants.loc[State_plants['FUEL_GROUP']=='Natural Gas'].copy()
        if len(State_NG_plants) == 0: 
            State_NG_prices.loc[:,my_state] = ['']*12
            
        else:
            NG_values = State_NG_plants.groupby('MONTH').mean()['FUEL_COST']
            
            if len(NG_values) == 12:
                State_NG_prices.loc[:,my_state] = NG_values.values
                
            else:
                
                for i in months:
                    try:  
                        State_NG_prices.loc[i-1,my_state] = NG_values[i]
            
                    except KeyError:
                        State_NG_prices.loc[i-1,my_state] = ''
                    
        ##STATE OIL###
        State_oil_plants = State_plants.loc[State_plants['FUEL_GROUP']=='Petroleum'].copy()
        if len(State_oil_plants) == 0: 
            State_oil_prices.loc[:,my_state] = ['']*12
            
        else:
            oil_values = State_oil_plants.groupby('MONTH').mean()['FUEL_COST']
            
            if len(oil_values) == 12:
                State_oil_prices.loc[:,my_state] = oil_values.values
                
            else:
                
                for i in months:
                    try:  
                        State_oil_prices.loc[i-1,my_state] = oil_values[i]
            
                    except KeyError:
                        State_oil_prices.loc[i-1,my_state] = ''
    
    #Filling out missing state data
    if (State_coal_prices['WA'].eq('')).sum() != 0:
        State_coal_prices['WA'] = State_coal_prices['UT'].copy()
        
    if (State_coal_prices['OR'].eq('')).sum() != 0:
        State_coal_prices['OR'] = State_coal_prices['UT'].copy()
        
    if (State_coal_prices['ID'].eq('')).sum() != 0:
        State_coal_prices['ID'] = State_coal_prices['UT'].copy()
        
    if (State_coal_prices['MT'].eq('')).sum() != 0:
        State_coal_prices['MT'] = State_coal_prices['UT'].copy()
        
    if (State_coal_prices['CA'].eq('')).sum() != 0:
        State_coal_prices['CA'] = State_coal_prices['AZ'].copy()
        
    if (State_coal_prices['MA'].eq('')).sum() != 0:
        State_coal_prices['MA'] = State_coal_prices['VA'].copy()
        
    if (State_coal_prices['NH'].eq('')).sum() != 0:
        State_coal_prices['NH'] = State_coal_prices['OH'].copy()
        
    if (State_coal_prices['NY'].eq('')).sum() != 0:
        State_coal_prices['NY'] = State_coal_prices['OH'].copy()
        
    if (State_coal_prices['MD'].eq('')).sum() != 0:
        State_coal_prices['MD'] = State_coal_prices['VA'].copy()
        
    if (State_coal_prices['NV'].eq('')).sum() != 0:
        State_coal_prices['NV'] = State_coal_prices['UT'].copy()
        
    if (State_coal_prices['MS'].eq('')).sum() != 0:
        State_coal_prices['MS'] = State_coal_prices['TN'].copy()
        
    if (State_NG_prices['NH'].eq('')).sum() != 0:
        State_NG_prices['NH'] = State_NG_prices['OH'].copy()
        
    if (State_oil_prices['AR'].eq('')).sum() != 0:
        State_oil_prices['AR'] = State_oil_prices['TN'].copy()
        
    if (State_oil_prices['OK'].eq('')).sum() != 0:
        State_oil_prices['OK'] = State_oil_prices['TX'].copy()
        
    if (State_oil_prices['CA'].eq('')).sum() != 0:
        State_oil_prices['CA'] = State_oil_prices['AZ'].copy()
        
    if (State_oil_prices['CO'].eq('')).sum() != 0:
        State_oil_prices['CO'] = State_oil_prices['AZ'].copy()
        
    if (State_oil_prices['WA'].eq('')).sum() != 0:
        State_oil_prices['WA'] = State_oil_prices['WY'].copy()
        
    if (State_oil_prices['IL'].eq('')).sum() != 0:
        State_oil_prices['IL'] = State_oil_prices['TN'].copy()
        
    if (State_oil_prices['MS'].eq('')).sum() != 0:
        State_oil_prices['MS'] = State_oil_prices['TN'].copy()
        
    if (State_oil_prices['NH'].eq('')).sum() != 0:
        State_oil_prices['NH'] = State_oil_prices['MA'].copy()
        
    if (State_oil_prices['MT'].eq('')).sum() != 0:
        State_oil_prices['MT'] = State_oil_prices['WY'].copy()
        
    if (State_oil_prices['OR'].eq('')).sum() != 0:
        State_oil_prices['OR'] = State_oil_prices['WY'].copy()
        
    if (State_oil_prices['ID'].eq('')).sum() != 0:
        State_oil_prices['ID'] = State_oil_prices['WY'].copy()
    
    if (State_oil_prices['MD'].eq('')).sum() != 0:
        State_oil_prices['MD'] = State_oil_prices['VA'].copy()
        
    if (State_oil_prices['AL'].eq('')).sum() != 0:
        State_oil_prices['AL'] = State_oil_prices['TN'].copy()
        
    if (State_oil_prices['NV'].eq('')).sum() != 0:
        State_oil_prices['NV'] = State_oil_prices['AZ'].copy()
        
    if (State_oil_prices['LA'].eq('')).sum() != 0:
        State_oil_prices['LA'] = State_oil_prices['TX'].copy()
        
    if (State_oil_prices['NE'].eq('')).sum() != 0:
        State_oil_prices['NE'] = State_oil_prices['WY'].copy()
        
    if (State_oil_prices['NE'].eq('')).sum() != 0:
        State_oil_prices['NE'] = State_oil_prices['WY'].copy()
        
    if (State_oil_prices['OK'].eq('')).sum() != 0:
        State_oil_prices['OK'] = State_oil_prices['TX'].copy()
        
    if (State_oil_prices['NM'].eq('')).sum() != 0:
        State_oil_prices['NM'] = State_oil_prices['AZ'].copy()
        
    if (State_oil_prices['UT'].eq('')).sum() != 0:
        State_oil_prices['UT'] = State_oil_prices['AZ'].copy()
        
    if (State_oil_prices['SD'].eq('')).sum() != 0:
        State_oil_prices['SD'] = State_oil_prices['WY'].copy()
    
    #Finding monthly average fuel price info for each BA and saving it 
    for BA in all_BAs:
        
        idx = all_BAs.index(BA)
        BA_plants = EIA_923.loc[EIA_923['Balancing\nAuthority Code']==BA].copy()
        
        ##BA COAL###
        BA_coal_plants = BA_plants.loc[BA_plants['FUEL_GROUP']=='Coal'].copy()
        if len(BA_coal_plants) == 0: 
            BA_coal_prices.loc[:,BA] = ['']*12
            
        else:
            coal_values = BA_coal_plants.groupby('MONTH').mean()['FUEL_COST']
            
            if len(coal_values) == 12:
                BA_coal_prices.loc[:,BA] = coal_values.values
                
            else:
                
                for i in months:
                    try:  
                        BA_coal_prices.loc[i-1,BA] = coal_values[i]
            
                    except KeyError:
                        BA_coal_prices.loc[i-1,BA] = ''
        
        ##BA NG###
        BA_NG_plants = BA_plants.loc[BA_plants['FUEL_GROUP']=='Natural Gas'].copy()
        if len(BA_NG_plants) == 0: 
            BA_NG_prices.loc[:,BA] = ['']*12
            
        else:
            NG_values = BA_NG_plants.groupby('MONTH').mean()['FUEL_COST']
            
            if len(NG_values) == 12:
                BA_NG_prices.loc[:,BA] = NG_values.values
                
            else:
                
                for i in months:
                    try:  
                        BA_NG_prices.loc[i-1,BA] = NG_values[i]
            
                    except KeyError:
                        BA_NG_prices.loc[i-1,BA] = ''
        

        ##BA OIL###
        BA_oil_plants = BA_plants.loc[BA_plants['FUEL_GROUP']=='Petroleum'].copy()
        if len(BA_oil_plants) == 0: 
            BA_oil_prices.loc[:,BA] = ['']*12
            
        else:
            oil_values = BA_oil_plants.groupby('MONTH').mean()['FUEL_COST']
            
            if len(oil_values) == 12:
                BA_oil_prices.loc[:,BA] = oil_values.values
                
            else:
                
                for i in months:
                    try:  
                        BA_oil_prices.loc[i-1,BA] = oil_values[i]
            
                    except KeyError:
                        BA_oil_prices.loc[i-1,BA] = ''
    
    #Finding absent WECC BAs
    WECC_remain_BAs = [a for a in WECC_BAs if a not in all_BAs]
    
    #Filling out missing BA data
    for fuel in fuels:
        
        for BA in all_BAs:
            
            selected_data = globals()['BA_{}_prices'.format(fuel)].loc[:,BA].copy()
            
            if (selected_data.eq('')).sum() != 0:
                
                if BA in WECC_BAs:
                    
                    all_states = WECC_BA_state_dic[BA]
                    new_prices = globals()['State_{}_prices'.format(fuel)].loc[:,all_states].mean(axis=1)
                    globals()['BA_{}_prices'.format(fuel)].loc[:,BA] = new_prices.values
                    
                elif BA in EIA_exclusive_BAs:
                    
                    all_states = EIA_BA_state_dic[BA]
                    new_prices = globals()['State_{}_prices'.format(fuel)].loc[:,all_states].mean(axis=1)
                    globals()['BA_{}_prices'.format(fuel)].loc[:,BA] = new_prices.values
                    
                else:
                    pass
                    
            else:
                pass
            
    #Filling out absent BA data from GO WECC
    for fuel in fuels:
        
        for BA in WECC_remain_BAs:
            
            all_states = WECC_BA_state_dic[BA]
            new_prices = globals()['State_{}_prices'.format(fuel)].loc[:,all_states].mean(axis=1)
            globals()['BA_{}_prices'.format(fuel)][BA] = new_prices.values
            
    
    #Exporting fuel price datasets     
    with pd.ExcelWriter('{}_Fuel_Price_Data.xlsx'.format(year), engine='openpyxl') as writer:  
        BA_coal_prices.to_excel(writer, sheet_name='BA_coal',index=False)
        State_coal_prices.to_excel(writer, sheet_name='State_coal',index=False)
        
        BA_NG_prices.to_excel(writer, sheet_name='BA_NG',index=False)
        State_NG_prices.to_excel(writer, sheet_name='State_NG',index=False)
        
        BA_oil_prices.to_excel(writer, sheet_name='BA_oil',index=False)
        State_oil_prices.to_excel(writer, sheet_name='State_oil',index=False)
                
        
    
 


