# -*- coding: utf-8 -*-
"""
Created on Sun Oct 16 11:07:56 2022

@author: kakdemi
"""

import pandas as pd
import numpy as np
import os
from shutil import copy
from pathlib import Path
import sys
import yaml

def CERF_extract(NN,UC,T_p,BA_hurd,YY,Hydro_year,CERF_year,CS,Solar_wind_year):
    
    #Correcting the directory
    cwd = os.getcwd()
    os.chdir("{}\\CERF".format(cwd))

    #Reading CERF generator types from YAML file
    with open('Reference_files/cerf_generation_types.yml') as f:
        CERF_gen_dict = yaml.full_load(f)

    #Reading generic generator parameters
    generic_params = pd.read_excel('Reference_files/Generator_parameters.xlsx',header=0,index_col=0)
    
    #Reading solar and wind generator profiles
    solar_cf_profiles = pd.read_csv('CERF_outputs/solar_gen_cf_{}.csv'.format(Solar_wind_year),header=0)
    wind_cf_profiles = pd.read_csv('CERF_outputs/wind_gen_cf_{}.csv'.format(Solar_wind_year),header=0)
        
    #Defining all node numbers
    bus_information_df = pd.read_excel('../../Selected_nodes/Results_Excluded_Nodes_{}.xlsx'.format(NN),sheet_name='Bus',header=0)
    all_buses_int = [*bus_information_df['bus_i']]
    all_buses_str = ['bus_{}'.format(i) for i in all_buses_int]
    
    #Reading CERF generator outputs and organizing the generator related files depending on the year
    if CERF_year == 2015:
        CERF_generators = pd.read_csv('CERF_outputs/infrastructure_{}_{}.csv'.format(CERF_year,CS),header=0)
    else:
        CERF_generators = pd.read_csv('CERF_outputs/cerf_for_go_{}_{}.csv'.format(CS,CERF_year),header=0)
        
    #Filtering buses only present in GO WEST database and appending generator information
    CERF_generators_WEST = CERF_generators.loc[CERF_generators['lmp_zone'].isin(all_buses_int)].copy()
    CERF_generators_WEST.fillna(-999,inplace=True)
    CERF_generators_WEST.reset_index(inplace=True,drop=True)
    
    #Creating empty lists to store data for generator information
    gen_name = []
    gen_typ = []
    gen_node = []
    gen_maxcap = []
    gen_heatrate = []
    gen_mincap = []
    gen_var_om = []
    gen_no_load = []
    gen_st_cost = []
    gen_ramp = []
    gen_minup = []
    gen_mindown = []

    for j in range(0,len(CERF_generators_WEST)):
        
        CERF_gen_type = CERF_generators_WEST.loc[j,'tech_name']
        CERF_gen_cap = round(CERF_generators_WEST.loc[j,'unit_size_mw'],2)
        CERF_gen_name = CERF_generators_WEST.loc[j,'cerf_plant_id']
        CERF_gen_bus = CERF_generators_WEST.loc[j,'lmp_zone']
        
        try:
            CERF_heatrate = CERF_generators_WEST.loc[j,'heat_rate_btu_per_kWh']/1000
            CERF_VOM = CERF_generators_WEST.loc[j,'variable_om_usd_per_mwh']
        except KeyError:
            CERF_heatrate = -999
            CERF_VOM = -999
            
        if CERF_gen_type in CERF_gen_dict['Biomass_CERF_types']:
            gen_name.append('ID_{}'.format(CERF_gen_name))
            gen_node.append('bus_{}'.format(CERF_gen_bus))
            gen_maxcap.append(CERF_gen_cap)
            gen_typ.append('biomass')
        
            if CERF_heatrate<0:
                gen_heatrate.append(generic_params.loc['Heat rate (MMBtu/MWh)','Biomass'])
            else:
                gen_heatrate.append(CERF_heatrate)
                
            gen_mincap.append(round(generic_params.loc['Minimum capacity (%)','Biomass']*CERF_gen_cap/100,2))
            
            if CERF_VOM<0:
                gen_var_om.append(generic_params.loc['Variable operation and maintenance costs ($/MWh)','Biomass'])
            else:
                gen_var_om.append(CERF_VOM)
                
            gen_no_load.append(round(generic_params.loc['No load cost (Capacity Multiplier)','Biomass']*CERF_gen_cap,0))
            gen_st_cost.append(round(generic_params.loc['Start-up cost (Capacity Multiplier)','Biomass']*CERF_gen_cap,0))
            gen_ramp.append(round(generic_params.loc['Hourly ramp rate (%)','Biomass']*CERF_gen_cap/100,2))
            gen_minup.append(generic_params.loc['Minimum up time (hours)','Biomass'])
            gen_mindown.append(generic_params.loc['Minimum down time (hours)','Biomass'])
            
        elif CERF_gen_type in CERF_gen_dict['Coal_CERF_types']:
            gen_name.append('ID_{}'.format(CERF_gen_name))
            gen_node.append('bus_{}'.format(CERF_gen_bus))
            gen_maxcap.append(CERF_gen_cap)
            gen_typ.append('coal')
        
            if CERF_heatrate<0:
                gen_heatrate.append(generic_params.loc['Heat rate (MMBtu/MWh)','Coal'])
            else:
                gen_heatrate.append(CERF_heatrate)
                
            gen_mincap.append(round(generic_params.loc['Minimum capacity (%)','Coal']*CERF_gen_cap/100,2))
            
            if CERF_VOM<0:
                gen_var_om.append(generic_params.loc['Variable operation and maintenance costs ($/MWh)','Coal'])
            else:
                gen_var_om.append(CERF_VOM)
                
            gen_no_load.append(round(generic_params.loc['No load cost (Capacity Multiplier)','Coal']*CERF_gen_cap,0))
            gen_st_cost.append(round(generic_params.loc['Start-up cost (Capacity Multiplier)','Coal']*CERF_gen_cap,0))
            gen_ramp.append(round(generic_params.loc['Hourly ramp rate (%)','Coal']*CERF_gen_cap/100,2))
            gen_minup.append(generic_params.loc['Minimum up time (hours)','Coal'])
            gen_mindown.append(generic_params.loc['Minimum down time (hours)','Coal'])
            
        elif CERF_gen_type in CERF_gen_dict['NG_CERF_types']:
            gen_name.append('ID_{}'.format(CERF_gen_name))
            gen_node.append('bus_{}'.format(CERF_gen_bus))
            gen_maxcap.append(CERF_gen_cap)
            gen_typ.append('ngcc')
        
            if CERF_heatrate<0:
                gen_heatrate.append(generic_params.loc['Heat rate (MMBtu/MWh)','Natural Gas'])
            else:
                gen_heatrate.append(CERF_heatrate)
                
            gen_mincap.append(round(generic_params.loc['Minimum capacity (%)','Natural Gas']*CERF_gen_cap/100,2))
            
            if CERF_VOM<0:
                gen_var_om.append(generic_params.loc['Variable operation and maintenance costs ($/MWh)','Natural Gas'])
            else:
                gen_var_om.append(CERF_VOM)
                
            gen_no_load.append(round(generic_params.loc['No load cost (Capacity Multiplier)','Natural Gas']*CERF_gen_cap,0))
            gen_st_cost.append(round(generic_params.loc['Start-up cost (Capacity Multiplier)','Natural Gas']*CERF_gen_cap,0))
            gen_ramp.append(round(generic_params.loc['Hourly ramp rate (%)','Natural Gas']*CERF_gen_cap/100,2))
            gen_minup.append(generic_params.loc['Minimum up time (hours)','Natural Gas'])
            gen_mindown.append(generic_params.loc['Minimum down time (hours)','Natural Gas'])
            
        elif CERF_gen_type in CERF_gen_dict['Geothermal_CERF_types']:
            gen_name.append('ID_{}'.format(CERF_gen_name))
            gen_node.append('bus_{}'.format(CERF_gen_bus))
            gen_maxcap.append(CERF_gen_cap)
            gen_typ.append('geothermal')
        
            if CERF_heatrate<0:
                gen_heatrate.append(generic_params.loc['Heat rate (MMBtu/MWh)','Geothermal'])
            else:
                gen_heatrate.append(CERF_heatrate)
                
            gen_mincap.append(round(generic_params.loc['Minimum capacity (%)','Geothermal']*CERF_gen_cap/100,2))
            
            if CERF_VOM<0:
                gen_var_om.append(generic_params.loc['Variable operation and maintenance costs ($/MWh)','Geothermal'])
            else:
                gen_var_om.append(CERF_VOM)
                
            gen_no_load.append(round(generic_params.loc['No load cost (Capacity Multiplier)','Geothermal']*CERF_gen_cap,0))
            gen_st_cost.append(round(generic_params.loc['Start-up cost (Capacity Multiplier)','Geothermal']*CERF_gen_cap,0))
            gen_ramp.append(round(generic_params.loc['Hourly ramp rate (%)','Geothermal']*CERF_gen_cap/100,2))
            gen_minup.append(generic_params.loc['Minimum up time (hours)','Geothermal'])
            gen_mindown.append(generic_params.loc['Minimum down time (hours)','Geothermal'])
            
        elif CERF_gen_type in CERF_gen_dict['Oil_CERF_types']:
            gen_name.append('ID_{}'.format(CERF_gen_name))
            gen_node.append('bus_{}'.format(CERF_gen_bus))
            gen_maxcap.append(CERF_gen_cap)
            gen_typ.append('oil')
        
            if CERF_heatrate<0:
                gen_heatrate.append(generic_params.loc['Heat rate (MMBtu/MWh)','Oil'])
            else:
                gen_heatrate.append(CERF_heatrate)
                
            gen_mincap.append(round(generic_params.loc['Minimum capacity (%)','Oil']*CERF_gen_cap/100,2))
            
            if CERF_VOM<0:
                gen_var_om.append(generic_params.loc['Variable operation and maintenance costs ($/MWh)','Oil'])
            else:
                gen_var_om.append(CERF_VOM)
                
            gen_no_load.append(round(generic_params.loc['No load cost (Capacity Multiplier)','Oil']*CERF_gen_cap,0))
            gen_st_cost.append(round(generic_params.loc['Start-up cost (Capacity Multiplier)','Oil']*CERF_gen_cap,0))
            gen_ramp.append(round(generic_params.loc['Hourly ramp rate (%)','Oil']*CERF_gen_cap/100,2))
            gen_minup.append(generic_params.loc['Minimum up time (hours)','Oil'])
            gen_mindown.append(generic_params.loc['Minimum down time (hours)','Oil'])
        
        elif CERF_gen_type in CERF_gen_dict['Nuclear_CERF_types']:
            pass
        
        elif CERF_gen_type in CERF_gen_dict['Solar_CERF_types']:
            pass
            
        elif CERF_gen_type in CERF_gen_dict['OnshoreWind_CERF_types']:
            pass
            
        elif CERF_gen_type in CERF_gen_dict['OffshoreWind_CERF_types']:
            pass

        elif CERF_gen_type in CERF_gen_dict['Hydro_CERF_types']:
            pass
            
    
    #Creating mustrun (nuclear) file and copying it to relevant folder
    #Filtering nuclear generators
    mustrun_filter = CERF_generators_WEST.loc[CERF_generators_WEST['tech_name'].isin(CERF_gen_dict['Nuclear_CERF_types'])].copy()
    #Grouping nuclear generators and creating a dataframe to store bulk nuclear capacity at each node
    mustrun_selected = mustrun_filter.loc[:,['unit_size_mw','lmp_zone']].copy()
    mustrun_total = mustrun_selected.groupby('lmp_zone').sum()
    mustrun_df = pd.DataFrame(np.zeros((1,len(mustrun_total))),columns=[*mustrun_total.index])
    
    for k in range(0,len(mustrun_total)):
        mustrun_bus = mustrun_total.index[k]
        mustrun_df.loc[0,mustrun_bus] = mustrun_total.iloc[k,0]

    mustrun_df.columns = ['bus_{}'.format(z) for z in mustrun_df.columns]
    mustrun_df.to_csv('../Altered_simulation_folders/Exp{}{}_{}_{}_{}_{}/Inputs/must_run.csv'.format(NN,UC,T_p,BA_hurd,CERF_year,CS),index=None)
    
    
    #Creating solar timeseries and aggragating solar generators and adding those to datagenparams file
    #Filtering solar generators and finding unique solar nodes
    solar_filter = CERF_generators_WEST.loc[CERF_generators_WEST['tech_name'].isin(CERF_gen_dict['Solar_CERF_types'])].copy()
    
    #Creating empty solar timeseries for each bus
    solar_timeseries_df = pd.DataFrame(np.zeros((8760,len(all_buses_int))),columns=all_buses_int)
    
    for q in all_buses_int:
        
        sp_solar_nodal = solar_filter.loc[solar_filter['lmp_zone']==q]
        
        try:
            CERF_solar_VOM = sp_solar_nodal.loc[:,'variable_om_usd_per_mwh'].mean()
        except KeyError:
            CERF_solar_VOM=-999
        
        if len(sp_solar_nodal) == 0:
            pass
        
        else:
            #Adding relevant parameters to generators dataset
            total_nodal_solar_cap = sp_solar_nodal['unit_size_mw'].sum()
            nodal_solar_name = 'bus_{}_SOLAR'.format(q)
            gen_name.append(nodal_solar_name)
            gen_node.append('bus_{}'.format(q))
            gen_maxcap.append(total_nodal_solar_cap)
            gen_typ.append('solar')
            gen_heatrate.append(0)
            gen_mincap.append(0)
            
            if CERF_solar_VOM<0:
                gen_var_om.append(0)
            else:
                gen_var_om.append(CERF_solar_VOM)
                
            gen_no_load.append(0)
            gen_st_cost.append(0)
            gen_ramp.append(0)
            gen_minup.append(0)
            gen_mindown.append(0)
            
            #Altering solar timeseries by looking at generation
            plant_IDs_nodal_solar = [*sp_solar_nodal['cerf_plant_id']]
            total_nodal_solar_generation = solar_cf_profiles.loc[:,plant_IDs_nodal_solar].sum(axis=1)
            solar_timeseries_df.loc[:,q] = total_nodal_solar_generation.values

    solar_timeseries_df.columns = ['bus_{}'.format(z) for z in solar_timeseries_df.columns]
    solar_timeseries_df.to_csv('../Altered_simulation_folders/Exp{}{}_{}_{}_{}_{}/Inputs/nodal_solar.csv'.format(NN,UC,T_p,BA_hurd,CERF_year,CS),index=None)
    
    
    #Creating wind timeseries and aggragating wind generators and adding those to datagenparams file
    #Filtering wind generators and finding unique wind nodes
    wind_filter = CERF_generators_WEST.loc[CERF_generators_WEST['tech_name'].isin(CERF_gen_dict['OnshoreWind_CERF_types'])].copy()
    
    #Creating empty wind timeseries for each bus
    wind_timeseries_df = pd.DataFrame(np.zeros((8760,len(all_buses_int))),columns=all_buses_int)
    
    for q in all_buses_int:
        
        sp_wind_nodal = wind_filter.loc[wind_filter['lmp_zone']==q]
        
        try:
            CERF_wind_VOM = sp_wind_nodal.loc[:,'variable_om_usd_per_mwh'].mean()
        except KeyError:
            CERF_wind_VOM=-999
        
        if len(sp_wind_nodal) == 0:
            pass
        
        else:
            #Adding relevant parameters to generators dataset
            total_nodal_wind_cap = sp_wind_nodal['unit_size_mw'].sum()
            nodal_wind_name = 'bus_{}_WIND'.format(q)
            gen_name.append(nodal_wind_name)
            gen_node.append('bus_{}'.format(q))
            gen_maxcap.append(total_nodal_wind_cap)
            gen_typ.append('wind')
            gen_heatrate.append(0)
            gen_mincap.append(0)
            
            if CERF_wind_VOM<0:
                gen_var_om.append(0)
            else:
                gen_var_om.append(CERF_wind_VOM)
            
            gen_no_load.append(0)
            gen_st_cost.append(0)
            gen_ramp.append(0)
            gen_minup.append(0)
            gen_mindown.append(0)
            
            #Altering wind timeseries by looking at generation
            plant_IDs_nodal_wind = [*sp_wind_nodal['cerf_plant_id']]
            total_nodal_wind_generation = wind_cf_profiles.loc[:,plant_IDs_nodal_wind].sum(axis=1)
            wind_timeseries_df.loc[:,q] = total_nodal_wind_generation.values
 
    wind_timeseries_df.columns = ['bus_{}'.format(z) for z in wind_timeseries_df.columns]
    wind_timeseries_df.to_csv('../Altered_simulation_folders/Exp{}{}_{}_{}_{}_{}/Inputs/nodal_wind.csv'.format(NN,UC,T_p,BA_hurd,CERF_year,CS),index=None)
    
    
    #Creating offshorewind timeseries and aggragating offshorewind generators and adding those to datagenparams file
    #Filtering offshorewind generators and finding unique offshorewind nodes
    offshorewind_filter = CERF_generators_WEST.loc[CERF_generators_WEST['tech_name'].isin(CERF_gen_dict['OffshoreWind_CERF_types'])].copy()
    
    #Creating empty offshorewind timeseries for each bus
    offshorewind_timeseries_df = pd.DataFrame(np.zeros((8760,len(all_buses_int))),columns=all_buses_int)
    
    for q in all_buses_int:
        
        sp_offshorewind_nodal = offshorewind_filter.loc[offshorewind_filter['lmp_zone']==q]
        
        try:
            CERF_offshorewind_VOM = sp_offshorewind_nodal.loc[:,'variable_om_usd_per_mwh'].mean()
        except KeyError:
            CERF_offshorewind_VOM=-999
        
        if len(sp_offshorewind_nodal) == 0:
            pass
        
        else:
            #Adding relevant parameters to generators dataset
            total_nodal_offshorewind_cap = sp_offshorewind_nodal['unit_size_mw'].sum()
            nodal_offshorewind_name = 'bus_{}_OFFSHOREWIND'.format(q)
            gen_name.append(nodal_offshorewind_name)
            gen_node.append('bus_{}'.format(q))
            gen_maxcap.append(total_nodal_offshorewind_cap)
            gen_typ.append('offshorewind')
            gen_heatrate.append(0)
            gen_mincap.append(0)
            
            if CERF_offshorewind_VOM<0:
                gen_var_om.append(0)
            else:
                gen_var_om.append(CERF_offshorewind_VOM)
            
            gen_no_load.append(0)
            gen_st_cost.append(0)
            gen_ramp.append(0)
            gen_minup.append(0)
            gen_mindown.append(0)
            
            #Altering offshorewind timeseries by looking at generation
            plant_IDs_nodal_offshorewind = [*sp_offshorewind_nodal['cerf_plant_id']]
            total_nodal_offshorewind_generation = wind_cf_profiles.loc[:,plant_IDs_nodal_offshorewind].sum(axis=1)
            offshorewind_timeseries_df.loc[:,q] = total_nodal_offshorewind_generation.values

    offshorewind_timeseries_df.columns = ['bus_{}'.format(z) for z in offshorewind_timeseries_df.columns]
    offshorewind_timeseries_df.to_csv('../Altered_simulation_folders/Exp{}{}_{}_{}_{}_{}/Inputs/nodal_offshorewind.csv'.format(NN,UC,T_p,BA_hurd,CERF_year,CS),index=None)
    
    
    #Creating hydro timeseries and aggragating hydro generators and adding those to datagenparams file
    #Saving EIA IDs in a different column
    CERF_generators_WEST['EIA_ID'] = [int(r.split('_')[0]) for r in CERF_generators_WEST['cerf_plant_id']]
    #Filtering hydro generators and finding unique hydro nodes
    hydro_filter = CERF_generators_WEST.loc[CERF_generators_WEST['tech_name'].isin(CERF_gen_dict['Hydro_CERF_types'])].copy()
    
    #Reading EIA hydro data
    df_hydro = pd.read_csv('../../../Data_setup/Time_series_data/Hydro_generation/EIA_302_WECC_hydro_plants.csv',header=0)
    df_hydro_ts = pd.read_csv('../../../Data_setup/Time_series_data/Hydro_generation/Hydropower_organized_data/p_mean_max_min_MW_WECC_302plants_weekly_{}.csv'.format(Hydro_year),header=0)
    
    hydro_302_EIA_IDs = [*df_hydro['EIA_ID']]
    
    #Creating empty hydro timeseries for each bus
    hydro_timeseries_df_max = pd.DataFrame(np.zeros((365,len(all_buses_int))),columns=all_buses_int)
    hydro_timeseries_df_min = pd.DataFrame(np.zeros((365,len(all_buses_int))),columns=all_buses_int)
    hydro_timeseries_df_mean = pd.DataFrame(np.zeros((365,len(all_buses_int))),columns=all_buses_int)

    hydro_EIA_IDs_all = [*hydro_filter['EIA_ID'].unique()]
    
    #Creating hydropower timeseries
    for p in hydro_EIA_IDs_all:
        
        if p in hydro_302_EIA_IDs:
            sp_hydro_plant_node = hydro_filter.loc[hydro_filter['EIA_ID']==p]['lmp_zone'].values[0]
            
            max_hydro_timeseries = df_hydro_ts.loc[df_hydro_ts['EIA_ID']==p]['max'].repeat(7).reset_index(drop=True)
            min_hydro_timeseries = df_hydro_ts.loc[df_hydro_ts['EIA_ID']==p]['min'].repeat(7).reset_index(drop=True)
            mean_hydro_timeseries = df_hydro_ts.loc[df_hydro_ts['EIA_ID']==p]['mean'].repeat(7).reset_index(drop=True)
            mean_hydro_timeseries = mean_hydro_timeseries*24
            
            hydro_timeseries_df_max.loc[0:363,sp_hydro_plant_node] = max_hydro_timeseries + hydro_timeseries_df_max.loc[0:363,sp_hydro_plant_node]
            hydro_timeseries_df_min.loc[0:363,sp_hydro_plant_node] = min_hydro_timeseries + hydro_timeseries_df_min.loc[0:363,sp_hydro_plant_node]
            hydro_timeseries_df_mean.loc[0:363,sp_hydro_plant_node] = mean_hydro_timeseries + hydro_timeseries_df_mean.loc[0:363,sp_hydro_plant_node]
                
        else:
            pass
        
    hydro_timeseries_df_max.loc[364,:] = hydro_timeseries_df_max.loc[363,:]
    hydro_timeseries_df_min.loc[364,:] = hydro_timeseries_df_min.loc[363,:]
    hydro_timeseries_df_mean.loc[364,:] = hydro_timeseries_df_mean.loc[363,:]
    
    hydro_timeseries_df_max.columns = ['bus_{}'.format(z) for z in hydro_timeseries_df_max.columns]
    hydro_timeseries_df_min.columns = ['bus_{}'.format(z) for z in hydro_timeseries_df_min.columns]
    hydro_timeseries_df_mean.columns = ['bus_{}'.format(z) for z in hydro_timeseries_df_mean.columns]
    
    hydro_timeseries_df_max.to_csv('../Altered_simulation_folders/Exp{}{}_{}_{}_{}_{}/Inputs/Hydro_max.csv'.format(NN,UC,T_p,BA_hurd,CERF_year,CS),index=None)
    hydro_timeseries_df_min.to_csv('../Altered_simulation_folders/Exp{}{}_{}_{}_{}_{}/Inputs/Hydro_min.csv'.format(NN,UC,T_p,BA_hurd,CERF_year,CS),index=None)
    hydro_timeseries_df_mean.to_csv('../Altered_simulation_folders/Exp{}{}_{}_{}_{}_{}/Inputs/Hydro_total.csv'.format(NN,UC,T_p,BA_hurd,CERF_year,CS),index=None)
    
    #Adding hydropower parameters to datagenparams file
    for q in all_buses_int:
        
        sp_hydro_nodal = hydro_filter.loc[hydro_filter['lmp_zone']==q]
        
        try:
            CERF_hydro_VOM = sp_hydro_nodal.loc[:,'variable_om_usd_per_mwh'].mean()
        except KeyError:
            CERF_hydro_VOM=-999
        
        if len(sp_hydro_nodal) == 0:
            pass
        
        else:
            
            if hydro_timeseries_df_max.loc[:,'bus_{}'.format(q)].sum()<=0:
                pass
            
            else:
                #Adding relevant parameters to generators dataset
                total_nodal_hydro_cap = hydro_timeseries_df_max.loc[0,'bus_{}'.format(q)]
                nodal_hydro_name = 'bus_{}_HYDRO'.format(q)
                gen_name.append(nodal_hydro_name)
                gen_node.append('bus_{}'.format(q))
                gen_maxcap.append(total_nodal_hydro_cap)
                gen_typ.append('hydro')
                gen_heatrate.append(0)
                gen_mincap.append(0)
                
                if CERF_hydro_VOM<0:
                    gen_var_om.append(1)
                else:
                    gen_var_om.append(CERF_hydro_VOM)
                
                gen_no_load.append(1)
                gen_st_cost.append(1)
                gen_ramp.append(total_nodal_hydro_cap)
                gen_minup.append(0)
                gen_mindown.append(0)
    
    #Creating datagenparams file and exporting
    generators_df = pd.DataFrame(list(zip(gen_name,gen_typ,gen_node,gen_maxcap,gen_heatrate,gen_mincap,\
                                     gen_var_om,gen_no_load,gen_st_cost,gen_ramp,gen_minup,gen_mindown)),\
                                 columns=['name','typ','node','maxcap','heat_rate','mincap','var_om',\
                                          'no_load','st_cost','ramp','minup','mindn'])
        
    generators_df.to_csv('../Altered_simulation_folders/Exp{}{}_{}_{}_{}_{}/Inputs/data_genparams.csv'.format(NN,UC,T_p,BA_hurd,CERF_year,CS),index=None)
        
    
    #Creating generator-bus matrix
    gen_mat_df = pd.DataFrame(np.zeros((len(generators_df),len(all_buses_str))),columns=all_buses_str)
    all_gen_names = [*generators_df['name']]
    gen_mat_df.insert(loc=0, column='name', value=all_gen_names)
    gen_mat_df.index = all_gen_names
    
    for i in all_gen_names:
        
        generator_sp_bus = generators_df.loc[generators_df['name']==i]['node'].values[0]
        gen_mat_df.loc[i,generator_sp_bus] = 1
        
    gen_mat_df.to_csv('../Altered_simulation_folders/Exp{}{}_{}_{}_{}_{}/Inputs/gen_mat.csv'.format(NN,UC,T_p,BA_hurd,CERF_year,CS),index=None)
        
    
    #Creating thermal gens data file
    thermal_gens_filter = generators_df.loc[generators_df['typ'].isin(['coal', 'oil', 'ngcc', 'biomass', 'geothermal'])]
    thermal_gens_filter.reset_index(drop=True,inplace=True)
    
    #Creating empty lists to store data
    thermal_name = []
    thermal_bus = []
    thermal_fuel = []
    thermal_maxcap = []
    thermal_mincap = []
    thermal_heatrate = []
    
    for i in range(0,len(thermal_gens_filter)):
        
        thermal_name.append(thermal_gens_filter.loc[i,'name'])
        thermal_bus.append(int(thermal_gens_filter.loc[i,'node'].split('_')[1]))
        
        my_gen_type = thermal_gens_filter.loc[i,'typ']
        if my_gen_type == 'coal':
            thermal_fuel.append('BIT (Bituminous Coal)')
        elif my_gen_type == 'oil':
            thermal_fuel.append('OIL')
        elif my_gen_type == 'ngcc':
            thermal_fuel.append('NG (Natural Gas)')
        elif my_gen_type == 'biomass':
            thermal_fuel.append('BIO')
        elif my_gen_type == 'geothermal':
            thermal_fuel.append('GEO')
        else:
            pass
        
        thermal_maxcap.append(thermal_gens_filter.loc[i,'maxcap'])
        thermal_mincap.append(thermal_gens_filter.loc[i,'mincap'])
        thermal_heatrate.append(thermal_gens_filter.loc[i,'heat_rate'])
    
    nuclear_gens_filter = CERF_generators_WEST.loc[CERF_generators_WEST['tech_name'].isin(CERF_gen_dict['Nuclear_CERF_types'])].copy()
    nuclear_gens_filter.reset_index(drop=True,inplace=True)
    
    for j in range(0,len(nuclear_gens_filter)):
        
        thermal_name.append('ID_{}'.format(nuclear_gens_filter.loc[j,'cerf_plant_id']))
        thermal_bus.append(nuclear_gens_filter.loc[j,'lmp_zone'])
        thermal_fuel.append('NUC (Nuclear)')
        thermal_maxcap.append(nuclear_gens_filter.loc[j,'unit_size_mw'])
        thermal_mincap.append(nuclear_gens_filter.loc[j,'unit_size_mw'])
        
        try:
            sp_nuclear_heatrate = nuclear_gens_filter.loc[j,'heat_rate_btu_per_kWh']/1000
        except KeyError:
            sp_nuclear_heatrate=-999
        
        if sp_nuclear_heatrate<0:
            thermal_heatrate.append(0)
        else:
            thermal_heatrate.append(sp_nuclear_heatrate)
           
    thermal_gens = pd.DataFrame(list(zip(thermal_name,thermal_bus,thermal_fuel,thermal_maxcap,thermal_mincap,thermal_heatrate)),\
                                 columns=['Name','Bus','Fuel','Max_Cap','Min_Cap','Heat_Rate'])
        
    thermal_gens.to_csv('../Altered_simulation_folders/Exp{}{}_{}_{}_{}_{}/Inputs/thermal_gens.csv'.format(NN,UC,T_p,BA_hurd,CERF_year,CS),index=None)
        
    
    #Creating generator capacity bins
    sys.path.append('../../')
    #importing a function created in another script to generate a dictionary from the data_genparams file
    from dict_creator import dict_funct
    df_loss_dict=dict_funct(generators_df)
    #save the dictionary as a .npy file
    np.save('../Altered_simulation_folders/Exp{}{}_{}_{}_{}_{}/Inputs/gen_outage_cat.npy'.format(NN,UC,T_p,BA_hurd,CERF_year,CS), df_loss_dict)
    
    return None



