<?php
require 'database.php';

class LuigiRepository {
    private $db;

    function __construct() {
        $this->db = new LuigiDB();
        $this->ensure_database();
        $this->db->exec("PRAGMA foreign_keys=ON");
    }

    function get_db() {
        return $db;
    }

    function ensure_database() {
        $this->db->exec("create table if not exists Experiment"
                        . "(experiment_id integer primary key autoincrement,"
                        . " name varchar(256),"
                        . " root_task_id int,"
                        . " created timestamp not null,"
                        . " last_updated timestamp not null)");

        $this->db->exec("create table if not exists Task"
                        . "(task_id integer primary key autoincrement,"
                        . " experiment_id int not null,"
                        . " name varchar(512) not null,"
                        . " task_class varchar(256) not null,"
                        . " status varchar(16) not null,"
                        . " start_time timestamp,"
                        . " end_time timestamp,"
                        . " output_or_error mediumtext,"
                        . " last_updated timestamp not null,"
                        . " foreign key (experiment_id) references Experiment (experiment_id) on delete cascade on update cascade)");

        $this->db->exec("create table if not exists TaskDependency"
                        . "(parent_id int not null,"
                        . " child_id int not null,"
                        . " created timestamp not null,"
                        . " foreign key (parent_id) references Task (task_id) on delete cascade on update cascade,"
                        . " foreign key (child_id) references Task (task_id) on delete cascade on update cascade)");
    }

    function drop_all_tables() {
        foreach (array("TaskDependency", "Task", "Experiment") as $table) {
            $this->db->exec('drop table if exists ' . $table);
        }
    }

    function insert_experiment($name, $root_task_id, $created_timestamp) {
        $updated_timestamp = (new DateTime())->format('Y-m-d H:i:s.u');

        $this->db->exec("BEGIN;");

        $insert_smt = $this->db->prepare("insert into Experiment (name, root_task_id, created, last_updated)"
                                         . " values (:name, :root_id, :created_timestamp, :updated_timestamp);");
        $row_id_smt = $this->db->prepare("select last_insert_rowid();");


        $insert_smt->bindValue(':name', $name);
        $insert_smt->bindValue(':root_id', $root_task_id);
        $insert_smt->bindValue(':created_timestamp', $created_timestamp);
        $insert_smt->bindValue(':updated_timestamp', $updated_timestamp);

        $insert_smt->execute();
        $res = $row_id_smt->execute();
        $this->db->exec("COMMIT;");

        return $res->fetchArray(SQLITE3_NUM)[0];
    }

    function get_experiments() {
        $res = $this->db->query("select * from Experiment");
        $experiments = [];
        while ($r = $res->fetchArray(SQLITE3_ASSOC)) {
            array_push($experiments, $r);
        }
        return $experiments;
    }

    function check_experiment_exists_by_id($experiment_id) {
        $smt = $this->db->prepare("select 1 from Experiment where experiment_id=:experiment_id");
        $smt->bindValue(':experiment_id', $experiment_id);
        $res = $smt->execute();
        return $res->fetchArray() !== FALSE;
    }

    function update_experiment_root_task_id($experiment_id, $task_id) {
        $smt = $this->db->prepare("update Experiment set root_task_id=:task_id where experiment_id=:experiment_id");
        $smt->bindValue(':experiment_id', $experiment_id);
        $smt->bindValue(':task_id', $task_id);
        $smt->execute();
    }

    function update_experiment_timestamp($experiment_id) {
        $timestamp = (new DateTime())->format('Y-m-d H:i:s.u');
        $smt = $this->db->prepare("update Experiment set last_updated=:timestamp where experiment_id=:experiment_id");
        $smt->bindValue(':experiment_id', $experiment_id);
        $smt->bindValue(':timestamp', $timestamp);
        $smt->execute();
    }

    function delete_experiment($experiment_id) {
        $smt = $this->db->prepare("delete from Experiment where experiment_id=:experiment_id");
        $smt->bindValue(':experiment_id', $experiment_id);
        $smt->execute();
    }

    function insert_task($experiment_id, $name, $task_class, $status, $start_time, $end_time, $output_or_error) {
        $timestamp = (new DateTime())->format('Y-m-d H:i:s.u');
        $this->db->exec("BEGIN;");

        $insert_smt = $this->db->prepare("insert into Task (experiment_id, name, task_class, status, start_time,"
                                  . " end_time, output_or_error, last_updated) values(:experiment_id,"
                                  . " :name, :task_class, :status, :start_time, :end_time,"
                                  . " :output_or_error, :timestamp)");
        $row_id_smt = $this->db->prepare("select last_insert_rowid();");

        $insert_smt->bindValue(':experiment_id', $experiment_id);
        $insert_smt->bindValue(':name', $name);
        $insert_smt->bindValue(':task_class', $task_class);
        $insert_smt->bindValue(':status', $status);
        $insert_smt->bindValue(':start_time', $start_time);
        $insert_smt->bindValue(':end_time', $end_time);
        $insert_smt->bindValue(':output_or_error', $output_or_error);
        $insert_smt->bindValue(':timestamp', $timestamp);
        $insert_smt->execute();

        $res = $row_id_smt->execute();

        $this->db->exec("COMMIT;");

        return $res->fetchArray(SQLITE3_NUM)[0];
    }

    function get_tasks_for_experiment($experiment_id, $timestamp) {
        $smt = $this->db->prepare("select * from Task where experiment_id=:experiment_id and datetime(last_updated)>datetime(:timestamp)");
        $smt->bindValue(':experiment_id', $experiment_id);
        $smt->bindValue(':timestamp', $timestamp);
        $res = $smt->execute();

        $tasks = [];
        while ($r = $res->fetchArray(SQLITE3_ASSOC)) {
            array_push($tasks, $r);
        }
        return $tasks;
    }

    function check_task_exists_by_id($task_id) {
        $smt = $this->db->prepare("select task_id from Task where task_id=:task_id");
        $smt->bindValue(':task_id', $task_id);
        $res = $smt->execute();
        return $res->fetchArray() !== FALSE;
    }

    /**
     * Returns either the experiment_id of a given task or FALSE if
     * there is not task with the given id.
     */
    function get_task_experiment_id($task_id) {
        $smt = $this->db->prepare("select experiment_id from Task where task_id=:task_id");
        $smt->bindValue(':task_id', $task_id);
        $res = $smt->execute();
        $res = $res->fetchArray(SQLITE3_NUM);
        if ($res === FALSE)
            return FALSE;
        return $res[0];
    }

    function update_task_timestamp($task_id) {
        $timestamp = (new DateTime())->format('Y-m-d H:i:s.u');
        $smt = $this->db->prepare("update Task set last_updated=:timestamp where task_id=:task_id");
        $smt->bindValue(':task_id', $task_id);
        $smt->bindValue(':timestamp', $timestamp);
        $smt->execute();
    }

    function update_task_attributes($task_id, $status, $start_time, $end_time, $output_or_error) {
        $sql = "update Task set ";
        $attribute_strings = [];
        if ($status != NULL)
            array_push($attribute_strings, "status=:status");
        if ($start_time != NULL)
            array_push($attribute_strings, "start_time=:start_time");
        if ($end_time != NULL)
            array_push($attribute_strings, "end_time=:end_time");
        if ($output_or_error != NULL)
            array_push($attribute_strings, "output_or_error=:output_or_error");

        $sql .= implode(", ", $attribute_strings);
        $sql .= " where task_id=:task_id";
        $smt = $this->db->prepare($sql);
        $smt->bindValue(':task_id', $task_id);
        if ($status != NULL)
            $smt->bindValue(':status', $status);
        if ($start_time != NULL)
            $smt->bindValue(':start_time', $start_time);
        if ($end_time != NULL)
            $smt->bindValue(':end_time', $end_time);
        if ($output_or_error != NULL)
            $smt->bindValue(':output_or_error', $output_or_error);
        $res = $smt->execute();
    }

    function insert_task_dependency($parent_id, $child_id) {
        $timestamp = (new DateTime())->format('Y-m-d H:i:s.u');
        $smt = $this->db->prepare("insert into TaskDependency (parent_id, child_id, created) values (:parent_id, :child_id, :created_timestamp)");
        $smt->bindValue(':parent_id', $parent_id);
        $smt->bindValue(':child_id', $child_id);
        $smt->bindValue(':created_timestamp', $timestamp);
        $smt->execute();
    }

    function get_dependencies_for_tasks($task_ids) {
        if (sizeof($task_ids) == 0)
            return NULL;
        $sql = "select * from TaskDependency where parent_id in (" . implode(',', $task_ids) . ")";
        $res = $this->db->query($sql);
        $dependencies = [];
        while ($r = $res->fetchArray(SQLITE3_ASSOC)) {
            array_push($dependencies, $r);
        }
        return $dependencies;
    }

    function get_all() {
        echo("Experiments<br>");
        $res = $this->db->query("select * from Experiment");
        while($r = $res->fetchArray(SQLITE3_ASSOC)) {
            var_dump($r);
            echo("<br>");
        }
        echo("<br>Tasks<br>");
        $res = $this->db->query("select * from Task");
        while($r = $res->fetchArray(SQLITE3_ASSOC)) {
            var_dump($r);
            echo("<br>");
        }
        echo("<br>TaskDependencies<br>");
        $res = $this->db->query("select * from TaskDependency");
        while($r = $res->fetchArray(SQLITE3_ASSOC)) {
            var_dump($r);
            echo("<br>");
        }
    }
}
