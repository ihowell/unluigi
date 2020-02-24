import time

import gaps.task_status as task_status

from gaps.task import Task, flatten
from gaps.worker import Worker, SlurmWorker
from gaps.tools.ordered_set import OrderedSet
from gaps.tools.partition import partition_list


class TaskException(Exception):
    pass


class Scheduler:
    """The Scheduler class schedules tasks to be run

    The class does so by managing the dependency tree of tasks to be
    run and monitoring workers performing batches of tasks at a
    time. The scheduler periodically polls the workers to receieve
    updates and schedule new tasks.

    """
    def __init__(self, task_list, max_workers=1, worker_type="basic"):
        """Initialize the scheduler with a given list of tasks to run.

        Args:
           task_list ([gaps.Task]): A list of tasks to run

        """
        self.task_list = task_list
        self.frontier_tasks = OrderedSet()
        self.depends_on = {}
        self.depended_by = {}
        self.max_workers = max_workers
        self.worker_type = worker_type

    @staticmethod
    def task_key(task):
        return (task.__class__, tuple(task.to_str_params().items()))

    def _build_dag_tree(self):
        task_list = list(filter(lambda x: not x.complete(), self.task_list))

        while len(task_list) > 0:
            task = task_list.pop()

            task_key = self.task_key(task)
            requirements = flatten(task.requires())
            task_dependencies_completed = True
            for r in requirements:
                if not isinstance(r, Task):
                    raise TaskException("Requirement " + str(r) +
                                        " is not of type gaps.task.Task")

                requirement_key = self.task_key(r)

                if task_key not in self.depends_on:
                    self.depends_on[task_key] = []
                if requirement_key not in self.depended_by:
                    self.depended_by[requirement_key] = []

                self.depends_on[task_key].append(requirement_key)
                self.depended_by[requirement_key].append(task_key)

                if not r.complete():
                    task_dependencies_completed = False
                    task_list.append(r)

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

        # This is the main loop of the scheduler
        while len(active_workers) > 0 or len(self.frontier_tasks) > 0:
            # Update all slurm workers at once. Much more efficient than individually
            if self.worker_type == 'slurm':
                SlurmWorker.retrieve_slurm_updates(active_workers)

            # Parititon active workers into workers that are finished
            # and workers that are not
            active_workers, finished_workers = partition_list(
                lambda w: w.running, active_workers)

            for worker in finished_workers:
                tasks = worker.task_list
                task_statuses = worker.get_task_statuses()

                for task, status in zip(tasks, task_statuses):
                    if status == task_status.DONE:
                        succeeded_tasks.add(task)
                        for parent in self.depended_by[self.task_key(task)]:
                            if parent.ready():
                                self.frontier_tasks.add(parent)

                    elif status == task_status.WORKER_CANCELED:
                        if task.ready():
                            self.frontier_tasks.add(task)

                    elif status == task_status.FAILED:
                        failed_tasks.add(task)
                        parent_stack = OrderedSet(
                            self.depended_by[self.task_key(task)])
                        while len(parent_stack) > 0:
                            parent_task = parent_stack.pop()
                            canceled_tasks.add(parent_task)
                            parent_stack += self.depended_by[self.task_key(
                                parent)]

            # Instantiate new jobs from the frontier
            while len(self.frontier_tasks) > 0 and len(
                    active_workers) < self.max_workers:
                task = self.frontier_tasks.popleft()
                worker = Worker.create(self.worker_type, [task])
                worker.start()
                active_workers.append(worker)

            time.sleep(5)

        return succeeded_tasks, failed_tasks, canceled_tasks
