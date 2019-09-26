import os
import luigi

from unl_luigi.tasks.shell_task import ShellTask


class TrainTask(ShellTask):
    env_type = luigi.Parameter()
    env = luigi.Parameter()
    constraint = luigi.Parameter()
    reward_shaping = luigi.IntParameter()
    augmentation = luigi.Parameter()
    seed = luigi.IntParameter()

    def __init__(self, *args, **kwargs):
        super(TrainTask, self).__init__(*args, **kwargs)
        self.instance_name = "TrainTask_%s" % self.get_success_filename()
        print(os.path.join(self.tmp_path, self.get_success_filename()))

    def get_success_filename(self):
        return str(self.env_type) + str(self.env) + str(
            self.constraint) + str(self.reward_shaping) + str(
                self.augmentation) + str(self.seed)

    def run(self):
        cmd_str = 'OPENAI_LOGDIR="./openai_log/${SLURM_JOBID}" python -m baselines.run'
        cmd_str += ' --env ' + str(self.env) + "NoFrameskip-v4"
        if self.env_type == 'atari':
            cmd_str += ' --alg deepq'
            cmd_str += ' --num_timesteps 1e7'
        elif self.env_type == 'mujoco':
            cmd_str += ' --alg ppo2'
            cmd_str += ' --num_timesteps 1e6'
        if self.constraint:
            cmd_str += ' --constraints ' + str(self.constraint)
            cmd_str += ' augmentation ' + str(self.reward_shaping)
        if self.augmentation:
            cmd_str += ' --augmentation ' + str(self.augmentation)

        # print(self.get_success_file_path())
        # print(cmd_str)
        r = self.run_command(cmd_str)
        with open(os.path.join(self.tmp_path, self.get_success_filename()), 'w') as logfile:
            logfile.write(str(r))

    def output(self):
        return luigi.LocalTarget(os.path.join(self.tmp_path, self.get_success_filename() + '_success'))
