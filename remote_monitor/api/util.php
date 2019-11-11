<?php

function format_datetime($datetime) {
    return $datetime->format('Y-m-d H:i:s.u');
}

function ensure_type($possible_instance, $type, $instance_name) {
    if (!isset($possible_instance))
        die($instance_name . " was not set");

    if (gettype($possible_instance) !== $type)
        die($instance_name . " was not of type " . $type);
}

function ensure_integer($possible_integer, $integer_name) {
    ensure_type($possible_integer, "integer", $integer_name);
}

function ensure_string($possible_string, $string_name) {
    ensure_type($possible_string, "string", $string_name);
}

function ensure_boolean($possible_boolean, $boolean_name) {
    ensure_type($possible_boolean, "boolean", $boolean_name);
}

?>
