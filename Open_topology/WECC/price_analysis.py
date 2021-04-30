# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import pandas as pd
import math
import numpy as np
import matplotlib.pyplot as plt

########################################
# LOAD ALLOCATION FROM BALANCING AUTHORITY to NODES
########################################

NODE_NUMBER = [50,75]

for NN in NODE_NUMBER:
        
    FN = 'Exp' + str(NN) + '/duals.csv'
 
    # selected nodes
    df_prices = pd.read_csv(FN, header=0)
    buses = list(df_prices['Bus'].unique())
    
    locals()[FN + 'duals'] = np.zeros((8736,len(buses)))
    
    for b in buses:
        sample = df_prices.loc[df_prices['Bus']==b,'Value'].values
        # sample = sample.reset_index(drop=True)
        
        b_index = buses.index(b)
        locals()[FN + 'duals'][:,b_index] = sample
    
    plt.figure()
    plt.plot(locals()[FN + 'duals'])
    plt.xlabel('Day of Year',fontweight = 'bold',fontsize=12)
    plt.ylabel('Shadow Price ($/MWh)',fontweight='bold',fontsize=12)
    plt.ylim([15,30])
    
    fig_name = 'Exp' + str(NN) + '_duals.png'
    plt.savefig(fig_name,dpi=300)
    
    
 