import os
import sys

import pandas as pd
from pyvis.network import Network
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from matplotlib.patches import Patch

from Visualization.Drawer import Drawer


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
                G.add_edge(edge.source_node.id, edge.destination_node.id, title=str(edge.transfer_time), label=str(edge.id))



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
            ax.barh(task.name, task.interval, left=task.start, color=task.color, alpha=0.3)
            ax.barh(task.name, task.calc_time, left=task.possible_start, color=task.color)
            ax.barh(task.name, task.calc_time, left=task.latest_start, color=task.color, fill=False, hatch='///')

            ax.text(task.end + 0.1, rownum, task.batch, va='center', alpha=0.8)
            ax.text(task.start - 0.1, rownum, task.name, va='center', ha='right', alpha=0.7)
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

        plt.suptitle('SCHEDULE')

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

        plt.show()


    def draw_result_gantt(self, log):
        # fig, (ax, ax1) = plt.subplots(2, figsize=(16, 6), gridspec_kw={'height_ratios': [6, 1]})
        fig, ax = plt.subplots(figsize=(36, 16))

        rownum = 0
        for index, row in log.iterrows():
            # calc_time
            ax.barh(rownum, row.task_allocation_end - row.task_allocation_start, left=row.task_allocation_start,
                    color=row.color)
            # interval
            ax.barh(rownum, row.interval, left=row.task_start, color=row.color, alpha=0.3)
            # vm_time
            ax.barh(rownum, row.vm_end - row.vm_start, left=row.vm_start, color=row.color, alpha=0.6, fill=False,
                    hatch='///')
            # ax.barh(log.task_name, log.vm_end - log.vm_start, left=log.vm_start, color=log.color, alpha=0.6, fill=True,
            #         linewidth=10, edgecolor=log.color)
            ax.text(row.vm_end + 0.1, rownum, 'VM_' + str(row.vm_id), va='center')
            ax.text(row.vm_start - 0.1, rownum, row.task_name, va='center', ha='right')
            ax.text(row.task_allocation_start + (row.task_allocation_end - row.task_allocation_start)/2, rownum, row.task_batch, va='center')
            rownum += 1

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

        plt.suptitle('SCHEDULE')
        plt.show()
