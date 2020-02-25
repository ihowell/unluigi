import luigi
import functools
import itertools
from unluigi.tasks import slurm
import json
import random

from baselines_tasks.train_task import TrainTask, EvalTask

def create_tasks():
    # per-task info
    env_type = ['atari']
    env = ['Breakout', 'SpaceInvaders']
    constraint = ['1d_dithering2', '1d_actuation4']
    reward_shaping = [0, -0.0025, -0.005, -0.01]
    augmentation = ['', 'constraint_state', 'constraint_state_noembed', 'action_history']
    train_seed = [7842, 1206]
    eval_seed = [5722, 2579, 1892, 7583, 9238]
    arg_names = [
        'env_type', 'env', 'constraint', 'reward_shaping', 'augmentation',
        'train_seed', 'eval_seed'
    ]

    args = [
        dict(zip(arg_names, arg_vals)) for arg_vals in itertools.product(
            env_type, env, constraint, reward_shaping, augmentation, train_seed, eval_seed)
    ]
    tasks = [EvalTask(**a) for a in args]
    random.shuffle(tasks)
    return tasks
