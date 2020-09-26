# -*- coding: utf-8 -*-
"""
Created on Fri Sep 11 11:49:37 2020

@author: mzeigha
"""


import pandas as pd
import numpy as np


eGRID = pd.read_csv("eGRID_emission.csv")
generator = pd.read_csv("generators_DOE.csv")
emission = pd.read_csv("unit-list-emissions_v2.csv")

for i in generator.index:
    for j in eGRID.index:
        if generator.loc[i,'PLANT'] == eGRID.loc[j,'ORISPL']:
            generator.loc[i,'PLNOXAN'] = eGRID.loc[j,'PLNOXAN']
            generator.loc[i,'PLSO2AN'] = eGRID.loc[j,'PLSO2AN']
            generator.loc[i,'PLCO2AN'] = eGRID.loc[j,'PLCO2AN']
            generator.loc[i,'PLN2OAN'] = eGRID.loc[j,'PLN2OAN']
            generator.loc[i,'PLNOXRTA'] = eGRID.loc[j,'PLNOXRTA']
            generator.loc[i,'PLSO2RTA'] = eGRID.loc[j,'PLSO2RTA']
            generator.loc[i,'PLCO2RTA'] = eGRID.loc[j,'PLCO2RTA']
            generator.loc[i,'PLN2ORTA'] = eGRID.loc[j,'PLN2ORTA']


for i in generator.index:
    for j in emission.index:
        if generator.loc[i,'PLANT'] == emission.loc[j,'PLANT']:
            generator.loc[i,'CO2rate'] = emission.loc[j,'CO2rate']
            generator.loc[i,'NOXrate'] = emission.loc[j,'NOXrate']
            generator.loc[i,'SO2rate'] = emission.loc[j,'SO2rate']
          
            
generator.to_csv (r'generator_emission_v3.csv', index = False, header=True)