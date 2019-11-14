import requests
import warnings
import json
import os
from unluigi.config.experiment import ExperimentConfig
from unluigi.util.flatten import flatten


def get_experiment_id_path():
    return os.path.join(ExperimentConfig().experiment_dir, 'experiment_id')


def retrieve_new_experiment_id():
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
    print(response.text)
    return response.json()['task_id'] if response.status_code == 200 else None
