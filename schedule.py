
from copy import deepcopy

class Schedule():

    def __init__(self, project):
        self.failed = None
        self.tasks = deepcopy(project.tasks)
        self.tasks_scheduled = []
        self.task_starts = {}
        self.task_ends = {}
        self.task_resource_usage = [[[0 for t in range(project.T_max)] for i in project.tasks] for r in range(len(project.R_max))]
        self.resource_availability = [[project.R_max[r] for t in range(project.T_max)] for r in range(len(project.R_max))]
        self.unscheduling_attempts = 0
        self.makespan = None
