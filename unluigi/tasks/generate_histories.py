import luigi
import os
from unluigi.config.blackhole import BlackholeConfig
from unluigi.tasks.shell_task import ShellTask


class GenerateHistories(ShellTask):
    benchmark = luigi.Parameter()
    instance = luigi.Parameter()

    def __init__(self, *args, **kwargs):
        super(GenerateHistories, self).__init__(*args, **kwargs)
        self.instance_name = "GenerateHistories_%s_%s" % (self.benchmark,
                                                          self.instance)

    def output(self):
        return luigi.LocalTarget(
            os.path.join(BlackholeConfig().blackhole_path, self.benchmark,
                         "%s_tasks" % self.instance, "histories.success"))

    def run(self):
        blackhole_app_path = BlackholeConfig().blackhole_app
        blackhole_path = os.path.join(BlackholeConfig().blackhole_path,
                                      self.benchmark, self.instance)
        tasks_dir = os.path.join(BlackholeConfig().blackhole_path,
                                 self.benchmark, "%s_tasks" % self.instance)
        command = "%s -c crane_all_histories { -d %s -s 32 }" % (
            blackhole_app_path, blackhole_path)
        (returncode, stdout, stderr) = self.run_command(command)
        self.record_output(tasks_dir, "histories", returncode, stdout, stderr)

        with self.output().open('w') as out_file:
            out_file.write("1")
