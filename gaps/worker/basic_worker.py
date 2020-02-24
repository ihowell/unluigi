from gaps.worker.worker import Worker
import gaps.task_status as task_status


@Worker.register("basic")
class BasicWorker(Worker):
    """A basic worker runs tasks in the same thread as the scheduler

    This worker is not intended for scalable use, but just as a use
    case for testing. This worker immediately runs all tasks given to
    it when start is called, blocking the scheduler from continuing.

    """
    def start(self):
        self.task_statuses = []
        task_chain_failed = False
        for task in self.task_list:
            if not task_chain_failed:
                if task.ready():
                    task.run()
                    if task.complete():
                        self.task_statuses.append(task_status.DONE)
                    else:
                        self.task_statuses.append(task_status.FAILED)
                        task_chain_failed = True
                else:
                    self.task_statuses.append(task_status.WORKER_CANCELED)
            else:
                self.task_statuses.append(task_status.WORKER_CANCELED)

    def stop(self):
        return

    def is_running(self):
        return False

    def get_task_statuses(self):
        return self.task_statuses
