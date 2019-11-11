<?php
class LuigiDB extends SQLite3
{
    function __construct()
    {
        // Opens the database file and ensures that the given tables exist

        $this->open('luigi_sqlite.db');
    }
}
?>
