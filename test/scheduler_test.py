from absl.testing import parameterized

import gaps
from gaps.scheduler import Scheduler


class BasicTask(gaps.Task):
    txt = gaps.Parameter()

    def __init__(self, *args, **kwargs):
        super(BasicTask, self).__init__(*args, **kwargs)
        self.completed = False

    def complete(self):
        return self.completed

    def run(self):
        self.completed = True


class DependsTask(BasicTask):
    txt = gaps.Parameter()

    def __init__(self, *args, **kwargs):
        super(DependsTask, self).__init__(*args, **kwargs)
        self.completed = False

    def requires(self):
        return [BasicTask(txt=self.txt + "1"), BasicTask(txt=self.txt + "2")]

    def complete(self):
        return self.completed

    def run(self):
        self.completed = True


class SchedulerTest(parameterized.TestCase):
    def setUp(self):
        self.task_list = []
        self.task_list.append(BasicTask(txt="1"))
        self.task_list.append(BasicTask(txt="2"))
        self.task_list.append(DependsTask(txt="3"))

    def test_build_dag_tree(self):
        scheduler = gaps.scheduler.Scheduler(self.task_list)
        scheduler._build_dag_tree()

        depends_3_key = Scheduler.task_key(DependsTask(txt="3"))
        basic_31_key = Scheduler.task_key(BasicTask(txt="31"))
        basic_32_key = Scheduler.task_key(BasicTask(txt="32"))

        self.assertTrue(BasicTask(txt="1") in scheduler.frontier_tasks)
        self.assertTrue(BasicTask(txt="2") in scheduler.frontier_tasks)
        self.assertTrue(BasicTask(txt="31") in scheduler.frontier_tasks)
        self.assertTrue(BasicTask(txt="32") in scheduler.frontier_tasks)

        self.assertTrue(depends_3_key in scheduler.depends_on)
        self.assertTrue(basic_31_key in scheduler.depends_on[depends_3_key])
        self.assertTrue(basic_32_key in scheduler.depends_on[depends_3_key])

        self.assertTrue(basic_31_key in scheduler.depended_by)
        self.assertTrue(depends_3_key in scheduler.depended_by[basic_31_key])

        self.assertTrue(basic_32_key in scheduler.depended_by)
        self.assertTrue(depends_3_key in scheduler.depended_by[basic_32_key])
