import os
import re

from project import Task, Project

def load_instance(path_to_file):
    
    ### load raw text ###
    f = open(path_to_file, 'r')
    raw_lines = f.read().splitlines()
    stripped_lines = []
    for line in raw_lines:
        line = line.replace('\t', ',').replace('[', '').replace(']', '')
        stripped_lines.append(re.split(',', line))

    ### first line ###
    first_line = stripped_lines[0]
    n_activities = int(first_line[0]) # number of activities (incl. dummy activities)
    n_resources = int(first_line[1])
    
    ### load tasks (main body of instance file) ###
    tasks = {}
    for activity in range(n_activities):
        ### first block ###
        line1 = stripped_lines[activity+1]
        task_id = int(line1[0])
        n_successors = [int(line1[2]), int(line1[3]), int(line1[4]), int(line1[5])] # [# SS successors, # SF successors, # FS successors, # FF successors]
        successors = [[] for i in range(4)]
        k = 0 # counter to track where in line1 to get desired info.
        for i in range(4):
            if n_successors[i] > 0:
                for j in range(n_successors[i]):
                    successors[i].append((int(line1[6+2*k+j]), int(line1[6+2*k+n_successors[i]+j]))) # e.g. successor[i=2(FS)] = [(FS successor id, min. time-lag),...]
            k += n_successors[i]
        ### second block ###
        line2 = stripped_lines[n_activities+activity+1]
        w = int(line2[3]) # principle resource work content
        q_min = [] # min. per-period resource allocation for each resource 
        q_max = [] # max. per-period resource allocation for each resource
        for r in range(n_resources):
            q_min.append(int(line2[4+2*r]))
            q_max.append(int(line2[4+2*r+1]))
        ### create task ###
        task = Task(task_id, successors, w, q_min, q_max)
        tasks[task_id] = task 

    ### last line ###
    last_line = stripped_lines[2*n_activities+1]
    R_max = [] # resource_availabilities
    for r in range(n_resources):
        R_max.append(int(last_line[r]))
    l_min = int(last_line[n_resources]) # min. block length
    ### create project ###
    project_name = os.path.splitext(os.path.basename(os.path.normpath(path_to_file)))[0]
    project = Project(project_name, tasks, R_max, l_min)
    return(project)

