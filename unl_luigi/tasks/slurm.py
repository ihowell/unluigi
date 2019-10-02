'''
Modified from: https://github.com/pharmbio/sciluigi/blob/master/sciluigi/slurm.py

This module contains functionality related to integration with the SLURM HPC
resource manger.
'''

import datetime
import logging
import re
import time
import luigi.parameter
import luigi.task
import subprocess as sub
from unl_luigi.config.slurm import SlurmConfig

# ================================================================================

# Setup logging
log = logging.getLogger('luigi-interface')

# A few 'constants'
RUNMODE_LOCAL = 'runmode_local'
RUNMODE_HPC = 'runmode_hpc'
RUNMODE_MPI = 'runmode_mpi'

# ================================================================================


def get_argstr_hpc():
    '''
    Return a formatted string with arguments and option flags to SLURM
    commands such as salloc and sbatch, for non-MPI, HPC jobs.
    '''
    config = SlurmConfig()
    salloc_argstr = ' -A {g} -p {pt} -n {c} -J {j} '.format(
        g=config.group_name,
        pt=config.partition,
        c=config.cores,
        t=config.time,
        j=config.jobname)
    if config.time is not None:
        salloc_argstr += '-t {t} '.format(t=config.time)
    if config.gres is not None:
        salloc_argstr += '--gres={} '.format(config.gres)

    srun_argstr = ' srun -n 1 -c {thr} '.format(thr=config.threads)
    return salloc_argstr + srun_argstr


def get_argstr_mpi():
    '''
    Return a formatted string with arguments and option flags to SLURM
    commands such as salloc and sbatch, for MPI jobs.
    '''
    config = SlurmConfig()
    argstr = ' -A {g} -p {pt} -n {c1} -t {t} -J {j} mpirun -v -np {c2} '.format(
        g=config.group_name,
        pt=config.partition,
        c1=config.cores,
        t=config.time,
        j=config.jobname,
        c2=config.cores)
    return argstr


# ================================================================================


class SlurmTask(luigi.task.Task):
    '''
    Various convenience methods for executing jobs via SLURM
    '''

    # Main Execution methods
    def ex(self, command):
        '''
        Execute either locally or via SLURM, depending on config
        '''
        if isinstance(command, list):
            command = ' '.join(command)

        slurminfo = SlurmConfig()
        if slurminfo.runmode == RUNMODE_LOCAL:
            log.info('Executing command in local mode: %s', command)
            return self.ex_local(command)  # Defined in task.py
        elif slurminfo.runmode == RUNMODE_HPC:
            log.info('Executing command in HPC mode: %s', command)
            return self.ex_hpc(command)
        elif slurminfo.runmode == RUNMODE_MPI:
            log.info('Executing command in MPI mode: %s', command)
            return self.ex_mpi(command)

    def ex_local(self, command):
        '''
        Execute command locally (not through resource manager).
        '''
        # If list, convert to string
        if isinstance(command, list):
            command = sub.list2cmdline(command)

        proc = sub.Popen(command, shell=True, stdout=sub.PIPE, stderr=sub.PIPE)
        stdout, stderr = proc.communicate()
        retcode = proc.returncode

        # if len(stderr) > 0:
        #     log.debug('Stderr from command: %s', stderr)

        # if retcode != 0:
        #     errmsg = ('Command failed (retcode {ret}): {cmd}\n'
        #               'Command output: {out}\n'
        #               'Command stderr: {err}').format(ret=retcode,
        #                                               cmd=command,
        #                                               out=stdout,
        #                                               err=stderr)
        #     log.error(errmsg)
        #     raise Exception(errmsg)

        return (retcode, stdout, stderr)

    def ex_hpc(self, command):
        '''
        Execute command in HPC mode
        '''
        if isinstance(command, list):
            command = sub.list2cmdline(command)

        fullcommand = 'salloc %s %s' % (get_argstr_hpc(), command)
        print("Full hpc command: %s" % fullcommand)
        (retcode, stdout, stderr) = self.ex_local(fullcommand)

        self.log_slurm_info(stderr)
        return (retcode, stdout, stderr)

    def ex_mpi(self, command):
        '''
        Execute command in HPC mode with MPI support (multi-node, message passing interface).
        '''
        if isinstance(command, list):
            command = sub.list2cmdline(command)

        fullcommand = 'salloc %s %s' % (get_argstr_mpi(), command)
        (retcode, stdout, stderr) = self.ex_local(fullcommand)

        self.log_slurm_info(stderr)
        return (retcode, stdout, stderr)

    # Various convenience methods

    def assert_matches_character_class(self, char_class, a_string):
        '''
        Helper method, that tests whether a string matches a regex character class.
        '''
        if not bool(re.match('^{c}+$'.format(c=char_class), a_string)):
            raise Exception(
                'String {s} does not match character class {cc}'.format(
                    s=a_string, cc=char_class))

    def clean_filename(self, filename):
        '''
        Clean up a string to make it suitable for use as file name.
        '''
        return re.sub('[^A-Za-z0-9\_\ ]', '_', str(filename)).replace(' ', '_')

    # def get_task_config(self, name):
    #    return luigi.configuration.get_config().get(self.task_family, name)

    def log_slurm_info(self, slurm_stderr):
        '''
        Parse information of the following example form:

        salloc: Granted job allocation 5836263
        srun: Job step created
        salloc: Relinquishing job allocation 5836263
        salloc: Job allocation 5836263 has been revoked.
        '''

        matches = re.search('[0-9]+', str(slurm_stderr))
        if matches:
            jobid = matches.group(0)

            # Write slurm execution time to audit log
            cmd = 'sacct -j {jobid} --noheader --format=elapsed'.format(
                jobid=jobid)
            (_, jobinfo_stdout, _) = self.ex_local(cmd)
            sacct_matches = re.findall('([0-9\:\-]+)', str(jobinfo_stdout))

            if len(sacct_matches) < 2:
                log.warn('Not enough matches from sacct for task %s: %s',
                         self.instance_name,
                         ', '.join(['Match: %s' % m for m in sacct_matches]))
            else:
                slurm_exectime_fmted = sacct_matches[1]
                # Date format needs to be handled differently if the days field is included
                if '-' in slurm_exectime_fmted:
                    tobj = time.strptime(slurm_exectime_fmted, '%d-%H:%M:%S')
                    self.slurm_exectime_sec = int(
                        datetime.timedelta(tobj.tm_mday, tobj.tm_sec, 0, 0,
                                           tobj.tm_min,
                                           tobj.tm_hour).total_seconds())
                else:
                    tobj = time.strptime(slurm_exectime_fmted, '%H:%M:%S')
                    self.slurm_exectime_sec = int(
                        datetime.timedelta(0, tobj.tm_sec, 0, 0, tobj.tm_min,
                                           tobj.tm_hour).total_seconds())

                log.info('Slurm execution time for task %s was %ss',
                         self.instance_name, self.slurm_exectime_sec)
