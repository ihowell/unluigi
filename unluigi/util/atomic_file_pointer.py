import os
import random


class AtomicFilePointer():
    def __init__(self, path):
        self.path = path

    def open(self):
        if not os.path.exists(os.path.dirname(self.path)):
            os.makedirs(os.path.dirname(self.path))
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
