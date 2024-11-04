from CloudPlatform import CloudPlatform
from SchedulingModule.CJM.Criteria.Criteria import Criteria, TimeCriteria, AverageResourceLoadCriteria
from Utils.CSV.CSVHandler import CSVHandler
from SchedulingModule.CJM.Workflow import Workflow
import Utils.CloudConfiguration




if __name__ == '__main__':
    TEST_1_12 = 'JobExamples/test1_12.xml'

    MONTAGE50 = 'JobExamples/MONTAGE.n.50.0.dax'
    MONTAGE100 = 'JobExamples/MONTAGE.n.100.0.dax'
    MONTAGE500 = 'JobExamples/MONTAGE.n.500.0.dax'
    MONTAGE1000 = 'JobExamples/MONTAGE.n.1000.1.dax'

    CYBERSHAKE50 = 'JobExamples/CYBERSHAKE.n.50.0.dax'
    CYBERSHAKE100 = 'JobExamples/CYBERSHAKE.n.100.0.dax'
    CYBERSHAKE500 = 'JobExamples/CYBERSHAKE.n.500.0.dax'

    GENOME50 = 'JobExamples/GENOME.n.50.0.dax'
    GENOME100 = 'JobExamples/GENOME.n.100.0.dax'
    GENOME500 = 'JobExamples/GENOME.n.500.0.dax'

    LIGO50 = 'JobExamples/LIGO.n.50.0.dax'
    LIGO100 = 'JobExamples/LIGO.n.100.0.dax'
    LIGO500 = 'JobExamples/LIGO.n.500.0.dax'

    SIPHT50 = 'JobExamples/SIPHT.n.50.0.dax'
    SIPHT100 = 'JobExamples/SIPHT.n.100.0.dax'
    SIPHT500 = 'JobExamples/SIPHT.n.500.0.dax'
    ########################################################################################################################

    T = None
    MULTIPLE_STRATEGIES = False
    SCHEDULING_OPTIMIZATION_CRITERIA = 'max'
    # SCHEDULING_OPTIMIZATION_CRITERIA = 'min'

    CRITERIA: Criteria = AverageResourceLoadCriteria(SCHEDULING_OPTIMIZATION_CRITERIA)
    # CRITERIA: Criteria = TimeCriteria(SCHEDULING_OPTIMIZATION_CRITERIA)
    # CRITERIA: Criteria = CostCriteria(SCHEDULING_OPTIMIZATION_CRITERIA)

    ALLOCATION_OPTIMIZATION_CRITERIA = 'min'
    # ALLOCATION_OPTIMIZATION_CRITERIA = 'max' #????
    ########################################################################################################################

    workflow_examples = (MONTAGE50, MONTAGE100, MONTAGE500, MONTAGE1000,
                         CYBERSHAKE50, CYBERSHAKE100, CYBERSHAKE500,
                         GENOME50, GENOME100, GENOME500,
                         LIGO50, LIGO100, LIGO500,
                         SIPHT50, SIPHT100, SIPHT500)

    cloud_platform = CloudPlatform()
    # workflow_set = WorkflowSet()
    cloud_platform.add_workflow(Workflow(MONTAGE50,
                                      T,
                                      CRITERIA,
                                      MULTIPLE_STRATEGIES,
                                      1,
                                      1),
                                ALLOCATION_OPTIMIZATION_CRITERIA)
    # cloud_platform.add_workflow(Workflow(MONTAGE100,
    #                                   T,
    #                                   CRITERIA,
    #                                   MULTIPLE_STRATEGIES,
    #                                   1,
    #                                   1),
    #                             ALLOCATION_OPTIMIZATION_CRITERIA)
    cloud_platform.run()
    cloud_platform.get_cloud_result()




    # workflow_set.addWorkflow(Workflow(LIGO50, criteria, task_volume_multiplier=1, data_volume_multiplier=1, start_time=0))
    # workflow_set.addWorkflow(Workflow(MONTAGE1000, criteria, task_volume_multiplier=10, data_volume_multiplier=10, start_time=0))
    # workflow_set.addWorkflow(Workflow(LIGO50, criteria, task_volume_multiplier=1, data_volume_multiplier=1, start_time=0))
    # workflow_set.addWorkflow(Workflow(SIPHT50, criteria, task_volume_multiplier=1, data_volume_multiplier=1, start_time=0))
    # workflow_set.addWorkflow(Workflow(GENOME50, criteria, task_volume_multiplier=1, data_volume_multiplier=1, start_time=0))
    # workflow_set.addWorkflow(Workflow(CYBERSHAKE50, criteria, task_volume_multiplier=1, data_volume_multiplier=1, start_time=0))

    # workflow_set.addWorkflow(Workflow(MONTAGE50, criteria, 10, 10, 0))
    # workflow_set.addWorkflow(Workflow(MONTAGE50, criteria, 10, 10, 55))
    # workflow_set.addWorkflow(Workflow(MONTAGE50, criteria, 10, 10, 110))
    # workflow_set.addWorkflow(Workflow(MONTAGE50, criteria, 10, 10, 230))

    # workflow_set.addWorkflow(Workflow(MONTAGE50, criteria, 10, 10, 0))
    # workflow_set.addWorkflow(Workflow(MONTAGE50, criteria, 10, 10, 0))
    # workflow_set.addWorkflow(Workflow(MONTAGE50, criteria, 10, 10, 0))
    # workflow_set.addWorkflow(Workflow(MONTAGE50, criteria, 10, 10, 0))

    # workflow_set.addWorkflow(
    #     Workflow(MONTAGE50, criteria, task_volume_multiplier=100, data_volume_multiplier=100, start_time=3000))
    # workflow_set.addWorkflow(
    #     Workflow(CYBERSHAKE50, criteria, task_volume_multiplier=15, data_volume_multiplier=0, start_time=500))
    # workflow_set.addWorkflow(
    #     Workflow(SIPHT50, criteria, task_volume_multiplier=2, data_volume_multiplier=5, start_time=5000))
    # workflow_set.addWorkflow(
    #     Workflow(LIGO50, criteria, task_volume_multiplier=10, data_volume_multiplier=15, start_time=1000))
    # workflow_set.addWorkflow(
    #     Workflow(GENOME50, criteria, task_volume_multiplier=1, data_volume_multiplier=1, start_time=0))

    # workflow_set.addWorkflow(Workflow(MONTAGE50, criteria, task_volume_multiplier=100, data_volume_multiplier=100, start_time=0))
    # workflow_set.addWorkflow(Workflow(CYBERSHAKE50, criteria, task_volume_multiplier=15, data_volume_multiplier=0, start_time=-0))
    # workflow_set.addWorkflow(Workflow(SIPHT50, criteria, task_volume_multiplier=2.5, data_volume_multiplier=1, start_time=0))
    # workflow_set.addWorkflow(Workflow(LIGO50, criteria, task_volume_multiplier=10, data_volume_multiplier=10, start_time=0))
    # workflow_set.addWorkflow(Workflow(GENOME50, criteria, task_volume_multiplier=0.61, data_volume_multiplier=1, start_time=0))
