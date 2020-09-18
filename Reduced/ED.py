from pyomo.environ import *

model = AbstractModel()

#Sets
model.unit = Set() #Set of generating units i
model.segments = Set() #Set of linearized segments j
model.lines = Set() #Set of linearized segments l
model.buses = Set() #Set of linearized segments b

#Time 
model.HorizonHours = Param(within=PositiveIntegers)
model.hours = RangeSet(1,model.HorizonHours)
model.ramp_periods = RangeSet(2,4)

#Parameters
model.MinCost = Param(model.unit) #minimum cost of generating units
model.Pmin = Param(model.unit)
model.Pmax = Param(model.unit)
model.Rup = Param(model.unit)
model.Rdn = Param(model.unit)
model.Slope = Param(model.unit,model.segments)
model.Smax = Param(model.unit,model.segments)
model.Reactance = Param(model.lines)
model.Flowlim = Param(model.lines)
model.LinetoBusMap=Param(model.lines,model.buses)
model.BustoUnitMap=Param(model.unit,model.buses)
model.Load = Param(model.buses,model.hours) #Load of the system

#Variables
model.cost1 = Var(model.unit,model.hours)
model.cost2 = Var(model.unit, model.segments,model.hours,within=NonNegativeReals)
model.Flow= Var(model.lines,model.hours)
model.Theta= Var(model.buses,model.hours)

#Constraints#######################################################################
#Objective Function
def SysCost(model):
    cost1=4*sum(model.MinCost[i] for i in model.unit) 
    cost2=sum(model.cost2[i,j,k]*model.Slope[i,j] for i in model.unit for j in model.segments for k in model.hours)
    return cost1 + cost2
model.SystemCost = Objective(rule=SysCost, sense=minimize)
    
#Balance Constraint 
def Nodal_Balance(model,b,k):
    value1=sum(model.cost1[i,k]*model.BustoUnitMap[i,b] for i in model.unit)
    value2=sum (model.Flow[l,k]*model.LinetoBusMap[l,b] for l in model.lines)
    return value1 - value2 == model.Load[b,k]
model.Node_Constraint = Constraint(model.buses,model.hours,rule=Nodal_Balance)
    
#Minimum Power Generation Constraint 
def Pmin_unit(model,i,k):
    return  model.cost1[i,k] >= model.Pmin[i]
model.PminU_Constraint = Constraint(model.unit,model.hours,rule=Pmin_unit)
    
#Maximum Power Generation Constraint 
def Pmax_unit(model,i,k):
    return  model.cost1[i,k] <= model.Pmax[i]
model.PmaxU_Constraint = Constraint(model.unit,model.hours,rule=Pmax_unit)
    
def Smax_unit(model,i,j,k):
    return  model.cost2[i,j,k] <= model.Smax[i,j]
model.SmaxU_Constraint = Constraint(model.unit,model.segments,model.hours,rule=Smax_unit)

#Total Generation
def Ptot_unit(model,i,k):
    value = sum(model.cost2[i,j,k] for j in model.segments)
    return  model.cost1[i,k] == model.Pmin[i]+ value
model.PtotU_Constraint = Constraint(model.unit,model.hours,rule=Ptot_unit)

def Flow_line(model,l,k):
    value = sum(model.Theta[b,k]*model.LinetoBusMap[l,b] for b in model.buses)
    return  100*value == model.Flow[l,k]*model.Reactance[l]
model.FlowL_Constraint = Constraint(model.lines,model.hours,rule=Flow_line)

def Theta_bus(model,k):
        return model.Theta['B1',k] == 0
model.ThetaB_Constraint = Constraint(model.hours,rule=Theta_bus)

def FlowUP_line(model,l,k):
    return  model.Flow[l,k] <= model.Flowlim[l]
model.FlowU_Constraint = Constraint(model.lines,model.hours,rule=FlowUP_line)

#def FlowLow_line(model,l):
#    return  -1*model.Flow[l] <= model.Flowlim[l]
#model.FlowLL_Constraint = Constraint(model.lines,FlowLow_line)

#Ramp up generation 
def Rup_unit(model,i,k):
    a = model.cost1[i,k]
    b = model.cost1[i,k-1]
    return  a-b <= model.Rup[i]
model.RupU_Constraint = Constraint(model.unit,model.ramp_periods,rule=Rup_unit)

#Ramp down generation 
def Rdn_unit(model,i,k):
    a = model.cost1[i,k]
    b = model.cost1[i,k-1]
    return  b-a <= model.Rdn[i]
model.RdnU_Constraint = Constraint(model.unit,model.ramp_periods,rule=Rdn_unit)










