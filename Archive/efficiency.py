# -*- coding: utf-8 -*-
"""
Created on Fri Sep 11 11:49:37 2020

@author: mzeigha
"""


import pandas as pd
import numpy as np


generators = pd.read_csv("generators.csv")
MasterControl = pd.read_csv("MasterControl2.csv")


for i in generators.index:
    for j in MasterControl.index:
        if generators.loc[i,'name'] == MasterControl.loc[j,'Resource_ID']:
            generators.loc[i,'Name_Description'] = MasterControl.loc[j,'Name_Description']
            
generators.to_csv (r'new_generators.csv', index = False, header=True)