import luigi
import slurm
import os
import tar_target
import random


class atomic_file_pointer():
    def __init__(self, path):
        self.path = path

    def open(self):
        self.__tmp_path = self.generate_tmp_path(self.path)
        return self

    def close(self):
        self.move_to_final_destination()

    def move_to_final_destination(self):
        os.rename(self.tmp_path, self.path)

    def generate_tmp_path(self, path):
        return path + '-luigi-tmp-%09d' % random.randrange(0, 1e10)

    def __enter__(self):
        return self.open()

    def __exit__(self, exc_type, exc, traceback):
        return self.close()

    def __del__(self):
        if os.path.exists(self.tmp_path):
            os.remove(self.tmp_path)

    @property
    def tmp_path(self):
        return self.__tmp_path


class ArchiveDirectory(slurm.SlurmTask):
    directory_path = luigi.Parameter()
    output_tar = luigi.Parameter()
    relative_tar_path = luigi.Parameter()
    compression = luigi.Parameter(default="xz")

    def __init__(self, *args, **kwargs):
        super(ArchiveDirectory, self).__init__(*args, **kwargs)
        self.instance_name = "ArchiveDirectory_%s" % self.directory_path

    def output(self):
        return tar_target.TarTarget(self.output_tar)

    def run(self):
        with atomic_file_pointer(self.output_tar).open() as tar_file:
            self.ex(
                "tar cJf %s -C %s/ %s" %
                (tar_file.tmp_path, self.relative_tar_path,
                 os.path.relpath(self.directory_path, self.relative_tar_path)))
