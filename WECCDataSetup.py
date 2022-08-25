
import csv
import pandas as pd
import numpy as np


######=================================================########
######               Segment A.1                       ########
######=================================================########

SimDays = 365
SimHours = SimDays * 24
HorizonHours = 24  ##planning horizon (e.g., 24, 48, 72 hours etc.)
# TransLoss = 0.075  ##transmission loss as a percent of generation
# n1criterion = 0.75 ##maximum line-usage as a percent of line-capacity
# res_margin = 0.15  ##minimum reserve as a percent of system demand
# spin_margin = 0.50 ##minimum spinning reserve as a percent of total reserve

data_name = 'WECC_data'


######=================================================########
######               Segment A.2                       ########
######=================================================########

#read parameters for dispatchable resources
df_gen = pd.read_csv('data_genparams.csv',header=0)

#read generation and transmission data
df_bustounitmap = pd.read_csv('gen_mat.csv',header=0)
df_linetobusmap = pd.read_csv('line_to_bus.csv',header=0)
df_line_params = pd.read_csv('line_params.csv',header=0)
lines = list(df_line_params['line'])

##daily ts of hydro at nodal-level
df_hydro_MAX = pd.read_csv('Hydro_max.csv',header=0)
df_hydro_MIN = pd.read_csv('Hydro_min.csv',header=0)
df_hydro_TOTAL = pd.read_csv('Hydro_total.csv',header=0)

empty = []
sites = list(df_hydro_MAX.columns)
for i in sites:
    if sum(df_hydro_MAX[i]) > 0:
        pass
    else:
        empty.append(i)

df_hydro_MAX = df_hydro_MAX.drop(columns=empty)
df_hydro_MIN = df_hydro_MIN.drop(columns=empty)
df_hydro_TOTAL = df_hydro_TOTAL.drop(columns=empty)


##hourly ts of dispatchable solar-power at each plant
df_solar = pd.read_csv('nodal_solar.csv',header=0)   

empty = []
sites = list(df_solar.columns)
for i in sites:
    if sum(df_solar[i]) > 0:
        pass
    else:
        empty.append(i)

df_solar = df_solar.drop(columns=empty)

##
##hourly ts of dispatchable wind-power at each plant
df_wind = pd.read_csv('nodal_wind.csv',header=0)

empty = []
sites = list(df_wind.columns)
for i in sites:
    if sum(df_wind[i]) > 0:
        pass
    else:
        empty.append(i)

df_wind = df_wind.drop(columns=empty)

##hourly ts of load at substation-level
df_load = pd.read_csv('nodal_load.csv',header=0) 

# #hourly minimum reserve as a function of load (e.g., 15% of current load)
# df_reserves = pd.DataFrame((df_load.iloc[:,:].sum(axis=1)*res_margin).values,columns=['Reserve'])

##must run at substation-level
df_must = pd.read_csv('must_run.csv',header=0)
h3 = df_must.columns

## Fuel prices at substation-level
df_fuel = pd.read_csv('Fuel_prices.csv',header=0)

#BA to BA transmission limit data
BA_to_BA_hurdle_data = pd.read_csv('BA_to_BA_hurdle_scaled.csv',header=0)
all_BA_BA_connections = list(BA_to_BA_hurdle_data['BA_to_BA'])
BA_to_BA_transmission_matrix = pd.read_csv('BA_to_BA_transmission_matrix.csv',header=0)


######=================================================########
######               Segment A.3                       ########
######=================================================########

####======== Lists of Nodes and Thermal Units of the Power System ========#######

all_nodes = list(df_load.columns)

all_thermals = list(df_fuel.columns)

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


    # Hydro
    f.write('set Hydro :=\n')
    # pull relevant generators
    for gen in range(0,len(df_gen)):
        if df_gen.loc[gen,'typ'] == 'hydro':
            unit_name = df_gen.loc[gen,'name']
            unit_name = unit_name.replace(' ','_')
            f.write(unit_name + ' ')
    f.write(';\n\n') 
    
    # Solar
    f.write('set Solar :=\n')
    # pull relevant generators
    for gen in range(0,len(df_gen)):
        if df_gen.loc[gen,'typ'] == 'solar':
            unit_name = df_gen.loc[gen,'name']
            unit_name = unit_name.replace(' ','_')
            f.write(unit_name + ' ')
    f.write(';\n\n') 
    
    # Wind
    f.write('set Wind :=\n')
    # pull relevant generators
    for gen in range(0,len(df_gen)):
        if df_gen.loc[gen,'typ'] == 'wind':
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
    f.write('set buses :=\n')
    for z in all_nodes:
        f.write(z + ' ')
    f.write(';\n\n')
    
    print('nodes')
    
    # lines
    f.write('set lines :=\n')
    for z in lines:
        f.write(z + ' ')
    f.write(';\n\n')
    
    print('lines')
    
    #BA to BA exchange limit
    f.write('set exchanges :=\n')
    for z in all_BA_BA_connections:
        f.write(z + ' ')
    f.write(';\n\n')
    
    
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
    # f.write('param TransLoss := %0.3f;' % TransLoss)
    # f.write('\n\n')
    # f.write('param n1criterion := %0.3f;' % n1criterion)
    # f.write('\n\n')
    # f.write('param spin_margin := %0.3f;' % spin_margin)
    # f.write('\n\n')


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
    f.write('param:' + '\t' + 'FlowLim' + '\t' +'Reactance :=' + '\n')
    for z in lines:
        idx = lines.index(z)
        f.write(z + '\t' + str(df_line_params.loc[idx,'limit']) + '\t' + str(df_line_params.loc[idx,'reactance']) + '\n')
    f.write(';\n\n')

    print('trans paths')
    
    #BA to BA exchange hurdle
    f.write('param:' + '\t' +'ExchangeHurdle :=' + '\n')
    for z in all_BA_BA_connections:
        idx = all_BA_BA_connections.index(z)
        f.write(z + '\t' + str(BA_to_BA_hurdle_data.loc[idx,'Hurdle_$/MWh']) + '\n')
    f.write(';\n\n')
    
    
######=================================================########
######               Segment A.9                       ########
######=================================================########

####### Hourly timeseries (load, hydro, solar, wind, reserve)
    
    # load (hourly)
    f.write('param:' + '\t' + 'SimDemand:=' + '\n')      
    for z in all_nodes:
        for h in range(0,len(df_load)):
            f.write(z + '\t' + str(h+1) + '\t' + str(df_load.loc[h,z]) + '\n')
    f.write(';\n\n')
    
    print('load')
    
    # wind and solar (hourly)
    f.write('param:' + '\t' + 'SimSolar:=' + '\n')
    s_gens = df_solar.columns
    for z in s_gens:
        for h in range(0,len(df_solar)):
            f.write(z + '_SOLAR' + '\t' + str(h+1) + '\t' + str(df_solar.loc[h,z]) + '\n')
    f.write(';\n\n')
    
    print('solar')
    
    f.write('param:' + '\t' + 'SimWind:=' + '\n')
    w_gens = df_wind.columns
    for z in w_gens:
        for h in range(0,len(df_wind)):
            f.write(z + '_WIND' + '\t' + str(h+1) + '\t' + str(df_wind.loc[h,z]) + '\n')
    f.write(';\n\n')
    
    print('wind')
    
    # hydro (daily)
    f.write('param:' + '\t' + 'SimHydro_MAX:=' + '\n')
    h_gens = df_hydro_MAX.columns      
    for z in h_gens:
        for h in range(0,len(df_hydro_MAX)): 
        # for h in range(0,240):
            f.write(z + '_HYDRO' + '\t' + str(h+1) + '\t' + str(df_hydro_MAX.loc[h,z]) + '\n')
    f.write(';\n\n')

    # hydro (daily)
    f.write('param:' + '\t' + 'SimHydro_MIN:=' + '\n')
    h_gens = df_hydro_MIN.columns      
    for z in h_gens:
        for h in range(0,len(df_hydro_MIN)): 
        # for h in range(0,240):
            f.write(z + '_HYDRO' + '\t' + str(h+1) + '\t' + str(df_hydro_MIN.loc[h,z]) + '\n')
    f.write(';\n\n')
    
    # hydro (daily)
    f.write('param:' + '\t' + 'SimHydro_TOTAL:=' + '\n')
    h_gens = df_hydro_TOTAL.columns      
    for z in h_gens:
        for h in range(0,len(df_hydro_MAX)): 
        # for h in range(0,240):
            f.write(z + '_HYDRO' + '\t' + str(h+1) + '\t' + str(df_hydro_TOTAL.loc[h,z]) + '\n')
    f.write(';\n\n')
    
    print('hydro')

####### Nodal must run
     
    f.write('param:' + '\t' + 'Must:=' + '\n')
    for z in all_nodes:
        if z in h3:
            f.write(z + '\t' + str(df_must.loc[0,z]) + '\n')
        else:
            f.write(z + '\t' + str(0) + '\n')
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
    # f.write('param' + '\t' + 'SimReserves:=' + '\n')
    # # for h in range(0,240):
    # for h in range(0,len(df_load)):
    #         f.write(str(h+1) + '\t' + str(df_reserves.loc[h,'Reserve']) + '\n')
    # f.write(';\n\n')
    
    # print('time series')
    

###### Maps
    
    f.write('param BustoUnitMap:' +'\n')
    f.write('\t')

    for j in df_bustounitmap.columns:
        if j!= 'name':
            f.write(j + '\t')
    f.write(':=' + '\n')
    for i in range(0,len(df_bustounitmap)):   
        for j in df_bustounitmap.columns:
            f.write(str(df_bustounitmap.loc[i,j]) + '\t')
        f.write('\n')
    f.write(';\n\n')
    
    print('Bus to units')


    f.write('param LinetoBusMap:' +'\n')
    f.write('\t')

    for j in df_linetobusmap.columns:
        if j!= 'line':
            f.write(j + '\t')
    f.write(':=' + '\n')
    for i in range(0,len(df_linetobusmap)):   
        for j in df_linetobusmap.columns:
            f.write(str(df_linetobusmap.loc[i,j]) + '\t')
        f.write('\n')
    f.write(';\n\n')
    
    print('line to bus')
    
    #BA to BA exchange matrix
    f.write('param ExchangeMap:' +'\n')
    f.write('\t')

    for j in BA_to_BA_transmission_matrix.columns:
        if j!= 'Exchange':
            f.write(j + '\t')
    f.write(':=' + '\n')
    for i in range(0,len(BA_to_BA_transmission_matrix)):   
        for j in BA_to_BA_transmission_matrix.columns:
            f.write(str(BA_to_BA_transmission_matrix.loc[i,j]) + '\t')
        f.write('\n')
    f.write(';\n\n')
    
######=================================================########
######               Segment A.10                       ########
######=================================================########

####### Daily fuel prices

    f.write('param:' + '\t' +'SimFuelPrice:=' + '\n')      
    for z in all_thermals:
        for d in range(0,int(SimHours/24)): 
            f.write(z + '\t' + str(d+1) + '\t' + str(df_fuel.loc[d,z]) + '\n')
    f.write(';\n\n')
    
    print('fuel prices')


print ('Complete:',data_name)
