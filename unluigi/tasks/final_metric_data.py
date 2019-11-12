import luigi
import os
from unluigi.config.blackhole import BlackholeConfig
from unluigi.tasks.shell_task import ShellTask
from unluigi.tasks.parse_stardust_file import ParseStardustFile


class FinalMetricData(ShellTask):
    benchmark = luigi.Parameter()
    instance = luigi.Parameter()

    def __init__(self, *args, **kwargs):
        super(FinalMetricData, self).__init__(*args, **kwargs)
        self.instance_name = "FinalMetricData_%s_%s" % (self.benchmark,
                                                        self.instance)

    def requires(self):
        return ParseStardustFile(benchmark=self.benchmark,
                                 instance=self.instance)

    def output(self):
        return luigi.LocalTarget(
            os.path.join(BlackholeConfig().blackhole_path,
                         "%s_tasks" % self.benchmark, "final_metrics.success"))

    def run(self):
        blackhole_app = BlackholeConfig().blackhole_app
        blackhole_path = os.path.join(BlackholeConfig().blackhole_path,
                                      self.benchmark, self.instance)
        tasks_dir = os.path.join(BlackholeConfig().blackhole_path,
                                 self.benchmark, "%s_tasks" % self.instance)

        command = "%s -c final_metrics { -d %s -m Bpd -m Cpd -m Vipd}" % (
            blackhole_app, blackhole_path)
        (returncode, stdout, stderr) = self.run_command(command)

        self.record_output(tasks_dir, "final_metrics", returncode, stdout,
                           stderr)

        with self.output().open('w') as out_file:
            out_file.write("1")
