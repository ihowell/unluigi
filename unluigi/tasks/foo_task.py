import luigi
import os

import unluigi.util as util

from unluigi.util.atomic_file_pointer import AtomicFilePointer


class FooTask(luigi.Task):
    foo_directory = luigi.Parameter()
    foo_num = luigi.NumericalParameter(var_type=int,
                                       min_value=0,
                                       max_value=10000)

    def output(self):
        return luigi.LocalTarget(
            os.path.join(self.foo_directory, "foo_%d.txt" % self.foo_num))

    def run(self):
        with AtomicFilePointer(self.output().path).open() as foo_file:
            util.ex_local("echo %d > %s" % (self.foo_num, foo_file.tmp_path))
