<?php
require 'luigi_service.php';
require_once 'util.php';

$service = new LuigiService();

$now = format_datetime(new DateTime());

$input_json = file_get_contents('php://input');
$input = json_decode($input_json, TRUE);

ensure_integer($input['experiment_id'], "input['experiment_id']");
ensure_string($input['action'], "action['action']");

$experiment_id = $input['experiment_id'];
$action = SQLite3::escapeString($input['action']);

if ($action === 'complete') {
    $service->complete_experiment($experiment_id);
} else if($action === 'canceled') {
    $service->complete_experiment($experiment_id, TRUE);
} else {
    die("Undetermined action " . $action);
}
?>
