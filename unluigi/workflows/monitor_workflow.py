import luigi
import os
from unluigi.tasks.bar_monitor_task import BarMonitorTask
from unluigi.tasks.monitor import MonitorExperiment, MonitorTask


class FooWorkflow(MonitorTask, luigi.WrapperTask):
    root_path = luigi.Parameter()
    foo_num = luigi.IntParameter()

    def get_task_name(self):
        return "FooWorkflow " + str(self.foo_num)

    def requires(self):
        foo_dir = os.path.join(self.root_path, 'foo')
        bar_dir = os.path.join(self.root_path, 'bar')

        if not os.path.isdir(foo_dir):
            os.makedirs(foo_dir)

        if not os.path.isdir(bar_dir):
            os.makedirs(bar_dir)

        return BarMonitorTask(foo_path=os.path.join(foo_dir, "foo_%s.txt"),
                              foo_num=self.foo_num,
                              parent_id=self.get_task_id())


class Experiment(MonitorExperiment, luigi.WrapperTask):
    def get_task_name(self):
        return "Experiment"

    def requires(self):
        return [
            FooWorkflow(foo_num=i, parent_id=self.get_task_id())
            for i in range(1)
        ]


def create_tasks(
        #root_path
):
    return [Experiment()]
