# -*- coding: utf-8 -*-
"""
Created on Sun Aug  9 00:47:29 2020

@author: jkern
"""

import pandas as pd
import numpy as np

df = pd.read_csv('data_genparams.csv',header=0)
gens = list(df.loc[:,'name'])

df_nodes = pd.read_csv('reduced_buses.csv',header=0)
all_nodes = list(df_nodes['bus_i'])

A = np.zeros((len(gens),len(all_nodes)))

df_A = pd.DataFrame(A)
df_A.columns = all_nodes
df_A['name'] = gens
df_A.set_index('name',inplace=True)

for i in range(0,len(gens)):
    node = df.loc[i,'node']
    g = gens[i]
    df_A.loc[g,node] = 1

df_A.to_csv('gen_mat.csv')

