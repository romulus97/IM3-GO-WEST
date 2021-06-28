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

NODE_NUMBER = [50,75,100,125,150,200,225,250,275,300]
TRANS_NUMBER = [25,50,75,100]

scenario_results = np.zeros((len(NODE_NUMBER),len(TRANS_NUMBER)))

for NN in NODE_NUMBER:
    
    for TN in TRANS_NUMBER:
        
        print(NN,TN)
        n_index = NODE_NUMBER.index(NN)
        t_index = TRANS_NUMBER.index(TN)
        
        FN = 'results/duals_Exp' + str(NN) + '_simple_' + str(TN) + '.csv'
     
        # selected nodes
        try:
            df_prices = pd.read_csv(FN, header=0)
            buses = list(df_prices['Bus'].unique())
        
            # locals()[FN + 'duals'] = np.zeros((8736,len(buses)))
            
            count = 0
            
            for b in buses:
                
                sample = df_prices.loc[df_prices['Bus']==b,'Value'].values
                count+=sum(sample>9999)
            
            count = count/(len(buses)*8760)
            
            scenario_results[n_index,t_index] = count
            
        except FileNotFoundError:
            scenario_results[n_index,t_index] = -999
                
            # sample = sample.reset_index(drop=True)
            
            # b_index = buses.index(b)
            # locals()[FN + 'duals'][:,b_index] = sample
        
        # plt.figure()
        # plt.plot(locals()[FN + 'duals'])
        # plt.xlabel('Day of Year',fontweight = 'bold',fontsize=12)
        # plt.ylabel('Shadow Price ($/MWh)',fontweight='bold',fontsize=12)
        # plt.ylim([0,200])
        
        # fig_name = 'Exp' + str(NN) + '_coal.png'
        # plt.savefig(fig_name,dpi=300)

df = pd.DataFrame(scenario_results)
df.to_csv('LOLP.csv')
        
     