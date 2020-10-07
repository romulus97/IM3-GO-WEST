# -*- coding: utf-8 -*-
"""
Created on Fri Sep 11 11:49:37 2020

@author: mzeigha
"""


import pandas as pd


eGRID = pd.read_csv("eGRID_emission.csv")
generator = pd.read_csv("generators_DOE.csv")
emission = pd.read_csv("AP3_CA_Plants.csv")

for i in generator.index:
    for j in eGRID.index:
        if generator.loc[i,'DOE'] == eGRID.loc[j,'ORISPL']:
            generator.loc[i,'PLNOXRTA'] = eGRID.loc[j,'PLNOXRTA']
            generator.loc[i,'PLSO2RTA'] = eGRID.loc[j,'PLSO2RTA']
            generator.loc[i,'PLCO2RTA'] = eGRID.loc[j,'PLCO2RTA']
            generator.loc[i,'PLN2ORTA'] = eGRID.loc[j,'PLN2ORTA']


for i in generator.index:
    for j in emission.index:
        if generator.loc[i,'DOE'] == emission.loc[j,'PLANT']:
            generator.loc[i,'yr'] = emission.loc[j,'yr']
            generator.loc[i,'SO2_lbs_MD'] = emission.loc[j,'SO2_lbs_MD']
            generator.loc[i,'NOX_lbs_MD'] = emission.loc[j,'NOX_lbs_MD']
            generator.loc[i,'PM_MD_KWH'] = emission.loc[j,'PM_MD_KWH']
          
            
generator.to_csv (r'generator_emission_v3.csv', index = False, header=True)