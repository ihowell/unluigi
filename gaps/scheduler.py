import time
import logging
import gaps

import gaps.task_status as task_status

from gaps.task import Task, flatten
from gaps.worker import Worker, SlurmWorker
from gaps.tools.ordered_set import OrderedSet
from gaps.tools.partition import partition_list

logger = logging.getLogger('gaps-interface')


class TaskException(Exception):
    pass


class scheduler(gaps.Config):
    poll_interval = gaps.FloatParameter(default=0.1)
    max_workers = gaps.IntParameter(default=1)
    worker_type = gaps.ChoiceParameter(choices=Worker.get_worker_types(),
                                       default='basic')


class Scheduler:
    """The Scheduler class schedules tasks to be run

    The class does so by managing the dependency tree of tasks to be
    run and monitoring workers performing batches of tasks at a
    time. The scheduler periodically polls the workers to receieve
    updates and schedule new tasks.

    """
    def __init__(self, task_list, worker_type=None):
        """Initialize the scheduler with a given list of tasks to run.

        Args:
           task_list ([gaps.Task]): A list of tasks to run

        """
        self.task_list = task_list
        self.frontier_tasks = OrderedSet()
        self.depends_on = {}
        self.depended_by = {}
        self.worker_type = worker_type

    def _build_dag_tree(self):
        task_list = list(filter(lambda x: not x.complete(), self.task_list))

        while len(task_list) > 0:
            task = task_list.pop()

            # task_key = self.task_key(task)
            requirements = flatten(task.requires())
            task_dependencies_completed = True

            if task not in self.depends_on:
                self.depends_on[task] = []
            if task not in self.depended_by:
                self.depended_by[task] = []

            for requirement in requirements:
                if not isinstance(requirement, Task):
                    raise TaskException("Requirement " + str(requirement) +
                                        " is not of type gaps.task.Task")

                if requirement not in self.depends_on:
                    self.depends_on[requirement] = []
                if requirement not in self.depended_by:
                    self.depended_by[requirement] = []

                self.depends_on[task].append(requirement)
                self.depended_by[requirement].append(task)

                if not requirement.complete():
                    task_dependencies_completed = False
                    task_list.append(requirement)

            if task_dependencies_completed:
                self.frontier_tasks.append(task)

    def run(self):
        self._build_dag_tree()

        active_workers = []

        succeeded_tasks = set()

        # Tasks in this set failed at execution time
        failed_tasks = set()

        # Tasks in this set were canceled due to downstream task failures
        canceled_tasks = set()

        config = scheduler()

        worker_type = self.worker_type or config.worker_type

        # This is the main loop of the scheduler
        while len(active_workers) > 0 or len(self.frontier_tasks) > 0:
            # Update all slurm workers at once. Much more efficient than individually
            if worker_type == 'slurm':
                SlurmWorker.retrieve_slurm_updates(active_workers)

            # Parititon active workers into workers that are finished
            # and workers that are not
            active_workers, finished_workers = partition_list(
                lambda w: w.is_running(), active_workers)
            # logger.debug(
            #     'Scheduler found %d active workers and %d finished workers',
            #     len(active_workers), len(finished_workers))

            for worker in finished_workers:
                tasks = worker.task_list
                task_statuses = worker.get_task_statuses()

                for task, status in zip(tasks, task_statuses):
                    if status == task_status.DONE:
                        logger.debug('Worker completed task %s', task)
                        succeeded_tasks.add(task)
                        print(self.depended_by)
                        for parent in self.depended_by[task]:
                            print(parent)
                            if parent.ready():
                                self.frontier_tasks.add(parent)

                    elif status == task_status.WORKER_CANCELED:
                        logger.debug('Worker canceled task %s', task)
                        if task.ready():
                            self.frontier_tasks.add(task)
                        else:
                            canceled_tasks.add(task)

                    elif status == task_status.FAILED:
                        logger.debug('Worker failed task %s', task)
                        failed_tasks.add(task)
                        parent_stack = OrderedSet(self.depended_by[task])

                        while len(parent_stack) > 0:
                            parent = parent_stack.pop()
                            canceled_tasks.add(parent)
                            parent_stack += self.depended_by[parent]
                    else:
                        logger.error('Unseen status %s for task %s', status,
                                     task)

            num_new_tasks = min(len(self.frontier_tasks),
                                config.max_workers - len(active_workers))
            if num_new_tasks > 0:
                logger.debug('Scheudler starting %d new tasks', num_new_tasks)

            # Instantiate new jobs from the frontier
            while len(self.frontier_tasks) > 0 and len(
                    active_workers) < config.max_workers:
                task = self.frontier_tasks.pop(last=False)
                if task.complete():
                    for parent in self.depended_by[task]:
                        self.frontier_tasks.add(parent)
                else:
                    worker = Worker.create(worker_type, [task])
                    worker.start()
                    active_workers.append(worker)

            time.sleep(config.poll_interval)

        return succeeded_tasks, failed_tasks, canceled_tasks
