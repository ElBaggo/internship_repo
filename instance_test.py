
from gurobipy import *

import os.path

from load_instance import load_instance
from dt3 import mip_solve
from project import Project
from schedule import Schedule
from schedule_plot import schedule_plot

instance_folder_name = 'testset_ubo10'
instance_name = 'psp1_r1.sch'
time_limit = 60

def get_schedule(model, project):
    #populating schedule object with optimal solution
    schedule = Schedule(project)
    schedule.failed = 0
    V = [i for i in project.tasks]
    N = V[1:-1] 
    vars = model.getVars() 
    schedule.makespan = vars[-1].X
    x = [[x for x in vars if 'x[{}'.format(i) in x.VarName] for i in project.tasks]
    y = [[y for y in vars if 'y[{}'.format(i) in y.VarName] for i in project.tasks]
    q = [[[q for q in vars if 'q[{},{}'.format(r,i) in q.VarName] for i in project.tasks] for r in range(len(project.R_max))]
    for i in N:
        schedule.task_starts[i] = next(j for j in range(len(x[i])) if x[i][j].X == 1)
        schedule.task_ends[i] = next(j for j in range(len(y[i])) if y[i][j].X == 1)
        for r in range(len(project.R_max)):
            schedule.task_resource_usage[r][i] = [q.X for q in q[r][i]]
            for t in range(project.T_max):
                schedule.resource_availability[r][t] -= schedule.task_resource_usage[r][i][t]
    return schedule 

test_instances_dir = os.path.join('test_instances', instance_folder_name)
project = load_instance(os.path.join(test_instances_dir, instance_name))
print(instance_name)
model = mip_solve(project, time_limit)
status = model.Status
if project.dgraph == 1:
    print('project is infeasible with respect to temporal constraints')
if status == GRB.Status.INFEASIBLE:
    print('project is infeasible')
if status == GRB.Status.OPTIMAL:
    print('optimal makespan is {}. Found in {} seconds.'.format(model.ObjVal, model.Runtime))
    model.write(os.path.join('solutions', '%s.sol' %project.name))
    schedule = get_schedule(model, project)
    schedule_plot(schedule, project)
if status == GRB.Status.TIME_LIMIT:
    if model.SolCount == 0:
        if model.ObjBound < 0: # i.e. when LB not found
            print('No solution or LB has been found.')
        else:
            print('No solution has been found. LB on optimal is {}'.format(model.ObjBound)) 
    elif model.SolCount != 0:
        if model.ObjBound < 0: # i.e. when LB not found
            print('A solution with makespan {} has been found. No LB has been found.'.format(model.ObjVal))
            schedule = get_schedule(model, project)
        else:
            print('A solution with makespan {} has been found. The optimality gap is {}.'.format(model.ObjVal, model.MIPGap))
            schedule = get_schedule(model, project)



