# -*- coding: utf-8 -*-
"""
Created on Fri May 27 15:33:18 2022

@author: hssemba
"""
import numpy as np
import pandas as pd

def dict_funct(dataset):
    def gencat(row):  
        if row['maxcap'] <= 50 :
            return "below_50"
        elif row['maxcap'] <= 100:
            return "50_100"
        elif row['maxcap'] <= 200:
            return "100_200"
        elif row['maxcap'] <= 300:
            return "200_300"
        elif row['maxcap'] <= 400:
            return "300_400"
        elif row['maxcap'] <= 600:
            return "400_600"
        elif row['maxcap'] <= 800:
            return "600_800"
        elif row['maxcap'] <= 1000:
            return "800_1000"
        else:
            return "ovr_1000"

    
    #new size
    dataset['gen_categ'] = dataset.apply(lambda row: gencat(row), axis=1)
    
    Nu_All_n_100_200=[] 
    Nu_600_800 =[]
    Nu_200_300 =[]
    Nu_400_600=[]
    Nu_300_400=[]
    Nu_800_1000=[]
    Nu_All_n_0_100=[]
    Nu_100_200 =[]
    Nu_All_n_ovr_200 =[]
    Nu_50_100 =[]
    Nu_below_50 =[]
    Nu_ovr_1000 =[]
    Ga_All_n_100_200 =[]
    Ga_600_800 =[]
    Ga_200_300  =[]
    Ga_400_600 =[]
    Ga_300_400  =[]
    Ga_800_1000 =[]
    Ga_All_n_0_100 =[]
    Ga_100_200 =[]
    Ga_All_n_ovr_200 =[]
    Ga_50_100  =[]
    Ga_below_50  =[]
    Ga_ovr_1000  =[]
    Co_All_n_100_200 =[]
    Co_600_800 =[]
    Co_200_300 =[]
    Co_400_600 =[]
    Co_300_400 =[]
    Co_800_1000 =[]
    Co_All_n_0_100 =[]
    Co_100_200  =[]
    Co_All_n_ovr_200 =[]
    Co_50_100  =[]
    Co_below_50  =[]
    Co_ovr_1000 =[]
    
    for i in range(0, len(dataset)):
        if dataset.loc[i,"typ"]=="ngcc" and dataset.loc[i,"gen_categ"]=="below_50" :
            Ga_below_50.append(dataset.loc[i,"name"])
        if dataset.loc[i,"typ"]=="coal" and dataset.loc[i,"gen_categ"]=="below_50" :
            Co_below_50.append(dataset.loc[i,"name"])
        if dataset.loc[i,"typ"]=="ngcc" and dataset.loc[i,"gen_categ"]=="50_100" :
            Ga_50_100.append(dataset.loc[i,"name"])
        if dataset.loc[i,"typ"]=="coal" and dataset.loc[i,"gen_categ"]=="50_100" :
            Co_50_100.append(dataset.loc[i,"name"])
        if dataset.loc[i,"typ"]=="ngcc" and dataset.loc[i,"gen_categ"]=="100_200" :
            Ga_100_200.append(dataset.loc[i,"name"])
        if dataset.loc[i,"typ"]=="coal" and dataset.loc[i,"gen_categ"]=="100_200" :
            Co_100_200.append(dataset.loc[i,"name"])        
        if dataset.loc[i,"typ"]=="ngcc" and dataset.loc[i,"gen_categ"]=="200_300" :
            Ga_200_300.append(dataset.loc[i,"name"])
        if dataset.loc[i,"typ"]=="coal" and dataset.loc[i,"gen_categ"]=="200_300" :
            Co_200_300.append(dataset.loc[i,"name"])         
        if dataset.loc[i,"typ"]=="ngcc" and dataset.loc[i,"gen_categ"]=="300_400" :
            Ga_300_400.append(dataset.loc[i,"name"])
        if dataset.loc[i,"typ"]=="coal" and dataset.loc[i,"gen_categ"]=="300_400" :
            Co_300_400.append(dataset.loc[i,"name"])          
        if dataset.loc[i,"typ"]=="ngcc" and dataset.loc[i,"gen_categ"]=="400_600" :
            Ga_400_600.append(dataset.loc[i,"name"])
        if dataset.loc[i,"typ"]=="coal" and dataset.loc[i,"gen_categ"]=="400_600" :
            Co_400_600.append(dataset.loc[i,"name"])     
        if dataset.loc[i,"typ"]=="ngcc" and dataset.loc[i,"gen_categ"]=="600_800" :
            Ga_600_800.append(dataset.loc[i,"name"])
        if dataset.loc[i,"typ"]=="coal" and dataset.loc[i,"gen_categ"]=="600_800" :
            Co_600_800.append(dataset.loc[i,"name"])
        if dataset.loc[i,"typ"]=="ngcc" and dataset.loc[i,"gen_categ"]=="800_1000" :
            Ga_800_1000.append(dataset.loc[i,"name"])
        if dataset.loc[i,"typ"]=="coal" and dataset.loc[i,"gen_categ"]=="800_1000" :
            Co_800_1000.append(dataset.loc[i,"name"])
        if dataset.loc[i,"typ"]=="ngcc" and dataset.loc[i,"gen_categ"]=="ovr_1000" :
            Ga_ovr_1000.append(dataset.loc[i,"name"])
        if dataset.loc[i,"typ"]=="coal" and dataset.loc[i,"gen_categ"]=="ovr_1000" :
            Co_ovr_1000.append(dataset.loc[i,"name"])

    for i in range(0, len(dataset)):               
        if dataset.loc[i,"typ"]=="ngcc" and dataset.loc[i,"maxcap"]<=100 :
            Ga_All_n_0_100.append(dataset.loc[i,"name"])
        elif dataset.loc[i,"typ"]=="coal" and dataset.loc[i,"maxcap"]<=100 :
            Co_All_n_0_100.append(dataset.loc[i,"name"])     
        elif dataset.loc[i,"typ"]=="ngcc" and dataset.loc[i,"maxcap"]<=200 :
            Ga_All_n_100_200.append(dataset.loc[i,"name"])
        elif dataset.loc[i,"typ"]=="coal" and dataset.loc[i,"maxcap"]<=200 :
            Co_All_n_100_200.append(dataset.loc[i,"name"])
        elif dataset.loc[i,"typ"]=="ngcc" and dataset.loc[i,"maxcap"]>200 :
            Ga_All_n_ovr_200.append(dataset.loc[i,"name"])
        elif dataset.loc[i,"typ"]=="coal" and dataset.loc[i,"maxcap"]>200 :
            Co_All_n_ovr_200.append(dataset.loc[i,"name"])
            
    Dict = {}
    #Dict["Nuclear_below_50"]= Nu_below_50
    #Dict["Nuclear_50_100"]= Nu_50_100
    #Dict["Nuclear_100_200"]= Nu_100_200
    #Dict["Nuclear_200_300"] = Nu_200_300
    #Dict["Nuclear_300_400"] = Nu_300_400
    #Dict["Nuclear_400_600"] = Nu_400_600
    #Dict["Nuclear_600_800"] = Nu_600_800
    #Dict["Nuclear_800_1000"] = Nu_800_1000
    #Dict["Nuclear_ovr_1000"]= Nu_ovr_1000
    #Dict["Nuclear_All_n_0_100"] = Nu_All_n_0_100
    #Dict["Nuclear_All_n_100_200"] = Nu_All_n_100_200
    #Dict["Nuclear_All_n_ovr_200"]= Nu_All_n_ovr_200
    Dict["Gas_below_50"]= Ga_below_50
    Dict["Gas_50_100"]= Ga_50_100
    Dict["Gas_100_200"]= Ga_100_200
    Dict["Gas_200_300"] = Ga_200_300
    Dict["Gas_300_400"] = Ga_300_400
    Dict["Gas_400_600"] = Ga_400_600
    Dict["Gas_600_800"] = Ga_600_800
    Dict["Gas_800_1000"] = Ga_800_1000
    Dict["Gas_ovr_1000"]= Ga_ovr_1000
    Dict["Gas_All_n_0_100"] = Ga_All_n_0_100
    Dict["Gas_All_n_100_200"] = Ga_All_n_100_200
    Dict["Gas_All_n_ovr_200"]= Ga_All_n_ovr_200
    Dict["Coal_below_50"]= Co_below_50
    Dict["Coal_50_100"]= Co_50_100
    Dict["Coal_100_200"]= Co_100_200
    Dict["Coal_200_300"] = Co_200_300
    Dict["Coal_300_400"] = Co_300_400
    Dict["Coal_400_600"] = Co_400_600
    Dict["Coal_600_800"] = Co_600_800
    Dict["Coal_800_1000"] = Co_800_1000
    Dict["Coal_ovr_1000"]= Co_ovr_1000
    Dict["Coal_All_n_0_100"] = Co_All_n_0_100
    Dict["Coal_All_n_100_200"] = Co_All_n_100_200
    Dict["Coal_All_n_ovr_200"]= Co_All_n_ovr_200
            
    
    return Dict
