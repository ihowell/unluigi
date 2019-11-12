import luigi
import os
from unluigi.config.blackhole import BlackholeConfig
from unluigi.tasks.shell_task import ShellTask


class CheckpointDatabase(ShellTask):
    benchmark = luigi.Parameter()
    instance = luigi.Parameter()

    def __init__(self, *args, **kwargs):
        super(CheckpointDatabase, self).__init__(*args, **kwargs)
        self.instance_name = "CheckpointDatabase_%s_%s" % (self.benchmark,
                                                           self.instance)

    def output(self):
        return luigi.LocalTarget(
            os.path.join(BlackholeConfig().blackhole_path, self.benchmark,
                         "%s_tasks" % self.instance, "checkpoint.success"))

    def run(self):
        blackhole_app_path = BlackholeConfig().blackhole_app
        blackhole_path = os.path.join(BlackholeConfig().blackhole_path,
                                      self.benchmark, self.instance)
        tasks_dir = os.path.join(BlackholeConfig().blackhole_path,
                                 self.benchmark, "%s_tasks" % self.instance)

        command = "%s -c crane_checkpoint { -d %s }" % (blackhole_app_path,
                                                        blackhole_path)
        (returncode, stdout, stderr) = self.run_command(command)
        self.record_output(tasks_dir, "checkpoint", return_code, stdout,
                           stderr)

        with self.output().open('w') as out_file:
            out_file.write("1")
