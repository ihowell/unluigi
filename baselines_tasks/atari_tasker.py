import luigi
import functools
import itertools
from unl_luigi.tasks import slurm
import json

from baselines_tasks.train_task import TrainTask

PREAMBLE_PATH = "/Users/equint/Documents/GitHub/unl-luigi/baselines_tasks/local_preamble.sh"


def create_tasks():
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
        TrainTask(preamble_path=PREAMBLE_PATH,
                  platform='crane',
                  tmp_path='./',
                  keep_tmp_files=False,
                  **a) for a in args
    ]
