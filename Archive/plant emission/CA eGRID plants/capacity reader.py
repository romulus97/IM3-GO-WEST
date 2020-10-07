# -*- coding: utf-8 -*-
"""
Created on Fri Sep 11 11:49:37 2020

@author: mzeigha
"""


import pandas as pd

eGRID = pd.read_csv("eGIRD_capacity.csv")
generator = pd.read_csv("generator_DOE_clean.csv")

for i in generator.index:
    for j in eGRID.index:
        if generator.loc[i,'Name'] == eGRID.loc[j,'ORISPL']:
            generator.loc[i,'PNAME'] = eGRID.loc[j,'PNAME']
            generator.loc[i,'PLPRMFL'] = eGRID.loc[j,'PLPRMFL']
            generator.loc[i,'PLFUELCT'] = eGRID.loc[j,'PLFUELCT']
            generator.loc[i,'NAMEPCAP'] = eGRID.loc[j,'NAMEPCAP']


            
generator.to_csv (r'generator_DOE_cap.csv', index = False, header=True)