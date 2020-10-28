# -*- coding: utf-8 -*-
"""
Created on Tue Oct 27 10:13:47 2020

@author: jkern
"""

import pandas as pd
import numpy as np

df_data = pd.read_csv('hourly_hydro.csv',header=0)
s = np.shape(df_data)
units = list(df_data.columns)

daily = np.zeros((365,len(units)))

for u in units:
    for i in range(0,len(daily)):        
        idx = units.index(u)
        daily[i,idx] = sum(df_data.loc[i*24:i*24+24,u])

df_daily = pd.DataFrame(daily)
df_daily.columns = units
df_daily.to_csv('data_hydro.csv')

