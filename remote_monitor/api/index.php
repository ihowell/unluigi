<?php
require 'luigi_service.php';

$service = new LuigiService();
$all = $service->get_all();

header('Content-Type: application/json');
echo json_encode($all);
?>
