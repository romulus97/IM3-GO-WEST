# -*- coding: utf-8 -*-
"""
Created on Sun Aug  9 00:47:29 2020

@author: jkern
"""

import pandas as pd
import numpy as np

df = pd.read_csv('data_transparams.csv',header=0)
sources = df.loc[:,'source']
sinks = df.loc[:,'sink']
combined = np.append(sources, sinks)
df_combined = pd.DataFrame(combined,columns=['node'])
unique_nodes = df_combined['node'].unique()

A = np.zeros((len(unique_nodes),len(unique_nodes)))

df_Sus = pd.DataFrame(A)
df_Sus.columns = unique_nodes

df_Mw = pd.DataFrame(A)
df_Mw.columns = unique_nodes

node_list = list(unique_nodes)

for i in range(0,len(df)):
    s = df.loc[i,'source']
    k = df.loc[i,'sink']

    node_id = node_list.index(s)
    
    df_Mw.loc[node_id,k] = df.loc[i,'linemva']

df_Mw.to_csv('trans_MW_mat.csv')

for i in range(0,len(df)):
    s = df.loc[i,'source']
    k = df.loc[i,'sink']

    node_id = node_list.index(s)
    
    df_Sus.loc[node_id,k] = df.loc[i,'linesus']
    
df_Sus.to_csv('trans_sus_mat.csv')

