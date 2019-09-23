import luigi
import functools
import itertools

from baselines_tasks.train_task import TrainTask


class AtariTaskerTask(luigi.Task):
    def requires(self):
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
        return [TrainTask(**a) for a in args]


if __name__ == "__main__":
    t = AtariTaskerTask()
    t.requires()
