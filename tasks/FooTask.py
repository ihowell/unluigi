import luigi
from util.AtomicFilePointer import AtomicFilePointer
import os
from tasks.ShellTask import ShellTask


class FooTask(ShellTask):
    foo_directory = luigi.Parameter()
    foo_num = luigi.NumericalParameter(var_type=int,
                                       min_value=0,
                                       max_value=10000)

    def __init__(self, *args, **kwargs):
        super(FooTask, self).__init__(*args, **kwargs)
        self.instance_name = "FooTask_%d" % self.foo_num

    def output(self):
        return luigi.LocalTarget(
            os.path.join(self.foo_directory, "foo_%d.txt" % self.foo_num))

    def run(self):
        with AtomicFilePointer(self.output().path).open() as foo_file:
            self.run_command("echo %d > %s" %
                             (self.foo_num, foo_file.tmp_path))
