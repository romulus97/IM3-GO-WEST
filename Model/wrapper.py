# -*- coding: utf-8 -*-
"""
Created on Tue Jun 20 22:14:07 2017

@author: YSu
"""

from pyomo.opt import SolverFactory
from WECC_MILP import model as m1
from pyomo.core import Var
from pyomo.core import Constraint
from pyomo.core import Param
from operator import itemgetter
import pandas as pd
import numpy as np
from datetime import datetime
import pyomo.environ as pyo

days =2
# def sim(days):

instance = m1.create_instance('WECC_data.dat')
opt = SolverFactory("cplex")

H = instance.HorizonHours
D = 2
K=range(1,H+1)


#Space to store results
mwh=[]
# on=[]
# switch=[]
# srsv=[]
# nrsv=[]
vlt_angle=[]

df_generators = pd.read_csv('data_genparams.csv',header=0)

#max here can be (1,365)
for day in range(1,days):
    
    for z in instance.nodes:
    #load Demand and Reserve time series data
        for i in K:
            instance.HorizonDemand[z,i] = instance.SimDemand[z,(day-1)*24+i]
            instance.HorizonReserves[i] = instance.SimReserves[(day-1)*24+i]

    for z in instance.Hydro:
    #load Hydropower time series data
        
        for i in K:
            instance.HorizonHydro[z,i] = instance.SimHydro[z,(day-1)*24+i]
    
    # for z in instance.s_nodes:
    # #load Solar time series data
    #     for i in K:
    #         instance.HorizonSolar[z,i] = instance.SimSolar[z,(day-1)*24+i]
 
    # for z in instance.w_nodes:
    # #load Wind time series data
    #     for i in K:
    #         instance.HorizonWind[z,i] = instance.SimWind[z,(day-1)*24+i]
    

    result = opt.solve(instance,tee=True,symbolic_solver_labels=True) ##,tee=True to check number of variables\n",
    instance.solutions.load_from(result)  

 
    for v in instance.component_objects(Var, active=True):
        varobject = getattr(instance, str(v))
        a=str(v)
       
        # if a=='solar':
        #     for index in varobject:
        #         if int(index[1]>0 and index[1]<25):
        #             if index[0] in instance.s_nodes:
        #                 solar.append((index[0],index[1]+((day-1)*24),varobject[index].value))  
        
        # if a=='wind':
        #     for index in varobject:
        #         if int(index[1]>0 and index[1]<25):
        #             if index[0] in instance.w_nodes:
        #                 wind.append((index[0],index[1]+((day-1)*24),varobject[index].value))   
        
        if a=='vlt_angle':
            for index in varobject:
                if int(index[1]>0 and index[1]<25):
                    if index[0] in instance.nodes:
                        vlt_angle.append((index[0],index[1]+((day-1)*24),varobject[index].value))
                        
        if a=='mwh':
            for index in varobject:
                if int(index[1]>0 and index[1]<25):
                    mwh.append((index[0],index[1]+((day-1)*24),varobject[index].value))                                            
        
        # if a=='on':  
        #     for index in varobject:
        #         if int(index[1]>0 and index[1]<25):
        #             on.append((index[0],index[1]+((day-1)*24),varobject[index].value))

        # if a=='switch':
        #     for index in varobject:
        #         if int(index[1]>0 and index[1]<25):
        #             switch.append((index[0],index[1]+((day-1)*24),varobject[index].value))
                    
        # if a=='srsv':    
        #     for index in varobject:
        #         if int(index[1]>0 and index[1]<25):
        #             srsv.append((index[0],index[1]+((day-1)*24),varobject[index].value))

        # if a=='nrsv':    
        #     for index in varobject:
        #         if int(index[1]>0 and index[1]<25):
        #             nrsv.append((index[0],index[1]+((day-1)*24),varobject[index].value))

    print(day)
        
# solar_pd=pd.DataFrame(solar,columns=('Node','Time','Value'))
# wind_pd=pd.DataFrame(wind,columns=('Node','Time','Value'))
vlt_angle_pd=pd.DataFrame(vlt_angle,columns=('Node','Time','Value'))
mwh_pd=pd.DataFrame(mwh,columns=('Generator','Time','Value'))
# on_pd=pd.DataFrame(on,columns=('Generator','Time','Value'))
# switch_pd=pd.DataFrame(switch,columns=('Generator','Time','Value'))
# srsv_pd=pd.DataFrame(srsv,columns=('Generator','Time','Value'))
# nrsv_pd=pd.DataFrame(nrsv,columns=('Generator','Time','Value'))

#to save outputs
mwh_pd.to_csv('mwh.csv')
# solar_pd.to_csv('solar.csv')
# wind_pd.to_csv('wind.csv')
vlt_angle_pd.to_csv('vlt_angle.csv')
# on_pd.to_csv('on.csv')
# switch_pd.to_csv('switch.csv')
# srsv_pd.to_csv('srsv.csv')
# nrsv_pd.to_csv('nrsv.csv')


    # return None


