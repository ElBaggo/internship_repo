
import random
import math

class Task():

    def __init__(self, id, min_lags, w, q_min, q_max):
        self.id = id
        self.SS_min = min_lags[0]
        self.SS_succ = None #list of +ve min-lag SS successors. Initialised in project init
        self.SS_pred = None #list of +ve min-lag SS predecessors. Initialised in project init
        self.w = w
        self.q_min = q_min
        self.q_max = q_max
        n_res = len(q_min)
        #alpha, beta
        if q_min[0] != q_max[0]:
            self.alpha = [(q_max[r]-q_min[r])/(q_max[0]-q_min[0]) for r in range(n_res)]
            self.r_dep = [r for r in range(1, n_res) if q_min[r] < q_max[r]]
            self.r_ind = [r for r in range(1, n_res) if q_min[r] == q_max[r]]
        else:
            self.alpha = [0 for r in range(n_res)]
            self.r_dep = []
            self.r_ind = [r for r in range(n_res)]
        self.beta = [q_min[r]-q_min[0]*self.alpha[r] for r in range(n_res)]
        #d_min, d_max
        if q_max[0] != 0 and q_min[0] != 0:
            self.d_min = math.ceil(w/q_max[0])
        else:
            self.d_min = 0
        if q_min[0] != 0:
            self.d_max = math.ceil(w/q_min[0])
        else:
            self.d_max = 0
        #ES, LS. Initialised in project temporal_analysis
        self.ES = None
        self.LS = None
        self.EF = None
        self.LS = None


class Project():

    def __init__(self, name, tasks, R_max, l_min):
        self.name = name
        self.tasks = tasks #tasks = {task_id : task_object}
        self.R_max = R_max
        self.l_min = l_min
        self.T_max = sum(max(self.tasks[i].d_max, max([0] + [SS_min[1] for SS_min in self.tasks[i].SS_min])) for i in self.tasks)
        self.DAG = {i:[succ[0] for succ in self.tasks[i].SS_min] for i in self.tasks} # precedence network without weights
        self.SCCs = self.get_SCCs()
        self.dgraph = self.temporal_analysis()
        #task SS successors
        for i in self.tasks:
            self.tasks[i].SS_succ = []
            for successor in self.tasks[i].SS_min:
                if successor[1] >= 0:
                    self.tasks[i].SS_succ.append(successor[0])
        #task SS predecessors
        for j in self.tasks:
            self.tasks[j].SS_pred = []
            for i in self.tasks:
                if j in self.tasks[i].SS_succ:
                    self.tasks[j].SS_pred.append(i)
        
    def get_SCCs(self):
        nodes_traversed = []
        visited = [False for i in self.tasks]
        for i in self.tasks:
            if visited[i] == False:
                DFS(self.DAG, i, visited, nodes_traversed)
        transpose_DAG = {j:[i for i in self.DAG if j in self.DAG[i]] for j in self.tasks} # DAG with arcs reversed.
        visited = [False for i in self.tasks]
        SCCs = []
        while nodes_traversed:
            i = nodes_traversed.pop()
            if visited[i] == False:
                SCC = []
                DFS(transpose_DAG, i, visited, SCC)
                SCCs.append(SCC)
        return SCCs

    def temporal_analysis(self):
        dgraph = [[-self.T_max for j in self.tasks] for i in self.tasks]
        for i in self.tasks:
            dgraph[i][i] = 0
            dgraph[0][i] = 0
            for successor in self.tasks[i].SS_min:
                dgraph[i][successor[0]] = successor[1]
        ### floyd-warshall algorithm ###
        for k in self.tasks:
            for i in self.tasks:
                for j in self.tasks:
                    dgraph[i][j] = max(dgraph[i][j], dgraph[i][k]+dgraph[k][j])
        for i in self.tasks:
            if dgraph[i][i] != 0:
                return(1)
        for i in self.tasks:
            self.tasks[i].ES = dgraph[0][i]
            self.tasks[i].LS = -dgraph[i][0]
            self.tasks[i].EF = self.tasks[i].ES + self.tasks[i].d_min
            self.tasks[i].LF = self.tasks[i].LS + self.tasks[i].d_max
        return dgraph

    # randomly generates an alr by topological ordering wrt +ve min time-lags
    def gen_alr1(self):
        positive_DAG = {i:[succ[0] for succ in self.tasks[i].SS_min if succ[1] > 0] for i in self.tasks} # precedence network with -ve min lags removed 
        alr = []
        visited = [False for i in self.tasks]
        while False in visited:
            i = random.choice([v for v in self.tasks])
            if visited[i] == False:
                random_DFS(positive_DAG, i, visited, alr)
        return alr

# DFS required for get_SCCs
def DFS(DAG, v, visited, nodes_traversed):
    visited[v] = True
    for i in DAG[v]:
        if visited[i] == False:
            DFS(DAG, i, visited, nodes_traversed)
    nodes_traversed.append(v) 

# random_DFS required for gen_alr1
def random_DFS(DAG, v, visited, nodes_traversed):
    visited[v] = True
    while False in DAG[v]:
        i = random.choice(DAG[v])
        if visited[i] == False:
            random_DFS(DAG, i, visited, nodes_traversed)
    nodes_traversed.append(v)
