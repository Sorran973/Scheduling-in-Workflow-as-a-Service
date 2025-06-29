import pandas as pd
from pyvis.network import Network
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from matplotlib.patches import Patch

import Utils.Configuration
from Utils import Configuration
from Utils.Visualization.Drawer import Drawer


def rand_color(row):
    import secrets
    s = "#"
    x = 0
    while x < 6:
        s += secrets.choice("0123456789ABCDEF")
        x += 1
    return s


class PyvisDrawer(Drawer):

    GRAPH_OUTPUT = 'Output/pyvis_graph.html'

    def draw_graph(self, nodes, edges):
        # G = Network(directed=True)
        G = nx.DiGraph()

        group_id = 0
        # level = 0
        for arr_nodes in nodes:
            for node in arr_nodes:
                G.add_node(node.id, size=10, label=str(node.id), title=node.name, group=group_id)
            #     level=
            group_id += 1
            # level += 1

        for arr_edges in edges:
            for edge in arr_edges:
                G.add_edge(edge.node_from.id, edge.node_to.id, title=str(edge.transfer_time), label=str(edge.id))



        network = Network(height="750px", width="100%", directed=True,
                          bgcolor="white", font_color="black", layout=True)
        # network.show_buttons(filter_=['layout', 'interaction', 'manipulation', 'physics'])

        network.set_options('var options = { "layout": { "hierarchical": { "enabled" : true, '
                            '"levelSeparation" : 150, "nodeSpacing" : 100, "treeSpacing" : 200, '
                            '"blockShifting" : true, "edgeMinimization" : true, "parentCentralization": true, '
                            '"direction" : "UD", "sortMethod" : "directed", "shakeTowards" : "roots"} } }')

        network.from_nx(G)
        network.show(self.GRAPH_OUTPUT)


    def draw_gantt(self, nodes):

        arr_color = ['tab:blue', 'tab:orange', 'tab:red', 'tab:green', 'tab:purple', 'tab:brown', 'tab:pink',
                     'tab:gray', 'tab:olive', 'tab:cyan']
        fig, ax = plt.subplots()

        yticks = []
        y_labels = []
        num_nodes = 0
        for arr in nodes:
            num_nodes += len(arr)

        i = 0
        for arr in nodes:
            for node in arr:
                if node.name != "entry" and node.name != "finish":
                    ax.broken_barh([(node.start_time, node.finish_time - node.start_time)], (num_nodes, 0.8), facecolors=arr_color[i])
                    num_nodes -= 1

                    yticks.append(num_nodes + 2)
                    y_labels.append(node.id - 1)
            i += 1


        ax.set_ylim(0, num_nodes)
        ax.set_xlim(0, nodes[-1][-2].finish_time)
        ax.set_xlabel('time')
        ax.set_ylabel('tasks')
        ax.set_yticks(yticks, labels=y_labels)
        ax.grid(False)

        # plt.yticks([])
        plt.show()
        fig.savefig(self.GANTT_OUTPUT, format="pdf")


    def draw_new_gantt(self, nodes):
        arr_color = ['tab:green', 'tab:blue', 'tab:orange', 'tab:red', 'tab:purple', 'tab:brown', 'tab:pink',
                     'tab:gray', 'tab:olive', 'tab:cyan']

        fig, (ax, ax1) = plt.subplots(2, figsize=(16, 6), gridspec_kw={'height_ratios': [6, 1]})

        num_nodes = 0
        global_num_nodes = 0
        for arr in nodes:
            num_nodes += len(arr)
            global_num_nodes += len(arr)

        i = 0
        for arr in nodes:
            for node in arr:
                if node.name != "entry" and node.name != "finish":
                    ax.barh(node.name, node.finish_time - node.start_time, left=node.start_time, color=arr_color[i], alpha=0.3)
                    ax.text(node.start_time - 0.1, node.id, node.id, va='center', ha='right', alpha=0.7)

                    num_nodes -= 1

                    # yticks.append(num_nodes + 2)
                    # y_labels.append(node.id - 1)
            i += 1


        # grid lines
        ax.set_axisbelow(True)
        ax.xaxis.grid(color='gray', linestyle='dashed', alpha=0.2, which='both')

        # ticks
        xticks = np.arange(0, nodes[-1][-2].finish_time + 1, (int)((global_num_nodes - 2) /5))
        # xticks_labels = pd.date_range(0, end=df.end.max()).strftime("%m/%d")
        xticks_minor = np.arange(0, nodes[-1][-2].finish_time + 1, 1)
        ax.set_xticks(xticks)
        # ax.set_xticks(xticks_minor, minor=True)
        ax.set_yticks([])

        # remove spines
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['left'].set_position(('outward', 10))
        ax.spines['top'].set_visible(False)

        plt.suptitle('INTERVALS')

        ##### LEGENDS #####
        # legend_elements = [Patch(facecolor='#E64646', label='Leader'),
        #                    Patch(facecolor='#34D05C', label='Batch')]
        #
        # ax1.legend(handles=legend_elements, loc='upper center', ncol=5, frameon=False)

        # clean second axis
        ax1.spines['right'].set_visible(False)
        ax1.spines['left'].set_visible(False)
        ax1.spines['top'].set_visible(False)
        ax1.spines['bottom'].set_visible(False)
        ax1.set_xticks([])
        ax1.set_yticks([])

        plt.show()



    def draw_batches_gantt(self, tasks):
        c_dict = {'Leader': '#E64646', 'Batch': '#34D05C', 'CPU 2': '#E69646', 'CPU 4': '#34D0C3', 'CPU 5': '#3475D0',
                  'None': '#000000', 'IO': '#44D05C'}
        for task in tasks:
            task.color = c_dict[task.status]

        ##### PLOT #####
        fig, (ax, ax1) = plt.subplots(2, figsize=(36, 16), gridspec_kw={'height_ratios': [15, 1]})

        # bars
        rownum = 0
        for task in tasks:
            ax.barh(rownum, task.interval, left=task.start, color=task.color, alpha=0.3)
            ax.barh(rownum, task.calc_time, left=task.possible_start, color=task.color)
            # ax.barh(rownum, task.calc_time, left=task.latest_start, color=task.color, fill=False, hatch='///')

            ax.text(task.end + 0.1, rownum, task.batch, va='center', alpha=0.8)
            ax.text(task.start - 0.1, rownum, task.id, va='center', ha='right', alpha=0.7)
            rownum += 1


        # grid lines
        ax.set_axisbelow(True)
        ax.xaxis.grid(color='gray', linestyle='dashed', alpha=0.2, which='both')

        # ticks
        end_max = max(tasks, key=lambda x: x.end).end
        xticks = np.arange(0, end_max + 1, int((end_max + 1) / 5))
        # xticks_labels = pd.date_range(0, end=tasks.end.max()).strftime("%m/%d")
        # xticks_minor = np.arange(0, tasks.end.max() + 1, 1)
        ax.set_xticks(xticks)
        # ax.set_xticks(xticks_minor, minor=True)
        ax.set_yticks([])

        # remove spines
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['left'].set_position(('outward', 10))
        ax.spines['top'].set_visible(False)


        ##### LEGENDS #####
        legend_elements = [Patch(facecolor='#E64646', label='Leader'),
                           Patch(facecolor='#34D05C', label='Batch')]

        ax1.legend(handles=legend_elements, loc='upper center', ncol=5, frameon=False)

        # clean second axis
        ax1.spines['right'].set_visible(False)
        ax1.spines['left'].set_visible(False)
        ax1.spines['top'].set_visible(False)
        ax1.spines['bottom'].set_visible(False)
        ax1.set_xticks([])
        ax1.set_yticks([])

        plt.suptitle(Utils.Configuration.CJM_CRITERIA.__class__.__name__ + " " +
                     Utils.Configuration.SCHEDULING_OPTIMIZATION_CRITERIA + " " +
                     Utils.Configuration.VMA_CRITERIA.__class__.__name__ + " " +
                     Utils.Configuration.ALLOCATION_OPTIMIZATION_CRITERIA)
        plt.show()
        fig.savefig(Utils.Configuration.GANTT_FIGURES_BATCHES, format="pdf")


    def draw_batches_gantt_for_mixed(self, tasks):
        c_dict = {'Leader': '#E64646', 'Batch': '#34D05C', 'CPU 2': '#E69646', 'CPU 4': '#34D0C3', 'CPU 5': '#3475D0',
                  'None': '#000000', 'IO': '#44D05C'}
        for task in tasks:
            task.color = c_dict[task.status]

        ##### PLOT #####
        fig, (ax, ax1) = plt.subplots(2, figsize=(36, 16), gridspec_kw={'height_ratios': [15, 1]})

        # bars
        rownum = 0
        for task in tasks:
            ax.barh(rownum, task.interval, left=task.start, color=task.color, alpha=0.3)
            ax.barh(rownum, task.calc_time, left=task.start, color=task.color)
            # ax.barh(rownum, task.calc_time, left=task.latest_start, color=task.color, fill=False, hatch='///')

            ax.text(task.end + 0.1, rownum, task.batch, va='center', alpha=0.8)
            ax.text(task.start - 0.1, rownum, task.id, va='center', ha='right', alpha=0.7)
            rownum += 1


        # grid lines
        ax.set_axisbelow(True)
        ax.xaxis.grid(color='gray', linestyle='dashed', alpha=0.2, which='both')

        # ticks
        end_max = max(tasks, key=lambda x: x.end).end
        xticks = np.arange(0, end_max + 1, int((end_max + 1) / 5))
        # xticks_labels = pd.date_range(0, end=tasks.end.max()).strftime("%m/%d")
        # xticks_minor = np.arange(0, tasks.end.max() + 1, 1)
        ax.set_xticks(xticks)
        # ax.set_xticks(xticks_minor, minor=True)
        ax.set_yticks([])

        # remove spines
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['left'].set_position(('outward', 10))
        ax.spines['top'].set_visible(False)


        ##### LEGENDS #####
        legend_elements = [Patch(facecolor='#E64646', label='Leader'),
                           Patch(facecolor='#34D05C', label='Batch')]

        ax1.legend(handles=legend_elements, loc='upper center', ncol=5, frameon=False)

        # clean second axis
        ax1.spines['right'].set_visible(False)
        ax1.spines['left'].set_visible(False)
        ax1.spines['top'].set_visible(False)
        ax1.spines['bottom'].set_visible(False)
        ax1.set_xticks([])
        ax1.set_yticks([])

        plt.suptitle(Utils.Configuration.CJM_CRITERIA.__class__.__name__ + " " +
                     Utils.Configuration.SCHEDULING_OPTIMIZATION_CRITERIA + " " +
                     Utils.Configuration.VMA_CRITERIA.__class__.__name__ + " " +
                     Utils.Configuration.ALLOCATION_OPTIMIZATION_CRITERIA)
        plt.show()
        fig.savefig(Utils.Configuration.GANTT_FIGURES_BATCHES, format="pdf")

    def draw_big_batches_gantt(self, tasks, figure_name):
        c_dict = {'Leader': '#E64646', 'Batch': '#34D05C', 'CPU 2': '#E69646', 'CPU 4': '#34D0C3', 'CPU 5': '#3475D0',
                  'None': '#000000', 'IO': '#44D05C'}
        for task in tasks:
            task.color = c_dict[task.status]

        ##### PLOT #####
        # fig, (ax, ax1) = plt.subplots(2, figsize=(36, 16), gridspec_kw={'height_ratios': [15, 1]})
        fig, ax = plt.subplots(figsize=(640, 640))


        # bars
        rownum = 0
        for task in tasks:
            ax.barh(rownum, task.interval, left=task.start, color=task.color, alpha=0.3)
            ax.barh(rownum, task.calc_time, left=task.possible_start, color=task.color)
            # ax.barh(rownum, task.calc_time, left=task.latest_start, color=task.color, fill=False, hatch='///')

            ax.text(task.end + 0.1, rownum, task.batch, va='center', alpha=0.8)
            ax.text(task.start - 0.1, rownum, task.id, va='center', ha='right', alpha=0.7)
            rownum += 1


        # grid lines
        ax.set_axisbelow(True)
        ax.xaxis.grid(color='gray', linestyle='dashed', alpha=0.2, which='both')

        # ticks
        end_max = max(tasks, key=lambda x: x.end).end
        xticks = np.arange(0, end_max, int(end_max / 5))
        # xticks_labels = pd.date_range(0, end=tasks.end.max()).strftime("%m/%d")
        # xticks_minor = np.arange(0, tasks.end.max() + 1, 1)
        ax.set_xticks(xticks)
        # ax.set_xticks(xticks_minor, minor=True)
        ax.set_yticks([])

        # remove spines
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['left'].set_position(('outward', 10))
        ax.spines['top'].set_visible(False)

        plt.suptitle(Utils.Configuration.CJM_CRITERIA.__class__.__name__ + " " +
                     Utils.Configuration.SCHEDULING_OPTIMIZATION_CRITERIA + " " +
                     Utils.Configuration.VMA_CRITERIA.__class__.__name__ + " " +
                     Utils.Configuration.ALLOCATION_OPTIMIZATION_CRITERIA)

        fig.savefig(figure_name, format="pdf", bbox_inches='tight')


    def draw_result_gantt(self, log, figure_name):
        # fig, (ax, ax1) = plt.subplots(2, figsize=(16, 6), gridspec_kw={'height_ratios': [6, 1]})
        # fig, ax = plt.subplots(figsize=(76, 46))
        fig, ax = plt.subplots(figsize=(16, 6))
        # fig, ax = plt.subplots(figsize=(108, 48))

        # my_data = [
        #     [0, 0, """5X""", 1, 1, 0, 0.0, 10.0, 10.0, 0.0, 0, 0.0, 10.0, 0, 10.0, 50,0, 'new'],
        #     [0, 0, """5X""", 2, 2, 1, 11.0, 26.0, 15.0, 10.0, 0, 11.0, 26.0, 0, 26.0, 75, 0.0, 'active'],
        #     [0, 0, """5X""", 3, 3, 2, 27.0, 32.0, 5.0, 26.0, 0, 27.0, 32.0, 0, 32.0, 25, 0.0, 'active'],
        #     [0, 10, """5X""", 4, 4, 1, 11.0, 21.0, 10.0, 10.0, 1, 11.0, 21.0, 0, 21.0, 55, 0, 'new'],
        #     [0, 10, """5X""", 6, 6, 2, 22.0, 32.0, 10.0, 21.0, 1, 22.0, 32.0, 0, 32.0, 55, 0.0, 'active'],
        #     [0, 18, """2X""", 5, 5, 1, 11.5, 20.5, 9.0, 10.0, 1.5, 11.5, 20.5, 0, 20.5, 22, 0, 'new']
        # ]
        #
        # df = pd.DataFrame(my_data, columns=['workflow_id', 'vm_id', 'vm_type', 'task_id', 'task_name', 'task_batch', 'task_start',
        #                                  'task_end', 'interval', 'vm_start', 'vm_input_time', 'task_allocation_start',
        #                                  'task_allocation_end', 'vm_output_time', 'vm_end', 'allocation_cost', 'idle_time', 'vm_status'])
        #
        # df["vm_all_time"] = (df["vm_end"] - df["vm_start"])
        # df["vm_processing_time"] = (df["task_allocation_end"] - df["task_allocation_start"])
        # df["vm_setting_time"] = (df["vm_all_time"] - df["vm_processing_time"] - df["vm_input_time"] - df["vm_output_time"])
        # df["vm_all_time"] = (df["vm_all_time"] + df["idle_time"])
        #
        # color = df[["workflow_id"]]
        # color = color.drop_duplicates()
        # color["color"] = color.apply(lambda x: rand_color(x), axis=1)
        # df = pd.merge(df, color, on='workflow_id', how='left')
        # df = df.sort_values(["vm_id", "vm_start"])

        rownum = 0
        for index, row in log.iterrows():
            if row.task_id == 47:
                print()
            # calc_time
            ax.barh(rownum, row.task_allocation_end - row.task_allocation_start, left=row.task_allocation_start,
                    color=row.color)
            # interval
            ax.barh(rownum, row.interval, left=row.task_start, color=row.color, alpha=0.3)
            # vm_time
            ax.barh(rownum, row.vm_end - row.vm_start, left=row.vm_start, color=row.color, alpha=0.6, fill=False,
                    hatch='///') # fill=True, linewidth=10, edgecolor=log.color
            # if row.task_id == 1:
            #     ax.barh(rownum, 1, left=row.vm_end, color=row.color, alpha=0.6, fill=False, hatch='///')
            # if row.task_id == 2:
            #     ax.barh(rownum, 1, left=row.vm_end, color=row.color, alpha=0.6, fill=False, hatch='///')
            # if row.task_id == 4:
            #     ax.barh(rownum, 1, left=row.vm_end, color=row.color, alpha=0.6, fill=False, hatch='///')
            # if row.task_id == 5:
            #     ax.barh(rownum, 1.5, left=row.vm_end, color=row.color, alpha=0.6, fill=False, hatch='///')
            # vm_prepare_and_shutdown_time
            if row.task_name[0] != 'o':
                if row.vm_status == "new":
                    # ax.barh(rownum, row.vm_input_time, left=row.vm_start, color=row.color, alpha=0.6, fill=False, hatch='|||')
                    ax.barh(rownum, Configuration.VM_PREP_TIME, left=row.vm_start, color=row.color, alpha=0.6, fill=False, hatch='|||')
            else:
                ax.barh(rownum, Configuration.VM_SHUTDOWN_TIME, left=row.vm_start, color=row.color, alpha=0.6, fill=False, hatch='|||')
            # idle_time
            ax.barh(rownum, row.idle_time, left=row.vm_start - row.idle_time, color='#000000')

            ax.text(row.vm_end + 0.1, rownum, 'VM_' + str(row.vm_id) + '_' + row.vm_type, va='center')
            ax.text(row.vm_start - 0.1, rownum, str(row.task_id) + '_' + str(row.workflow_id) + '_' + str(row.task_name), va='center', ha='right')
            ax.text(row.task_allocation_start + (row.task_allocation_end - row.task_allocation_start)/2, rownum, row.task_batch, va='center')
            rownum += 1
            # if row.task_id == 1:
            #     ax.text(row.vm_end + 1 + 0.1, rownum, 'VM_' + row.vm_type, va='center')
            #     ax.text(row.vm_start - 0.1, rownum, str(row.task_id), va='center', ha='right')
            #     ax.text(row.task_allocation_start + (row.task_allocation_end - row.task_allocation_start) / 2, rownum,
            #             row.task_batch, va='center')
            # elif row.task_id == 2:
            #     ax.text(row.vm_end + 1 + 0.1, rownum, 'VM_' + row.vm_type, va='center')
            #     ax.text(row.vm_start - 0.1, rownum, str(row.task_id), va='center', ha='right')
            #     ax.text(row.task_allocation_start + (row.task_allocation_end - row.task_allocation_start) / 2, rownum,
            #             row.task_batch, va='center')
            # elif row.task_id == 4:
            #     ax.text(row.vm_end + 1 + 0.1, rownum, 'VM_' + row.vm_type, va='center')
            #     ax.text(row.vm_start - 0.1, rownum, str(row.task_id), va='center', ha='right')
            #     ax.text(row.task_allocation_start + (row.task_allocation_end - row.task_allocation_start) / 2, rownum,
            #             row.task_batch, va='center')
            # elif row.task_id == 5:
            #     ax.text(row.vm_end + 1.5 + 0.1, rownum, 'VM_' + row.vm_type, va='center')
            #     ax.text(row.vm_start - 0.1, rownum, str(row.task_id), va='center', ha='right')
            #     ax.text(row.task_allocation_start + (row.task_allocation_end - row.task_allocation_start) / 2, rownum,
            #             row.task_batch, va='center')
            # else:
            #     ax.text(row.vm_end + 0.1, rownum, 'VM_' + row.vm_type, va='center')
            #     ax.text(row.vm_start - 0.1, rownum, str(row.task_id), va='center', ha='right')
            #     ax.text(row.task_allocation_start + (row.task_allocation_end - row.task_allocation_start) / 2, rownum,
            #             row.task_batch, va='center')
            # rownum += 1

        # grid lines
        # ax.set_axisbelow(True)
        # ax.xaxis.grid(color='gray', linestyle='dashed', alpha=0.2, which='both')

        # ticks
        xticks = np.arange(0, log.task_end.max() + 1, int((log.task_end.max() + 1) / 5))
        xticks_labels = pd.date_range(0, end=log.task_end.max()).strftime("%m/%d")
        # xticks_minor = np.arange(0, tasks.end.max() + 1, 1)
        ax.set_xticks(xticks)
        # ax.set_xticks(xticks_minor, minor=True)
        # ax.set_xticks(, labels=)
        ax.set_yticks([])

        # remove spines
        # ax.spines['right'].set_visible(False)
        # ax.spines['left'].set_visible(False)
        # ax.spines['left'].set_visible(False)
        # ax.spines['top'].set_visible(False)

        plt.suptitle(Utils.Configuration.CJM_CRITERIA.__class__.__name__ + " " +
                     Utils.Configuration.SCHEDULING_OPTIMIZATION_CRITERIA + " " +
                     Utils.Configuration.VMA_CRITERIA.__class__.__name__ + " " +
                     Utils.Configuration.ALLOCATION_OPTIMIZATION_CRITERIA)
        # plt.show()
        fig.savefig(figure_name, format="pdf", bbox_inches='tight')


    def draw_dynamic(self):
        # arrival rate / # of leased VM
        # t = [0.5, 1, 2, 6, 12, 60, 100]
        #
        # s1 = [13226, 13277, 13316, 13279, 13257, 13168, 13168]
        # s2 = [13906, 13906, 13906, 13906, 13906, 13906, 13906]
        # s3 = [3912, 4116, 4334, 4503, 4574, 4619, 4633]
        # s4 = [4955, 4955, 4955, 4955, 4955, 4955, 4955]
        # s5 = [409280, 409486, 409602, 409601, 409586, 409578, 409596]
        # s6 = [409650, 409650, 409650, 409650, 409650, 409650, 409650]

        # axs.set_xlim(0, 60)
        # axs.set_ylim(2500, 6000)
        # axs.set_xlabel('Arrival Rate')
        # axs.set_ylabel('# of leased VM')

        # data volume (all)
        t = [0.01, 0.1, 1, 10, 100]
        costVMA = [713652, 81039, 18035, 12078, 11509]
        costNewVM = [748395, 85276, 18936, 12299, 11721]
        timeVMA = [20849, 2434, 593.5, 409.5, 391.3]
        timeNewVM = [20849, 2435, 593.7, 409.6, 391.5]
        leasedVMA = [4438, 4349, 4213, 4131, 4051]
        leasedNewVM = [4955, 4955, 4955, 4955, 4955]
        idleVMA = [13853, 7019, 3152, 2111, 1525]
        idleNewVM = [0, 0, 0, 0, 0]

        fig, axs = plt.subplots(4, 1, layout='constrained')
        axs[0].plot(t, costVMA, t, costNewVM)
        axs[0].set_xlim(0, 100)
        axs[0].set_ylim(11500, 750000)
        axs[0].set_xlabel('Data Volume (*)')
        axs[0].set_ylabel('Cost (k)')
        axs[0].grid(True)

        axs[1].plot(t, timeVMA, t, timeNewVM)
        axs[1].set_xlim(0, 100)
        axs[1].set_ylim(390, 20850)
        axs[1].set_ylabel('Time (k)')
        axs[1].grid(True)

        axs[2].plot(t, leasedVMA, t, leasedNewVM)
        axs[2].set_xlim(0, 100)
        axs[2].set_ylim(4000, 5000)
        axs[2].set_ylabel('# of leased VM')
        axs[2].grid(True)

        axs[3].plot(t, idleVMA, t, idleNewVM)
        axs[3].set_xlim(0, 100)
        axs[3].set_ylim(1500, 14000)
        axs[3].set_ylabel('Idle Time')
        axs[3].grid(True)


        # data volume / # of leased VM
        # t = [0.01, 0.1, 1.0, 10.0, 100.0]
        # s1 = [177_353, 23_729, 8_265, 6_725, 6_553]
        # s2 = [183_852, 25_521, 9_706, 8_145, 7_995]
        # s3 = [2_175_535, 334_384, 150_189, 131_921, 130_370]
        # s4 = [2_175_915, 334_515, 150_375, 132_284, 130_532]
        # s5 = [4_177, 3_706, 3_228, 3_127, 3_075]
        # s6 = [4_955, 4_955, 4_955, 4_955, 4_955]

        # fig, axs = plt.subplots(4, 1, layout='constrained')
        # axs[0].plot(t, costVMA, t, costNewVM)
        # axs[0].set_xlim(0, 20)
        # axs[0].set_ylim(13100, 14000)
        # axs[0].set_xlabel('Data Volume (*)')
        # axs[0].set_ylabel('Cost (k)')
        # axs[0].grid(True)
        #
        # axs[1].plot(t, s3, t, s4)
        # axs[1].set_xlim(0, 20)
        # axs[1].set_ylim(3800, 5000)
        # axs[1].set_ylabel('Time')
        # axs[1].grid(True)
        #
        # axs[2].plot(t, s5, t, s6)
        # axs[2].set_xlim(0, 20)
        # axs[2].set_ylim(409200, 409700)
        # axs[2].set_ylabel('# of leased VM')
        # axs[2].grid(True)

        # axs[0].plot(t, s1, t, s2)
        # axs[0].set_xlim(0, 10)
        # axs[0].set_ylim(6000, 190000)
        # axs[0].set_ylabel('Cost')
        # axs[0].grid(True)
        #
        # axs[1].plot(t, s3, t, s4)
        # axs[1].set_xlim(0, 10)
        # axs[1].set_ylim(130000, 2200000)
        # axs[1].set_ylabel('Time')
        # axs[1].grid(True)
        #
        # axs[2].plot(t, s5, t, s6)
        # axs[2].set_xlim(0, 10)
        # axs[2].set_ylim(3000, 5500)
        # axs[2].set_xlabel('Data Volume')
        # axs[2].set_ylabel('# of leased VM')
        # axs[2].grid(True)

        plt.show()
        print()

    def draw_charts(self):
        species = ("0.01", "0.1", "1", "10", "100")
        cost = {
            'vma': (713652, 81039, 18035, 12078, 11509),
            'new_vm': (748395, 85276, 18936, 12299, 11721)
        }
        time = {
            'vma': (20849, 2434, 593.5, 409.5, 391.3),
            'new_vm': (20849, 2435, 593.7, 409.6, 391.5)
        }
        leased_vm = {
            'vma': (4438, 4349, 4213, 4131, 4051),
            'new_vm': (4955, 4955, 4955, 4955, 4955)
        }
        idle_time = {
            'vma': (13853, 7019, 3152, 2111, 1525),
            'new_vm': (0, 0, 0, 0, 0)
        }

        cost_max = max(max(cost.values()))
        time_max = max(max(time.values()))
        lease_max = max(max(leased_vm.values()))
        idle_max = max(max(idle_time.values()))

        x = np.arange(len(species))  # the label locations
        width = 0.25  # the width of the bars
        multiplier = 0

        # fig, ax = plt.subplots(layout='constrained')
        fig, axs = plt.subplots(1, 1, layout='constrained')

        # for attribute, measurement in cost.items():
        #     offset = width * multiplier
        #     axs[0].bar(x + offset, measurement, width, label=attribute)
        #     # rects = axs[0].bar(x + offset, measurement, width, label=attribute)
        #     # ax.bar_label(rects, padding=3)
        #     multiplier += 1

        multiplier = 0
        for attribute, measurement in time.items():
            offset = width * multiplier
            axs.bar(x + offset, measurement, width, label=attribute)
            multiplier += 1
        #
        # multiplier = 0
        # for attribute, measurement in time.items():
        #     offset = width * multiplier
        #     axs[2].bar(x + offset, measurement, width, label=attribute)
        #     multiplier += 1
        #
        # multiplier = 0
        # for attribute, measurement in time.items():
        #     offset = width * multiplier
        #     axs[3].bar(x + offset, measurement, width, label=attribute)
        #     multiplier += 1

        # axs[0].set_xlabel('Data Volume (*)')
        # axs[0].set_ylabel('Cost (k)')
        # axs[0].set_xticks(x + width, species)
        # axs[0].legend(loc='center left', bbox_to_anchor=(1, 0.5))
        # axs[0].set_ylim(0, cost_max)

        axs.set_xlabel('Data Volume (*)')
        axs.set_ylabel('Time (k)')
        axs.set_xticks(x + width, species)
        axs.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        axs.set_ylim(0, time_max)

        # axs[0].set_xlabel('Data Volume (*)')
        # axs[2].set_ylabel('# of leased VM')
        # axs[2].set_xticks(x + width, species)
        # axs[2].legend(loc='center left', bbox_to_anchor=(1, 0.5))
        # axs[2].set_ylim(0, lease_max)

        # axs[0].set_xlabel('Data Volume (*)')
        # axs[3].set_ylabel('Idle Time')
        # axs[3].set_xticks(x + width, species)
        # axs[3].legend(loc='center left', bbox_to_anchor=(1, 0.5))
        # axs[3].set_ylim(0, idle_max)


        plt.show()
        print()

    def draw_big_gantt(self, log, figure_name):
        fig, ax = plt.subplots(figsize=(640, 640))

        rownum = 0
        for index, row in log.iterrows():
            if row.task_name[:3] != "off":
                ax.barh(rownum, row.vm_end - row.vm_start, left=row.vm_start, color=row.color) # VM time
                ax.barh(rownum, row.task_allocation_start - row.vm_start, left=row.vm_start, color=row.color, alpha=0.6, fill=False, # data input transfer time
                        hatch='///')  # fill=True, linewidth=10, edgecolor=log.color
                ax.barh(rownum, row.idle_time, left=row.vm_start - row.idle_time, color='#000000') # idle time
                ax.text(row.vm_end + 0.1, rownum, 'VM_' + str(row.vm_id) + '_' + row.vm_type, va='center') # VM description
                ax.text(row.vm_start - 0.1, rownum, str(row.task_id) + '_' + str(row.workflow_id) + '_' + str(row.task_name), va='center', ha='right') # task description
                rownum += 1
            else:
                ax.barh(rownum, row.vm_end - row.vm_start, left=row.vm_start, alpha=0.6, fill=False, # data output transfer time
                        hatch='///')  # fill=True, linewidth=10, edgecolor=log.color
                ax.text(row.vm_end + 0.1, rownum, 'VM_' + str(row.vm_id) + '_' + row.vm_type, va='center')  # VM description
                ax.text(row.vm_start - 0.1, rownum, str(row.task_id) + '_' + str(row.workflow_id) + '_' + str(row.task_name),
                        va='center', ha='right')  # task description
                rownum += 1


        # grid lines
        # ax.set_axisbelow(True)
        # ax.xaxis.grid(color='gray', linestyle='dashed', alpha=0.2, which='both')

        # ticks
        xticks = np.arange(0, log.vm_end.max(), int(log.vm_end.max() / 5))
        # xticks_final = np.append(xticks, log.vm_end.max())
        xticks_labels = pd.date_range(0, end=log.task_end.max()).strftime("%m/%d")
        # xticks_minor = np.arange(0, tasks.end.max() + 1, 1)
        ax.set_xticks(xticks)
        # ax.set_xticks(xticks_minor, minor=True)
        # ax.set_xticks(, labels=)
        ax.set_yticks([])

        # remove spines
        # ax.spines['right'].set_visible(False)
        # ax.spines['left'].set_visible(False)
        # ax.spines['left'].set_visible(False)
        # ax.spines['top'].set_visible(False)
        # plt.show()
        fig.savefig(figure_name, format="pdf", bbox_inches='tight')