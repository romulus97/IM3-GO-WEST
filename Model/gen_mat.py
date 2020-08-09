# -*- coding: utf-8 -*-
"""
Created on Sun Aug  9 00:47:29 2020

@author: jkern
"""

import pandas as pd
import numpy as np

df = pd.read_excel('WECC generators.xlsx',sheet_name = 'data_genparams',header=0)
gens = df.loc[:,'name']
gen_nodes = df.loc[:,'node']
unique_nodes = gen_nodes.unique()

A = np.zeros((len(gens),len(unique_nodes)))

df_A = pd.DataFrame(A)
df_A.columns = unique_nodes

for i in range(0,len(gens)):
    node = gen_nodes.loc[i]
    df_A.loc[i,node] = 1

df_A.to_csv('gen_mat.csv')

