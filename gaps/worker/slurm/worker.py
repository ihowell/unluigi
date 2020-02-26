import os
import sys
import subprocess
import logging

import gaps
import gaps.task_status as task_status
import gaps.worker.slurm.client as slurm_client

from gaps.worker.worker import Worker
from gaps.worker.slurm.config import SlurmConfig

logger = logging.getLogger('gaps-interface')


def get_hpc_args(job_name, task_list_str):
    """
    Return a formatted string with arguments and option flags to SLURM
    commands such as salloc and sbatch, for non-MPI, HPC jobs.
    """
    config = SlurmConfig()

    args = [
        'sbatch',
        '--licenses=common',
        '--partition=%s' % config.partition,
        '-N%d' % config.nodes,
        '--mem-per-cpu=%s' % config.mem_per_cpu,
        '--output=%s/worker.%s.out' % (config.log_dir, '%J'),
        '--error=%s/worker.%s.err' % (config.log_dir, '%J'),
        '--job-name=%s' % job_name,
    ]

    if config.time is not None:
        args.append('--time {t} '.format(t=config.time))
    if config.gres is not None:
        args.append('--gres={} '.format(config.gres))

    args += [
        os.path.join(os.path.dirname(os.path.realpath(__file__)),
                     'run_python.sh'),
        slurm_client.__file__,
        task_list_str,
    ]
    return args


@Worker.register("slurm")
class SlurmWorker(Worker):
    """A basic worker runs tasks in the same thread as the scheduler

    This worker is not intended for scalable use, but just as a use
    case for testing. This worker immediately runs all tasks given to
    it when start is called, blocking the scheduler from continuing.
    """
    def __init__(self, *args, **kwargs):
        super(SlurmWorker, self).__init__(*args, **kwargs)
        self._is_running = False
        self.task_statuses = []
        if not gaps.util.test_slurm_availability():
            logger.warn(
                'Instantiating Slurm Worker in a non-slurm compatible environment'
            )

    @staticmethod
    def retrieve_slurm_updates(workers):
        """Retrieves updates from slurm and passes them on to the workers"""
        worker_ids = [worker.worker_id for worker in workers]
        args = [
            '/usr/bin/squeue', '-h', '-o', '%j,%t', '-n', ','.join(worker_ids)
        ]
        slurm_q = subprocess.run(args,
                                 stdout=subprocess.PIPE,
                                 universal_newlines=True,
                                 check=True)
        running_ids = []
        for line in slurm_q.stdout.splitlines():
            split = line.split(',')
            running_ids.append(split[0].strip())

        for worker in workers:
            worker.update_from_slurm(worker.worker_id in running_ids)

    def update_from_slurm(self, is_running):
        """Updates values from slurm info retrieval"""
        self._is_running = is_running

    def _get_cli_args(self):
        """Generate the cli arguments to be passed to slurm"""
        config = SlurmConfig()
        if not os.path.exists(config.log_dir):
            os.makedirs(config.log_dir)
        task_list_str = slurm_client.serialize_task_list(self.task_list)
        args = get_hpc_args(self.worker_id, task_list_str)
        return args

    def start(self):
        self.task_statuses = [task_status.RUNNING for _ in self.task_list]
        cli_args = self._get_cli_args()
        subprocess.run(cli_args, check=True)

    def stop(self):
        cli_args = ['scancel', '-n' % self.worker_id]
        subprocess.run(cli_args, check=True)

    def is_running(self):
        return self._is_running

    def get_task_statuses(self):
        self.task_statuses = []
        task_chain_complete = False
        for task in self.task_list:
            if not task_chain_complete:
                if task.complete():
                    self.task_statuses.append(task_status.DONE)
                elif self._is_running:
                    self.task_statuses = task_status.RUNNING
                    task_chain_complete = True
                else:
                    self.task_statuses.append(task_status.FAILED)
                    task_chain_complete = True
            elif self._is_running:
                self.task_statuses.append(task_status.PENDING)
            else:
                self.task_statuses.append(task_status.WORKER_CANCELED)
        return self.task_statuses
