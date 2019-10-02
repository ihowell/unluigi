import luigi


class BlackholeWebConfig(luigi.Config):
    # The path to the directory of blackhole data. This directory is
    # hierarchically structured as: benchmark/instance/consistency
    blackhole_web_path = luigi.Parameter(default=None)
