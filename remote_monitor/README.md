# Luigi_visulizer


## API
To interact with the API, you just need to send specific GET requests with given bodies. The api endpoints and how to use them are described below:


### Experiments

* Navigation: `/api/experiments.php`

* Usage: A normal get request here will return in JSON a list of all experiments present in the database, along with all of their properties.


### Tasks

* Navigation: `/api/tasks.php`

* Usage: The tasks endpoint retrieves tasks associated with given experiments. The first call to this endpoint should contain a body like:
```
{
    "experiment_id": 1
}
```
This will retrieve all tasks associated with the experiment with id 1. In addition, it will pass back the timestamp that the request is good for in the field `last_retrieved_udpates`. Pass this value into the tasks endpoint the next time you call it, like:
```
{
    "experiment_id": 1,
    "last_retrieved_updates" 1572549963
}
```
Passing in this field will fetch only the tasks that have been updated since you last polled the endpoint, leading to much more efficient updates.


### Insert Experiment

* Navigation: `/api/insert_experiment.php`

* Usage: To insert an experiment, you will need to send a body with the name of the new experiment:
```
{
    "experiment_name": "My new experiment"
}
```
This endpoint will return the id of the newly added experiment.


### Insert Task

* Navigation: `/api/insert_task.php`

* Usage: There are two types of tasks, root tasks and worker tasks. A root task links together all the workerflows in an experiment, whereas a worker task takes part in a workflow. To add a root task, send a get request to the endpoint with this body schema:
```
{
    "task_name": "Root Task Name",
    "task_class": "root_task_class", //< This is just an example. It can be named anything
    "root_task": true,
    "experiment_id": 1
}
```
If adding a worker task, send this body instead:
```
{
    "task_name": "Root Task Name",
    "task_class": "root_task_class", //< This is just an example. It can be named anything
    "root_task": false,
    "parent_task_id": 1
}
```
Adding a worker task will insert the task and link it to its parent, so the parent task must be added to the database first. In either case, the id of the new task will be returned.


### Update Task

* Navigation: `/api/update_task.php`

* Usage Once tasks have been created (or before other tasks have been created), tasks can updated as started, stopped, or canceled. Each of these types of actions simply go to the update task endpoint. To flag the start of a task, send the following body to the endpoint:
```
{
    "task_id": 1,
    "action": "begin"
}
```
To flag the end of a task send the body:
```
{
    "task_id": 1,
    "action": "end",
    "succeeded": true,
    "output_or_error": "Output message from task"
}
```
You use the `end` action to mark a task either as succeeded or failed and provide additional information if required. Finally, to mark a task as canceled (such as in the event of an upstream error), send:
```
{
    "task_id": 1,
    "action": "cancel"
}
```


### Delete Experiment

* Navigation: `api/delete_experiment.php`

* Usage: Sometimes, you may wish to delete old experiments, simply send the `experiment_id` in a JSON body as before to the endpoint:
```
{
    "experiment_id": 1
}
```
