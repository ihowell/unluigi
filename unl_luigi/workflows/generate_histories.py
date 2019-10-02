import luigi
import glob
import os
import unl_luigi.util as util
from unl_luigi.config.blackhole import BlackholeConfig
from unl_luigi.config.stardust import StardustConfig
from unl_luigi.tasks.archive_directory import ArchiveDirectory
from unl_luigi.tasks.checkpoint_database import CheckpointDatabase
from unl_luigi.tasks.generate_histories import GenerateHistories
from unl_luigi.tasks.parse_stardust_file import ParseStardustFile


class Workflow(luigi.WrapperTask):
    benchmark = luigi.Parameter()
    instance = luigi.Parameter()

    def requires(self):
        stardust_path = os.path.join(StardustConfig().stardust_path,
                                     self.benchmark, self.instance)
        blackhole_path = os.path.join(BlackholeConfig().blackhole_path,
                                      self.benchmark, self.instance)

        tasks = [
            ParseStardustFile(stardust_instance=stardust_path,
                              blackhole_path=blackhole_path),
            CheckpointDatabase(database_path=blackhole_path),
            GenerateHistories(database_path=blackhole_path),
            ArchiveDirectory(
                directory_path=blackhole_path,
                output_tar="%s.tar.xz" % blackhole_path,
                relative_tar_path=BlackholeConfig().blackhole_path)
        ]

        return util.sequence_tasks(tasks)


def create_tasks():
    task_specs = []

    stardust_path = StardustConfig().stardust_path
    for directory in os.listdir(stardust_path):
        benchmark_path = os.path.join(stardust_path, directory)
        if os.path.isdir(benchmark_path):
            for file_path in glob.glob("%s/**/out.sd" % benchmark_path,
                                       recursive=True):
                benchmark = os.path.relpath(file_path, stardust_path)
                benchmark = benchmark.split("/")[:-2]
                benchmark = os.path.join(*benchmark)

                instance = os.path.relpath(
                    file_path, os.path.join(stardust_path, benchmark))
                instance = instance.split(".xml.outputFiles")[0]

                task_specs.append((benchmark, instance))

    return [
        Workflow(benchmark=benchmark, instance=instance)
        for (benchmark, instance) in task_specs
    ]
