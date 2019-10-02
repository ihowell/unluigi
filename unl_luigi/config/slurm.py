import luigi


class SlurmConfig(luigi.Config):
    runmode = luigi.Parameter(
        default=None)  # One of RUNMODE_LOCAL|RUNMODE_HPC|RUNMODE_MPI
    group_name = luigi.Parameter(default=None)
    partition = luigi.Parameter(default=None)
    cores = luigi.IntParameter(default=1)
    time = luigi.Parameter(default=None)
    jobname = luigi.Parameter(default=None)
    threads = luigi.IntParameter(default=1)
    gres = luigi.Parameter(default=None)
