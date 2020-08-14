# coding: utf-8
from __future__ import division # convert int or long division arguments to floating point values before division
from pyomo.environ import *
from pyomo.opt import SolverFactory
import itertools


model = AbstractModel()


######=================================================########
######               Segment B.1                       ########
######=================================================########

### Generators by fuel-type
model.Coal = Set()
model.Oil = Set()
model.Gas = Set()
model.Slack = Set()
model.Hydro = Set()
model.Must = Set()

#all generators
model.Generators = model.Coal | model.Oil | model.Gas | model.Slack | model.Hydro | model.Must


###Allocate generators that will ensure minimum reserves
model.ResGenerators = model.Coal | model.Oil | model.Gas


######=================================================########
######               Segment B.2                       ########
######=================================================########

### Nodal sets
model.nodes = Set()
model.sources = Set(within=model.nodes)
model.sinks = Set(within=model.nodes)

######=================================================########
######               Segment B.3                       ########
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
######               Segment B.4                       ########
######=================================================########

######==== Transmission line parameters =======#######
model.linemva = Param(model.sources, model.sinks)
model.linesus = Param(model.sources, model.sinks)

### Transmission Loss as a %discount on production
model.TransLoss = Param(within=NonNegativeReals)

### Maximum line-usage as a percent of line-capacity
model.n1criterion = Param(within=NonNegativeReals)

### Minimum spinning reserve as a percent of total reserve
model.spin_margin = Param(within=NonNegativeReals)


######=================================================########
######               Segment B.5                       ########
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
model.ramp_periods = RangeSet(2,24)

######=================================================########
######               Segment B.6                       ########
######=================================================########

#Demand over simulation period
model.SimDemand = Param(model.nodes*model.SH_periods, within=NonNegativeReals)
#Horizon demand
model.HorizonDemand = Param(model.nodes*model.hh_periods,within=NonNegativeReals,mutable=True)

#Reserve for the entire system
model.SimReserves = Param(model.SH_periods, within=NonNegativeReals)
model.HorizonReserves = Param(model.hh_periods, within=NonNegativeReals,mutable=True)

##Variable resources over simulation period
model.SimHydro = Param(model.Hydro, model.SH_periods, within=NonNegativeReals)
##model.SimSolar = Param(model.s_nodes, model.SH_periods, within=NonNegativeReals)
##model.SimWind = Param(model.w_nodes, model.SH_periods, within=NonNegativeReals)

#Variable resources over horizon
model.HorizonHydro = Param(model.Hydro,model.hh_periods,within=NonNegativeReals,mutable=True)
##model.HorizonSolar = Param(model.s_nodes,model.hh_periods,within=NonNegativeReals,mutable=True)
##model.HorizonWind = Param(model.w_nodes,model.hh_periods,within=NonNegativeReals,mutable=True)

##Initial conditions
model.ini_on = Param(model.Generators, within=Binary, initialize=0,mutable=True) 
model.ini_mwh = Param(model.Generators,initialize=0,mutable=True)

model.gen_mat = Param(model.Generators,model.nodes,within=Binary)


######=================================================########
######               Segment B.7                       ########
######=================================================########

######=======================Decision variables======================########
##Amount of day-ahead energy generated by each generator at each hour
model.mwh = Var(model.Generators,model.HH_periods, within=NonNegativeReals,initialize=0)

# #1 if unit is on in hour i, otherwise 0
# model.on = Var(model.Generators,model.HH_periods, within=Binary, initialize=0)

# #1 if unit is switching on in hour i, otherwise 0
# model.switch = Var(model.Generators,model.HH_periods, within=Binary,initialize=0)

# #Amount of spining reserve offered by an unit in each hour
# model.srsv = Var(model.Generators,model.HH_periods, within=NonNegativeReals,initialize=0)

# #Amount of non-sping reserve offered by an unit in each hour
# model.nrsv = Var(model.Generators,model.HH_periods, within=NonNegativeReals,initialize=0)

###dispatch of solar-power in each hour
##model.solar = Var(model.s_nodes,model.HH_periods,within=NonNegativeReals)
##
###dispatch of wind-power in each hour
##model.wind = Var(model.w_nodes,model.HH_periods,within=NonNegativeReals)

#Voltage angle at each node in each hour
model.vlt_angle = Var(model.nodes,model.HH_periods,bounds = (-3.14,3.14), initialize=0)



######=================================================########
######               Segment B.8                       ########
######=================================================########

######================Objective function=============########

def SysCost(model):
    # fixed = sum(model.maxcap[j]*model.fix_om[j]*model.on[j,i] for i in model.hh_periods for j in model.Generators)
    # starts = sum(model.maxcap[j]*model.st_cost[j]*model.switch[j,i] for i in model.hh_periods for j in model.Generators)
    coal = sum(model.mwh[j,i]*(model.heat_rate[j]*2 + model.var_om[j]) for i in model.hh_periods for j in model.Coal)  
    oil = sum(model.mwh[j,i]*(model.heat_rate[j]*10 + model.var_om[j]) for i in model.hh_periods for j in model.Oil)
    gas = sum(model.mwh[j,i]*(model.heat_rate[j]*4.5 + model.var_om[j]) for i in model.hh_periods for j in model.Gas)
    hydro = sum(model.mwh[j,i]*(model.heat_rate[j] + model.var_om[j]) for i in model.hh_periods for j in model.Hydro)
    must_run = sum(model.mwh[j,i]*(model.heat_rate[j] + model.var_om[j]) for i in model.hh_periods for j in model.Must)    
    slack = sum(model.mwh[j,i]*model.heat_rate[j]*1000 for i in model.hh_periods for j in model.Slack)
    
    return coal +oil + gas + hydro + must_run + slack  ## fixed +starts 

model.SystemCost = Objective(rule=SysCost, sense=minimize)



######=================================================########
######               Segment B.9                      ########
######=================================================########

######========== Logical Constraint =========#############
#Switch is 1 if unit is turned on in current period
# def SwitchCon(model,j,i):
#     return model.switch[j,i] >= 1 - model.on[j,i-1] - (1 - model.on[j,i])
# model.SwitchConstraint = Constraint(model.Generators,model.hh_periods,rule = SwitchCon)


# ######========== Up/Down Time Constraint =========#############
# #Min Up time
# def MinUp(model,j,i,k):
#     if i > 0 and k > i and k < min(i+model.minup[j]-1,model.HorizonHours):
#         return model.on[j,i] - model.on[j,i-1] <= model.on[j,k]
#     else: 
#         return Constraint.Skip
# model.MinimumUp = Constraint(model.Generators,model.HH_periods,model.HH_periods,rule=MinUp)

# ##Min Down time
# def MinDown(model,j,i,k):
#     if i > 0 and k > i and k < min(i+model.mindn[j]-1,model.HorizonHours):
#         return model.on[j,i-1] - model.on[j,i] <= 1 - model.on[j,k]
#     else:
#         return Constraint.Skip
# model.MinimumDown = Constraint(model.Generators,model.HH_periods,model.HH_periods,rule=MinDown)


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
######               Segment B.10                      ########
######=================================================########

######=========== Capacity Constraints ============##########
#Constraints for Max & Min Capacity of dispatchable resources
# def MaxC(model,j,i):
#     return model.mwh[j,i]  <= model.on[j,i] * model.maxcap[j] 
# model.MaxCap= Constraint(model.Generators,model.hh_periods,rule=MaxC)

def MaxC(model,j,i):
    return model.mwh[j,i]  <=  model.maxcap[j] 
model.MaxCap= Constraint(model.Generators,model.hh_periods,rule=MaxC)


# def MinC(model,j,i):
#     return model.mwh[j,i] >= model.on[j,i] * model.mincap[j]
# model.MinCap= Constraint(model.Generators,model.hh_periods,rule=MinC)


#Max capacity constraints on domestic hydropower 
def HydroC(model,z,i):
    return model.mwh[z,i] <= model.HorizonHydro[z,i]  
model.HydroConstraint= Constraint(model.Hydro,model.hh_periods,rule=HydroC)

###Max capacity constraints on solar 
##def SolarC(model,z,i):
##    return model.solar[z,i] <= model.HorizonSolar[z,i]  
##model.SolarConstraint= Constraint(model.s_nodes,model.hh_periods,rule=SolarC)
##
###Max capacity constraints on wind
##def WindC(model,z,i):
##    return model.wind[z,i] <= model.HorizonWind[z,i]  
##model.WindConstraint= Constraint(model.w_nodes,model.hh_periods,rule=WindC)


######=================================================########
######               Segment B.11.1                    ########
######=================================================########

#########======================== Power balance in sub-station nodes 
def Nodal_Balance(model,z,i):
    demand = model.HorizonDemand[z,i]
    power_flow = 100*sum(model.linesus[z,k] * (model.vlt_angle[z,i] - model.vlt_angle[k,i]) for k in model.sinks)   
    gen = sum(model.mwh[j,i]*model.gen_mat[j,z] for j in model.Generators)    
    return power_flow + demand <= (1 - model.TransLoss)*gen

model.Node_Constraint = Constraint(model.nodes,model.hh_periods,rule=Nodal_Balance)

####=== Reference Node =====#####
def ref_node(model,i):
    return model.vlt_angle['HOOVER_20',i] == 0
model.Ref_NodeConstraint= Constraint(model.hh_periods,rule= ref_node)


######========== Transmission Capacity Constraints (N-1 Criterion) =========#############
def MaxLine(model,s,k,i):
    if model.linemva[s,k] > 0:
        return (model.n1criterion) * model.linemva[s,k] >= model.linesus[s,k] * (model.vlt_angle[s,i] - model.vlt_angle[k,i])
    else:
        return Constraint.Skip
model.MaxLineConstraint= Constraint(model.sources,model.sinks,model.hh_periods,rule=MaxLine)

def MinLine(model,s,k,i):
    if model.linemva[s,k] > 0:
        return (-model.n1criterion) * model.linemva[s,k] <= model.linesus[s,k] * (model.vlt_angle[s,i] - model.vlt_angle[k,i])
    else:
        return Constraint.Skip
model.MinLineConstraint= Constraint(model.sources,model.sinks,model.hh_periods,rule=MinLine)



######=================================================########
######               Segment B.13                      ########
######=================================================########

######===================Reserve and zero-sum constraints ==================########

# ##System Reserve Requirement
# def SysReserve(model,i):
#     return sum(model.srsv[j,i] for j in model.ResGenerators) + sum(model.nrsv[j,i] for j in model.ResGenerators) >= model.HorizonReserves[i]
# model.SystemReserve = Constraint(model.hh_periods,rule=SysReserve)

# ##Spinning Reserve Requirement
# def SpinningReq(model,i):
#     return sum(model.srsv[j,i] for j in model.ResGenerators) >= model.spin_margin * model.HorizonReserves[i] 
# model.SpinReq = Constraint(model.hh_periods,rule=SpinningReq)           

# ##Spinning reserve can only be offered by units that are online
# def SpinningReq2(model,j,i):
#     return model.srsv[j,i] <= model.on[j,i]*model.maxcap[j]
# model.SpinReq2= Constraint(model.Generators,model.hh_periods,rule=SpinningReq2) 

# ##Non-Spinning reserve can only be offered by units that are offline
# def NonSpinningReq(model,j,i):
#     return model.nrsv[j,i] <= (1 - model.on[j,i])*model.maxcap[j]
# model.NonSpinReq= Constraint(model.Generators,model.hh_periods,rule=NonSpinningReq)


# ######========== Zero Sum Constraint =========#############
# def ZeroSum(model,j,i):
#     return model.mwh[j,i] + model.srsv[j,i] + model.nrsv[j,i] <= model.maxcap[j]
# model.ZeroSumConstraint=Constraint(model.Generators,model.hh_periods,rule=ZeroSum)


######======================================#############
######==========        End        =========#############
######=======================================############

