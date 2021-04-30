# -*- coding: utf-8 -*-
"""
Created on Mon Oct 12 23:22:13 2020

@author: jkern
"""

import pandas as pd
import networkx as nx
import numpy as np

df_data = pd.read_csv('connectivity_check.csv',header=0)

graph = {}

sources = list(df_data['source'])
sinks = list(df_data['sink'])

G = nx.Graph()
G.add_nodes_from(sources)

edges = []
for i in range(0,len(df_data)):
    j = sources[i]
    k = sinks[i]
    edges.append((j,k))

G.add_edges_from(edges)

for c in sorted(nx.connected_components(G), key=len, reverse=True):
    print(len(c)) 

S = [G.subgraph(c).copy() for c in nx.connected_components(G)]

for i in range(0,len(S)):
    d = list(S[i].nodes)
    fn = 'graph_' + str(i) + '.txt'
    np.savetxt(fn,d)


    
    