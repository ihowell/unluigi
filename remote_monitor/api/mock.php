<?php
require 'luigi_service.php';

$service = new LuigiService();
$service->drop_all_tables();
$service->ensure_database();

$now = new DateTime();
$now_string = $now->format('Y-m-d H:i:s.u');

$hour_ago = new DateTime();
$hour_ago->modify('-1 hour');
$hour_ago_string = $hour_ago->format('Y-m-d H:i:s.u');

$half_hour_ago = new DateTime();
$half_hour_ago->modify('-30 min');
$half_hour_ago_string = $half_hour_ago->format('Y-m-d H:i:s.u');

$experiment_id = $service->insert_experiment("Experiment 0", $hour_ago_string);

$root_task_id = $service->insert_root_task($experiment_id, "Root Task", "scheduler", "Pending", NULL, NULL, NULL);

$workflow_1_id = $service->insert_worker_task($root_task_id, "Workflow 1", "workflow", "Pending", NULL, NULL, NULL);
$calculate_1_id = $service->insert_worker_task($workflow_1_id, "Calculate 1", "calculate", "InProgress", $half_hour_ago_string, NULL, NULL);
$parse_1_id = $service->insert_worker_task($calculate_1_id, "Parse 1", "parse", "Complete", $hour_ago_string, $half_hour_ago_string, NULL);


$workflow_2_id = $service->insert_worker_task($root_task_id, "Workflow 2", "workflow", "Pending", $hour_ago_string, NULL, NULL);
$calculate_2_id = $service->insert_worker_task($workflow_2_id, "Calculate 2", "calculate", "Pending", $hour_ago_string, NULL, NULL);
$parse_2_id = $service->insert_worker_task($calculate_2_id, "Parse 2", "parse", "Complete", $hour_ago_string, NULL, NULL);


$workflow_3_id = $service->insert_worker_task($root_task_id, "Workflow 3", "workflow", "Pending", $hour_ago_string, NULL, NULL);
$calculate_3_id = $service->insert_worker_task($workflow_3_id, "Calculate 3", "calculate", "Pending", $hour_ago_string, NULL, NULL);
$parse_3_id = $service->insert_worker_task($calculate_3_id, "Parse 3", "parse", "Complete", $hour_ago_string, NULL, NULL);


$experiment_2_id = $service->insert_experiment("Experiment 1", $half_hour_ago_string);

$root_2_task_id = $service->insert_root_task($experiment_2_id, "Root Task", "scheduler", "Complete", $now_string, $now_string, NULL);

$workflow_1_id = $service->insert_worker_task($root_2_task_id, "Workflow B", "workflow", "Complete", $now_string, $now_string, "All tasks for workflow B complete");
$calculate_1_id = $service->insert_worker_task($workflow_1_id, "Calculate B", "calculate", "Complete", $half_hour_ago_string, $now_string, NULL);
$parse_1_id = $service->insert_worker_task($calculate_1_id, "Parse B", "parse", "Complete", $half_hour_ago_string, $half_hour_ago_string, NULL);

$service->get_all();
?>
