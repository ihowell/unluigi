import luigi
import luigi.local_target
import tarfile
import os
import random
import warnings
import tempfile

_tar_read_modes = ['r', 'r:', 'r:*', 'r:gz', 'r:bz2', 'r:xz']
_tar_write_modes = [
    'x', 'x:', 'x:gz', 'x:bz2', 'x:xz', 'w', 'w:', 'w:gz', 'w:bz2', 'w:xz'
]
_tar_modes = _tar_read_modes + _tar_write_modes


class atomic_archive(tarfile.TarFile):
    """Abstract class to create a Target that creates a temporary archive
    in the local filesystem before moving it to its final destination.
    This class is just for the writing part of the Target, i.e.,
    adding files to the archive. See :class:`luigi.file.LocalTarget`
    for example

    """
    @classmethod
    def open(cls, name=None, *args, **kwargs):
        if name is not None:
            tmp_path = cls.generate_tmp_path(name)
            return super(atomic_archive, cls).open(tmp_path,
                                                   *args,
                                                   real_path=name,
                                                   **kwargs)
        else:
            return super(atomic_archive, cls).open(name, *args, **kwargs)

    def __init__(self, name, *args, real_path=None, **kwargs):
        if real_path is not None:
            self.path = real_path
            self.__tmp_path = name
        else:
            self.path = name
            self.__tmp_path = self.generate_tmp_path(name)
        super(atomic_archive, self).__init__(self.__tmp_path, *args, **kwargs)

    def close(self):
        super(atomic_archive, self).close()
        self.move_to_final_destination()

    def move_to_final_destination(self):
        os.rename(self.tmp_path, self.path)

    @classmethod
    def generate_tmp_path(cls, path):
        return path + '-luigi-tmp-%09d' % random.randrange(0, 1e10)

    def __del__(self):
        if os.path.exists(self.tmp_path):
            os.remove(self.tmp_path)

    @property
    def tmp_path(self):
        return self.__tmp_path

    def __exit__(self, exc_type, exc, traceback):
        " Close/commit the file if there are no exception "
        if exc_type:
            return
        return super(atomic_archive, self).__exit__(exc_type, exc, traceback)


class ArchiveTarget(luigi.local_target.FileSystemTarget):
    fs = luigi.local_target.LocalFileSystem()

    def __init__(self, path=None, is_tmp=False):
        if not path:
            if not is_tmp:
                raise Exception('path or is_tmp must be set')
            path = os.path.join(
                tempfile.gettempdir(),
                'luigi-tmp-%09d' % random.randint(0, 999999999))
        super(ArchiveTarget, self).__init__(path)
        self.is_tmp = is_tmp

    def makedirs(self):
        """
        Create all parent folders if they do not exist.
        """
        normpath = os.path.normpath(self.path)
        parentfolder = os.path.dirname(normpath)
        if parentfolder:
            try:
                os.makedirs(parentfolder)
            except OSError:
                pass

    def open(self, mode='w', *args, **kwargs):
        if mode not in _tar_write_modes:
            raise Exception("Received mode %s. Mode must be one of: %s" %
                            (mode, str(_tar_write_modes)))

        if mode[0] in ['w', 'x']:
            self.makedirs()
            # return atomic_archive(self.path, mode=mode, **kwargs)
            return atomic_archive.open(self.path, mode, *args, **kwargs)
        raise Exception("Should never reach here")

    def move(self, new_path, raise_if_exists=False):
        self.fs.move(self.path, new_path, raise_if_exists=raise_if_exists)

    def move_dir(self, new_path):
        self.move(new_path)

    def remove(self):
        self.fs.remove(self.path)

    def copy(self, new_path, raise_if_exists=False):
        self.fs.copy(self.path, new_path, raise_if_exists)

    @property
    def fn(self):
        warnings.warn("Use LocalTarget.path to reference filename",
                      DeprecationWarning,
                      stacklevel=2)
        return self.path
