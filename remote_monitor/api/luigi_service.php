<?php
require 'luigi_repository.php';
require_once 'util.php';

class LuigiService {
    private $repo;

    function __construct() {
        $this->repo = new LuigiRepository();
    }

    function drop_all_tables() {
        $this->repo->drop_all_tables();
    }

    function ensure_database() {
        $this->repo->ensure_database();
    }

    /**
     * Inserts a specified expeirment and returns the experiment_id of
     * the experiment after inserting it.
     */
    function insert_experiment($name, $created_timestamp) {
        return $this->repo->insert_experiment($name, -1, $created_timestamp);
    }

    function get_experiments() {
        return $this->repo->get_experiments();
    }

    function delete_experiment($experiment_id) {
        return $this->repo->delete_experiment($experiment_id);
    }

    function insert_root_task($experiment_id, $name, $task_class, $status, $start_time, $end_time, $output_or_error) {
        if (!$this->repo->check_experiment_exists_by_id($experiment_id)) {
            die("Experiment with id " . $experiment_id . " does not exist.");
            return;
        }
        $task_id = $this->repo->insert_task($experiment_id, $name, $task_class, $status, $start_time, $end_time, $output_or_error);
        $this->repo->update_experiment_root_task_id($experiment_id, $task_id);
        return $task_id;
    }

    function insert_worker_task($parent_id, $name, $task_class, $status, $start_time, $end_time, $output_or_error) {
        $experiment_id = $this->repo->get_task_experiment_id($parent_id);
        if ($experiment_id === FALSE) {
            die("Parent task with id " . $parent_id . " does not exist.");
        }
        $task_id = $this->repo->insert_task($experiment_id, $name, $task_class, $status, $start_time, $end_time, $output_or_error);
        $this->repo->insert_task_dependency($parent_id, $task_id);
        return $task_id;
    }

    function begin_task($task_id) {
        $this->repo->update_task_attributes($task_id, "inprogress", format_datetime(new DateTime()), NULL, NULL);
        $this->repo->update_task_timestamp($task_id);
    }

    function end_task($task_id, $succeeded, $output_or_error) {
        $status;
        if ($succeeded)
            $status = "succeeded";
        else
            $status = "failed";
        $this->repo->update_task_attributes($task_id, $status, NULL, format_datetime(new DateTime()), $output_or_error);
        $this->repo->update_task_timestamp($task_id);
    }

    function cancel_task($task_id) {
        $this->repo->update_task_attributes($task_id, "canceled", NULL, NULL, "Canceled task due to upstream error.");
        $this->repo->update_task_timestamp($task_id);
    }

    function get_task_updates_for_experiment($experiment_id, $timestamp = NULL) {
        if ($timestamp == NULL) {
            $timestamp = new DateTime();
            $timestamp->setTimestamp(0);
            $timestamp = format_datetime($timestamp);
        }
        return $this->repo->get_tasks_for_experiment($experiment_id, $timestamp);
    }

    function get_depdendencies_for_tasks($task_ids) {
        return $this->repo->get_dependencies_for_tasks($task_ids);
    }

    function get_all() {
        $this->repo->get_all();
    }
}
?>
