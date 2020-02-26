import os
import shutil
import pathlib

from absl.testing import parameterized

import gaps


class BasicTask(gaps.Task):
    directory = gaps.Parameter()
    txt = gaps.Parameter()

    def output(self):
        return gaps.LocalTarget(
            os.path.join(self.directory, 'basic-' + self.txt + '.txt'))

    def run(self):
        with self.output().open('w') as out_file:
            out_file.write('hello-' + self.txt)


class DependsTask(BasicTask):
    directory = gaps.Parameter()
    txt = gaps.Parameter()

    def requires(self):
        return [
            BasicTask(directory=self.directory, txt=self.txt + '1'),
            BasicTask(directory=self.directory, txt=self.txt + '2')
        ]

    def output(self):
        return gaps.LocalTarget(
            os.path.join(self.directory, 'depends-' + self.txt + '.txt'))

    def run(self):
        with self.output().open('w') as out_file:
            for input_target in self.input():
                with input_target.open('r') as in_file:
                    out_file.write(in_file.read() + '\n')


class BasicWorkflowIntegrationTest(parameterized.TestCase):
    def setUp(self):
        exp_dir = self.get_exp_dir()
        if os.path.exists(exp_dir):
            shutil.rmtree(exp_dir)
        os.makedirs(self.get_exp_dir())

    def tearDown(self):
        exp_dir = self.get_exp_dir()
        if os.path.exists(exp_dir):
            shutil.rmtree(exp_dir)

    def get_exp_dir(self):
        base_path = os.getenv('WORK', pathlib.Path(__file__).parent.absolute())
        return os.path.join(base_path, 'basic-workflow-integration')

    def test_run_scheduler_basic_worker(self):
        exp_dir = os.path.join(self.get_exp_dir(), 'basic')
        self.task_list = []
        self.task_list.append(BasicTask(directory=exp_dir, txt='1'))
        self.task_list.append(BasicTask(directory=exp_dir, txt='2'))
        self.task_list.append(DependsTask(directory=exp_dir, txt='3'))

        scheduler = gaps.scheduler.Scheduler(self.task_list,
                                             worker_type='basic')
        scheduler.run()

        for task in self.task_list:
            self.assertTrue(task.complete())

    def test_run_scheduler_slurm_worker(self):
        if gaps.util.test_slurm_availability():
            exp_dir = os.path.join(self.get_exp_dir(), 'slurm')
            self.task_list = []
            self.task_list.append(BasicTask(directory=exp_dir, txt='1'))
            self.task_list.append(BasicTask(directory=exp_dir, txt='2'))
            self.task_list.append(DependsTask(directory=exp_dir, txt='3'))

            scheduler = gaps.scheduler.Scheduler(self.task_list,
                                                 worker_type='slurm')
            scheduler.run()

            for task in self.task_list:
                self.assertTrue(task.complete())
