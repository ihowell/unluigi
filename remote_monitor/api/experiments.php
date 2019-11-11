<?php
require 'luigi_service.php';

$service = new LuigiService();

$experiments = $service->get_experiments();

$data = ['experiments' => $experiments];
header('Content-Type: application/json');
echo json_encode($data);
?>
