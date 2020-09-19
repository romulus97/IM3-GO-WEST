# -*- coding: utf-8 -*-
"""
Created on Sun Aug  9 00:47:29 2020

@author: jkern
"""

import pandas as pd
import numpy as np

df = pd.read_excel('data_transparams.xlsx',header=0)
sources = df.loc[:,'source']
sinks = df.loc[:,'sink']
combined = np.append(sources, sinks)
df_combined = pd.DataFrame(combined,columns=['node'])
unique_nodes = df_combined['node'].unique()
unique_nodes.sort()

A = np.zeros((len(df),len(unique_nodes)))

df_line_to_bus = pd.DataFrame(A)
df_line_to_bus.columns = unique_nodes

negative = []
positive = []
lines = []
ref_node = 0
reactance = []
limit = []

for i in range(0,len(df)):
    s = df.loc[i,'source']
    k = df.loc[i,'sink']
    line = s + '_' + k
    if s == 'MESA_CAL_20': 
        lines.append(line)
        positive.append(s)
        negative.append(k)
        df_line_to_bus.loc[ref_node,s] = 1
        df_line_to_bus.loc[ref_node,k] = -1
        reactance.append(df.loc[i,'reactance'])
        limit.append(df.loc[i,'linemva'])
        ref_node += 1
    elif k == 'MESA_CAL_20':      
        lines.append(line)
        positive.append(k)
        negative.append(s)
        df_line_to_bus.loc[ref_node,k] = 1
        df_line_to_bus.loc[ref_node,s] = -1
        reactance.append(df.loc[i,'reactance'])
        limit.append(df.loc[i,'linemva'])
        ref_node += 1
        
for i in range(0,len(df)):
    s = df.loc[i,'source']
    k = df.loc[i,'sink']
    line = s + '_' + k
    if s != 'MESA_CAL_20':
        if k != 'MESA_CAL_20':
            lines.append(line)
            
            if s in positive and k in negative:
                df_line_to_bus.loc[ref_node,s] = 1
                df_line_to_bus.loc[ref_node,k] = -1
            
            elif k in positive and s in negative:
                df_line_to_bus.loc[ref_node,k] = 1
                df_line_to_bus.loc[ref_node,s] = -1
                
            elif s in positive and k in positive:
                df_line_to_bus.loc[ref_node,s] = 1
                df_line_to_bus.loc[ref_node,k] = -1
            
            elif s in negative and k in negative:   
                df_line_to_bus.loc[ref_node,s] = 1
                df_line_to_bus.loc[ref_node,k] = -1
                
            elif s in positive:
                df_line_to_bus.loc[ref_node,s] = 1
                df_line_to_bus.loc[ref_node,k] = -1
                negative.append(k)
            elif s in negative:
                df_line_to_bus.loc[ref_node,k] = 1
                df_line_to_bus.loc[ref_node,s] = -1   
                positive.append(k)
            elif k in positive:
                df_line_to_bus.loc[ref_node,k] = 1
                df_line_to_bus.loc[ref_node,s] = -1  
                negative.append(s)
            elif k in negative:
                df_line_to_bus.loc[ref_node,s] = 1
                df_line_to_bus.loc[ref_node,k] = -1 
                positive.append(s)
            else:
                positive.append(s)
                negative.append(k)
                df_line_to_bus.loc[ref_node,s] = 1
                df_line_to_bus.loc[ref_node,k] = -1

            reactance.append(df.loc[i,'reactance'])
            limit.append(df.loc[i,'linemva'])
            ref_node += 1

df_line_to_bus['line'] = lines
#df_line_to_bus.to_csv('line_to_bus.csv')


df_line_params = pd.DataFrame()
df_line_params['line'] = lines
df_line_params['reactance'] = reactance
df_line_params['limit'] = limit 
df_line_params.to_csv('line_params.csv')


