import luigi
import functools
import itertools
from unl_luigi.tasks import slurm
import json

from baselines_tasks.train_task import TrainTask
from unl_luigi.tasks.root_task import RootTask

CONFIG_PATH = '/Users/equint/Documents/GitHub/unl-luigi/example_configurations/local_config.json'


class AtariTaskerTask(luigi.WrapperTask):
    def requires(self):
        with open(CONFIG_PATH, 'r') as config_json:
            config = json.load(config_json)

        slurminfo = slurm.SlurmInfo(slurm.RUNMODE_LOCAL, "LuigiSetup", "batch",
                                    1, 0, "Luigi_Workflow_Test", 1)
        if config['platform'] == "crane":
            slurminfo = slurm.SlurmInfo(slurm.RUNMODE_HPC,
                                        config['crane']['account'],
                                        config['crane']['partition'], 1, None,
                                        "Luigi_Workflow_Test", 1)

        # per-task info
        env_type = ['atari']
        env = ['Seaquest', 'SpaceInvader']
        constraint = ['', '1d_dithering', '1d_actuation']
        reward_shaping = [0, -1, -10, -100, -1000]
        augmentation = ['', 'constraint_state', 'action_history']
        seed = [403297842]
        arg_names = [
            'env_type', 'env', 'constraint', 'reward_shaping', 'augmentation',
            'seed'
        ]
        args = [
            dict(zip(arg_names, arg_vals)) for arg_vals in itertools.product(
                env_type, env, constraint, reward_shaping, augmentation, seed)
        ]

        return [
            TrainTask(slurminfo=slurminfo,
                      platform='crane',
                      tmp_path='./',
                      keep_tmp_files=False,
                      **a) for a in args
        ]
