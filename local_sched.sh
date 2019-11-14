#!/bin/sh

export LUIGI_CONFIG_PARSER=toml
export LUIGI_CONFIG_PATH=/Users/ihowell/Projects/unluigi/example_configurations/local_config.toml
python3 unluigi/sched.py unluigi/workflows/monitor_workflow.py
