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

        self.assertTrue(len(task_list) == len(second_task_list))
        for task_1, task_2 in zip(task_list, second_task_list):
            self.assertTrue(task_1 == task_2)
