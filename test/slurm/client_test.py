"""Test module for slurm client functionality"""

from absl.testing import parameterized

import gaps
from gaps.worker.slurm.client import serialize_task_list, deserialize_task_list


class BasicTask(gaps.Task):
    """Test task. Should not be used for anything every"""
    foo_param = gaps.Parameter()


class SlurmClientTest(parameterized.TestCase):
    """Basic test suite for slurm client methods"""
    def test_serialization_deserialization(self):
        """Test serializationa and deserialization of tasks"""
        task_list = [
            BasicTask(foo_param='basic_worker_test_dir'),
            BasicTask(foo_param='asdflk')
        ]
        task_list_str = serialize_task_list(task_list)
        second_task_list = deserialize_task_list(task_list_str)

        print('Task list orig', task_list)
        print('Task list finl', second_task_list)
        print('Task list string', task_list_str)
        self.assertTrue(len(task_list) == len(second_task_list))
        for task_1, task_2 in zip(task_list, second_task_list):
            # Cannot do trivial equality, as when a task is reloaded,
            # it has a new module name
            print('modules', task_1.__class__.__module__,
                  task_2.__class__.__module__)
            print('families', task_1.get_task_family(),
                  task_2.get_task_family())
            self.assertTrue(
                task_1.get_task_family() == task_2.get_task_family())
            self.assertTrue(task_1.to_str_params() == task_2.to_str_params())
