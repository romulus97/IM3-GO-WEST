# -*- coding: utf-8 -*-
"""
Created on Sun Aug  9 00:47:29 2020

@author: jkern
"""

import pandas as pd
import numpy as np

df = pd.read_csv('data_genparams.csv',header=0)
gens = df.loc[:,'name']
gen_nodes = df.loc[:,'node']
unique_nodes = gen_nodes.unique()

g_nodes = pd.read_excel('node_lists.xlsx', sheet_name = 'generation_only', header=0)##Generation nodes without demand
g_nodes = list(g_nodes['Name'])

d_nodes = pd.read_excel('node_lists.xlsx', sheet_name = 'demand_only',header=0) ##Transformers with demand
d_nodes = list(d_nodes['Name'])

t_nodes = pd.read_excel('node_lists.xlsx', sheet_name = 'neither',header=0) ##Transformers without demand
t_nodes = list(t_nodes['Name'])

all_nodes = g_nodes + t_nodes + d_nodes 

A = np.zeros((len(gens),len(all_nodes)))

df_A = pd.DataFrame(A)
df_A.columns = all_nodes

for i in range(0,len(gens)):
    node = df.loc[i,'node']
    df_A.loc[i,node] = 1

df_A.to_csv('gen_mat.csv')

