import luigi
import os
from unluigi.tasks.foo_monitor_task import FooMonitorTask
from unluigi.tasks.monitor import MonitorTask
from unluigi.tasks.shell_task import ShellTask
from unluigi.util.atomic_file_pointer import AtomicFilePointer


class BarMonitorTask(MonitorTask, ShellTask):
    foo_path = luigi.Parameter()
    foo_num = luigi.IntParameter()
    bar_directory = luigi.Parameter()

    def get_task_name(self):
        return "BarMonitorTask " + str(self.foo_num)

    def requires(self):
        return FooMonitorTask(parent_id=self.get_task_id(),
                              foo_num=self.foo_num)

    def output(self):
        return luigi.LocalTarget(
            os.path.join(self.bar_directory,
                         "bar_%d_success.txt" % self.foo_num))

    def run(self):
        with self.get_monitor_context() as ctx:
            with AtomicFilePointer(
                    os.path.join(self.bar_directory, "bar_%d.txt" %
                                 self.foo_num)).open() as bar_file:
                (returncode, stdout,
                 stderr) = self.ex("echo \"%d - bar\" > %s" %
                                   (self.foo_num, bar_file.tmp_path))

                if returncode > 0:
                    ctx.end_task(
                        False,
                        "Returncode: " + str(returncode) + "\n" + str(stderr))
                    raise Exception(
                        "Received error code %s: %s -> %s" %
                        (returncode, self.foo_path, self.bar_directory))

            ctx.end_task(True, stdout.decode('utf-8'))
            with self.output().open('w') as out_file:
                out_file.write("1")
