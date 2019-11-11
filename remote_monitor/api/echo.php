<?php
$input_json = file_get_contents('php://input');
echo $input_json;
file_put_contents("my.json", $input_json);
?>
