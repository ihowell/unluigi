import luigi
import glob
import os
from unluigi.config.blackhole import BlackholeConfig
from unluigi.config.stardust import StardustConfig
from unluigi.tasks.archive_blackhole import ArchiveBlackhole


class Workflow(luigi.WrapperTask):
    benchmark = luigi.Parameter()
    instance = luigi.Parameter()

    def requires(self):
        return ArchiveBlackhole(benchmark=self.benchmark,
                                instance=self.instance)


def create_tasks():
    task_specs = []

    stardust_path = StardustConfig().stardust_path
    for directory in os.listdir(stardust_path):
        benchmark_path = os.path.join(stardust_path, directory)
        if os.path.isdir(benchmark_path):
            for file_path in glob.glob("%s/**.sd" % benchmark_path,
                                       recursive=True):
                benchmark = os.path.relpath(file_path, stardust_path)
                benchmark = benchmark.split("/")[:-1]
                benchmark = os.path.join(*benchmark)

                instance = os.path.relpath(
                    file_path, os.path.join(stardust_path, benchmark))
                instance = instance.split('.')[0]

                task_specs.append((benchmark, instance))

    return [
        Workflow(benchmark=benchmark, instance=instance)
        for (benchmark, instance) in task_specs
    ]
