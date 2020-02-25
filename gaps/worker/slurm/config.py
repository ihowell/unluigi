import gaps


class SlurmConfig(gaps.Config):
    log_dir = gaps.Parameter()
    group_name = gaps.Parameter()
    partition = gaps.Parameter()
    mem_per_cpu = gaps.Parameter(default='8192M')
    num_tasks = gaps.IntParameter(default=1)
    nodes = gaps.IntParameter(default=1)
    jobname = gaps.Parameter()
    threads = gaps.IntParameter(default=1)
    time = gaps.OptionalParameter(default=None)
    gres = gaps.OptionalParameter(default=None)
