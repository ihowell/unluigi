import luigi
import os
from unluigi.targets.archive_target import ArchiveTarget
from unluigi.config.blackhole import BlackholeConfig
from unluigi.tasks.archive_directory import ArchiveDirectory
from unluigi.tasks.generate_histories import GenerateHistories


class ArchiveBlackhole(ArchiveDirectory):
    benchmark = luigi.Parameter()
    instance = luigi.Parameter()

    def __init__(self, *args, **kwargs):
        super(ArchiveBlackhole, self).__init__(*args, **kwargs)
        self.instance_name = "ArchiveBlackhole_%s_%s" % (self.benchmark,
                                                         self.instance)

    @property
    def output_tar(self):
        blackhole_path = os.path.join(BlackholeConfig().blackhole_path,
                                      self.benchmark, self.instance)
        return "%s.tar.xz" % blackhole_path

    def output(self):
        return ArchiveTarget(self.output_tar)

    def requires(self):
        GenerateHistories(benchmark=self.benchmark, instance=self.instance)

    def run(self):
        blackhole_path = os.path.join(BlackholeConfig().blackhole_path,
                                      self.benchmark, self.instance)
        self.archive_directory(blackhole_path, "%s.tar.xz" % blackhole_path,
                               BlackholeConfig().blackhole_path)
