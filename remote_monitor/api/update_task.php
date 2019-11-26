<?php
require 'luigi_service.php';
require_once 'util.php';

$service = new LuigiService();

$now = format_datetime(new DateTime());

$input_json = file_get_contents('php://input');
$input = json_decode($input_json, TRUE);

if (!isset($input['task_id']) or gettype($input['task_id']) != "integer")
    die("['task_id'] either not provided or is not integer");
if (!isset($input['action']) or gettype($input['action']) != "string")
    die("['action'] either not provided or is not string");

$task_id = $input['task_id'];
$action = SQLite3::escapeString($input['action']);

if ($action === 'begin') {
    $service->begin_task($task_id);
} else if($action === 'end') {
    if (!isset($input['succeeded']) or gettype($input['succeeded']) != "boolean")
        die("['succeeded'] either not provided or is not boolean");
    if (!isset($input['output_or_error']) or gettype($input['output_or_error']) != "string")
        die("['output_or_error'] either not provided or is not string");
    $succeeded = $input['succeeded'];
    $output_or_error = SQLite3::escapeString($input['output_or_error']);
    $service->end_task($task_id, $succeeded, $output_or_error);
} else if ($action == 'found_completed') {
    $service->found_task_completed($task_id);
} else if ($action === 'cancel') {
    $service->cancel_task($task_id);
} else {
    die("Given action not one of begin, end, cancel");
}
?>
