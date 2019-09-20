import luigi
import slurm
import os
import tempfile


class ShellTask(slurm.SlurmTask):
    platform = luigi.Parameter()
    # TODO: tmp_path needs a clearer name
    tmp_path = luigi.Parameter()
    keep_tmp_files = luigi.BoolParameter()

    def run_command(self,
                    command,
                    memory_limit=None,
                    time_limit=None,
                    perf_file=None):
        """Generate a bash script and run the script"""
        self_path = os.path.dirname(os.path.abspath(__file__))

        preamble = None
        if self.platform == "crane":
            with open("%s/crane_preamble.sh" % self_path,
                      'r') as preamble_file:
                preamble = preamble_file.read()

        memlimit_cmd = ""
        if memory_limit is not None:
            memlimit_cmd = "ulimit -S -v %d; " % memory_limit

        timelimit_cmd = ""
        if time_limit is not None:
            timelimit_cmd = "timeout --signal %d " % time_limit

        perfstat_cmd = ""
        if perf_file is not None:
            perfstat_cmd = "perf stat -o %s " % perf_file

        formatted_command = "%s%s%s%s" % (memlimit_cmd, timelimit_cmd,
                                          perfstat_cmd, command)

        prefix = None
        self.tmp_path = '%s/' % self.tmp_path

        with tempfile.NamedTemporaryFile(
                'w', prefix=prefix, suffix=".sh",
                delete=not self.keep_tmp_files) as command_file:
            if preamble is not None:
                command_file.write(preamble)
                command_file.write('\n')

            command_file.write(formatted_command)
            command_file.flush()
            execute_command = "bash %s" % command_file.name
            return_values = self.ex(execute_command)
        return return_values
