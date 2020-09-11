# -*- coding: utf-8 -*-
"""
Created on Fri Sep 11 11:49:37 2020

@author: mzeigha
"""


import pandas as pd
import numpy as np


eff = pd.read_csv("efficiency.csv")
gen = pd.read_csv("generators.csv")


for i in eff.index:
    for j in gen.index:
        if gen.loc[j,'DOE'] == eff.loc[i,'DOE']:
            gen.loc[j,'CapFac'] = eff.loc[i,'Plant_capacity_factor']
            gen.loc[j,'CalCapFac'] = eff.loc[i,'CalCapFac']
            
gen.to_csv (r'export_dataframe.csv', index = False, header=True)