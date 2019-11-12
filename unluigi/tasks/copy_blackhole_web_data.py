import luigi
import os
from unluigi.tasks.final_metric_data import FinalMetricData
from unluigi.config.blackhole import BlackholeConfig
from unluigi.config.blackhole_web import BlackholeWebConfig
from unluigi.tasks.shell_task import ShellTask


class CopyBlackholeWebData(ShellTask):
    # Should be the name of the instance. For example: mug
    benchmark = luigi.Parameter()

    # Should be of the form consistency_instance. For example:
    # CT_mug-1-88-3
    instance = luigi.Parameter()

    def __init__(self, *args, **kwargs):
        super(CopyBlackholeWebData, self).__init__(*args, **kwargs)
        self.instance_name = "FinalMetricData_%s_%s" % (self.benchmark,
                                                        self.instance)

    def requires(self):
        return FinalMetricData(benchmark=self.benchmark,
                               instance=self.instance)

    def output(self):
        return luigi.LocalTarget(
            os.path.join(BlackholeConfig().blackhole_path, self.benchmark,
                         "%s_tasks" % self.instance,
                         "copy_blackhole_web_data.success"))

    def run(self):
        blackhole_path = BlackholeConfig().blackhole_path
        blackhole_web_path = BlackholeWebConfig().blackhole_web_path

        tokens = self.instance.split('_')
        consistency = tokens[0]
        instance = "_".join(tokens[1:])

        data_path = os.path.join(blackhole_path, self.benchmark, self.instance)
        web_path = os.path.join(blackhole_web_path, self.benchmark, instance,
                                consistency)
        tasks_dir = os.path.join(blackhole_path, self.benchmark,
                                 "%s_tasks" % self.instance)

        remote_path = '@' in web_path

        command = ""
        if not remote_path:
            command += "mkdir -p %s ; " % web_path

        command += "rsync -aRm %s/./ %s --include='*/' --include='*.json' --include='static.db' --exclude='*'" % (
            data_path, web_path)
        (returncode, stdout, stderr) = self.run_command(command)

        self.record_output(tasks_dir, "copy_blackhole_web_data", returncode,
                           stdout, stderr)

        with self.output().open('w') as out_file:
            out_file.write("1")
