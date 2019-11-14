import luigi
from luigi.parameter import ParameterVisibility
from unluigi.util import monitor_tools


class MonitorExperiment():
    def __init__(self, *args, **kwargs):
        task_id = self.get_task_id()
        print("Experiment root task id: " + str(task_id))

    def get_task_id(self):
        if "monitor_task_id" not in self.__dict__:
            self.monitor_task_id = monitor_tools.ensure_task(self, True)
        return self.monitor_task_id

    def get_task_name(self):
        raise Exception("Need to define get_task_name for class " +
                        str(self.get_task_family()))


class MonitorTask():
    parent_id = luigi.IntParameter(visibility=ParameterVisibility.HIDDEN)
    root_task = luigi.BoolParameter(default=False,
                                    visibility=ParameterVisibility.HIDDEN)

    def __init__(self, *args, **kwargs):
        self.get_task_id()

    def get_task_id(self):
        if "monitor_task_id" not in self.__dict__:
            self.monitor_task_id = monitor_tools.ensure_task(self,
                                                             root_task=True)
        return self.monitor_task_id

    def get_task_name(self):
        raise Exception("Need to define get_task_name for class " +
                        str(self.get_task_family()))
