import luigi


class StardustConfig(luigi.Config):
    # The path to the directory of Stardust log data. This directory
    # is hierarchically structured as: benchmark/consistency_instance
    stardust_path = luigi.Parameter(default=None)
