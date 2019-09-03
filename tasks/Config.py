import luigi
import os
import json


class Config(luigi.Task):
    config_path = luigi.Parameter()

    def output(self):
        return luigi.LocalTarget(
            os.path.join(os.path.dirname(config_path),
                         "config_auto_generated.json"))

    def run(self):
        with open(self.config_path, 'r') as original_config:
            with self.output().open('w') as config_file:
                config = json.load(original_config)
                config['project_root'] = os.path.dirname(config_path)
                json.dump(config, config_file)
