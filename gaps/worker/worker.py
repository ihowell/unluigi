"""Defines the worker interface and factory."""
import abc
import json
import hashlib
import re

TASK_ID_INVALID_CHAR_REGEX = re.compile(r'[^A-Za-z0-9_]')


def worker_id_str(worker):
    """Converts a worker to a string id

    This works by hashing the unique parameters assigned to a worker,
    i.e., the task list. Then, these are formatted into a Worker_%s
    string.
    """
    task_hashables = []
    for task in worker.task_list:
        task_hashables.append(task.task_family)
        task_hashables.append(task.to_str_params())
    param_str = json.dumps(task_hashables,
                           separators=(',', ':'),
                           sort_keys=True)
    tasks_hash = hashlib.md5(param_str.encode('utf-8')).hexdigest()
    return 'Worker_%s' % tasks_hash


class Worker(abc.ABC):
    """The Worker class is responsible for running tasks in an environment

    The worker class takes an ordered list of parameterized tasks and
    runs them in a given environment. This environment is usually
    created by extending the Worker class to other classes. For
    instance, a SlurmWorker might execute all of its tasks in a
    batched slurm-file, thus parallelizing the work done across a
    cluster.
    """
    worker_mapping = {}

    @staticmethod
    def register(name):
        """Register a worker type with the worker factory"""
        def _thunk(cls):
            Worker.worker_mapping[name] = cls
            return cls

        return _thunk

    @staticmethod
    def create(type_s, *args, **kwargs):
        """Create a worker of a given type from the factory"""
        return Worker.worker_mapping[type_s](*args, **kwargs)

    def __init__(self, task_list, *args, **kwargs):
        """Setups up a worker

        Args:
           task_list ([gaps.Task]): A list of parameterized tasks in running order
        """
        super(Worker, self).__init__(*args, **kwargs)
        self.task_list = task_list
        self.worker_id = worker_id_str(self)
        self.__hash = hash(self.worker_id)

    @abc.abstractmethod
    def start(self):
        """Starts task in the worker's task list

        """
    @abc.abstractmethod
    def stop(self):
        """Cancels the worker's tasks and shuts down
        """
    @abc.abstractmethod
    def is_running(self):
        """Returns whether the worker is currently running
        """
    @abc.abstractmethod
    def get_task_statuses(self):
        """Returns the status of each task

        Note that if the worker is currently running, it may not have
        access to the status of each task. It may only be able to say
        which tasks are currently complete accurately.

        Returns:
           results [task_status]: The status of each task in the task list given to the worker

        """
