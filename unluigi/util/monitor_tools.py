import requests
import warnings
from unluigi.util.flatten import flatten


def ensure_experiment(experiment_name):
    """Ensures that the task exists in the database and returns the id of
    the task. If the task does not exist, returns null.

    """
    response = requests.post('http://localhost/api/insert_experiment.php')
    return response.json(
    )['experiment_id'] if response.status_code == 200 else None


def ensure_task(task):
    """Ensures that the task exists in the database and returns the id of
    the task. If the task does not exist, returns null.

    """
    params = task.to_str_params()
    requires = flatten(task.requires())
    requires = {t.get_task_family(): t.to_str_params() for t in requires}
    print("Requires: " + str(requires))
    response = requests.post('http://localhost/api/echo.php',
                             json={
                                 "class": task.get_task_family(),
                                 "params": params,
                                 "requires": requires
                             })
    print("Status code: " + str(response.status_code))
    print("Response: " + str(response.json()))
    if response.status_code != 200:
        warnings.warn("Warning: Was not able to ensure task")
    return response.json()['task_id'] if response.status_code == 200 else None
