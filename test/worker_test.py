from absl.testing import parameterized

from gaps.task import Task
from gaps.parameter import Parameter
from gaps.worker import Worker


class BasicTask(Task):
    txt = Parameter()

    def __init__(self, *args, **kwargs):
        super(BasicTask, self).__init__(*args, **kwargs)
        self.completed = False

    def complete(self):
        return self.completed

    def run(self):
        self.completed = True


class SchedulerTest(parameterized.TestCase):
    def test_worker_factory(self):
        basic_worker = Worker.create("basic", [BasicTask(txt="3")])
        self.assertTrue(isinstance(basic_worker, Worker))
