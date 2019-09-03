from types import MethodType


def sequence_tasks(tasks):
    prev_task = None
    for task in tasks:

        def requires_method(self):
            return self.prev_task

        task.requires = MethodType(requires_method, task)
        setattr(task, "prev_task", prev_task)
        prev_task = task
    return prev_task
