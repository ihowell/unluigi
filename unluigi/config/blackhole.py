import luigi


class BlackholeConfig(luigi.Config):
    # The path to the actual blackhole application
    blackhole_app = luigi.Parameter(default=None)

    # The path to the directory of blackhole data. This directory is
    # hierarchically structured as: benchmark/instance/consistency_instance
    blackhole_path = luigi.Parameter(default=None)
