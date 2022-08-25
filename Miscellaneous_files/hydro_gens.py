# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import pandas as pd

df = pd.read_csv('p_mean_max_min_MW_WECC_317plants_2005water_weekly.csv',header=0)

a = list(df['plant'].unique())

df_a= pd.DataFrame(a)
df_a.columns = ['plant']
df_a.to_csv('WM_hydro_plants.csv')