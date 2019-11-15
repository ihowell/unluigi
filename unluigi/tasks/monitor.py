import luigi
from luigi.parameter import ParameterVisibility
from unluigi.util import monitor_tools
import logging

logger = logging.getLogger('luigi-interface')


class MonitorContext():
    def __init__(self, task_id):
        self.task_id = task_id
        self.completed_task = False

    def __enter__(self):
        monitor_tools.send_task_began(self.task_id)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self.completed_task:
            self.end_task(False, "Catastrophic error. Exited run function")

    def end_task(self, succeeded, output_or_error):
        self.completed_task = True
        monitor_tools.send_task_completed(self.task_id, succeeded,
                                          output_or_error)


class MonitorExperiment():
    def __init__(self, *args, **kwargs):
        super(MonitorExperiment, self).__init__(*args, **kwargs)
        self.get_task_id()
        if self.complete():
            monitor_tools.send_found_task_completed(self.get_task_id())

    def get_task_id(self):
        if "monitor_task_id" not in self.__dict__:
            self._monitor_task_id = monitor_tools.ensure_task(self, True)
        return self._monitor_task_id

    def get_task_name(self):
        raise Exception("Need to define get_task_name for class " +
                        str(self.get_task_family()))

    def get_monitor_context(self):
        return MonitorContext(self.get_task_id())


class MonitorTask():
    parent_id = luigi.IntParameter(visibility=ParameterVisibility.HIDDEN)
    root_task = luigi.BoolParameter(default=False,
                                    visibility=ParameterVisibility.HIDDEN)

    def __init__(self, *args, **kwargs):
        super(MonitorTask, self).__init__(*args, **kwargs)
        self.get_task_id()
        if self.complete():
            monitor_tools.send_found_task_completed(self.get_task_id())

    def get_task_id(self):
        if "monitor_task_id" not in self.__dict__:
            self._monitor_task_id = monitor_tools.ensure_task(self)
        return self._monitor_task_id

    def get_task_name(self):
        raise Exception("Need to define get_task_name for class " +
                        str(self.get_task_family()))

    def get_monitor_context(self):
        return MonitorContext(self.get_task_id())
