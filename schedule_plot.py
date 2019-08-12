

import matplotlib.pyplot as plt

def schedule_plot(schedule, project):
    V = [i for i in project.tasks]
    N = V[1:-1]
    fig, axs = plt.subplots(len(project.R_max), sharex=True, sharey=True)
    fig.suptitle(project.name)
    for r in range(len(project.R_max)):
        tasks_plotted = []
        for i in N:
            for t in range(schedule.task_starts[i], schedule.task_ends[i]):
                bottom = sum(schedule.task_resource_usage[r][j][t] for j in tasks_plotted)
                duration = schedule.task_ends[i] - schedule.task_starts[i]
                axs[r].broken_barh([(t, 1)], (bottom, schedule.task_resource_usage[r][i][t]), facecolor='C{}'.format(i%10))
            if schedule.task_resource_usage[r][i][schedule.task_starts[i]] > 0.001:
                axs[r].text(schedule.task_starts[i] + duration/2, bottom + schedule.task_resource_usage[r][i][t]/2, i, color = 'black')
            tasks_plotted.append(i)
    plt.savefig('gantt_plots/{}_gantt_plot.png'.format(project.name))    
    

    for i in N:
        print('w[{}]='.format(i), sum([schedule.task_resource_usage[0][i][t] for t in range(project.T_max)]))

