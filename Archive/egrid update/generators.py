# -*- coding: utf-8 -*-
"""
Created on Fri Sep 25 17:48:42 2020

@author: mzeigha
"""


import pandas as pd
import numpy as np


generators = pd.read_csv("generators.csv")
MS = pd.read_excel("MasterControl_update.xlsx")

for i in MS.index:
    if MS.loc[i , 'Resource_ID']== 0 :
       MS.loc[i , 'Resource_ID'] =MS.loc[i -1 , 'Resource_ID']



for i in generators.index:
    for j in MS.index:
        if generators.loc[i,'name'] == MS.loc[j,'Resource_ID']:
            generators.loc[i,'Name_Description'] = MS.loc[j,'Name_Description']
            
MS.to_csv (r'new_gen.csv', index = False, header=True)