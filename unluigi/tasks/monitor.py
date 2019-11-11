import luigi
from unluigi.util import monitor_tools
from unluigi.tasks import shell_task


def setup_monitor_experiment(experiment_name):
    experiment_id = monitor_tools.ensure_experiment(experiment_name)


class MonitorTask(shell_task.ShellTask):
    def __init__(self, *args, **kwargs):
        super(MonitorTask, self).__init__(*args, **kwargs)
        self.monitor_task_id = monitor_tools.ensure_task(self)
