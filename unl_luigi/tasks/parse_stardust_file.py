import luigi
import os
from unl_luigi.config.blackhole import BlackholeConfig
from unl_luigi.tasks.shell_task import ShellTask


class ParseStardustFile(ShellTask):
    """Precondition: blackhole_path ends with a /"""
    stardust_instance = luigi.Parameter()
    blackhole_path = luigi.Parameter()

    def __init__(self, *args, **kwargs):
        super(ParseStardustFile, self).__init__(*args, **kwargs)
        self.instance_name = "ParseStardustFile_%s" % self.stardust_instance

    def output(self):
        return luigi.LocalTarget("%s_tasks/parse.success" %
                                 self.blackhole_path)

    def run(self):
        input_file = "%s.xml.outputFiles/out.sd" % (self.stardust_instance)

        consistency_args = ""
        if "prepeak-poac1" in self.blackhole_path.lower():
            consistency_args = "-n GAC -n POAC1 -g 0 -g 2 -m 1-0 -m 3-1 -m 4-1"
        elif "anpoac" in self.blackhole_path.lower():
            consistency_args = "-n STR2 -n POACQ -g 0 -m 1-0 -m 2-1 -m 3-1"
        elif "apoacaroundu" in self.blackhole_path.lower():
            consistency_args = "-n STR2 -n POACPartial -g 0 -m 1-0 -m 2-1 -m 3-1"
        elif "apoac" in self.blackhole_path.lower():
            consistency_args = "-n APOAC -g 0 -m 1-0 -m 2-0"
        elif "a-ucyc-bfsc-poac" in self.blackhole_path.lower():
            consistency_args = "-n STR2 -n POACQ -g 0 -m 1-0 -m 2-1 -m 3-1"
        elif "poac1" in self.blackhole_path.lower():
            consistency_args = "-n POAC1 -m 0-0 -m 1-0"
        elif "pw-ac2" in self.blackhole_path.lower():
            consistency_args = "-n PW-AC2 -g 1 -m 0-0"
        elif "r3c" in self.blackhole_path.lower():
            consistency_args = "-n PerTuple -g 1 -m 0-0"
        elif "r4c" in self.blackhole_path.lower():
            consistency_args = "-n PerTuple -g 1 -m 0-0"
        elif "wr3c" in self.blackhole_path.lower():
            consistency_args = "-n PerTuple -g 1 -m 0-0"
        elif "wr43c" in self.blackhole_path.lower():
            consistency_args = "-n PerTuple -g 1 -m 0-0"

        command = "%s -c crane_parse { -i %s -d %s %s}" % (BlackholeConfig(
        ).blackhole_app, input_file, self.blackhole_path, consistency_args)
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
