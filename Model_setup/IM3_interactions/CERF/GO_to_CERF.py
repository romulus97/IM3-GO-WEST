# -*- coding: utf-8 -*-
"""
Created on Sat Oct  8 12:59:51 2022

@author: kakdemi
"""

import pandas as pd
import numpy as np

#Defining the year
year=2019

#Reading the data
LMP = pd.read_parquet('duals.parquet')

#Getting all bus names and organizing the layout
buses_str = [*LMP['Bus'].unique()]
buses_int = [int(i[4:]) for i in buses_str]
number_of_nodes = len(buses_int)
hour_nums = [*range(1,8761)]
number_of_hours = len(hour_nums)

Organized_LMP = pd.DataFrame(np.zeros((number_of_hours,number_of_nodes)),columns=buses_str)

for bus in buses_str:
    Bus_LMPs = LMP.loc[LMP['Bus']==bus]['Value'].values
    Organized_LMP.loc[:,bus] = Bus_LMPs

Organized_LMP.columns = buses_int
Organized_LMP.insert(loc=0, column='hour', value=hour_nums)

#Writing the LMP data for CERF
Organized_LMP.to_csv('lmp_8760_{}.csv'.format(year),index=False)


