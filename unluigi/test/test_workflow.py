import luigi
import os
import time
from unluigi.tasks.monitor import MonitorExperiment, MonitorTask
from unluigi.test.test_config import TestConfig


class SmallDependency(MonitorTask, luigi.Task):
    num = luigi.IntParameter()

    def get_task_name(self):
        return "SmallDepdendency_" + str(self.num)

    def output(self):
        return luigi.LocalTarget(
            os.path.join(TestConfig().output_dir, "small_%d.out" % self.num))

    def run(self):
        with self.get_monitor_context() as ctx:
            time.sleep(3)

            ctx.end_task(True, '{"output": 1}')
            with self.output().open('w') as out_file:
                out_file.write('1')


class LargeDependency(MonitorTask, luigi.Task):
    num = luigi.IntParameter()

    def get_task_name(self):
        return "LargeDependency_" + str(self.num)

    def output(self):
        return luigi.LocalTarget(
            os.path.join(TestConfig().output_dir, "large_%d.out" % self.num))

    def run(self):
        with self.get_monitor_context() as ctx:
            time.sleep(10)
            ctx.end_task(True, '{"output": 1}')
            with self.output().open('w') as out_file:
                out_file.write('1')


class Calculation(MonitorTask, luigi.Task):
    num = luigi.IntParameter()

    def get_task_name(self):
        return "Calculation_" + str(self.num)

    def requires(self):
        return [
            LargeDependency(parent_id=self.get_task_id(), num=self.num),
            [
                SmallDependency(parent_id=self.get_task_id(),
                                num=5 * self.num + i) for i in range(5)
            ]
        ]

    def output(self):
        return luigi.LocalTarget(
            os.path.join(TestConfig().output_dir,
                         "calculation_%d.out" % self.num))

    def run(self):
        with self.get_monitor_context() as ctx:
            time.sleep(5)
            ctx.end_task(True, '{"output": 1}')
            with self.output().open('w') as out_file:
                out_file.write('1')


class Workflow(MonitorTask, luigi.WrapperTask):
    num = luigi.IntParameter()

    def get_task_name(self):
        return "Workflow " + str(self.num)

    def requires(self):
        return Calculation(parent_id=self.get_task_id(), num=self.num)


class Experiment(MonitorExperiment, luigi.WrapperTask):
    def get_task_name(self):
        return "Experiment"

    def requires(self):
        return [
            Workflow(parent_id=self.get_task_id(), num=i) for i in range(5)
        ]


def create_tasks(
        #root_path
):
    return [Experiment()]
