import luigi
import os
import tempfile
from unluigi.tasks import slurm


class ShellConfig(luigi.Config):
    preamble_path = luigi.Parameter(default=None)
    tmp_path_prefix = luigi.Parameter(default=None)
    keep_tmp_files = luigi.BoolParameter(default=False)


class ShellTask(slurm.SlurmTask):
    def run_command(self,
                    command,
                    memory_limit=None,
                    time_limit=None,
                    perf_file=None):
        """Generate a bash script and run the script"""
        config = ShellConfig()

        preamble = None
        if config.preamble_path is not None:
            with open(config.preamble_path, 'r') as preamble_file:
                preamble = preamble_file.read()

        formatted_command = ""

        if memory_limit is not None:
            formatted_command += "ulimit -S -v %d; " % memory_limit
        if time_limit is not None:
            formatted_command += "timeout --signal %d " % time_limit
        if perf_file is not None:
            formatted_command += "perf stat -o %s " % perf_file
        formatted_command += command

        prefix = None
        if config.tmp_path_prefix is not None:
            prefix = '%s/' % config.tmp_path_prefix if config.tmp_path_prefix[-1] != '/' else config.tmp_path_prefix
            if not os.path.exists(prefix):
                os.makedirs(prefix)

        with tempfile.NamedTemporaryFile(
                'w', prefix=prefix, suffix=".sh",
                delete=not config.keep_tmp_files) as command_file:
            if preamble is not None:
                command_file.write(preamble)
                command_file.write('\n')

            command_file.write(formatted_command)
            command_file.flush()
            execute_command = "bash %s" % command_file.name

            return_values = self.ex(execute_command)
        return return_values
