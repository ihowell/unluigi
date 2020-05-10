import luigi
import functools
import itertools
from unluigi.tasks import slurm
import json
import random

from baselines_tasks.train_task import TrainTask, EvalTask

env_type = ['atari']
reward_shaping = [0, -0.001, -0.0025, -0.005, -0.01]
augmentation = ['', 'constraint_state', 'action_history']

def twod_tasks():
    env = ['Seaquest']
    constraint = ['2d_actuation4', '2d_actuation4_dense', '2d_actuation4_hard', '2d_dithering4', '2d_dithering4_dense', '2d_dithering4_hard']
    train_seed = []#7842, 1206, 8610]
    eval_seed = []#5722, 2579, 1892, 7583, 9238]
    arg_names = [
        'env_type', 'env', 'constraint', 'reward_shaping', 'augmentation',
        'train_seed', 'eval_seed'
    ]
    args = [
        dict(zip(arg_names, arg_vals)) for arg_vals in itertools.product(
            env_type, env, constraint, reward_shaping, augmentation, train_seed, eval_seed)
    ]
    args = [d for d in args if not ('hard' in d['constraint'] and d['reward_shaping'] != 0)]
    return [EvalTask(**a) for a in args]


def oned_tasks():
    # per-task info
    env = ['Breakout', 'SpaceInvaders']
    constraint = ['1d_dithering2', '1d_dithering2_dense', '1d_dithering2_hard', '1d_actuation4', '1d_actuation4_dense', '1d_actuation4_hard']
    train_seed = []#7842, 1206, 8610]
    eval_seed = []#5722, 2579, 1892, 7583, 9238]
    arg_names = [
        'env_type', 'env', 'constraint', 'reward_shaping', 'augmentation',
        'train_seed', 'eval_seed'
    ]

    args = [
        dict(zip(arg_names, arg_vals)) for arg_vals in itertools.product(
            env_type, env, constraint, reward_shaping, augmentation, train_seed, eval_seed)
    ]
    args = [d for d in args if not ('hard' in d['constraint'] and d['reward_shaping'] != 0)]
    return [EvalTask(**a) for a in args]

def breakout_tasks():
    # per-task info
    env_type = ['atari']
    env = ['Breakout']
    constraint = ['paddle_ball_distance', 'paddle_ball_distance_dense', 'paddle_ball_distance_hard']
    reward_shaping = [0, -0.0025, -0.005, -0.01]
    augmentation = ['', 'constraint_state', 'action_history']
    train_seed = [7842]#, 1206, 8610]
    eval_seed = [5722, 2579]#, 1892, 7583, 9238]
    arg_names = [
        'env_type', 'env', 'constraint', 'reward_shaping', 'augmentation',
        'train_seed', 'eval_seed'
    ]

    args = [
        dict(zip(arg_names, arg_vals)) for arg_vals in itertools.product(
            env_type, env, constraint, reward_shaping, augmentation, train_seed, eval_seed)
    ]
    args = [d for d in args if not ('hard' in d['constraint'] and d['reward_shaping'] != 0)]
    return [EvalTask(**a) for a in args]

def create_tasks():
    tasks = oned_tasks() + twod_tasks() + breakout_tasks()
    random.shuffle(tasks)
    return tasks

