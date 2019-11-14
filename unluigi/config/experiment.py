import luigi


class ExperimentConfig(luigi.Config):
    experiment_dir = luigi.Parameter()
    experiment_name = luigi.Parameter()
    server_url = luigi.Parameter(default="http://localhost/")
