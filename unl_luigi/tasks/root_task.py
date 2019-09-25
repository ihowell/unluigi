from abc import ABC
import json
import luigi

CONFIG_PATH = '/Users/equint/Documents/GitHub/unl-luigi/example_configurations/local_config.json'

class Config(luigi.ExternalTask):


    def output(self):
        return luigi.LocalTarget(CONFIG_PATH)


class RootTask(luigi.WrapperTask, ABC):
    def run(self):
        slurminfo = slurm.SlurmInfo(slurm.RUNMODE_LOCAL, "LuigiSetup", "batch",
                                    1, 0, "Luigi_Workflow_Test", 1)
        if self.config['platform'] == "crane":
            slurminfo = slurm.SlurmInfo(slurm.RUNMODE_HPC,
                                        self.config['crane']['account'],
                                        self.config['crane']['partition'], 1,
                                        None, "Luigi_Workflow_Test", 1)

    def load_config(self):
        with open(config_path, 'r') as config_json:
            config = json.load(config_json)
        assert isinstance(config, dict)
        assert 'platform' in config
        if config['platform'] == 'crane':
            assert 'crane' in config
            assert 'account' in config['crane']
            assert 'partition' in config['crane']
        assert 'max_running_jobs' in config
        assert 'local_scheduler' in config
        assert 'keep_tmp_files' in config
