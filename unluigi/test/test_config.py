import luigi


class TestConfig(luigi.Config):
    output_dir = luigi.Parameter()
