import glob
import luigi
import os
import unl_luigi.util as util
from unl_luigi.config.blackhole import BlackholeConfig
from unl_luigi.config.stardust import StardustConfig
from unl_luigi.tasks.parse_stardust_file import ParseStardustFile
from unl_luigi.tasks.final_metric_data import FinalMetricData
from unl_luigi.tasks.copy_blackhole_web_data import CopyBlackholeWebData


class Workflow(luigi.WrapperTask):
    benchmark = luigi.Parameter()
    instance = luigi.Parameter()

    def requires(self):
        stardust_instance_path = os.path.join(StardustConfig().stardust_path,
                                              self.benchmark, self.instance)
        blackhole_path = os.path.join(BlackholeConfig().blackhole_path,
                                      self.benchmark, self.instance)
        tasks = [
            ParseStardustFile(stardust_instance=stardust_instance_path,
                              blackhole_path=blackhole_path),
            FinalMetricData(blackhole_path=blackhole_path),
            CopyBlackholeWebData(benchmark=self.benchmark,
                                 consistency_instance=self.instance)
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
