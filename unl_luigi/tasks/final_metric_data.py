import luigi
import os
from unl_luigi.config.blackhole import BlackholeConfig
from unl_luigi.tasks.shell_task import ShellTask


class FinalMetricData(ShellTask):
    blackhole_path = luigi.Parameter()

    def __init__(self, *args, **kwargs):
        super(FinalMetricData, self).__init__(*args, **kwargs)
        self.instance_name = "FinalMetricData_%s" % self.blackhole_path

    def output(self):
        return luigi.LocalTarget("%s_tasks/final_metrics.success" %
                                 self.blackhole_path)

    def run(self):
        extra_args = ""

        hlc_id = None
        if "prepeak-poac" in self.blackhole_path.lower():
            hlc_id = 1
        elif "anpoac" in self.blackhole_path.lower():
            hlc_id = 1
        elif "apoacaroundu" in self.blackhole_path.lower():
            hlc_id = 1
        elif "a-ucyc-bfsc-poac" in self.blackhole_path.lower():
            hlc_id = 1

        if hlc_id is not None:
            extra_args += "--hlc %d" % hlc_id

        blackhole_app = BlackholeConfig().blackhole_app
        command = "%s -c final_metrics { -d %s -m Bpd -m Cpd -m Vipd %s }" % (
            blackhole_app, self.blackhole_path, extra_args)
        (returncode, stdout, stderr) = self.run_command(command)

        base_path = "%s_tasks" % self.blackhole_path
        if not os.path.exists(base_path):
            os.makedirs(base_path)

        with open("%s/final_metrics.retcode" % base_path, 'w') as out_file:
            out_file.write(str(returncode))
        with open("%s/final_metrics.out" % base_path, 'w') as out_file:
            out_file.write(stdout.decode("utf-8"))
        with open("%s/final_metrics.err" % base_path, 'w') as out_file:
            out_file.write(stderr.decode("utf-8"))

        if returncode > 0:
            raise Exception("Received error code %s in FinalMetricData: %s" %
                            (returncode, self.blackhole_path))

        with self.output().open('w') as out_file:
            out_file.write("1")
