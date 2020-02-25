import os
import random
import warnings
import tempfile
import gaps


class atomic_path():
    """Abstract class to create a Target that creates a temporary archive
    in the local filesystem before moving it to its final destination.
    This class is just for the writing part of the Target, i.e.,
    adding files to the archive. See :class:`gaps.file.LocalTarget`
    for example

    """
    @classmethod
    def open(cls, name=None, *args, **kwargs):
        if name is not None:
            tmp_path = cls.generate_tmp_path(name)
            return cls(tmp_path, *args, real_path=name, **kwargs)
        else:
            return cls(name, *args, **kwargs)

    def __init__(self, name, real_path=None):
        if real_path is not None:
            self.path = real_path
            self.__tmp_path = name
        else:
            self.path = name
            self.__tmp_path = self.generate_tmp_path(name)

    def close(self):
        self.move_to_final_destination()

    def move_to_final_destination(self):
        os.rename(self.tmp_path, self.path)

    @classmethod
    def generate_tmp_path(cls, path):
        return path + '-gaps-tmp-%09d' % random.randrange(0, 1e10)

    def __del__(self):
        if os.path.exists(self.tmp_path):
            if os.path.isdir(self.tmp_path):
                os.rmdir(self.tmp_path)
            else:
                os.remove(self.tmp_path)

    @property
    def tmp_path(self):
        return self.__tmp_path

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        " Close/commit the file if there are no exceptions "
        if exc_type:
            return
        if os.path.exists(self.tmp_path):
            self.move_to_final_destination()


class PathTarget(gaps.local_target.FileSystemTarget):
    fs = gaps.local_target.LocalFileSystem()

    def __init__(self, path=None, is_tmp=False):
        if not path:
            if not is_tmp:
                raise Exception('path or is_tmp must be set')
            path = os.path.join(tempfile.gettempdir(),
                                'gaps-tmp-%09d' % random.randint(0, 999999999))
        super(PathTarget, self).__init__(path)
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

    def open(self, *args, **kwargs):
        self.makedirs()
        return atomic_path.open(self.path, *args, **kwargs)

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

    def __del__(self):
        if self.is_tmp and self.exists():
            self.remove()
