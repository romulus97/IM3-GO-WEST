
import csv
import pandas as pd
import numpy as np


######=================================================########
######               Segment A.1                       ########
######=================================================########

SimDays = 365
SimHours = SimDays * 24
HorizonHours = 24  ##planning horizon (e.g., 24, 48, 72 hours etc.)
TransLoss = 0.075  ##transmission loss as a percent of generation
n1criterion = 0.75 ##maximum line-usage as a percent of line-capacity
res_margin = 0.15  ##minimum reserve as a percent of system demand
spin_margin = 0.50 ##minimum spinning reserve as a percent of total reserve

data_name = 'WECC_data'


######=================================================########
######               Segment A.2                       ########
######=================================================########

#read parameters for dispatchable resources
df_gen = pd.read_csv('data_genparams.csv',header=0)

#read gen_matrix assignments
df_gen_mat = pd.read_csv('gen_mat.csv',header=0)

#read gen_matrix assignments
df_trans_sus = pd.read_csv('trans_sus_mat.csv',header=0)

#read gen_matrix assignments
df_trans_mw = pd.read_csv('trans_MW_mat.csv',header=0)

##hourly ts of dispatchable hydropower at each domestic dam
df_hydro = pd.read_csv('data_hydro.csv',header=0)

####hourly ts of dispatchable solar-power at each plant
##df_solar = pd.read_csv('data_solar.csv',header=0)   
##
####hourly ts of dispatchable wind-power at each plant
##df_wind = pd.read_csv('data_wind.csv',header=0)

##hourly ts of load at substation-level
df_load = pd.read_csv('data_load.csv',header=0) 

#hourly minimum reserve as a function of load (e.g., 15% of current load)
df_reserves = pd.DataFrame((df_load.iloc[:,:].sum(axis=1)*res_margin).values,columns=['Reserve'])

######=================================================########
######               Segment A.3                       ########
######=================================================########

####======== Lists of Nodes of the Power System ========########
df_hydro = pd.read_csv('data_hydro.csv',header=0)
h_nodes = df_hydro.columns

g_nodes = pd.read_excel('node_lists.xlsx', sheet_name = 'generation_only', header=0)##Generation nodes without demand
g_nodes = list(g_nodes['Name'])

d_nodes = pd.read_excel('node_lists.xlsx', sheet_name = 'demand_only',header=0) ##Transformers with demand
d_nodes = list(d_nodes['Name'])

t_nodes = pd.read_excel('node_lists.xlsx', sheet_name = 'neither',header=0) ##Transformers without demand
t_nodes = list(t_nodes['Name'])

all_nodes = g_nodes + t_nodes + d_nodes 


######=================================================########
######               Segment A.4                       ########
######=================================================########

######====== write data.dat file ======########
with open(''+str(data_name)+'.dat', 'w') as f:

  
####### generator sets by type  
    # Coal
    f.write('set Coal :=\n')
    # pull relevant generators
    for gen in range(0,len(df_gen)):
        if df_gen.loc[gen,'typ'] == 'coal':
            unit_name = df_gen.loc[gen,'name']
            unit_name = unit_name.replace(' ','_')
            f.write(unit_name + ' ')
    f.write(';\n\n')        

    # Oil_ic
    f.write('set Oil :=\n')
    # pull relevant generators
    for gen in range(0,len(df_gen)):
        if df_gen.loc[gen,'typ'] == 'oil':
            unit_name = df_gen.loc[gen,'name']
            unit_name = unit_name.replace(' ','_')
            f.write(unit_name + ' ')
    f.write(';\n\n')  

    # Gas_cc
    f.write('set Gas :=\n')
    # pull relevant generators
    for gen in range(0,len(df_gen)):
        if df_gen.loc[gen,'typ'] == 'ngcc':
            unit_name = df_gen.loc[gen,'name']
            unit_name = unit_name.replace(' ','_')
            f.write(unit_name + ' ')
        elif df_gen.loc[gen,'typ'] == 'ngct':
            unit_name = df_gen.loc[gen,'name']
            unit_name = unit_name.replace(' ','_')
            f.write(unit_name + ' ')        
    f.write(';\n\n')  

    # Slack
    f.write('set Slack :=\n')
    # pull relevant generators
    for gen in range(0,len(df_gen)):
        if df_gen.loc[gen,'typ'] == 'slack':
            unit_name = df_gen.loc[gen,'name']
            unit_name = unit_name.replace(' ','_')
            f.write(unit_name + ' ')
    f.write(';\n\n')  

    # Hydro
    f.write('set Hydro :=\n')
    # pull relevant generators
    for gen in range(0,len(df_gen)):
        if df_gen.loc[gen,'typ'] == 'hydro':
            unit_name = df_gen.loc[gen,'name']
            unit_name = unit_name.replace(' ','_')
            f.write(unit_name + ' ')
    f.write(';\n\n') 

    # Must run
    f.write('set Must :=\n')
    # pull relevant generators
    for gen in range(0,len(df_gen)):
        if df_gen.loc[gen,'typ'] == 'must':
            unit_name = df_gen.loc[gen,'name']
            unit_name = unit_name.replace(' ','_')
            f.write(unit_name + ' ')
    f.write(';\n\n')  

    print('Gen sets')

######=================================================########
######               Segment A.5                       ########
######=================================================########

######Set nodes, sources and sinks
    # nodes
    f.write('set nodes :=\n')
    for z in all_nodes:
        f.write(z + ' ')
    f.write(';\n\n')
    
    # sources
    f.write('set sources :=\n')
    for z in all_nodes:
        f.write(z + ' ')
    f.write(';\n\n')
    
    # sinks
    f.write('set sinks :=\n')
    for z in all_nodes:
        f.write(z + ' ')
    f.write(';\n\n')
    
    print('nodes')
    
######=================================================########
######               Segment A.6                       ########
######=================================================########
       
####### simulation period and horizon
    f.write('param SimHours := %d;' % SimHours)
    f.write('\n')
    f.write('param SimDays:= %d;' % SimDays)
    f.write('\n\n')   
    f.write('param HorizonHours := %d;' % HorizonHours)
    f.write('\n\n')
    f.write('param TransLoss := %0.3f;' % TransLoss)
    f.write('\n\n')
    f.write('param n1criterion := %0.3f;' % n1criterion)
    f.write('\n\n')
    f.write('param spin_margin := %0.3f;' % spin_margin)
    f.write('\n\n')


######=================================================########
######               Segment A.7                       ########
######=================================================########
    
####### create parameter matrix for generators
    f.write('param:' + '\t')
    for c in df_gen.columns:
        if c != 'name':
            f.write(c + '\t')
    f.write(':=\n\n')
    for i in range(0,len(df_gen)):    
        for c in df_gen.columns:
            if c == 'name':
                unit_name = df_gen.loc[i,'name']
                unit_name = unit_name.replace(' ','_')
                unit_name = unit_name.replace('&','_')
                unit_name = unit_name.replace('.','')
                f.write(unit_name + '\t')  
            else:
                f.write(str((df_gen.loc[i,c])) + '\t')               
        f.write('\n')
    f.write(';\n\n')     
    
    print('Gen params')

######=================================================########
######               Segment A.8                       ########
######=================================================########

####### create parameter matrix for transmission paths (source and sink connections)
    f.write('param:' + '\t' + 'linemva' + '\t' +'linesus :=' + '\n')
    for z in all_nodes:
        for x in all_nodes:
            x_index = all_nodes.index(x)
            f.write(z + '\t' + x + '\t' + str(df_trans_mw.loc[x_index,z]) + '\t' + str(df_trans_sus.loc[x_index,z]) + '\n')
    f.write(';\n\n')

    print('trans paths')
######=================================================########
######               Segment A.9                       ########
######=================================================########

####### Hourly timeseries (load, hydro, solar, wind, reserve)
    
    # load (hourly)
    f.write('param:' + '\t' + 'SimDemand:=' + '\n')      
    for z in all_nodes:
        if z in d_nodes:
            for h in range(0,len(df_load)):
                f.write(z + '\t' + str(h+1) + '\t' + str(df_load.loc[h,z]) + '\n')
        else:
            for h in range(0,len(df_load)):
                f.write(z + '\t' + str(h+1) + '\t' + str(0) + '\n')

    f.write(';\n\n')

    # hydro (hourly)
    f.write('param:' + '\t' + 'SimHydro:=' + '\n')
    h_gens = df_hydro.columns      
    for z in h_gens:
        for h in range(0,len(df_hydro)): 
        # for h in range(0,240):
            f.write(z + '\t' + str(h+1) + '\t' + str(df_hydro.loc[h,z]) + '\n')
    f.write(';\n\n')

##    # solar (hourly)
##    f.write('param:' + '\t' + 'SimSolar:=' + '\n')      
##    for z in s_nodes:
##        for h in range(0,len(df_solar)): 
##            f.write(z + '\t' + str(h+1) + '\t' + str(df_solar.loc[h,z]) + '\n')
##    f.write(';\n\n')
##
##    # wind (hourly)
##    f.write('param:' + '\t' + 'SimWind:=' + '\n')      
##    for z in w_nodes:
##        for h in range(0,len(df_wind)): 
##            f.write(z + '\t' + str(h+1) + '\t' + str(df_wind.loc[h,z]) + '\n')
##    f.write(';\n\n')
    
###### System-wide hourly reserve
    f.write('param' + '\t' + 'SimReserves:=' + '\n')
    # for h in range(0,240):
    for h in range(0,len(df_load)):
            f.write(str(h+1) + '\t' + str(df_reserves.loc[h,'Reserve']) + '\n')
    f.write(';\n\n')
    
    print('time series')
    

###### Gen matrix
    
    f.write('param' + '\t' + 'gen_mat:=' + '\n')
    for i in range(0,len(df_gen)):
        for j in df_gen_mat.columns:
            if j!= 'name':
                f.write(df_gen.loc[i,'name'] + '\t' + j + '\t' + str(df_gen_mat.loc[i,j]) + '\n')
    f.write(';\n\n')


print ('Complete:',data_name)
