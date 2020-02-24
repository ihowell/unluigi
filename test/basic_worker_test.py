import os
import shutil
from absl.testing import parameterized

import gaps
from gaps import Worker


class BasicTask(gaps.Task):
    root_dir = gaps.Parameter()

    def output(self):
        return gaps.LocalTarget(os.path.join(self.root_dir, "foo.txt"))

    def run(self):
        with self.output().open('w') as out_file:
            out_file.write("hello world")


class BasicWorkerTest(parameterized.TestCase):
    def setUp(self):
        if not os.path.exists("basic_worker_test_dir"):
            os.makedirs("basic_worker_test_dir")

    def tearDown(self):
        if os.path.exists("basic_worker_test_dir"):
            shutil.rmtree("basic_worker_test_dir")

    def test_basic_worker(self):
        basic_worker = Worker.create(
            "basic", [BasicTask(root_dir="basic_worker_test_dir")])
        basic_worker.start()
