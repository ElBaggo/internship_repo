
from gurobipy import *

import os.path
import re

from load_instance import load_instance
from dt3 import mip_solve
from project import Task, Project

instance_folder_name = 'testset_ubo10'
time_limit = 60

test_instances_dir = os.path.join('test_instances', instance_folder_name)
current_dir = os.path.dirname(__file__)
results_name = instance_folder_name + '_mip_results.txt'
f1 = open(os.path.join(current_dir, 'results', results_name), 'w+')
f1.write('{} \nno* - instance is not feasible wrt temporal constraints \n \ninstance \t #tsks \t feas \t opt \t LB \t sol \t gap \t time \n'.format(os.path.splitext(results_name)[0]))
f1.close()
for full_filename in sorted(os.listdir(test_instances_dir), key = lambda filename: int(''.join(re.findall(r'\d+', filename)))):
    print(full_filename)
    project = load_instance(os.path.join(test_instances_dir, full_filename))
    f1 = open(os.path.join(current_dir, 'results', results_name), 'a+')
    # check feasibility of temporal constraints
    if project.dgraph == 1:
        f1.write('{} \t {} \t no* \t - \t - \t - \t - \t - \n'.format(project.name, len(project.tasks)))
        continue
    model = mip_solve(project, time_limit)
    status = model.Status
    if status == GRB.Status.INFEASIBLE:
        f1.write('{} \t {} \t no \t - \t - \t - \t - \t - \n'.format(project.name, len(project.tasks)))
    elif status == GRB.Status.OPTIMAL:
        f1.write('{} \t {} \t yes \t yes \t {:.1f} \t {:.1f} \t {:.2f} \t {:.1f}\n'.format(project.name, len(project.tasks), model.ObjBound, model.ObjVal, model.MIPGap, model.Runtime))
    elif status == GRB.Status.TIME_LIMIT:    
        if model.SolCount == 0:
            if model.ObjBound < 0: # i.e. when LB not found
                f1.write('{} \t {} \t - \t no \t - \t - \t - \t {} \n'.format(project.name, len(project.tasks), model.ObjVal, model.MIPGap, time_limit))
            else:
                f1.write('{} \t {} \t - \t no \t {:.1f} \t - \t - \t {} \n'.format(project.name, len(project.tasks), model.ObjBound, time_limit)) 
        elif model.SolCount != 0:
            if model.ObjBound < 0: # i.e. when LB not found
                f1.write('{} \t {} \t yes \t no \t - \t {:.1f} \t - \t {} \n'.format(project.name, len(project.tasks), model.ObjVal, time_limit))
            else:
                f1.write('{} \t {} \t yes \t no \t {:.1f} \t {:.1f} \t {:.2f} \t {} \n'.format(project.name, len(project.tasks), model.ObjBound, model.ObjVal, model.MIPGap, time_limit))
    f1.close()

