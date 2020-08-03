# coding: utf-8
from __future__ import division # convert int or long division arguments to floating point values before division
from pyomo.environ import *
from pyomo.opt import SolverFactory
import itertools

gd_nodes = ['GS1','GS2','GS3','GS5','GS7','KPCM','KPT','SHV','SRP'] ##Dispatchables with demand
gn_nodes = ['STH','Thai','Viet'] ##Dispatchables without demand

g_nodes = gd_nodes + gn_nodes 
print ('Gen_Nodes:',len(g_nodes))


model = AbstractModel()


######=================================================########
######               Segment B.1                       ########
######=================================================########

## string indentifiers for the set of generators (in the order of g_nodes list)
model.GD1Gens =  Set()
model.GD2Gens =  Set()
model.GD3Gens =  Set()
model.GD4Gens =  Set()
model.GD5Gens =  Set()
model.GD6Gens =  Set()
model.GD7Gens =  Set()
model.GD8Gens =  Set()
model.GD9Gens =  Set()

model.GN1Gens =  Set()
model.GN2Gens =  Set()
model.GN3Gens =  Set()


model.Generators = model.GD1Gens | model.GD2Gens | model.GD3Gens | model.GD4Gens | \
                   model.GD5Gens | model.GD6Gens | model.GD7Gens | model.GD8Gens | \
                   model.GD9Gens | model.GN1Gens | model.GN2Gens | model.GN3Gens
                   


######=================================================########
######               Segment B.2                       ########
######=================================================########

### Generators by fuel-type
model.Coal = Set()
model.Oil = Set()
model.Slack = Set()
model.Gas = Set()
mode.Hydro = Set()

######=================================================########
######               Segment B.3                       ########
######=================================================########

### Nodal sets
model.nodes = Set()
model.sources = Set(within=model.nodes)
model.sinks = Set(within=model.nodes)


model.s_nodes = Set() # nodes with solar generation
model.h_nodes = Set() # nodes with hydro generation
model.d_nodes = Set() # nodes with demand
model.gd_nodes = Set() # nodes with generation and demand
model.gn_nodes = Set() # nodes with generation but *no* demand
model.td_nodes = Set() # nodes with demand but *no* generation 
model.tn_nodes = Set() # nodes with *no* demand and *no* generation



######=================================================########
######               Segment B.4                       ########
######=================================================########

#####==== Parameters for dispatchable resources ===####

#Generator type
model.typ = Param(model.Generators)

#Node name
model.node = Param(model.Generators)

#Max capacity
model.maxcap = Param(model.Generators)

#Min capacity
model.mincap = Param(model.Generators)

#Heat rate
model.heat_rate = Param(model.Generators)

#Variable O&M
model.var_om = Param(model.Generators)

#Fixed O&M cost
model.fix_om  = Param(model.Generators)

#Start cost
model.st_cost = Param(model.Generators)

#Ramp rate
model.ramp  = Param(model.Generators)

#Minimun up time
model.minup = Param(model.Generators)

#Minmun down time
model.mindn = Param(model.Generators)


######=================================================########
######               Segment B.5                       ########
######=================================================########

######==== Transmission line parameters =======#######
model.linemva = Param(model.sources, model.sinks)
model.linesus = Param(model.sources, model.sinks)

### Transmission Loss as a %discount on production
model.TransLoss = Param(within=NonNegativeReals)


######=================================================########
######               Segment B.6                       ########
######=================================================########

######===== Parameters/initial_conditions to run simulation ======####### 
## Full range of time series information
model.SimHours = Param(within=PositiveIntegers)
model.SH_periods = RangeSet(1,model.SimHours+1)
model.SimDays = Param(within=PositiveIntegers)
model.SD_periods = RangeSet(1,model.SimDays+1)

# Operating horizon information 
model.HorizonHours = Param(within=PositiveIntegers)
model.HH_periods = RangeSet(0,model.HorizonHours)
model.hh_periods = RangeSet(1,model.HorizonHours)
model.ramp_periods = RangeSet(2,model.HorizonHours)

######=================================================########
######               Segment B.7                       ########
######=================================================########

#Demand over simulation period
model.SimDemand = Param(model.d_nodes*model.SH_periods, within=NonNegativeReals)

#Horizon demand
model.HorizonDemand = Param(model.d_nodes*model.hh_periods,within=NonNegativeReals,mutable=True)

#Reserve for the entire system
model.SimReserves = Param(model.SH_periods, within=NonNegativeReals)
model.HorizonReserves = Param(model.hh_periods, within=NonNegativeReals,mutable=True)

##Variable resources over simulation period
model.SimHydro = Param(model.h_nodes, model.SH_periods, within=NonNegativeReals)
model.SimSolar = Param(model.s_nodes, model.SH_periods, within=NonNegativeReals)

#Variable resources over horizon
model.HorizonHydro = Param(model.h_nodes,model.hh_periods,within=NonNegativeReals,mutable=True)
model.HorizonSolar = Param(model.s_nodes,model.hh_periods,within=NonNegativeReals,mutable=True)

##Initial conditions
model.ini_on = Param(model.Generators, within=Binary, initialize=0,mutable=True) 
model.ini_mwh = Param(model.Generators,initialize=0,mutable=True)



######=================================================########
######               Segment B.8                       ########
######=================================================########

######=======================Decision variables======================########

##Amount of day-ahead energy generated by each generator at each hour
model.mwh_1 = Var(model.Generators,model.HH_periods, within=NonNegativeReals,initialize=0)
model.mwh_2 = Var(model.Generators,model.HH_periods, within=NonNegativeReals,initialize=0)
model.mwh_3 = Var(model.Generators,model.HH_periods, within=NonNegativeReals,initialize=0)

#1 if unit is on in hour i, otherwise 0
model.on = Var(model.Generators,model.HH_periods, within=Binary, initialize=0)

#1 if unit is switching on in hour i, otherwise 0
model.switch = Var(model.Generators,model.HH_periods, within=Binary,initialize=0)

#Amount of non-sping reserve offered by an unit in each hour
model.nrsv = Var(model.Generators,model.HH_periods, within=NonNegativeReals,initialize=0)

#dispatch of hydropower from each domestic dam in each hour
model.hydro = Var(model.h_nodes,model.HH_periods,within=NonNegativeReals)

##dispatch of solar-power in each hour
model.solar = Var(model.s_nodes,model.HH_periods,within=NonNegativeReals)

#Voltage angle at each node in each hour
model.vlt_angle = Var(model.nodes,model.HH_periods)


######=================================================########
######               Segment B.9                       ########
######=================================================########

######=============Objective function==================########

def SysCost(model):
    
    fixed = sum(model.fix_om[j]*model.on[j,i] for i in model.hh_periods for j in model.Generators)
    
    starts = sum(model.st_cost[j]*model.switch[j,i] for i in model.hh_periods for j in model.Generators)
    
    coal1 = sum(model.mwh_1[j,i]*(model.seg1[j]*2 + model.var_om[j]) for i in model.hh_periods for j in model.Coal)  
    coal2 = sum(model.mwh_2[j,i]*(model.seg2[j]*2 + model.var_om[j]) for i in model.hh_periods for j in model.Coal)  
    coal3 = sum(model.mwh_3[j,i]*(model.seg3[j]*2 + model.var_om[j]) for i in model.hh_periods for j in model.Coal)  

    gas1 = sum(model.mwh_1[j,i]*(model.seg1[j]*5.0 + model.var_om[j]) for i in model.hh_periods for j in model.Gas)  
    gas2 = sum(model.mwh_2[j,i]*(model.seg2[j]*5.0 + model.var_om[j]) for i in model.hh_periods for j in model.Gas)  
    gas3 = sum(model.mwh_3[j,i]*(model.seg3[j]*5.0 + model.var_om[j]) for i in model.hh_periods for j in model.Gas)  

    oil1 = sum(model.mwh_1[j,i]*(model.seg1[j]*12 + model.var_om[j]) for i in model.hh_periods for j in model.Oil)   
    oil2 = sum(model.mwh_2[j,i]*(model.seg2[j]*12 + model.var_om[j]) for i in model.hh_periods for j in model.Oil)   
    oil3 = sum(model.mwh_3[j,i]*(model.seg3[j]*12 + model.var_om[j]) for i in model.hh_periods for j in model.Oil)   

    slack1 = sum(model.mwh_1[j,i]*model.seg1[j]*1000 for i in model.hh_periods for j in model.Slack)
    slack2 = sum(model.mwh_2[j,i]*model.seg2[j]*1000 for i in model.hh_periods for j in model.Slack)
    slack3 = sum(model.mwh_3[j,i]*model.seg3[j]*1000 for i in model.hh_periods for j in model.Slack)
    
# add gas
    
    return fixed + starts + coal1 + coal2 + coal3 + oil1 + oil2 + oil3 + gas1 + gas2 + gas3 + slack1 + slack2 + slack3  

model.SystemCost = Objective(rule=SysCost, sense=minimize)



######=================================================########
######               Segment B.10                      ########
######=================================================########

######========== Logical Constraint =========#############
##Switch is 1 if unit is turned on in current period
def SwitchCon(model,j,i):
    return model.switch[j,i] >= 1 - model.on[j,i-1] - (1 - model.on[j,i])
model.SwitchConstraint = Constraint(model.Generators,model.hh_periods,rule = SwitchCon)


######========== Up/Down Time Constraint =========#############
##Min Up time
def MinUp(model,j,i,k):
    if i > 0 and k > i and k < min(i+model.minup[j]-1,model.HorizonHours):
        return model.on[j,i] - model.on[j,i-1] <= model.on[j,k]
    else: 
        return Constraint.Skip
model.MinimumUp = Constraint(model.Generators,model.HH_periods,model.HH_periods,rule=MinUp)

##Min Down time
def MinDown(model,j,i,k):
   if i > 0 and k > i and k < min(i+model.mindn[j]-1,model.HorizonHours):
       return model.on[j,i-1] - model.on[j,i] <= 1 - model.on[j,k]
   else:
       return Constraint.Skip
model.MinimumDown = Constraint(model.Generators,model.HH_periods,model.HH_periods,rule=MinDown)


######==========Ramp Rate Constraints =========#############
def Ramp1(model,j,i):
    a = model.mwh[j,i]
    b = model.mwh[j,i-1]
    return a - b <= model.ramp[j] 
model.RampCon1 = Constraint(model.Generators,model.ramp_periods,rule=Ramp1)

def Ramp2(model,j,i):
    a = model.mwh[j,i]
    b = model.mwh[j,i-1]
    return b - a <= model.ramp[j] 
model.RampCon2 = Constraint(model.Generators,model.ramp_periods,rule=Ramp2)


######=================================================########
######               Segment B.11                      ########
######=================================================########

######=========== Capacity Constraints ============##########
#Constraints for Max & Min Capacity of dispatchable resources
#derate factor can be below 1 for dry years, otherwise 1
def MaxC(model,j,i):
    return model.mwh_1[j,i] + model.mwh_2[j,i] + model.mwh_3[j,i]  <= model.on[j,i] * model.maxcap[j]
model.MaxCap= Constraint(model.Generators,model.hh_periods,rule=MaxC)

def MinC(model,j,i):
    return model.mwh_1[j,i] + model.mwh_2[j,i] + model.mwh_3[j,i] >= model.on[j,i] * model.mincap[j]
model.MinCap= Constraint(model.Generators,model.hh_periods,rule=MinC)

#Max capacity constraints on domestic hydropower 
def HydroC(model,z,i):
    return model.hydro[z,i] <= model.HorizonHydro[z,i]  
model.HydroConstraint= Constraint(model.h_nodes,model.hh_periods,rule=HydroC)

##Max capacity constraints on solar 
def SolarC(model,z,i):
    return model.solar[z,i] <= model.HorizonSolar[z,i]  
model.SolarConstraint= Constraint(model.s_nodes,model.hh_periods,rule=SolarC)

###Max capacity constraints on wind
##def WindC(model,z,i):
##    return model.wind[z,i] <= model.HorizonWind[z,i]  
##model.WindConstraint= Constraint(model.w_nodes,model.hh_periods,rule=WindC)



######=================================================########
######               Segment B.12.1                    ########
######=================================================########

######=================== Power balance in nodes of variable resources (without demand in this case) =================########

###Hydropower Plants
def HPnodes_Balance(model,z,i):
    dis_hydro = model.hydro[z,i]
    #demand = model.HorizonDemand[z,i]
    impedance = sum(model.linesus[z,k] * (model.vlt_angle[z,i] - model.vlt_angle[k,i]) for k in model.sinks)
    return (1 - model.TransLoss) * dis_hydro == impedance ##- demand
model.HPnodes_BalConstraint= Constraint(model.h_nodes,model.hh_periods,rule= HPnodes_Balance)

####Solar Plants
def Solarnodes_Balance(model,z,i):
    dis_solar = model.solar[z,i]
    impedance = sum(model.linesus[z,k] * (model.vlt_angle[z,i] - model.vlt_angle[k,i]) for k in model.sinks)
    return (1 - model.TransLoss) * dis_solar == impedance ##- demand
model.Solarnodes_BalConstraint= Constraint(model.s_nodes,model.hh_periods,rule= Solarnodes_Balance)

#######Wind Plants
##def Windnodes_Balance(model,z,i):
##    dis_wind = model.wind[z,i]
##    impedance = sum(model.linesus[z,k] * (model.vlt_angle[z,i] - model.vlt_angle[k,i]) for k in model.sinks)
##    return (1 - model.TransLoss) * dis_wind == impedance ##- demand
##model.Windnodes_BalConstraint= Constraint(model.w_nodes,model.hh_periods,rule= Windnodes_Balance)



######=================================================########
######               Segment B.12.2                    ########
######=================================================########

#########======================== Power balance in sub-station nodes (with/without demand) ====================#######
###With demand
def TDnodes_Balance(model,z,i):
    demand = model.HorizonDemand[z,i]
    impedance = sum(model.linesus[z,k] * (model.vlt_angle[z,i] - model.vlt_angle[k,i]) for k in model.sinks)   
    return - demand == impedance
model.TDnodes_BalConstraint= Constraint(model.td_nodes,model.hh_periods,rule= TDnodes_Balance)

###Without demand
def TNnodes_Balance(model,z,i):
    #demand = model.HorizonDemand[z,i]
    impedance = sum(model.linesus[z,k] * (model.vlt_angle[z,i] - model.vlt_angle[k,i]) for k in model.sinks)   
    return 0 == impedance
model.TNnodes_BalConstraint= Constraint(model.tn_nodes,model.hh_periods,rule= TNnodes_Balance)




######=================================================########
######               Segment B.12.3                    ########
######=================================================########

##########============ Power balance in nodes of dispatchable resources with demand ==============############
def GD1_Balance(model,i):
    gd = 1
    thermo = sum(model.mwh[j,i] for j in model.GD1Gens)
    demand = model.HorizonDemand[gd_nodes[gd-1],i]
    impedance = sum(model.linesus[gd_nodes[gd-1],k] * (model.vlt_angle[gd_nodes[gd-1],i] - model.vlt_angle[k,i]) for k in model.sinks)   
    return (1 - model.TransLoss) * thermo - demand == impedance
model.GD1_BalConstraint= Constraint(model.hh_periods,rule= GD1_Balance)

def GD2_Balance(model,i):
    gd = 2
    thermo = sum(model.mwh[j,i] for j in model.GD2Gens)
    demand = model.HorizonDemand[gd_nodes[gd-1],i]
    impedance = sum(model.linesus[gd_nodes[gd-1],k] * (model.vlt_angle[gd_nodes[gd-1],i] - model.vlt_angle[k,i]) for k in model.sinks)   
    return (1 - model.TransLoss) * thermo - demand == impedance
model.GD2_BalConstraint= Constraint(model.hh_periods,rule= GD2_Balance)

def GD3_Balance(model,i):
    gd = 3
    thermo = sum(model.mwh[j,i] for j in model.GD3Gens)
    demand = model.HorizonDemand[gd_nodes[gd-1],i]
    impedance = sum(model.linesus[gd_nodes[gd-1],k] * (model.vlt_angle[gd_nodes[gd-1],i] - model.vlt_angle[k,i]) for k in model.sinks)   
    return (1 - model.TransLoss) * thermo - demand == impedance
model.GD3_BalConstraint= Constraint(model.hh_periods,rule= GD3_Balance)

def GD4_Balance(model,i):
    gd = 4
    thermo = sum(model.mwh[j,i] for j in model.GD4Gens)
    demand = model.HorizonDemand[gd_nodes[gd-1],i]
    impedance = sum(model.linesus[gd_nodes[gd-1],k] * (model.vlt_angle[gd_nodes[gd-1],i] - model.vlt_angle[k,i]) for k in model.sinks)   
    return (1 - model.TransLoss) * thermo - demand == impedance
model.GD4_BalConstraint= Constraint(model.hh_periods,rule= GD4_Balance)

def GD5_Balance(model,i):
    gd = 5
    thermo = sum(model.mwh[j,i] for j in model.GD5Gens)
    demand = model.HorizonDemand[gd_nodes[gd-1],i]
    impedance = sum(model.linesus[gd_nodes[gd-1],k] * (model.vlt_angle[gd_nodes[gd-1],i] - model.vlt_angle[k,i]) for k in model.sinks)   
    return (1 - model.TransLoss) * thermo - demand == impedance
model.GD5_BalConstraint= Constraint(model.hh_periods,rule= GD5_Balance)

def GD6_Balance(model,i):
    gd = 6
    thermo = sum(model.mwh[j,i] for j in model.GD6Gens)
    demand = model.HorizonDemand[gd_nodes[gd-1],i]
    impedance = sum(model.linesus[gd_nodes[gd-1],k] * (model.vlt_angle[gd_nodes[gd-1],i] - model.vlt_angle[k,i]) for k in model.sinks)   
    return (1 - model.TransLoss) * thermo - demand == impedance
model.GD6_BalConstraint= Constraint(model.hh_periods,rule= GD6_Balance)

def GD7_Balance(model,i):
    gd = 7
    thermo = sum(model.mwh[j,i] for j in model.GD7Gens)
    demand = model.HorizonDemand[gd_nodes[gd-1],i]
    impedance = sum(model.linesus[gd_nodes[gd-1],k] * (model.vlt_angle[gd_nodes[gd-1],i] - model.vlt_angle[k,i]) for k in model.sinks)   
    return (1 - model.TransLoss) * thermo - demand == impedance
model.GD7_BalConstraint= Constraint(model.hh_periods,rule= GD7_Balance)

def GD8_Balance(model,i):
    gd = 8
    thermo = sum(model.mwh[j,i] for j in model.GD8Gens)
    demand = model.HorizonDemand[gd_nodes[gd-1],i]
    impedance = sum(model.linesus[gd_nodes[gd-1],k] * (model.vlt_angle[gd_nodes[gd-1],i] - model.vlt_angle[k,i]) for k in model.sinks)   
    return (1 - model.TransLoss) * thermo - demand == impedance
model.GD8_BalConstraint= Constraint(model.hh_periods,rule= GD8_Balance)

def GD9_Balance(model,i):
    gd = 9
    thermo = sum(model.mwh[j,i] for j in model.GD9Gens)
    demand = model.HorizonDemand[gd_nodes[gd-1],i]
    impedance = sum(model.linesus[gd_nodes[gd-1],k] * (model.vlt_angle[gd_nodes[gd-1],i] - model.vlt_angle[k,i]) for k in model.sinks)   
    return (1 - model.TransLoss) * thermo - demand == impedance
model.GD9_BalConstraint= Constraint(model.hh_periods,rule= GD9_Balance)



##########============ Power balance in nodes of dispatchable resources without demand ==============############
def GN1_Balance(model,i):
    gn = 1
    thermo = sum(model.mwh[j,i] for j in model.GN1Gens)    
    impedance = sum(model.linesus[gn_nodes[gn-1],k] * (model.vlt_angle[gn_nodes[gn-1],i] - model.vlt_angle[k,i]) for k in model.sinks)   
    return (1 - model.TransLoss) * thermo == impedance #- demand
model.GN1_BalConstraint= Constraint(model.hh_periods,rule= GN1_Balance)

def GN2_Balance(model,i):
    gn = 2
    thermo = sum(model.mwh[j,i] for j in model.GN2Gens)    
    impedance = sum(model.linesus[gn_nodes[gn-1],k] * (model.vlt_angle[gn_nodes[gn-1],i] - model.vlt_angle[k,i]) for k in model.sinks)   
    return (1 - model.TransLoss) * thermo == impedance #- demand
model.GN2_BalConstraint= Constraint(model.hh_periods,rule= GN2_Balance)

def GN3_Balance(model,i):
    gn = 3
    thermo = sum(model.mwh[j,i] for j in model.GN3Gens)    
    impedance = sum(model.linesus[gn_nodes[gn-1],k] * (model.vlt_angle[gn_nodes[gn-1],i] - model.vlt_angle[k,i]) for k in model.sinks)   
    return (1 - model.TransLoss) * thermo == impedance #- demand
model.GN3_BalConstraint= Constraint(model.hh_periods,rule= GN3_Balance)



######=================================================########
######               Segment B.13                    ########
######=================================================########

######==================Transmission  constraints==================########

####=== Reference Node =====#####
def ref_node(model,i):
    return model.vlt_angle['GS1',i] == 0
model.Ref_NodeConstraint= Constraint(model.hh_periods,rule= ref_node)


######========== Transmission Capacity Constraints (N-1 Criterion) =========#############
def MaxLine(model,s,k,i):
    if model.linemva[s,k] > 0:
        return (0.75) * model.linemva[s,k] >= model.linesus[s,k] * (model.vlt_angle[s,i] - model.vlt_angle[k,i])
    else:
        return Constraint.Skip
model.MaxLineConstraint= Constraint(model.sources,model.sinks,model.hh_periods,rule=MaxLine)

def MinLine(model,s,k,i):
    if model.linemva[s,k] > 0:
        return (-0.75) * model.linemva[s,k] <= model.linesus[s,k] * (model.vlt_angle[s,i] - model.vlt_angle[k,i])
    else:
        return Constraint.Skip
model.MinLineConstraint= Constraint(model.sources,model.sinks,model.hh_periods,rule=MinLine)



######=================================================########
######               Segment B.14                      ########
######=================================================########

######===================Reserve and zero-sum constraints ==================########

##System Reserve Requirement
def SysReserve(model,i):
    return sum(model.srsv[j,i] for j in model.Oil_st) + sum(model.srsv[j,i] for j in model.Coal_st)\
           + sum(model.srsv[j,i] for j in model.Oil_ic)\
           + sum(model.nrsv[j,i] for j in model.Oil_st) + sum(model.nrsv[j,i] for j in model.Coal_st)\
           + sum(model.nrsv[j,i] for j in model.Oil_ic) >= model.HorizonReserves[i]
model.SystemReserve = Constraint(model.hh_periods,rule=SysReserve)

##Spinning Reserve Requirement
def SpinningReq(model,i):
    return sum(model.srsv[j,i] for j in model.Oil_st) + sum(model.srsv[j,i] for j in model.Coal_st)\
           + sum(model.srsv[j,i] for j in model.Oil_ic)>= 0.5 * model.HorizonReserves[i] 
model.SpinReq = Constraint(model.hh_periods,rule=SpinningReq)           

##Spinning reserve can only be offered by units that are online
def SpinningReq2(model,j,i):
    return model.srsv[j,i] <= model.on[j,i]*model.maxcap[j] *model.deratef[j]
model.SpinReq2= Constraint(model.Generators,model.hh_periods,rule=SpinningReq2) 

##Non-Spinning reserve can only be offered by units that are offline
def NonSpinningReq(model,j,i):
    return model.nrsv[j,i] <= (1 - model.on[j,i])*model.maxcap[j] *model.deratef[j]
model.NonSpinReq= Constraint(model.Generators,model.hh_periods,rule=NonSpinningReq)


######========== Zero Sum Constraint =========#############
def ZeroSum(model,j,i):
    return model.mwh[j,i] + model.srsv[j,i] + model.nrsv[j,i] <= model.maxcap[j]
model.ZeroSumConstraint=Constraint(model.Generators,model.hh_periods,rule=ZeroSum)


######======================================#############
######==========        End        =========#############
######=======================================############

