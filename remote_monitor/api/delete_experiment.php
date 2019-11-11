<?php
require 'luigi_service.php';
require_once 'util.php';

$service = new LuigiService();

$inputJSON = file_get_contents('php://input');
$input = json_decode($inputJSON, TRUE);


if (!isset($input['experiment_id']) or gettype($input['experiment_id']) !== "integer")
    die("experiment_id not provided or not of type integer");

$service->delete_experiment($input['experiment_id']);
?>
