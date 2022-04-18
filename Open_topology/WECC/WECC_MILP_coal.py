# coding: utf-8
from pyomo.environ import *
from pyomo.environ import value
import numpy as np

model = AbstractModel()

######=================================================########
######               Segment B.1                       ########
######=================================================########

### Generators by fuel-type
model.Coal = Set()
model.Oil = Set()
model.Gas = Set()
model.Hydro = Set()
model.Solar = Set()
model.Wind = Set()

#all generators
model.Thermal = model.Coal | model.Oil | model.Gas
model.Generators = model.Thermal | model.Hydro | model.Solar | model.Wind
model.Dispatchable = model.Hydro | model.Oil | model.Gas

# transmission sets
model.lines = Set() 
model.buses = Set()

# BA to BA transmission sets
model.exchanges = Set() 

#Generator type
model.typ = Param(model.Generators,within=Any)

#Node name
model.node = Param(model.Generators,within=Any)

#Max capacity
model.maxcap = Param(model.Generators)

#Min capacity
model.mincap = Param(model.Generators)

#Heat rate
model.heat_rate = Param(model.Generators)

#Variable O&M
model.var_om = Param(model.Generators)

#Fixed O&M cost
model.no_load  = Param(model.Generators)

#Start cost
model.st_cost = Param(model.Generators)

#Ramp rate
model.ramp  = Param(model.Generators)

#Minimun up time
model.minup = Param(model.Generators)

#Minimun down time
model.mindn = Param(model.Generators)

#transmission parameters
model.Reactance = Param(model.lines)
model.FlowLim = Param(model.lines)
model.LinetoBusMap=Param(model.lines,model.buses)
model.BustoUnitMap=Param(model.Generators,model.buses)
model.ExchangeHurdle=Param(model.exchanges)
model.ExchangeMap=Param(model.exchanges,model.lines, mutable=True)

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
model.SimDemand = Param(model.buses*model.SH_periods, within=NonNegativeReals)

#Horizon demand
model.HorizonDemand = Param(model.buses*model.hh_periods,within=NonNegativeReals,mutable=True)

#Reserve for the entire system
# model.SimReserves = Param(model.SH_periods, within=NonNegativeReals)
# model.HorizonReserves = Param(model.hh_periods, within=NonNegativeReals,mutable=True)

##Variable resources over simulation period
model.SimHydro_MAX = Param(model.Hydro, model.SH_periods, within=NonNegativeReals)
model.SimHydro_MIN = Param(model.Hydro, model.SH_periods, within=NonNegativeReals)
model.SimHydro_TOTAL = Param(model.Hydro, model.SH_periods, within=NonNegativeReals)
model.SimSolar = Param(model.Solar, model.SH_periods, within=NonNegativeReals)
model.SimWind = Param(model.Wind, model.SH_periods, within=NonNegativeReals)

#Variable resources over horizon
model.HorizonHydro_MAX = Param(model.Hydro,within=NonNegativeReals,mutable=True)
model.HorizonHydro_MIN = Param(model.Hydro,within=NonNegativeReals,mutable=True)
model.HorizonHydro_TOTAL = Param(model.Hydro,within=NonNegativeReals,mutable=True)
model.HorizonSolar = Param(model.Solar,model.hh_periods,within=NonNegativeReals,mutable=True)
model.HorizonWind = Param(model.Wind,model.hh_periods,within=NonNegativeReals,mutable=True)

#Must run resources
model.Must = Param(model.buses,within=NonNegativeReals)

#Fuel prices over simulation period
model.SimFuelPrice = Param(model.Thermal,model.SD_periods, within=NonNegativeReals)
model.FuelPrice = Param(model.Thermal,within = NonNegativeReals, mutable=True)

######=================================================########
######               Segment B.7                       ########
######=================================================########

######=======================Decision variables======================########
##Amount of day-ahead energy generated by each generator at each hour
model.mwh = Var(model.Generators,model.HH_periods, within=NonNegativeReals,initialize=0)

#1 if unit is on in hour i, otherwise 0
model.on = Var(model.Coal,model.HH_periods, within=Binary, initialize=0)

#1 if unit is switching on in hour i, otherwise 0
model.switch = Var(model.Coal,model.HH_periods, within=Binary,initialize=0)

# #Amount of spining reserve offered by an unit in each hour
# model.srsv = Var(model.Generators,model.HH_periods, within=NonNegativeReals,initialize=0)

# #Amount of non-sping reserve offered by an unit in each hour
# model.nrsv = Var(model.Generators,model.HH_periods, within=NonNegativeReals,initialize=0)

# slack variables
model.S = Var(model.hh_periods, within=NonNegativeReals,initialize=0)


# transmission line variables 
model.Flow= Var(model.lines,model.hh_periods,initialize=0)
model.Theta= Var(model.buses,model.hh_periods)


######=================================================########
######               Segment B.8                       ########
######=================================================########

######================Objective function=============########

def SysCost(model):
    fixed = sum(model.no_load[j]*model.on[j,i] for i in model.hh_periods for j in model.Coal)
    starts = sum(model.st_cost[j]*model.switch[j,i] for i in model.hh_periods for j in model.Coal)
    gen = sum(model.mwh[j,i]*(model.heat_rate[j]*model.FuelPrice[j] + model.var_om[j]) for i in model.hh_periods for j in model.Thermal)  
    slack = sum(model.S[i]*1000 for i in model.hh_periods)
    hydro_cost = sum(model.mwh[j,i]*0.01 for i in model.hh_periods for j in model.Hydro)
    wind_cost = sum(model.mwh[j,i]*0.01 for i in model.hh_periods for j in model.Wind)
    solar_cost = sum(model.mwh[j,i]*0.01 for i in model.hh_periods for j in model.Solar)
    exchange_cost = sum(model.Flow[l,i]*model.ExchangeMap[k,l]*model.ExchangeHurdle[k] for l in model.lines for i in model.hh_periods for k in model.exchanges)

    return fixed + starts + gen + slack + hydro_cost + wind_cost + solar_cost + exchange_cost
    
model.SystemCost = Objective(rule=SysCost, sense=minimize)


######=================================================########
######               Segment B.9                      ########
######=================================================########

#####========== Logical Constraint =========#############
# Switch is 1 if unit is turned on in current period
def SwitchCon(model,j,i):
    return model.switch[j,i] >= 1 - model.on[j,i-1] - (1 - model.on[j,i])
model.SwitchConstraint = Constraint(model.Coal,model.hh_periods,rule = SwitchCon)


######========== Up/Down Time Constraint =========#############
#Min Up time
def MinUp(model,j,i,k):
    if i > 0 and k > i and k < min(i+model.minup[j]-1,model.HorizonHours):
        return model.on[j,i] - model.on[j,i-1] <= model.on[j,k]
    else: 
        return Constraint.Skip
model.MinimumUp = Constraint(model.Coal,model.HH_periods,model.HH_periods,rule=MinUp)

##Min Down time
def MinDown(model,j,i,k):
    if i > 0 and k > i and k < min(i+model.mindn[j]-1,model.HorizonHours):
        return model.on[j,i-1] - model.on[j,i] <= 1 - model.on[j,k]
    else:
        return Constraint.Skip
model.MinimumDown = Constraint(model.Coal,model.HH_periods,model.HH_periods,rule=MinDown)


#####==========Ramp Rate Constraints =========#############
def Ramp1(model,j,i):
    a = model.mwh[j,i]
    b = model.mwh[j,i-1]
    return a - b <= model.ramp[j] 
model.RampCon1 = Constraint(model.Thermal,model.ramp_periods,rule=Ramp1)

def Ramp2(model,j,i):
    a = model.mwh[j,i]
    b = model.mwh[j,i-1]
    return b - a <= model.ramp[j] 
model.RampCon2 = Constraint(model.Thermal,model.ramp_periods,rule=Ramp2)


######=================================================########
######               Segment B.10                      ########
######=================================================########

#####=========== Capacity Constraints ============##########
# Constraints for Max & Min Capacity of dispatchable resources
def MaxCC(model,j,i):
    return model.mwh[j,i]  <= model.on[j,i] * model.maxcap[j] 
model.MaxCapC= Constraint(model.Coal,model.hh_periods,rule=MaxCC)


def MinC(model,j,i):
    return model.mwh[j,i] >= model.on[j,i] * model.mincap[j]
model.MinCap= Constraint(model.Coal,model.hh_periods,rule=MinC)

#####=========== Capacity Constraints ============##########
# Constraints for Max & Min Capacity of dispatchable resources
def MaxC(model,j,i):
    return model.mwh[j,i]  <= model.maxcap[j] 
model.MaxCap= Constraint(model.Dispatchable,model.hh_periods,rule=MaxC)


#Max production constraints on domestic hydropower 
def HydroP(model,j,i):
    daily = sum(model.mwh[j,i] for i in model.hh_periods)
    return  daily <= model.HorizonHydro_TOTAL[j]    
model.HydroPROD= Constraint(model.Hydro,model.hh_periods,rule=HydroP)

#Max capacity constraints on domestic hydropower 
def HydroX(model,j,i):
    return  model.mwh[j,i] <= model.HorizonHydro_MAX[j]    
model.HydroMAX= Constraint(model.Hydro,model.hh_periods,rule=HydroX)

#Max capacity constraints on domestic hydropower 
def HydroM(model,j,i):
    return  model.mwh[j,i] >= model.HorizonHydro_MIN[j]    
model.HydroMIN= Constraint(model.Hydro,model.hh_periods,rule=HydroM)


#Max capacity constraints on solar
def SolarC(model,j,i): 
    return  model.mwh[j,i] <= model.HorizonSolar[j,i]    
model.SolarConstraint= Constraint(model.Solar,model.hh_periods,rule=SolarC)

#Max capacity constraints on wind
def WindC(model,j,i): 
    return  model.mwh[j,i] <= model.HorizonWind[j,i]    
model.WindConstraint= Constraint(model.Wind,model.hh_periods,rule=WindC)


######=================================================########
######               Segment B.11.1                    ########
######=================================================########

def Nodal_Balance(model,z,i):
    power_flow = sum(model.Flow[l,i]*model.LinetoBusMap[l,z] for l in model.lines)   
    gen = sum(model.mwh[j,i]*model.BustoUnitMap[j,z] for j in model.Generators)    
    slack = model.S[i]
    must_run = model.Must[z]
    return gen + slack + must_run - power_flow == model.HorizonDemand[z,i] 
model.Node_Constraint = Constraint(model.buses,model.hh_periods,rule=Nodal_Balance)

def Flow_line(model,l,i):
    value = sum(model.Theta[z,i]*model.LinetoBusMap[l,z] for z in model.buses)
    return  100*value == model.Flow[l,i]*model.Reactance[l]
model.FlowL_Constraint = Constraint(model.lines,model.hh_periods,rule=Flow_line)

def Theta_bus(model,i):
        return model.Theta['bus_10001',i] == 0
model.ThetaB_Constraint = Constraint(model.hh_periods,rule=Theta_bus)

def FlowUP_line(model,l,i):
    return  model.Flow[l,i] <= model.FlowLim[l]
model.FlowU_Constraint = Constraint(model.lines,model.hh_periods,rule=FlowUP_line)

def FlowLow_line(model,l,i):
    return  -1*model.Flow[l,i] <= model.FlowLim[l]
model.FlowLL_Constraint = Constraint(model.lines,model.hh_periods,rule=FlowLow_line)

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

