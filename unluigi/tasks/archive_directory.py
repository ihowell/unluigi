import luigi
import os
import random
from unluigi.util.atomic_file_pointer import AtomicFilePointer
from unluigi.tasks.slurm import SlurmTask


class ArchiveDirectory(SlurmTask):
    compression = luigi.Parameter(default="xz")

    def archive_directory(self, directory_path, output_tar, relative_tar_path):
        with AtomicFilePointer(output_tar).open() as tar_file:
            self.ex("tar cJf %s -C %s/ %s" %
                    (tar_file.tmp_path, relative_tar_path,
                     os.path.relpath(directory_path, relative_tar_path)))
