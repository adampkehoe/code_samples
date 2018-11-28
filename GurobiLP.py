import LPCompAssignment1
from random import seed
from itertools import product
from pyomo.environ import *
from pyomo.opt import SolverFactory

# use RNG seed known to produce feasible problem
seed(12345)
m = ConcreteModel()

# index sets
I = [_ for _ in range(10)] # rows
J = [_ for _ in range(10)] # cols
m.I = Set(initialize=I)
m.J = Set(initialize=J)

# parameters
A = comp1.random_matrix(10, 10, p=0.6, L=-10, U=30, keep=True)
Aflat = [v for s in A for v in s]
m.A = Param(m.I, m.J, initialize=dict(zip(product(I, J), Aflat)))
b = comp1.random_matrix(10, 1, p=0.8, L=0, U=50, keep=True)
bflat = [v for s in b for v in s]
m.b = Param(m.I, initialize=dict(zip(I, bflat)))

# variables
# note that variables are not restricted to non-negative real numbers
m.x = Var(m.J, domain=Reals)

# objective
# note the objective here is inconsequential since only one solution should
# exist; as such, the objective is arbitrarily assigned the sum of x, which
# is a linear combination
def objective_rule(m):
    return sum(m.x[j] for j in m.J)
m.obj = Objective(sense=minimize, rule=objective_rule)

# constraints
def con_equalities(m, i):
    return sum(m.A[i, j] * m.x[j] for j in m.J) == m.b[i]
m.con_equalities = Constraint(m.I, rule=con_equalities)

# solve the model
opt = SolverFactory('gurobi')
results = opt.solve(m, tee=True)

# results
results.write()
print("\n\nx =")
for i in m.x:
    print("{:2.3f},".format(m.x[i].value)),
print("\n\nA =")
for row in range(len(A)):
    for col in range(len(A[0])):
        print("{:2.3f},".format(A[row][col])),
        print("")
print("\n\nb^T =")
for row in range(len(b)):
    for col in range(len(b[0])):
        print("{:2.3f},".format(b[row][col]))