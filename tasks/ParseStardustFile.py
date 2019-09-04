import luigi
import slurm
import os
from tasks.ShellTask import ShellTask


class ParseStardustFile(ShellTask):
    """Precondition: blackhole_path ends with a /"""
    blackhole_app = luigi.Parameter()
    stardust_instance = luigi.Parameter()
    blackhole_path = luigi.Parameter()

    def output(self):
        return luigi.LocalTarget("%s_tasks/parse.success" %
                                 self.blackhole_path)

    def run(self):
        input_file = "%s.xml.outputFiles/out.sd" % (self.stardust_instance)

        command = "%s -c crane_parse { -i %s -d %s }" % (
            self.blackhole_app, input_file, self.blackhole_path)
        (returncode, stdout, stderr) = self.run_command(command)

        base_path = "%s_tasks/" % self.blackhole_path
        if not os.path.exists(base_path):
            os.makedirs(base_path)

        with open("%s/parse.retcode" % base_path, 'w') as out_file:
            out_file.write(str(returncode))
        with open("%s/parse.out" % base_path, 'w') as out_file:
            out_file.write(stdout.decode("utf-8"))
        with open("%s/parse.err" % base_path, 'w') as out_file:
            out_file.write(stderr.decode("utf-8"))

        if returncode > 0:
            raise Exception(
                "Received error code %s in ParseStardustFile: %s -> %s" %
                (returncode, self.stardust_instance, self.blackhole_path))

        with self.output().open('w') as out_file:
            out_file.write("1")
