import luigi
import os
from unl_luigi.config.blackhole import BlackholeConfig
from unl_luigi.config.blackhole_web import BlackholeWebConfig
from unl_luigi.tasks.shell_task import ShellTask


class CopyBlackholeWebData(ShellTask):
    benchmark = luigi.Parameter()
    consistency_instance = luigi.Parameter()

    def output(self):
        blackhole_path = BlackholeConfig().blackhole_path
        return luigi.LocalTarget(
            "%s/%s_tasks/copy_blackhole_web_data.success" % (os.path.join(
                blackhole_path, self.benchmark), self.consistency_instance))

    def run(self):
        blackhole_path = BlackholeConfig().blackhole_path
        blackhole_web_path = BlackholeWebConfig().blackhole_web_path

        tokens = self.consistency_instance.split('_')
        consistency = tokens[0]
        instance = "_".join(tokens[1:])

        data_path = os.path.join(blackhole_path, self.benchmark,
                                 self.consistency_instance)
        web_path = os.path.join(blackhole_web_path, self.benchmark, instance,
                                consistency)

        remote_path = '@' in web_path

        command = ""
        if not remote_path:
            command += "mkdir -p %s ; " % web_path

        command += "rsync -aRm %s/./ %s --include='*/' --include='*.json' --include='static.db' --exclude='*'" % (
            data_path, web_path)
        print("Running command: command")
        (returncode, stdout, stderr) = self.run_command(command)

        base_path = "%s/%s_tasks" % (os.path.join(
            blackhole_path, self.benchmark), self.consistency_instance)
        if not os.path.exists(base_path):
            os.makedirs(base_path)

        with open("%s/copy_blackhole_web_data.retcode" % base_path,
                  'w') as out_file:
            out_file.write(str(returncode))
        with open("%s/copy_blackhole_web_data.out" % base_path,
                  'w') as out_file:
            out_file.write(stdout.decode("utf-8"))
        with open("%s/copy_blackhole_web_data.err" % base_path,
                  'w') as out_file:
            out_file.write(stderr.decode("utf-8"))

        if returncode > 0:
            raise Exception(
                "Received error code %s in CopyBlackholeWebData: %s" %
                (returncode, blackhole_path))

        with self.output().open('w') as out_file:
            out_file.write("1")
