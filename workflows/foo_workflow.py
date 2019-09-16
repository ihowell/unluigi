import luigi
import slurm
import json
import os
from tasks.FooTask import FooTask
from tasks.BarTask import BarTask
import util


class FooWorkflow(luigi.WrapperTask):
    config_path = luigi.Parameter()
    foo_num = luigi.NumericalParameter(var_type=int,
                                       min_value=0,
                                       max_value=10000)

    def __init__(self, *args, **kwargs):
        super(FooWorkflow, self).__init__(*args, **kwargs)
        with open(self.config_path, 'r') as read_config:
            config = json.load(read_config)
            config['config_dir'] = os.path.dirname(self.config_path)
            self.config = config

    def requires(self):
        slurminfo = slurm.SlurmInfo(slurm.RUNMODE_LOCAL, "LuigiSetup", "batch",
                                    1, 0, "Luigi_Workflow_Test", 1)
        if self.config['platform'] == "crane":
            slurminfo = slurm.SlurmInfo(slurm.RUNMODE_HPC,
                                        self.config['crane']['account'],
                                        self.config['crane']['partition'], 1,
                                        None, "Luigi_Workflow_Test", 1)

        foo_dir = os.path.join(self.config['config_dir'], 'foo')
        bar_dir = os.path.join(self.config['config_dir'], 'bar')

        config_txt = json.dumps(self.config)
        tasks = [
            FooTask(slurminfo=slurminfo,
                    config=config_txt,
                    foo_directory=foo_dir,
                    foo_num=self.foo_num),
            BarTask(slurminfo=slurminfo,
                    config=config_txt,
                    foo_path=os.path.join(foo_dir, "foo_%s.txt"),
                    foo_num=self.foo_num,
                    bar_directory=bar_dir)
        ]

        return util.sequence_tasks(tasks)


class CreateWorkflows(luigi.WrapperTask):
    config_path = luigi.Parameter()

    def requires(self):
        config = None
        with open(self.config_path, 'r') as config_file:
            config = json.load(config_file)
        # Create Tasks Here

        return [
            FooWorkflow(config_path=self.config_path, foo_num=i)
            for i in range(5)
        ]
