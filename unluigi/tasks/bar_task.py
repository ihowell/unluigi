import luigi
import os

import unluigi.util as util

from unluigi.util.atomic_file_pointer import AtomicFilePointer


class BarTask(luigi.Task):
    foo_path = luigi.Parameter()
    foo_num = luigi.NumericalParameter(var_type=int,
                                       min_value=0,
                                       max_value=10000)
    bar_directory = luigi.Parameter()

    def output(self):
        return luigi.LocalTarget(
            os.path.join(self.bar_directory,
                         "bar_%d_success.txt" % self.foo_num))

    def run(self):
        with AtomicFilePointer(
                os.path.join(self.bar_directory,
                             "bar_%d.txt" % self.foo_num)).open() as bar_file:
            (returncode, stdout, stderr) = util.ex_local(
                "echo \"%d - bar\" > %s" % (self.foo_num, bar_file.tmp_path))

        if returncode > 0:
            raise Exception("Received error code %s: %s -> %s" %
                            (returncode, self.foo_path, self.bar_directory))

        with self.output().open('w') as out_file:
            out_file.write("1")
