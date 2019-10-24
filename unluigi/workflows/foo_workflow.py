import luigi
import os
import unluigi.util as util
from unluigi.tasks.foo_task import FooTask
from unluigi.tasks.bar_task import BarTask


class FooWorkflow(luigi.WrapperTask):
    root_path = luigi.Parameter()
    foo_num = luigi.NumericalParameter(var_type=int,
                                       min_value=0,
                                       max_value=10000)

    def requires(self):
        foo_dir = os.path.join(self.root_path, 'foo')
        bar_dir = os.path.join(self.root_path, 'bar')

        if not os.path.isdir(foo_dir):
            os.makedirs(foo_dir)

        if not os.path.isdir(bar_dir):
            os.makedirs(bar_dir)

        tasks = [
            FooTask(foo_num=self.foo_num),
            BarTask(foo_path=os.path.join(foo_dir, "foo_%s.txt"),
                    foo_num=self.foo_num)
        ]

        return util.sequence_tasks(tasks)


def create_tasks(root_path):
    return [FooWorkflow(foo_num=i) for i in range(5)]
