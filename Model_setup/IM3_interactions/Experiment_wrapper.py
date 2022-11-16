# -*- coding: utf-8 -*-
"""
Created on Thu Nov  3 21:22:58 2022

@author: kakdemi
"""

import os
from shutil import copy
from pathlib import Path
import sys
sys.path.append('../IM3_interactions/CERF')
from CERF_extractor import CERF_extract
sys.path.append('../IM3_interactions/GCAM')
from GCAM_extractor import GCAM_extract
sys.path.append('../IM3_interactions/TELL')
from TELL_extractor import TELL_extract

################### USER INPUTS ###################

#Defining case name and details
Years = [2020] #This does not affect the IM3 experiment year, it's just a notation to select the correct folder created by reduced network data allocation script
NODE_NUMBER = [100]

# UC_TREATMENTS = ['_simple','_coal','_coal_gas']
UC_TREATMENTS = ['_simple']

line_limit_MW_scaling = [2000]
BA_hurdle_scaling = [0]

# Climate_scenarios = ['rcp85cooler_ssp3', 'rcp85cooler_ssp5', 'rcp85hotter_ssp3','rcp85hotter_ssp5', 'rcp45cooler_ssp3', 'rcp45cooler_ssp5','rcp45hotter_ssp3', 'rcp45hotter_ssp5']
Climate_scenarios = ['rcp45cooler_ssp3']

Hydro_year = 2015

CERF_year = 2015 #IM3 experiment year
TELL_year = 2020
GCAM_year = CERF_year

###################################################

#Defining the case name, creating relevant folders, copying relevant files
for YY in Years:
    for NN in NODE_NUMBER:
        for UC in UC_TREATMENTS:
            for T_p in line_limit_MW_scaling:
                for BA_hurd in BA_hurdle_scaling:
                    for CS in Climate_scenarios:
                    
                        case_name = '{}{}_{}_{}_{}'.format(NN,UC,T_p,BA_hurd,YY)
                        
                        path=str(Path.cwd()) + str(Path('/Altered_simulation_folders/Exp{}{}_{}_{}_{}_{}'.format(NN,UC,T_p,BA_hurd,CERF_year,CS)))
                        os.makedirs(path,exist_ok=True)
                        
                        path_2=str(Path.cwd()) + str(Path('/Altered_simulation_folders/Exp{}{}_{}_{}_{}_{}'.format(NN,UC,T_p,BA_hurd,CERF_year,CS))) + str(Path('/Inputs'))
                        os.makedirs(path_2,exist_ok=True)
                        
                        path_3=str(Path.cwd()) + str(Path('/Altered_simulation_folders/Exp{}{}_{}_{}_{}_{}'.format(NN,UC,T_p,BA_hurd,CERF_year,CS))) + str(Path('/Outputs'))
                        os.makedirs(path_3,exist_ok=True)
                        
                        #Copying model files
                        copy('../../UCED/wrapper{}.py'.format(UC),path)
                        copy('../WECCDataSetup.py',path)
                        
                        if UC == '_simple':
                            copy('../../UCED/WECC{}.py'.format(UC),path)
                        else:          
                            copy('../../UCED/WECC_MILP{}.py'.format(UC),path)
                            copy('../../UCED/WECC_LP{}.py'.format(UC),path)
                            
                        #Copying topology related and generic inputs
                        copy('../../UCED/Simulation_folders/Exp{}/Inputs/BA_to_BA_hurdle_scaled.csv'.format(case_name),path_2)
                        copy('../../UCED/Simulation_folders/Exp{}/Inputs/BA_to_BA_transmission_matrix.csv'.format(case_name),path_2)
                        copy('../../UCED/Simulation_folders/Exp{}/Inputs/line_params.csv'.format(case_name),path_2)
                        copy('../../UCED/Simulation_folders/Exp{}/Inputs/line_to_bus.csv'.format(case_name),path_2)
                        copy('../../UCED/Simulation_folders/Exp{}/Inputs/west_2020_lostcap.csv'.format(case_name),path_2) #This needs to be changed
    
                        #Calling CERF extractor
                        CERF_extract(NN,UC,T_p,BA_hurd,YY,Hydro_year,CERF_year,CS)
                        print('CERF extractor finished.')
                        #Calling GCAM extractor
                        GCAM_extract(NN,UC,T_p,BA_hurd,YY,Hydro_year,GCAM_year,CS)
                        print('GCAM extractor finished.')
                        #Calling TELL extractor
                        TELL_extract(NN,UC,T_p,BA_hurd,YY,Hydro_year,TELL_year,CS)
                        print('TELL extractor finished.')
                    










