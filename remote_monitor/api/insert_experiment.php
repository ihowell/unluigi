<?php
require 'luigi_service.php';
require_once 'util.php';

$service = new LuigiService();

$now = format_datetime(new DateTime());

$input_json = file_get_contents('php://input');
$input = json_decode($input_json, TRUE);

ensure_string($input['experiment_name'], "input['experiment_name']");
$name = SQLite3::escapeString($input['experiment_name']);

$experiment_id = $service->insert_experiment($name, $now);

$data = ['experiment_id' => $experiment_id];
header('Content-Type: application/json');
echo json_encode($data);
?>
