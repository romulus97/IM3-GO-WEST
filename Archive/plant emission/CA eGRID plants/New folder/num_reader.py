# -*- coding: utf-8 -*-
"""
Created on Sun Oct  4 14:00:14 2020

@author: mzeigha
"""


import pandas as pd

num = pd.read_csv("generators_not_covered_num.csv")
generator = pd.read_csv("generator_DOE.csv")
eGRID = pd.read_csv("eGIRD_capacity.csv")


for i in generator.index:
    for j in num.index:
        if generator.loc[i,'num_1'] == num.loc[j,'num']:
            generator.loc[i,'Name_Description'] = num.loc[j,'Name_Description']
            generator.loc[i,'netcap'] = num.loc[j,'netcap']
            generator.loc[i,'typ'] = num.loc[j,'typ']
            
for i in generator.index:
    for j in eGRID.index:
        if generator.loc[i,'DOE'] == eGRID.loc[j,'ORISPL']:
            generator.loc[i,'PLPRMFL'] = eGRID.loc[j,'PLPRMFL']
            generator.loc[i,'PLFUELCT'] = eGRID.loc[j,'PLFUELCT']
            generator.loc[i,'NAMEPCAP'] = eGRID.loc[j,'NAMEPCAP']

            
generator.to_csv (r'generator_DOE_cap_num.csv', index = False, header=True)