import luigi


class ShellConfig(luigi.Config):
    preamble_path = luigi.Parameter(default=None)
    tmp_path_prefix = luigi.Parameter(default=None)
    keep_tmp_files = luigi.BoolParameter(default=False)
