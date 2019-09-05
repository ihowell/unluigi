import luigi
import slurm
import json
import glob
import os
from tasks.ArchiveDirectory import ArchiveDirectory
from tasks.CheckpointDatabase import CheckpointDatabase
from tasks.GenerateHistories import GenerateHistories
from tasks.ParseStardustFile import ParseStardustFile
import util


class Workflow(luigi.WrapperTask):
    config_path = luigi.Parameter()
    benchmark = luigi.Parameter()
    instance = luigi.Parameter()

    def __init__(self, *args, **kwargs):
        super(Workflow, self).__init__(*args, **kwargs)
        with open(self.config_path, 'r') as read_config:
            config = json.load(read_config)
            config['blackhole_path'] = os.path.dirname(self.config_path)
            self.config = config
            print(self.config)

    def requires(self):
        slurminfo = slurm.SlurmInfo(slurm.RUNMODE_LOCAL, "LuigiSetup",
                                    "batch", 1, 0, "Luigi_Workflow_Test", 1)
        if self.config['platform'] == "crane":
            slurminfo = slurm.SlurmInfo(slurm.RUNMODE_HPC, "choueiry",
                                        "batch", 1, None, "Luigi_Workflow_Test",
                                        1)

        stardust_path = os.path.join(self.config['stardust_path'],
                                     self.benchmark, self.instance)
        blackhole_path = os.path.join(self.config['blackhole_path'],
                                      self.benchmark, self.instance)
        blackhole_app = self.config['blackhole_app']

        config_txt = json.dumps(self.config)
        tasks = [
            ParseStardustFile(slurminfo, config_txt, blackhole_app,
                              stardust_path, blackhole_path),
            CheckpointDatabase(slurminfo, config_txt, blackhole_app,
                               blackhole_path),
            GenerateHistories(slurminfo, config_txt, blackhole_app,
                              blackhole_path),
            ArchiveDirectory(slurminfo, blackhole_path,
                             "%s.tar.xz" % blackhole_path,
                             self.config['blackhole_path'])
        ]

        return util.sequence_tasks(tasks)


class CreateWorkflows(luigi.WrapperTask):
    config_path = luigi.Parameter()

    def requires(self):
        config = None
        with open(self.config_path, 'r') as config_file:
            config = json.load(config_file)

        task_specs = []

        for directory in os.listdir(config['stardust_path']):
            benchmark_path = os.path.join(config['stardust_path'], directory)
            if os.path.isdir(benchmark_path):
                for file_path in glob.glob("%s/**/out.sd" % benchmark_path,
                                           recursive=True):
                    benchmark = os.path.relpath(file_path,
                                                config['stardust_path'])
                    benchmark = benchmark.split("/")[:-2]
                    benchmark = os.path.join(*benchmark)

                    instance = os.path.relpath(
                        file_path,
                        os.path.join(config['stardust_path'], benchmark))
                    instance = instance.split(".xml.outputFiles")[0]

                    task_specs.append((benchmark, instance))

        return [
            Workflow(config_path=self.config_path,
                     benchmark=benchmark,
                     instance=instance) for (benchmark, instance) in task_specs
        ]
