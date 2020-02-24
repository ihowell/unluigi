"""This module provides a client for running tasks via slurm"""

import argparse
import json
import importlib

import gaps


def serialize_task_list(task_list):
    """Serializes a task_list to a JSON string.

    This JSON string can then be deserialized by
    :ref:`deserialize_tasks` to be used as a task list for a
    BasicWorker.

    Args:
       task_list (iterable(Task)): The list of tasks to be serialized

    Returns:
       task_list_str (str): A serialization of the JSON-ified task list
    """
    output_obj = []
    for task in task_list:
        task_obj = {}
        cls = task.__class__
        task_obj['module'] = cls.__module__
        task_obj['class'] = cls.__name__
        task_obj['params'] = task.to_str_params()
        output_obj.append(task_obj)
    return json.dumps(output_obj, separators=(',', ':'))


def deserialize_task_list(task_list_str):
    """Deserializes a task list that has been serialized to a JSON string

    Args:
       task_list_str (str): The string of JSON representing a task list

    Returns:
       task_list (list(Task)): The list of tasks, deserialized
    """
    task_list_json = json.loads(task_list_str)
    task_list = []
    for task_obj in task_list_json:
        task_module = importlib.import_module(task_obj['module'])
        task_cls = getattr(task_module, task_obj['class'])
        task = task_cls.from_str_params(task_obj['params'])
        task_list.append(task)
    return task_list


def main():
    """Parses a task list from CLI args and then runs the task list in a BasicWorker
    """
    parser = argparse.ArgumentParser(
        description='Runs jobs on Crane nodes for the SlurmWorker')
    parser.add_argument('task_list_str')
    args = parser.parse_args()

    task_list = deserialize_task_list(args.task_list_str)
    worker = gaps.worker.BasicWorker(task_list)
    worker.start()


if __name__ == '__main__':
    main()
