import luigi
import os.path as osp

from unluigi.tasks.shell_task import ShellTask

class EvalTask(ShellTask):
    env_type = luigi.Parameter()
    env = luigi.Parameter()
    constraint = luigi.Parameter()
    reward_shaping = luigi.IntParameter()
    augmentation = luigi.Parameter()
    train_seed = luigi.IntParameter()
    eval_seed = luigi.IntParameter()

    def get_task_name_str(self):
        return self.train_task_name_str() + '_' + str(self.eval_seed)

    def get_output_dir(self):
        return osp.join('/work/scott/equint/baselines/', self.get_task_name_str())

    def train_task_name_str(self):    
        id_str = ''
        id_str += self.env + '_'
        id_str += self.constraint + '_'
        id_str += str(self.reward_shaping) + '_'
        id_str += self.augmentation + '_'
        id_str += str(self.train_seed)
        return id_str

    def get_train_task_dir(self):
        return osp.join('/work/scott/equint/baselines/', self.train_task_name_str())

    def requires(self):
        return TrainTask(self.env_type, self.env, self.constraint, self.reward_shaping, self.augmentation, self.train_seed)

    def run(self):
        cmd_str = 'python -m baselines.constraint.deepq.run_evaluation'
        cmd_str += ' --env ' + str(self.env) + "NoFrameskip-v4"

        if self.env_type == 'atari':
            cmd_str += ' --alg deepq'
            cmd_str += ' --num_timesteps 100000'
        elif self.env_type == 'mujoco':
            cmd_str += ' --alg ppo2'
            cmd_str += ' --num_timesteps 100000'
        if self.constraint:
            cmd_str += ' --constraints ' + str(self.constraint) + '_' + str(self.env)
            cmd_str += ' --reward_shaping ' + str(self.reward_shaping)
        if self.augmentation:
            if self.augmentation == 'constraint_state_noembed':
                cmd_str += ' --augmentation ' + str('constraint_state')
                cmd_str += ' --embed_constraint_state False'
            else:
                cmd_str += ' --augmentation ' + str(self.augmentation)
        if self.eval_seed:
            cmd_str += ' --seed ' + str(self.eval_seed)
        # eval specific stuff
        cmd_str += ' --log_path ' + self.get_output_dir()
        cmd_str += ' --save_path ' + self.get_train_task_dir() + '/model'

        r = self.run_command(cmd_str)
        print(r)
        

    def output(self):
        return {"success": luigi.LocalTarget(osp.join(self.get_output_dir(), 'final_log.txt'))}

class TrainTask(ShellTask):
    env_type = luigi.Parameter()
    env = luigi.Parameter()
    constraint = luigi.Parameter()
    reward_shaping = luigi.IntParameter()
    augmentation = luigi.Parameter()
    seed = luigi.IntParameter()

    def get_task_name_str(self):
        id_str = ''
        id_str += self.env + '_'
        id_str += self.constraint + '_'
        id_str += str(self.reward_shaping) + '_'
        id_str += self.augmentation + '_'
        id_str += str(self.seed)
        return id_str

    def get_output_dir(self):
        print(osp.join('/work/scott/equint/baselines/', self.get_task_name_str()))
        return osp.join('/work/scott/equint/baselines/', self.get_task_name_str())

    def run(self):
        cmd_str = 'python -m baselines.run'
        cmd_str += ' --env ' + str(self.env) + "NoFrameskip-v4"
        if self.env_type == 'atari':
            cmd_str += ' --alg deepq'
            cmd_str += ' --num_timesteps 1e7'
        elif self.env_type == 'mujoco':
            cmd_str += ' --alg ppo2'
            cmd_str += ' --num_timesteps 1e6'
        if self.constraint:
            cmd_str += ' --constraints ' + str(self.constraint) + '_' + str(self.env)
            cmd_str += ' --reward_shaping ' + str(self.reward_shaping)
        if self.augmentation:
            if self.augmentation == 'constraint_state_noembed':
                cmd_str += ' --augmentation ' + str('constraint_state')
                cmd_str += ' --embed_constraint_state False'
            else:
                cmd_str += ' --augmentation ' + str(self.augmentation)
        if self.seed:
            cmd_str += ' --seed ' + str(self.seed)
        cmd_str += ' --log_path ' + self.get_output_dir()
        cmd_str += ' --save_path ' + self.get_output_dir() + '/model'

        r = self.run_command(cmd_str)
        print(r)

    def output(self):
        return {"success": luigi.LocalTarget(osp.join(self.get_output_dir(), 'final_log.txt')), "model": luigi.LocalTarget(osp.join(self.get_output_dir(), 'model'))}
