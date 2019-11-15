import requests
import warnings
import json
import os
from unluigi.config.experiment import ExperimentConfig


class ExperimentContext:
    def __enter__(self):
        self.ended_experiment = False
        self.experiment_id = self.retrieve_new_experiment_id()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self.ended_experiment:
            self.complete_experiment(True)

    def retrieve_new_experiment_id(self):
        """Ensures that the task exists in the database and returns the id of
        the task. If the task does not exist, returns null.

        """
        response = requests.post(
            os.path.join(ExperimentConfig().server_url, 'api',
                         'insert_experiment.php'),
            json={'experiment_name': ExperimentConfig().experiment_name})

        if response.status_code == 200:
            path = get_experiment_id_path()
            if not os.path.exists(os.path.dirname(path)):
                os.makedirs(os.path.dirname(path))
            with open(path, 'w') as out_file:
                json.dump(response.json(), out_file)
            return response.json()['experiment_id']

    def complete_experiment(self, canceled=False):
        self.ended_experiment = True
        body = {
            'experiment_id': self.experiment_id,
            'action': 'complete' if not canceled else 'canceled'
        }
        api_endpoint = os.path.join(ExperimentConfig().server_url, 'api',
                                    'update_experiment.php')

        response = requests.post(api_endpoint, json=body)

        if response.status_code != 200:
            warnings.warn(
                "Warning: Was not able to update experiment to complete")


def get_experiment_id_path():
    return os.path.join(ExperimentConfig().experiment_dir, 'experiment_id')


def erase_old_experiment_id():
    path = get_experiment_id_path()
    if os.path.exists(path):
        os.remove(path)


def get_experiment_id():
    path = get_experiment_id_path()
    if not os.path.exists(path):
        raise Exception(
            "Error: Attempted to retrieve experiment_id when it does not exist."
        )
    with open(path, 'r') as f:
        experiment_id = json.load(f)['experiment_id']
    return experiment_id


def ensure_task(task, root_task=False):
    """Ensures that the task exists in the database and returns the id of
    the task. If the task does not exist and cannot be created, returns None.

    """
    params = task.to_str_params()
    body = {
        'root_task': root_task,
        'task_name': task.get_task_name(),
        'task_class': task.get_task_family(),
        'task_params': json.dumps(params),
        'experiment_id': get_experiment_id()
    }
    if not root_task:
        body['parent_task_id'] = task.parent_id

    api_endpoint = os.path.join(ExperimentConfig().server_url, 'api',
                                'ensure_task.php')

    response = requests.post(api_endpoint, json=body)

    if response.status_code != 200:
        warnings.warn("Warning: Was not able to ensure task")
    return response.json()['task_id'] if response.status_code == 200 else None


def send_task_began(task_id):
    body = {'task_id': task_id, 'action': 'begin'}
    api_endpoint = os.path.join(ExperimentConfig().server_url, 'api',
                                'update_task.php')

    response = requests.post(api_endpoint, json=body)
    if response.status_code != 200:
        warnings.warn("Unsuccessful in updating task %d to the begin state" %
                      task_id)


def send_task_succeeded(task_id, output):
    send_task_completed(task_id, True, output)


def send_task_failed(task_id, error):
    send_task_completed(task_id, False, error)


def send_task_completed(task_id, succeeded, output_or_error):
    body = {
        'task_id': task_id,
        'action': 'end',
        'succeeded': succeeded,
        'output_or_error': output_or_error
    }
    api_endpoint = os.path.join(ExperimentConfig().server_url, 'api',
                                'update_task.php')

    response = requests.post(api_endpoint, json=body)
    if response.status_code != 200:
        warnings.warn(
            "Unsuccessful in updating task %d to the %s completed state" %
            (task_id, 'success' if succeeded else 'failed'))


def send_found_task_completed(task_id):
    body = {'task_id': task_id, 'action': 'found_completed'}
    api_endpoint = os.path.join(ExperimentConfig().server_url, 'api',
                                'update_task.php')

    response = requests.post(api_endpoint, json=body)
    if response.status_code != 200:
        warnings.warn(
            "Unsuccessful in updating task %d to the found completed state" %
            task_id)
