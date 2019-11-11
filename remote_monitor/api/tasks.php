<?php
require 'luigi_service.php';
require_once 'util.php';

$service = new LuigiService();

$inputJSON = file_get_contents('php://input');
$input = json_decode($inputJSON, TRUE);


if (!isset($input['experiment_id']) or gettype($input['experiment_id']) !== "integer")
    die("experiment_id not provided or not of type integer");

$last_retrieved_updates = NULL;
if (isset($input['last_retrieved_updates'])) {
    if (gettype($input['last_retrieved_updates']) != "integer")
        die("['last_retrieved_updates'] not of type integer");
    $last_retrieved_updates = new DateTime();
    $last_retrieved_updates->setTimestamp($input['last_retrieved_updates']);
    $last_retrieved_updates = format_datetime($last_retrieved_updates);
}

$tasks = $service->get_task_updates_for_experiment($input['experiment_id'], $last_retrieved_updates);

if (sizeof($tasks) > 0) {
    $extract_task_id = function($task) {
        return $task['task_id'];
    };
    $task_ids = array_map($extract_task_id, $tasks);
    $task_dependencies = $service->get_depdendencies_for_tasks($task_ids);

    $task_map = [];
    for ($i = 0; $i < sizeof($tasks); $i++) {
        $task_map[$tasks[$i]['task_id']] = $i;
    }


    foreach ($task_dependencies as $task_dependency) {
        $task_index = $task_map[$task_dependency['parent_id']];
        if (!isset($tasks[$task_index]['dependencies']))
            $tasks[$task_index]['dependencies'] = [];
        array_push($tasks[$task_index]['dependencies'], $task_dependency['child_id']);
    }
}

$now = new DateTime();

$data = ['tasks' => $tasks, 'last_retrieved_updates' => $now->getTimestamp()];
header('Content-Type: application/json');
echo json_encode($data);
?>
