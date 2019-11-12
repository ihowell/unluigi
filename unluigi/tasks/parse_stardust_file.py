import luigi
import os
from unluigi.config.stardust import StardustConfig
from unluigi.config.blackhole import BlackholeConfig
from unluigi.tasks.shell_task import ShellTask


class ParseStardustFile(ShellTask):
    """Precondition: blackhole_path ends with a /"""
    benchmark = luigi.Parameter()
    instance = luigi.Parameter()

    def __init__(self, *args, **kwargs):
        super(ParseStardustFile, self).__init__(*args, **kwargs)
        self.instance_name = "ParseStardustFile_%s_%s" % (self.benchmark,
                                                          self.instance)

    def output(self):
        return luigi.LocalTarget(
            "%s/%s/%s_tasks/parse.success" %
            (BlackholeConfig().blackhole_path, self.benchmark, self.instance))

    def run(self):
        input_file = os.path.join(StardustConfig().stardust_path,
                                  self.benchmark, "%s.sd" % self.instance)
        output_dir = os.path.join(BlackholeConfig().blackhole_path,
                                  self.benchmark, self.instance)
        tasks_dir = os.path.join(BlackholeConfig().blackhole_path,
                                 self.benchmark, "%s_tasks" % self.instance)

        new_cons = []
        ignore_cons = []
        map_cons = []
        hlcs = []

        consistency_args = ""
        if "prepeak-poac1" in self.instance.lower():
            new_cons = ["GAC", "POAC1"]
            ignore_cons = [0, 2]
            map_cons = ["1-0", "3-1", "4-1"]
            hlcs = [1]
        elif "anpoac" in self.instance.lower():
            new_cons = ["STR2", "POACQ"]
            ignore_cons = [0]
            map_cons = ["1-0", "2-1", "3-1"]
            hlcs = [1]
        elif "apoacaroundu" in self.instance.lower():
            new_cons = ["STR2", "POACPartial"]
            ignore_cons = [0]
            map_cons = ["1-0", "2-1", "3-1"]
            hlcs = [1]
        elif "apoac" in self.instance.lower():
            new_cons = ["APOAC"]
            ignore_cons = [0]
            map_cons = ["1-0", "2-0"]
        elif "a-ucyc-bfsc-poac" in self.instance.lower():
            new_cons = ["STR2", "POACQ"]
            ignore_cons = [0]
            map_cons = ["1-0", "2-1", "3-1"]
        elif "poac1" in self.instance.lower():
            new_cons = ["POAC1"]
            map_cons = ["0-0", "1-0"]
        elif "pw-ac2" in self.instance.lower():
            new_cons = ["PW-AC2"]
            ignore_cons = [1]
            map_cons = ["0-0"]
        elif "r3c" in self.instance.lower():
            new_cons = ["PerTuple"]
            ignore_cons = [1]
            map_cons = ["0-0"]
        elif "r4c" in self.instance.lower():
            new_cons = ["PerTuple"]
            ignore_cons = [1]
            map_cons = ["0-0"]
        elif "wr3c" in self.instance.lower():
            new_cons = ["PerTuple"]
            ignore_cons = [1]
            map_cons = ["0-0"]
        elif "wr43c" in self.instance.lower():
            new_cons = ["PerTuple"]
            ignore_cons = [1]
            map_cons = ["0-0"]

        consistency_args = []
        for n in new_cons:
            consistency_args.extend(["-n", str(n)])
        for g in ignore_cons:
            consistency_args.extend(["-g", str(g)])
        for m in map_cons:
            consistency_args.extend(["-m", str(m)])
        for h in hlcs:
            consistency_args.extend(["-u", str(h)])

        consistency_args = " ".join(consistency_args)

        command = "%s -c crane_parse { -i %s -d %s %s}" % (BlackholeConfig(
        ).blackhole_app, input_file, output_dir, consistency_args)
        (returncode, stdout, stderr) = self.run_command(command)
        self.record_output(tasks_dir, "parse", returncode, stdout, stderr)

        with self.output().open('w') as out_file:
            out_file.write("1")
