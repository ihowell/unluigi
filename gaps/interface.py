# -*- coding: utf-8 -*-
#
# Copyright 2012-2015 Spotify AB
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""
This module contains the bindings for command line integration and dynamic loading of tasks


If you don't want to run gaps from the command line. You may use the methods
defined in this module to programatically run gaps.
"""

import logging
import os
import sys
import tempfile
import signal
import warnings

# from gaps import lock
from gaps import parameter
from gaps import scheduler
from gaps import task
from gaps import worker
from gaps.execution_summary import GapsRunResult
# from gaps.cmdline_parser import CmdlineParser
from gaps.setup_logging import InterfaceLogging


class core(task.Config):
    ''' Keeps track of a bunch of environment params.

    Uses the internal gaps parameter mechanism.
    The nice thing is that we can instantiate this class
    and get an object with all the environment variables set.
    This is arguably a bit of a hack.
    '''
    use_cmdline_section = False

    local_scheduler = parameter.BoolParameter(
        default=False,
        description='Use an in-memory central scheduler. Useful for testing.',
        always_in_help=True)
    scheduler_host = parameter.Parameter(
        default='localhost',
        description='Hostname of machine running remote scheduler',
        config_path=dict(section='core', name='default-scheduler-host'))
    scheduler_port = parameter.IntParameter(
        default=8082,
        description='Port of remote scheduler api process',
        config_path=dict(section='core', name='default-scheduler-port'))
    scheduler_url = parameter.Parameter(
        default='',
        description='Full path to remote scheduler',
        config_path=dict(section='core', name='default-scheduler-url'),
    )
    lock_size = parameter.IntParameter(
        default=1,
        description="Maximum number of workers running the same command")
    no_lock = parameter.BoolParameter(
        default=False,
        description='Ignore if similar process is already running')
    lock_pid_dir = parameter.Parameter(
        default=os.path.join(tempfile.gettempdir(), 'gaps'),
        description='Directory to store the pid file')
    take_lock = parameter.BoolParameter(
        default=False,
        description=
        'Signal other processes to stop getting work if already running')
    workers = parameter.IntParameter(
        default=1, description='Maximum number of parallel tasks to run')
    logging_conf_file = parameter.Parameter(
        default='', description='Configuration file for logging')
    log_level = parameter.ChoiceParameter(
        default='DEBUG',
        choices=['NOTSET', 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        description="Default log level to use when logging_conf_file is not set"
    )
    module = parameter.Parameter(
        default='',
        description='Used for dynamic loading of modules',
        always_in_help=True)
    parallel_scheduling = parameter.BoolParameter(
        default=False,
        description='Use multiprocessing to do scheduling in parallel.')
    parallel_scheduling_processes = parameter.IntParameter(
        default=0,
        description='The number of processes to use for scheduling in parallel.'
        ' By default the number of available CPUs will be used')
    assistant = parameter.BoolParameter(
        default=False, description='Run any task from the scheduler.')
    help = parameter.BoolParameter(
        default=False,
        description='Show most common flags and all task-specific flags',
        always_in_help=True)
    help_all = parameter.BoolParameter(
        default=False,
        description='Show all command line flags',
        always_in_help=True)


def _schedule_and_run(tasks, override_defaults=None):
    """
    :param tasks:
    :param override_defaults:
    :return: True if all tasks and their dependencies were successfully run (or already completed);
             False if any error occurred. It will return a detailed response of type GapsRunResult
             instead of a boolean if detailed_summary=True.
    """

    if override_defaults is None:
        override_defaults = {}
    env_params = core(**override_defaults)

    InterfaceLogging.setup(env_params)

    # kill_signal = signal.SIGUSR1 if env_params.take_lock else None
    # if (not env_params.no_lock and not (lock.acquire_for(
    #         env_params.lock_pid_dir, env_params.lock_size, kill_signal))):
    #     raise PidLockAlreadyTakenExit()

    sch = scheduler.Scheduler(tasks)

    success = True
    logger = logging.getLogger('gaps-interface')

    logger.info('Done scheduling tasks')
    succeeded_tasks, failed_tasks, canceled_tasks = sch.run()

    success = len(failed_tasks) == 0
    # gaps_run_result = GapsRunResult(worker, success)
    summary_text = """
    Tasks succeeded or found done: %d
    Tasks failed: %d
    Tasks not run %d
    """ % (len(succeeded_tasks), len(failed_tasks), len(canceled_tasks))
    # logger.info(gaps_run_result.summary_text)
    logger.info(summary_text)
    # return gaps_run_result


class PidLockAlreadyTakenExit(SystemExit):
    """
    The exception thrown by :py:func:`gaps.run`, when the lock file is inaccessible
    """
    pass


def run(*args, **kwargs):
    """
    Please dont use. Instead use `gaps` binary.

    Run from cmdline using argparse.

    :param use_dynamic_argparse: Deprecated and ignored
    """
    _run(*args, **kwargs)
    # gaps_run_result = _run(*args, **kwargs)
    # return gaps_run_result if kwargs.get(
    #     'detailed_summary') else gaps_run_result.scheduling_succeeded


def _run(cmdline_args=None,
         main_task_cls=None,
         worker_scheduler_factory=None,
         use_dynamic_argparse=None,
         local_scheduler=False,
         detailed_summary=False):
    if use_dynamic_argparse is not None:
        warnings.warn("use_dynamic_argparse is deprecated, don't set it.",
                      DeprecationWarning,
                      stacklevel=2)
    if cmdline_args is None:
        cmdline_args = sys.argv[1:]

    if main_task_cls:
        cmdline_args.insert(0, main_task_cls.task_family)
    # if local_scheduler:
    cmdline_args.append('--local-scheduler')
    # with CmdlineParser.global_instance(cmdline_args) as cp:
    #     return _schedule_and_run([cp.get_task_obj()], worker_scheduler_factory)


def build(tasks,
          worker_scheduler_factory=None,
          detailed_summary=False,
          **env_params):
    """
    Run internally, bypassing the cmdline parsing.

    Useful if you have some gaps code that you want to run internally.
    Example:

    .. code-block:: python

        gaps.build([MyTask1(), MyTask2()], local_scheduler=True)

    One notable difference is that `build` defaults to not using
    the identical process lock. Otherwise, `build` would only be
    callable once from each process.

    :param tasks:
    :param worker_scheduler_factory:
    :param env_params:
    :return: True if there were no scheduling errors, even if tasks may fail.
    """
    if "no_lock" not in env_params:
        env_params["no_lock"] = True

    _schedule_and_run(tasks)
    # gaps_run_result = _schedule_and_run(tasks,
    #                                     worker_scheduler_factory,
    #                                     override_defaults=env_params)
    # return gaps_run_result if detailed_summary else gaps_run_result.scheduling_succeeded