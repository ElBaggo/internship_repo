

#dt3 mip model from Naber & Kolisch (2014)

from gurobipy import *

import os

def mip_solve(project, time_limit):    

    model = Model("Intensity-based (FB-DT3)")
    model.setParam('TimeLimit', time_limit)
#    model.setParam('OutputFlag', 0) # silence gurobi output
    model.setParam('Threads', 4) # limit number of threads to 4

    #Index sets
    V = [i for i in project.tasks]
    N = V[1:-1] #set of non-dummy activities
    R = list(range(len(project.R_max))) # list of resource indices
    T = list(range(project.T_max)) # planning horizon
    T_act = [list(range(project.tasks[j].ES, project.tasks[j].LF+1)) for j in V] #feasible processing periods for each activity
    ST_act = [list(range(project.tasks[j].ES, project.tasks[j].LS+1)) for j in V] #feasible starting periods for each activity
    FT_act = [list(range(project.tasks[j].EF, project.tasks[j].LF+1)) for j in V] #feasible finishing periods for each activity

    #Variables
    x = model.addVars([(j,t) for j in V for t in T_act[j]], name = "x", vtype = GRB.BINARY)
    y = model.addVars([(j,t) for j in V for t in T_act[j]], name = "y", vtype = GRB.BINARY)
    delta = model.addVars([(j,t) for j in V for t in T_act[j]+[project.tasks[j].LF+1]], name = "delta", vtype = GRB.BINARY)
    q = model.addVars([(r,j,t) for r in R for j in V for t in T_act[j]+[project.tasks[j].ES-1,project.tasks[j].LF+1]], name = "q", vtype = GRB.CONTINUOUS)
    v = model.addVars([(j,t) for j in V for t in T_act[j]+[project.tasks[j].LF+1]], name = "v", vtype = GRB.CONTINUOUS)
    C_max = model.addVar(name = "C_max", vtype = GRB.CONTINUOUS)

    #Objective
    model.setObjective(C_max + quicksum(quicksum(q[0,j,t] for t in T_act[j]) - project.tasks[j].w for j in V), GRB.MINIMIZE)

    #Constraints
    model.addConstrs((C_max >= project.tasks[j].LF - quicksum(y[j,t] for t in T_act[j]) + 1 for j in V), name = "(31)")
    model.addConstrs((q[r,j,t] <= project.tasks[j].q_max[r]*(x[j,t] - y[j,t]) for r in R for j in V for t in T_act[j]), name = '(42new)')
    model.addConstrs((q[r,j,t] >= project.tasks[j].q_min[r]*(x[j,t] - y[j,t]) for r in R for j in V for t in T_act[j]), name = '(43new)')
#    model.addConstrs((q[r,j,t] <= project.tasks[j].q_max[r]*x[j,t] for r in R for j in V for t in ST_act[j] if t not in FT_act[j]), name = "(42a)")
#    model.addConstrs((q[r,j,t] <= project.tasks[j].q_max[r]*(x[j,t] - y[j,t]) for r in R for j in V for t in ST_act[j] if t in FT_act[j]), name = "(42b)")
#    model.addConstrs((q[r,j,t] <= project.tasks[j].q_max[r]*(1 - y[j,t]) for r in R for j in V for t in FT_act[j] if t not in ST_act[j]), name = "(42c)")
#    model.addConstrs((q[r,j,t] >= project.tasks[j].q_min[r]*x[j,t] for r in R for j in V for t in ST_act[j] if t not in FT_act[j]), name = "(43a)")
#    model.addConstrs((q[r,j,t] >= project.tasks[j].q_min[r]*(x[j,t] - y[j,t]) for r in R for j in V for t in ST_act[j] if t in FT_act[j]), name = "(43b)")
#    model.addConstrs((q[r,j,t] >= project.tasks[j].q_min[r]*(1 - y[j,t]) for r in R for j in V for t in FT_act[j] if t not in ST_act[j]), name = "(43c)")
    model.addConstrs((q[r,j,t] == project.tasks[j].alpha[r]*q[0,j,t] + project.tasks[j].beta[r]*(x[j,t] - y[j,t]) for j in V for r in project.tasks[j].r_dep for t in T_act[j]), name = "(44)")
    model.addConstrs((q[0,j,t] >= project.tasks[j].w*(v[j,t+1] - v[j,t]) for j in V for t in T_act[j]), name = "(45)")
    model.addConstrs((quicksum(q[r,j,t] for j in V if t in T_act[j]) <= project.R_max[r] + 0.0001 for r in R for t in T), name = "(5)")
    model.addConstrs((quicksum(delta[j,tau] for tau in range(t,t+project.l_min)) <= 1  for j in V for t in range(project.tasks[j].ES,project.tasks[j].LF-project.l_min+2) if project.l_min >= 2), name = "(6)")
    model.addConstrs((q[0,j,t] - q[0,j,t-1] <= project.tasks[j].q_max[0]*delta[j,t] for j in V for t in T_act[j]+[project.tasks[j].LF+1]), name = "(7)")
    model.addConstrs((q[0,j,t-1] - q[0,j,t] <= project.tasks[j].q_max[0]*delta[j,t] for j in V for t in T_act[j]+[project.tasks[j].LF+1]), name = "(8)")
    model.addConstrs((q[r,j,project.tasks[j].ES-1] == 0 for r in R for j in V), name = "(9a)")
    model.addConstrs((q[r,j,project.tasks[j].LF+1] == 0 for r in R for j in V), name = "(9b)")
    model.addConstrs((v[j,t] <= x[j,t] for j in V for t in ST_act[j]), name = "(32)")
    model.addConstrs((v[j,t] >= y[j,t] for j in V for t in FT_act[j]), name = "(33)")
    model.addConstrs((x[SS[0],t+SS[1]] <= x[j,t] for j in V for SS in project.tasks[j].SS_min for t in ST_act[j] if t+SS[1] in ST_act[SS[0]]), name = "(34)") #precedence constraint
    model.addConstrs((v[j,t] <= v[j,t+1] for j in V for t in T_act[j]), name = "(35)")
    model.addConstrs((x[j,t-1] <= x[j,t] for j in V for t in T_act[j] if t != project.tasks[j].ES), name = "(36)")
    model.addConstrs((y[j,t-1] <= y[j,t] for j in V for t in T_act[j] if t != project.tasks[j].ES), name = "(37)")
    model.addConstrs((v[j,project.tasks[j].ES] == 0 for j in N), name = "(38b)")
    model.addConstrs((v[j,project.tasks[j].LF] == 1 for j in V), name = "(39)")
    model.addConstrs((x[j,t] == 1 for j in V for t in range(project.tasks[j].LS, project.tasks[j].LF+1)), name = "(40)")
    model.addConstrs((y[j,t] == 0 for j in N for t in range(project.tasks[j].ES, project.tasks[j].EF)), name = "(41)")
    model.addConstrs((y[j,project.tasks[j].LF] == 1 for j in V), name = '(new 1)')
    model.addConstrs((q[r,j,t] >= 0 for r in R for j in V for t in T_act[j]+[project.tasks[j].ES-1,project.tasks[j].LF+1]), name = "(10)")
    model.addConstrs((0 <= v[j,t] <= 1 for j in V for t in T_act[j]+[project.tasks[j].LF+1]), name = "(47)")

    model.optimize()

    return model
    



