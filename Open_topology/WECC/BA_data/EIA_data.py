# -*- coding: utf-8 -*-
"""
Created on Thu Feb 11 22:24:48 2021

@author: jkern
"""
import pandas as pd
import numpy as np
import xlrd

df_BAs = pd.read_csv('BAs.csv',header=0)

#assign EIA 930 load for 2019 to each BA
abbr = list(df_BAs['Abbreviation'])

for a in abbr:

    idx = abbr.index(a)
    filename = '../../CSV_Files/' + a + '_Hourly_Load_Data.csv'
    b = pd.read_csv(filename,header=0)
    load = b.loc[b['Year']==2019,'Adjusted_Demand_MWh']
    
    if idx < 1:
        C = load
    else:
        C = np.column_stack((C,load))

r,c = np.shape(C)
for i in range(0,r):
    for j in range(0,c):
        if C[i,j] < 0:
            C[i,j] = 0
df_C = pd.DataFrame(C)
df_C.columns = abbr
df_C.to_csv('BA_load.csv')

for a in abbr:
    
    idx = abbr.index(a)
    filename = '../../Raw_Data/' + a + '.xlsx'
    b = pd.read_excel(filename,header=0,sheet_name='Published Hourly Data')
    solar = b.loc[b['UTC time'].dt.year == 2019,'Adjusted SUN Gen']
    wind = b.loc[b['UTC time'].dt.year == 2019,'Adjusted WND Gen']
    
    if idx < 1:
        S = solar
        W = wind
    else:
        S = np.column_stack((S,solar))
        W = np.column_stack((W,wind))

r,c = np.shape(S)
for i in range(0,r):
    for j in range(0,c):
        if S[i,j] < 0:
            S[i,j] = 0
df_S = pd.DataFrame(S)
df_S.columns = abbr
df_S.to_csv('BA_solar.csv')

r,c = np.shape(W)
for i in range(0,r):
    for j in range(0,c):
        if W[i,j] < 0:
            W[i,j] = 0
df_W = pd.DataFrame(W)
df_W.columns = abbr
df_W.to_csv('BA_wind.csv')