# -*- coding: utf-8 -*-
"""
@author: Adam Kehoe
"""


import pandas as pd
import numpy as np
from pyomo.environ import *
from pyomo.opt import SolverFactory
import OpexCaseStudy_Scenario1Control

no_warehouse_trans_cost = OpexCaseStudy_Scenario1Control.Output()
model = ConcreteModel() 
runid = input("What would you like to name output file?")

def run_model(model, runid):
    
    Data = pd.read_excel("Network Planning Case Study - Opex Analytics.xlsx", sheet_name=['Plants', 'Customers', 'Product', 'Annual Demand', 'Production Capacity', 'Distances'])
    Data['Setups'] = pd.read_excel("Network Planning Case Study - Opex Analytics.xlsx", sheet_name=['Setups'],skiprows=1)['Setups']
    
    #redefine capacity and demand in terms of quarters
    Data['Annual Demand']['Quarterly Demand'] = Data['Annual Demand']['Demand (in tonnes)'].astype('float')/4
    Data['Production Capacity']['Quarterly Production Capacity'] = Data['Production Capacity']['Annual Production Capacity'].astype('float')/4
    
    supply_nodes = Data['Plants']['ID'].values.tolist()
    demand_nodes = Data['Customers']['ID'].values.tolist()
    products = Data['Product']['ID'].values.tolist()
    quarters = ['2012a', '2012b', '2012c', '2012d', '2013a', '2013b', '2013c', '2013d', '2014a', '2014b', '2014c', '2014d']
    
    #set values for indexing
    model.i = Set(initialize=supply_nodes, doc = 'Plant IDs')
    model.j = Set(initialize=demand_nodes, doc = 'Warehouse IDs')
    model.k = Set(initialize=demand_nodes, doc = 'Customer IDs')
    model.l = Set(initialize=products, doc = 'Product IDs')
    model.t = Set(initialize=quarters, doc = 'Year')
    
    #parameters as dictionaries
    demand={}
    for t in model.t:
        for l in model.l:
            for k in model.k:
                demand[(l,t,k)] = Data['Annual Demand'].loc[(Data['Annual Demand']['Product ID'] == l) & (Data['Annual Demand']['Time Period'] == int(t[0:4])) & (Data['Annual Demand']['Customer ID'] == k)]['Quarterly Demand']
    
    product_available = {}
    for i in model.i:
        for l in model.l:
            for t in model.t:
                if i == 1 and l == 1:
                    product_available[(i,l,t)] = np.minimum(1080 * 100, Data['Production Capacity'].loc[(Data['Production Capacity']['Plant ID'] == i) & (Data['Production Capacity']['Product ID'] == l)]['Quarterly Production Capacity'].values)
                elif i != 1 and i == l:
                    product_available[(i,l,t)] = np.minimum(1080 * 50, Data['Production Capacity'].loc[(Data['Production Capacity']['Plant ID'] == i) & (Data['Production Capacity']['Product ID'] == l)]['Quarterly Production Capacity'].values)
                else:
                    product_available[(i,l,t)] = 0
    
    prod4_available = np.minimum(1080 * 50, Data['Production Capacity'].loc[(Data['Production Capacity']['Plant ID'] == 4) & (Data['Production Capacity']['Product ID'] == 4)]['Quarterly Production Capacity'].values)
    prod5_available = np.minimum(1080 * 50, Data['Production Capacity'].loc[(Data['Production Capacity']['Plant ID'] == 4) & (Data['Production Capacity']['Product ID'] == 5)]['Quarterly Production Capacity'].values)
    #reverse this for case in which 5 begins quarter 1
    for t in model.t:
        if t[4] == 'a' or t[4] == 'c':
            product_available[(4,5,t)] = min(1080*50 - 8*8 * 50, prod5_available)
            product_available[(4,4,t)] = min(1080*50 - 8*8 * 50, prod4_available)
        if t[4] == 'b' or t[4] == 'd':
            product_available[(4,5,t)] = min(1080*50 - 8*6 * 50, prod5_available)
            product_available[(4,4,t)] = min(1080*50 - 8*6 * 50, prod4_available)
    
    warehouse_distance = {}
    for j in model.j:
        for k in model.k:
            if Data['Distances'].loc[(Data['Distances']['Customer ID1'] == j) & (Data['Distances']['Customer ID2'] == k)]['Warehouse Distance'].values  <= 500:
                warehouse_distance[(j,k)] = 1
            else:
                warehouse_distance[(j,k)] = 0
                
    production_facility_distance = {}
    for i in model.i:
        for k in model.k:
            if Data['Distances'].loc[(Data['Distances']['Plant Id'] == i) & (Data['Distances']['Customer ID'] == k)]['Distance'].values  <= 500:
                production_facility_distance[(i,k)] = 1
            else:
                production_facility_distance[(i,k)] = 0  
    
    customer_distance = {}           
    for i in model.i:
        for j in model.j:
            customer_distance[(i,j)] = Data['Distances'].loc[(Data['Distances']['Plant Id'] == i) & (Data['Distances']['Customer ID'] == j)]['Distance'].values
    
    warehouse_to_customer_distance = {}
    for j in model.j:
        for k in model.k:
            warehouse_to_customer_distance[(j,k)] = Data['Distances'].loc[(Data['Distances']['Customer ID1'] == j) & (Data['Distances']['Customer ID2'] == k)]['Warehouse Distance'].values
            
    #Variables
    model.W = Var(model.j, within=Binary)
    model.x = Var(model.i, model.j, model.k, model.l, model.t, doc='Product l produced at plant i, stored at city j, shipped to city k, in quarter t')
    model.y = Var(model.i, model.i, model.k, model.l, model.t, doc='Product delivered directly to client without being sent to a warehouse')
    
    #Just commenting out this other valid way of generating the demand constraints. For this I preferred the way I've done it just because it's easier for me to see
    #model.demand = Param(model.l, model.t, model.k, initialize=demand)
    #def demand_constraint(model, l, t, k):
    #    return sum(model.x[i,j,k,l,td] for i in model.i for j in model.j) == model.demand[l,t,k]
    #model.demand_constraints = Constraint(model.l, model.t, model.k, rule=demand_constraint)
    
    #demand constraints
    model.demand_constraint = ConstraintList()
    for k in model.k:
        for l in model.l:
            for t in model.t:
                model.demand_constraint.add(sum(model.x[i,j,k,l,t] for i in model.i for j in model.j) + sum(model.y[i,p,k,l,t] for i in model.i for p in model.i) == np.float64(demand[(l,t,k)]))
                
    #80% within 500 miles demand constraints            
    model.location_demand_constraint = ConstraintList()
    for k in model.k:
        for t in model.t:
            for l in model.l:
                model.location_demand_constraint.add(sum(model.x[i,j,k,l,t]*warehouse_distance[(j,k)] for i in model.i for j in model.j) + sum(model.y[i,p,k,l,t]*production_facility_distance[(i,k)] for i in model.i for p in model.i) >= np.float64(.8*demand[(l,t,k)]))
    
    #capacity constraints            
    model.capacity_constraint = ConstraintList()
    for i in model.i:
        for l in model.l:
            for t in model.t:
                model.capacity_constraint.add(sum(model.x[i,j,k,l,t] for j in model.j for k in model.k)  + sum(model.y[i,p,k,l,t] for p in model.i for k in model.k) <= product_available[(i,l,t)])
    #plant 4 production must not exceed 50*1080 - (depending)[setuptime(4,5) or setuptime(5,4)]
    for t in model.t:
        if t[4] == 'a' or t[4] == 'c':
            model.capacity_constraint.add(sum(model.x[4,j,k,4,t] + model.x[4,j,k,5,t] for j in model.j for k in model.k)  + sum(model.y[4,p,k,4,t] + model.y[4,p,k,5,t] for p in model.i for k in model.k) <= 50*(1080-8*8))
        if t[4] == 'a' or t[4] == 'd':
            model.capacity_constraint.add(sum(model.x[4,j,k,4,t] + model.x[4,j,k,5,t] for j in model.j for k in model.k)  + sum(model.y[4,p,k,4,t] + model.y[4,p,k,5,t] for p in model.i for k in model.k) <= 50*(1080-6*8))
    
    #products must not stored at production facilities must necessarily be stored in warehouses if product is to be delivered (variable y takes care of storage at production facilities themselves)        
    model.warehouse_constraints = ConstraintList()
    for i in model.i:
        for j in model.j:
            for k in model.k:
                for l in model.l:
                    for t in model.t:
                        model.warehouse_constraints.add(model.x[i,j,k,l,t] <= (model.W[j]*product_available[(i,l,t)]))
    
    #non-negativity constraints                    
    model.non_negativity_constraint = ConstraintList()
    for i in model.i:
        for j in model.j:
            for k in model.k:
                for l in model.l:
                    for t in model.t:
                        model.non_negativity_constraint.add(model.x[i,j,k,l,t] >= 0)
    for i in model.i:
        for p in model.i:
            for k in model.k:
                for l in model.l:
                    for t in model.t:
                        model.non_negativity_constraint.add(model.y[i,p,k,l,t] >= 0)
                        
                        
    
    #define objective and solve
    model.obj = Objective(expr = sum(model.W[j] for j in model.j))
    solvername = 'glpk'
    solverpath_folder = r'C:\Users\Stuart\glpk-4.65\w64'
    solverpath_exe = r'C:/Users/Stuart/glpk-4.65/w64/glpsol.exe'
    opt = SolverFactory(solvername,executable=solverpath_exe)
    results = opt.solve(model, tee=True)
    results.write()
    
    def check_solution(model):
        for k in model.k:
            for l in model.l:
                for t in model.t:
                    r = value(sum(model.x[i,j,k,l,t] for i in model.i for j in model.j) + sum(model.y[i,p,k,l,t] for i in model.i for p in model.i))
                    print('Product delivered ==> {f}, Product demanded ==> {g}'.format(f=r, g=np.float64(demand[(l,t,k)])))
    #check_solution(model)
    
    def reporting(model, runid):
        print('Producing output reports')
        b = {}
        n = {}
        m = {}
        c_p = {}
        c_w = {}
        c_r = {}
        c_q = {}
        q = 0
        cost_w = 0
        built = []
        for j in model.j:
            b[j] = value(model.W[j])
            if model.W[j] == 1:
                q+=1
                built.append(Data['Customers'].loc[(Data['Customers']['ID'] == j)]['City'])
      
        #report on total product produced
        for i in model.i:
            for l in model.l:
                for t in model.t:
                    n[(i,l,t)] = value(sum(model.x[i,j,k,l,t] for j in model.j for k in model.k))
                    
        #report on total product delivered
        for k in model.k:
            for l in model.l:
                for t in model.t:
                    m[(k,l,t)] = value(sum(model.x[i,j,k,l,t] for i in model.i for j in model.j))
                    
        #transportation costs
        for i in model.i:
            for j in model.j:
                for t in model.t:
                    c_p[(i,j,t)] = value(sum(model.x[i,j,k,l,t] * (.2*customer_distance[i,j]) for k in model.k for l in model.l))
                    cost_w += c_p[(i,j,t)]
        for j in model.j:
            for k in model.k:
                for td in model.t:
                    c_w[(j,k,t)] = value(sum(model.x[i,j,k,l,t] * (.2*warehouse_to_customer_distance[j,k]) for i in model.i for l in model.l))
                    cost_w += c_w[(j,k,t)]
        for p in model.i:
            for k in model.k:
                for t in model.t:
                    c_q[(p,k,t)] = value(sum(model.y[i,p,k,l,t] * (customer_distance[p,j]) for i in model.i for l in model.l))
                    cost_w += c_q[(p,k,t)]
                    
        print('Minimum number of warehouses needed is {f}'.format(f=q))
        print('(Customer city ID)  ==>   1 = built, 0 = not built')
        for i, j in b.items():
            print('{f}   ==>     {g}'.format(f=i,g=j))
        print('(Plant ID, Product ID, Year)  ==>  Total Product Produced')
        for i, j in n.items():
            print('{f}   ==>     {g}'.format(f=i,g=j))
        print('(Customer ID, Product ID, Year)  ==> Total Product Delivered')
        for i, j in m.items():
            print('{f}   ==>     {g}'.format(f=i,g=j))
        
        total_transportation_cost = cost_w
        difference = total_transportation_cost-no_warehouse_trans_cost
        print('The impact on transportation cost is a total cost of {f}'.format(f=total_transportation_cost))
        print('Running the model without the ability to produce warehouses yields a cost of {f}, for a total increase in cost of {g}'.format(f=no_warehouse_trans_cost, g=difference))
        
        df1 = pd.Series({'Min Warehouses': q})
        df2 = pd.Series({'Cities built in': built})
        df3 = pd.Series({'Transportation Cost w/Warehouses': total_transportation_cost})
        df4 = pd.Series({'W/o': no_warehouse_trans_cost})
        df5 = pd.Series({'Difference': difference})
        df_output = pd.concat([df1, df2, df3, df4, df5], ignore_index=True, sort=True, axis=1)
        df_output.to_csv('Opex_Scenario1'+runid+'.csv')
        
    reporting(model, runid)
run_model(model, runid)