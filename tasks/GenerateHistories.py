import luigi
import slurm
import os
from tasks.ShellTask import ShellTask


class GenerateHistories(ShellTask):
    blackhole_app = luigi.Parameter()
    database_path = luigi.Parameter()

    def __init__(self, *args, **kwargs):
        super(GenerateHistories, self).__init__(*args, **kwargs)
        self.instance_name = "GenerateHistories_%s" % self.database_path

    def output(self):
        return luigi.LocalTarget("%s_tasks/histories.success" %
                                 self.database_path)

    def run(self):
        command = "%s -c crane_all_histories { -d %s -s 32 }" % (
            self.blackhole_app, self.database_path)
        (returncode, stdout, stderr) = self.run_command(command)

        base_path = "%s_tasks" % self.database_path
        if not os.path.exists(base_path):
            os.makedirs(base_path)

        with open("%s/histories.retcode" % base_path, 'w') as out_file:
            out_file.write(str(returncode))
        with open("%s/histories.out" % base_path, 'w') as out_file:
            out_file.write(stdout.decode("utf-8"))
        with open("%s/histories.err" % base_path, 'w') as out_file:
            out_file.write(stderr.decode("utf-8"))

        if returncode > 0:
            raise Exception("Received error code %s in ParseStardustFile: %s" %
                            (returncode, self.database_path))

        with self.output().open('w') as out_file:
            out_file.write("1")
