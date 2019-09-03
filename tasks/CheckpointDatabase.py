import luigi
import slurm
import os
from tasks.ShellTask import ShellTask


class CheckpointDatabase(ShellTask):
    blackhole_path = luigi.Parameter()
    database_path = luigi.Parameter()

    def output(self):
        return luigi.LocalTarget(self.database_path +
                                 "_tasks/checkpoint.success")

    def run(self):

        command = "%s -c crane_checkpoint { -d %s }" % (self.blackhole_path,
                                                        self.database_path)
        (returncode, stdout, stderr) = self.run_command(command)

        base_path = "%s_tasks" % self.database_path
        if not os.path.exists(base_path):
            os.makedirs(base_path)

        with open("%s/checkpoint.retcode" % base_path, 'w') as out_file:
            out_file.write(str(returncode))
        with open("%s/checkpoint.out" % base_path, 'w') as out_file:
            out_file.write(stdout.decode("utf-8"))
        with open("%s/checkpoint.err" % base_path, 'w') as out_file:
            out_file.write(stderr.decode("utf-8"))

        if returncode == 0:
            with self.output().open('w') as out_file:
                out_file.write("1")
