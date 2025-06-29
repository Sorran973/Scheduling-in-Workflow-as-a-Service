class Analyzer:
    @staticmethod
    def analyze_allocation(allocation, cjm_workflow_list):
        log = allocation.log
        log["vm_all_time"] = (log["vm_end"] - log["vm_start"])
        log["vm_processing_time"] = (log["task_allocation_end"] - log["task_allocation_start"])
        log["vm_setting_time"] = (log["vm_all_time"] - log["vm_processing_time"] - log["vm_input_time"] - log["vm_output_time"])
        log["vm_all_time"] = (log["vm_all_time"] + log["idle_time"])

        workload_time = log.vm_end.max() - log.vm_start.min()
        workload_time_without_first_and_last_vm = log.task_allocation_end.max() - log.task_allocation_start.min()
        workflow_log_list = []

        total_vm_num = len(log.vm_id)
        general_usage_vm_type = log.groupby('vm_type').size() # num of tasks that used
        vm_id_df = log[['vm_id', 'vm_type']]
        distinct_vm = vm_id_df.drop_duplicates()
        distinct_vm_num = len(distinct_vm)
        distinct_usage_vm_type = distinct_vm.groupby('vm_type').size()

        log_x = log[(log['vm_type'] == 'x')]
        total_time_x = log_x["vm_all_time"].sum()
        usage_vm_type_x = log_x.groupby(['vm_id'], as_index=False).size()
        n_total_vm_type_x = len(usage_vm_type_x)
        usage_vm_type_x["without_off"] = usage_vm_type_x["size"] - 1
        n_reuse_vm_type_x = len(usage_vm_type_x[(usage_vm_type_x["without_off"] > 1)])

        log_1X = log[(log['vm_type'] == '1X')]
        total_time_1X = log_1X["vm_all_time"].sum()
        usage_vm_type_1X = log_1X.groupby(['vm_id'], as_index=False).size()
        usage_vm_type_1X["without_off"] = usage_vm_type_1X["size"] - 1
        n_total_vm_type_1X = len(usage_vm_type_1X)
        n_reuse_vm_type_1X = len(usage_vm_type_1X[(usage_vm_type_1X["without_off"] > 1)])

        log_2X = log[(log['vm_type'] == '2X')]
        total_time_2X = log_2X["vm_all_time"].sum()
        usage_vm_type_2X = log_2X.groupby(['vm_id'], as_index=False).size()
        usage_vm_type_2X["without_off"] = usage_vm_type_2X["size"] - 1
        n_total_vm_type_2X = len(usage_vm_type_2X)
        n_reuse_vm_type_2X = len(usage_vm_type_2X[(usage_vm_type_2X["without_off"] > 1)])

        log_3X = log[(log['vm_type'] == '3X')]
        total_time_3X = log_3X["vm_all_time"].sum()
        usage_vm_type_3X = log_3X.groupby(['vm_id'], as_index=False).size()
        usage_vm_type_3X["without_off"] = usage_vm_type_3X["size"] - 1
        n_total_vm_type_3X = len(usage_vm_type_3X)
        n_reuse_vm_type_3X = len(usage_vm_type_3X[(usage_vm_type_3X["without_off"] > 1)])

        log_XXX = log[(log['vm_type'] == 'XXX')]
        total_time_XXX = log_XXX["vm_all_time"].sum()
        usage_vm_type_XXX = log_XXX.groupby(['vm_id'], as_index=False).size()
        usage_vm_type_XXX["without_off"] = usage_vm_type_XXX["size"] - 1
        n_total_vm_type_XXX = len(usage_vm_type_XXX)
        n_reuse_vm_type_XXX = len(usage_vm_type_XXX[(usage_vm_type_XXX["without_off"] > 1)])

        # workload_total_time = total_time_x + total_time_1X + total_time_2X + total_time_3X + total_time_XXX
        # time_percentage_x = total_time_x * 100 / workload_total_time
        # time_percentage_1X = total_time_1X * 100 / workload_total_time
        # time_percentage_2X = total_time_2X * 100 / workload_total_time
        # time_percentage_3X = total_time_3X * 100 / workload_total_time
        # time_percentage_XXX = total_time_XXX * 100 / workload_total_time



        for i in range(len(allocation.cost_of_workflow)): # num of workflow_id
            workflow_log = log[(log["workflow_id"] == i)]
            vm = workflow_log[["vm_input_time", "vm_output_time", "vm_all_time", "vm_processing_time", "vm_setting_time"]]
            vm['index'] = workflow_log['vm_id']
            vm.set_index('index', inplace=True)
            vm_distinct = vm.groupby("index").agg(lambda x: sum(x))
            vm_distinct["vm_utilization_percentage"] = ((vm_distinct["vm_processing_time"] +
                                                         vm_distinct["vm_input_time"] +
                                                         vm_distinct["vm_output_time"]) * 100 / vm_distinct["vm_all_time"])
            avg = round(vm_distinct["vm_utilization_percentage"].mean(), 1)
            # print(f"\tWorkflow VM utilization_percentage: {avg}")
            workflow_log_list.append(workflow_log)
            # print()


        num_workflow_deadline_met = 0
        total_cost = 0
        sum_of_workflows_time_total = 0
        sum_of_workflows_time_without_first_and_last_vm = 0
        only_task_time_total = 0
        only_vm_time_total = 0
        total_num_leased_vm = 0
        total_idle_time = 0

        for i, workflow_log in enumerate(workflow_log_list):
            workflow_time_without_first_and_last_vm = workflow_log.task_allocation_end.max() - workflow_log.task_allocation_start.min()
            if workflow_time_without_first_and_last_vm <= cjm_workflow_list[i]:
                num_workflow_deadline_met += 1

        #     vm_provisioning_delay
            total_cost += workflow_log.allocation_cost.sum()
            sum_of_workflows_time_total += workflow_log.vm_end.max() - workflow_log.vm_start.min()
            sum_of_workflows_time_without_first_and_last_vm += workflow_time_without_first_and_last_vm
            only_task_time_total += workflow_log.vm_processing_time.sum()
            only_vm_time_total += workflow_log.vm_all_time.sum()
            total_num_leased_vm += len(workflow_log.vm_id.drop_duplicates())
            total_idle_time += workflow_log.idle_time.sum()
        #     average_vm_utilization #???

        #     cost | arrival_rate(num_vorkflow/minute = 0.2, 0.5, 1.0, 2.0, 6.0, 12.0)
        #     percentage_workflow_deadline_met | arrival_rate(num_vorkflow / minute)
        #     num_leased_vm | arrival_rate(num_vorkflow / minute)
        percentage_workflow_deadline_met = num_workflow_deadline_met * 100 / allocation.num_workflows

        allocation.num_workflow_deadline_met = num_workflow_deadline_met
        allocation.percentage_workflow_deadline_met = percentage_workflow_deadline_met
        allocation.total_cost = total_cost
        allocation.workload_time = workload_time
        allocation.workload_time_without_first_and_last_vm = workload_time_without_first_and_last_vm
        allocation.sum_of_workflows_time_total = sum_of_workflows_time_total
        allocation.sum_of_workflows_time_without_first_and_last_vm = sum_of_workflows_time_without_first_and_last_vm
        allocation.only_vm_time_total = only_vm_time_total
        allocation.only_task_time_total = only_task_time_total
        # allocation.total_num_leased_vm = total_num_leased_vm
        allocation.total_num_leased_vm = distinct_vm_num
        allocation.total_idle_time = total_idle_time
        allocation.total_data_input_time = log.vm_input_time.sum()
        allocation.total_data_output_time = log.vm_output_time.sum()
        allocation.total_vm_setting_time = log.vm_setting_time.sum()

        print("Total Workload Statistics:")
        print(f"\tTotal number of workflows: {allocation.__class__}")
        print(f"\tTotal number of workflows: {allocation.num_workflows}")
        print(f"\tTotal number of deadlines met: {allocation.num_workflow_deadline_met}")
        print(f"\tPercentage of deadlines met: {allocation.percentage_workflow_deadline_met}")
        print(f"\tTotal cost: {allocation.total_cost}")
        print(f"\tWorkload Time: {allocation.workload_time}")
        # print(f"\tWorkload Time (without the first VM preparation time and the last VM shutdown time): {allocation.workload_time_without_first_and_last_vm}")
        # print(f"\tThe sum of all workflows time total: {allocation.sum_of_workflows_time_total}")
        # print(f"\tThe sum of all workflows time (without the first VM preparation time and the last VM shutdown time): {allocation.sum_of_workflows_time_without_first_and_last_vm}")
        print(f"\tThe sum of only vms time: {allocation.only_vm_time_total}")
        print(f"\tThe sum of only tasks time: {allocation.only_task_time_total}")
        print(f"\tTotal number of leased VM: {allocation.total_num_leased_vm}")
        print(f"\tTotal idle time: {allocation.total_idle_time}")
        print(f"\tTotal data input time: {allocation.total_data_input_time}")
        print(f"\tTotal data output time: {allocation.total_data_output_time}")
        print(f"\tTotal VM setting time: {allocation.total_vm_setting_time}")
        print(f"\tNum of usage / reuse vm_type x: {n_total_vm_type_x} / {n_reuse_vm_type_x}")
        print(f"\tNum of usage / reuse vm_type 1X: {n_total_vm_type_1X} / {n_reuse_vm_type_1X}")
        print(f"\tNum of usage / reuse vm_type 2X: {n_total_vm_type_2X} / {n_reuse_vm_type_2X}")
        print(f"\tNum of usage / reuse vm_type 3X: {n_total_vm_type_3X} / {n_reuse_vm_type_3X}")
        print(f"\tNum of usage / reuse vm_type XXX: {n_total_vm_type_XXX} / {n_reuse_vm_type_XXX}")
        # print(f"\tTime percentage vm_type x: {time_percentage_x}")
        # print(f"\tTime percentage vm_type 1X: {time_percentage_1X}")
        # print(f"\tTime percentage vm_type 2X: {time_percentage_2X}")
        # print(f"\tTime percentage vm_type 3X: {time_percentage_3X}")
        # print(f"\tTime percentage vm_type XXX: {time_percentage_XXX}")
        print()




    @staticmethod
    def print_workload_statistics(allocations):
        print("Total Workload Statistics:")
        for allocation in allocations:
            print(f"\tTotal number of workflows: {allocation.__class__}")
            print(f"\tTotal number of workflows: {allocation.num_workflows}")
            print(f"\tTotal number of deadlines met: {allocation.num_workflow_deadline_met}")
            print(f"\tPercentage of deadlines met: {allocation.percentage_workflow_deadline_met}")
            print(f"\tTotal cost: {allocation.total_cost}")
            print(f"\tWorkload Time: {allocation.workload_time}")
            # print(f"\tWorkload Time (without the first VM preparation time and the last VM shutdown time): {allocation.workload_time_without_first_and_last_vm}")
            # print(f"\tThe sum of all workflows time total: {allocation.sum_of_workflows_time_total}")
            # print(f"\tThe sum of all workflows time (without the first VM preparation time and the last VM shutdown time): {allocation.sum_of_workflows_time_without_first_and_last_vm}")
            print(f"\tThe sum of only vms time: {allocation.only_vm_time_total}")
            print(f"\tThe sum of only tasks time: {allocation.only_task_time_total}")
            print(f"\tTotal number of leased VM: {allocation.total_num_leased_vm}")
            print(f"\tTotal idle time: {allocation.total_idle_time}")
            print()

    @staticmethod
    def print_comparison_table(allocations):

        print(f"\tTotal cost of FTL: {allocations[0].total_cost}")
        print(f"\tTotal cost of ASAP: {allocations[1].total_cost}")
        print(f"\tTotal cost of ASAP_MIX: {allocations[2].total_cost}")
        print(f"\tTotal cost of New_VM: {allocations[3].total_cost}")
        print()
        print(f"\tWorkload Time of FTL: {allocations[0].workload_time}")
        print(f"\tWorkload Time of ASAP: {allocations[1].workload_time}")
        print(f"\tWorkload Time of ASAP_MIX: {allocations[2].workload_time}")
        print(f"\tWorkload Time of New_VM: {allocations[3].workload_time}")
        print()
        print(f"\tTotal number of leased VM of FTL: {allocations[0].total_num_leased_vm}")
        print(f"\tTotal number of leased VM of ASAP: {allocations[1].total_num_leased_vm}")
        print(f"\tTotal number of leased VM of ASAP_MIX: {allocations[2].total_num_leased_vm}")
        print(f"\tTotal number of leased VM of New_VM: {allocations[3].total_num_leased_vm}")
        print()
        print(f"\tTotal idle time of FTL: {allocations[0].total_idle_time}")
        print(f"\tTotal idle time of ASAP: {allocations[1].total_idle_time}")
        print(f"\tTotal idle time of ASAP_MIX: {allocations[2].total_idle_time}")
        print(f"\tTotal idle time of New_VM: {allocations[3].total_idle_time}")
        print()

