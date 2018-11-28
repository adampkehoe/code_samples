# -*- coding: utf-8 -*-
"""
Transportation of Fuel Payloads in Space

Contributors:
  Duncan Anderson
  Adam Kehoe
  Brent Austgen
"""

from itertools import product
from math import exp
import pandas
import os

from pyomo.environ import *
from pyomo.opt import *

import data
from rocketship import RocketShip

deltav_csv = './datasets/deltav_0.csv'
fuelcost_csv = './datasets/fuelcost_0.csv'

mod = ConcreteModel()

nodes = ['Earth', 'Mars', 'Ceres']
demand_nodes = ['Earth', 'Mars']
supply_nodes = ['Ceres']
edges = [edge for edge in product(demand_nodes, supply_nodes)] + \
        [edge for edge in product(supply_nodes, demand_nodes)]

# sets
print('defining sets')
mod.time = Set(initialize=range(8000), ordered=True)
mod.routes = Set(initialize=range(60, 406, 15))
mod.nodes = Set(initialize=nodes)
mod.d_nodes = Set(within=mod.nodes, initialize=demand_nodes)
mod.s_nodes = Set(within=mod.nodes, initialize=supply_nodes)
mod.edges = Set(within=mod.nodes * mod.nodes, initialize=edges)

def get_fuel_cost(mod, t, i, j, r):
    global fuelcost_df
    return float(fuelcost_df.at[t, '({}, {}, {})'.format(i, j, r)])

def get_fuel_prod(mod, t, i):
    return float(5000 if i == 'Ceres' else 0)

# parameters




#fuelcost_df = pandas.read_csv(fuelcost_csv, index_col=0)



# variables



def edges_leave(mod, i):
    return [edge for edge in mod.edges if edge[0] == i]

def edges_enter(mod, i):
    return [edge for edge in mod.edges if edge[1] == i]

# objective

def obj_earth_and_mars_total(mod):
    print('defining objective')
    return mod.fuel_storage[mod.time[-1], 'Earth'] + \
           mod.fuel_storage[mod.time[-1], 'Mars']
           
def obj_spill(mod):
    print('fuel spill obj def')
    return sum(mod.fuel_spill[t,'Earth']*exp(t*-.05/365) for t in mod.time) + \
            sum(mod.fuel_spill[t,'Mars']*exp(t*-.05/365) for t in mod.time)


# constraints

def con_ship_flow_balance(mod, t, i):

    if t > 0:
        return mod.ship_storage[t, i] == mod.ship_storage[t-1, i] - \
            sum(mod.launch[t-1, e, r]
                for e in edges_leave(mod, i) for r in mod.routes) + \
            sum(mod.launch[t-r-1, e, r]
                for e in edges_enter(mod, i) for r in mod.routes
                if t-r-1 >= 0)
    else:
        return mod.ship_storage[t, i] == (mod.num_ships if i == 'Ceres' else 0)



def con_fuel_flow_balance(mod, t, i):
    if t > 0:
        return mod.fuel_storage[t, i] == mod.fuel_storage[t-1, i] - \
            sum(mod.launch[t-1, e, r] * \
                (mod.ship.capacity if i in mod.s_nodes else mod.fuel_cost[t-1, e, r])
                for e in edges_leave(mod, i) for r in mod.routes) + \
            sum(mod.launch[t-r-1, e, r] * \
                ((mod.ship.capacity - mod.fuel_cost[t-r-1, e, r])
                if e[0] in mod.s_nodes else 0) for e in edges_enter(mod, i)
                for r in mod.routes if t-r-1 >= 0) + \
            mod.fuel_prod[t-1, i] - \
            mod.fuel_spill[t, i]
    else:
        return mod.fuel_storage[t, i] + mod.fuel_spill[t,i] == 0
    
#def con_lockdown(mod, t, i):
#    return mod.fuel_spill[t,i] <= 1000000


def con_ceres_fuel_cap(mod, t):
    return mod.fuel_storage[t, 'Ceres'] <= 1.5 * mod.ship.capacity

def run_model(mod,runid,ship):
    
    print('defining parameters')
    mod.num_ships = 1
    mod.ship = ship

    if not all(map(os.path.isfile, [deltav_csv])):
        print('  deltaV not found, building on the fly')
        DV, FC = data.make_model_data(range(132), mod.routes, mod.ship)
        DV.to_csv(deltav_csv)
        FC.to_csv(fuelcost_csv)
    deltav_df = pandas.read_csv(deltav_csv)
    global fuelcost_df
    fuelcost_df = pandas.DataFrame()
    for col in deltav_df.columns:
        if col != 't':
            if col[0] == 'C': # C for Ceres
                fuelcost_df[col] = deltav_df[col].apply(mod.ship.vel_to_fuel_full)
            else:
                fuelcost_df[col] = deltav_df[col].apply(mod.ship.vel_to_fuel_empty)
    
    mod.fuel_cost = Param(mod.time, mod.edges, mod.routes,
                          initialize=get_fuel_cost)
    mod.fuel_prod = Param(mod.time, mod.nodes,
                          initialize=get_fuel_prod)
    
    print('defining variables')
    mod.launch = Var(mod.time, mod.edges, mod.routes,
                     domain=NonNegativeIntegers)
    mod.ship_storage = Var(mod.time, mod.nodes, domain=NonNegativeIntegers)
    mod.fuel_storage = Var(mod.time, mod.nodes, domain=NonNegativeReals,
                           initialize=0)
    mod.fuel_spill = Var(mod.time, mod.nodes, domain=NonNegativeReals,
                         initialize=0)
     
    #mod.objective = Objective(rule=obj_earth_and_mars_total, sense=maximize)
    mod.objective = Objective(rule=obj_spill, sense=maximize)
    print('defining constraints')
    mod.con_ship_flow_balance = Constraint(mod.time, mod.nodes,
                                           rule=con_ship_flow_balance)    
    
    
    mod.con_fuel_flow_balance = Constraint(mod.time, mod.nodes,
                                       rule=con_fuel_flow_balance)

    mod.con_ceres_fuel_cap = Constraint(mod.time, rule=con_ceres_fuel_cap)
    
    #mod.con_lockdown_check = Constraint(mod.time, mod.nodes, rule=con_lockdown)

    print('preparing to solve')
    solver = SolverFactory('gurobi')
    results = solver.solve(mod, tee=True, keepfiles=True)
    results.write()
    reporting(mod, 'DAtest')

def reporting(mod, runid):
    print('producing output reports')
    df_launch = pandas.DataFrame()
    for r in mod.routes:
        for (i, j) in mod.edges:
            df_launch[(i, j, r)] = pandas.Series([mod.launch[t, i, j, r].value
                                                   for t in mod.time])
    print('sparse launch matrix complete')
    df_ship_storage = pandas.DataFrame()
    df_fuel_storage = pandas.DataFrame()
    df_fuel_spill = pandas.DataFrame()
    for i in mod.nodes:
        df_ship_storage[i] = pandas.Series([mod.ship_storage[t, i].value
                                           for t in mod.time])
        df_fuel_storage[i] = pandas.Series([mod.fuel_storage[t, i].value
                                           for t in mod.time])
        df_fuel_spill[i] = pandas.Series([mod.fuel_spill[t, i].value
                                         for t in mod.time])
    print('capacity report complete')
    f_use = []
    launch_dat = [[],[],[],[],[],[]]
    fuelcost_df.to_csv('fuelcost_'+runid+'.csv')
    for t in mod.time:
        f_use.append(0)
        for (i,j) in mod.edges:
            for r in mod.routes:
                if mod.launch[t,(i,j),r].value != None:     
                    x = mod.launch[t,(i,j),r].value
                rstr = '('+i+', '+j+', '+str(r)+')'
                f_use[t] += x * fuelcost_df[rstr][t]
                #print(t, f_use[t])
                launch_dat[0].append(t)
                launch_dat[1].append(i)
                launch_dat[2].append(j)
                launch_dat[3].append(r)
                launch_dat[4].append(t+r)
                launch_dat[5].append(x)
    df_launch2 = pandas.DataFrame(
        {'launch_time': launch_dat[0],
         'origin': launch_dat[1],
         'destination': launch_dat[2],
         'travel_time': launch_dat[3],
         'arrival_time': launch_dat[4],
         'shipcount': launch_dat[5]} )
    print('launch list report complete')
    df_fueluse = pandas.DataFrame(
        {'t': mod.time,
         'fuel_use': f_use})
    print('fuel use report complete')
    df_launch.to_csv('launchmatrix_'+runid+'.csv')
    df_ship_storage.to_csv('ship_storage_'+runid+'.csv')
    df_fuel_storage.to_csv('fuel_storage_'+runid+'.csv')
    df_fuel_spill.to_csv('fuel_spill_'+runid+'.csv')
    
    df_launch2.to_csv('launchlist_'+runid+'.csv',',')


ship_12 = RocketShip(mass=120000, capacity=800000, num_thrusters=16)
ship_13 = RocketShip(mass=120000, capacity=800000, num_thrusters=16)
ship_14 = RocketShip(mass=120000, capacity=800000, num_thrusters=16)
ship_base = RocketShip(mass=120000, capacity=800000, num_thrusters=15)
ship_16 = RocketShip(mass=120000, capacity=800000, num_thrusters=16)
ship_17 = RocketShip(mass=120000, capacity=800000, num_thrusters=16)
ship_18 = RocketShip(mass=120000, capacity=800000, num_thrusters=16)
ship_19 = RocketShip(mass=120000, capacity=800000, num_thrusters=16)
ship_20 = RocketShip(mass=120000, capacity=800000, num_thrusters=16)
run_model(mod, 'thrust_15',ship_base)
#run_model(mod, 'thrust_16',ship_16)
#run_model(mod, 'thrust_17',ship_17)
#run_model(mod, 'thrust_18',ship_18)
#run_model(mod, 'thrust_19',ship_19)
#run_model(mod, 'thrust_20',ship_20)
#run_model(mod, 'thrust_14',ship_14)
#run_model(mod, 'thrust_13',ship_13)
#run_model(mod, 'thrust_12',ship_12)