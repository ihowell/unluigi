import luigi
import os
from unluigi.util.atomic_file_pointer import AtomicFilePointer
from unluigi.tasks.shell_task import ShellTask


class FooTask(ShellTask):
    foo_directory = luigi.Parameter()
    foo_num = luigi.IntParameter()

    def output(self):
        return luigi.LocalTarget(
            os.path.join(self.foo_directory, "foo_%d.txt" % self.foo_num))

    def run(self):
        with AtomicFilePointer(self.output().path).open() as foo_file:
            self.run_command("echo %d > %s" %
                             (self.foo_num, foo_file.tmp_path))
