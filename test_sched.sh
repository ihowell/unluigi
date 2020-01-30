#!/bin/sh

export LUIGI_CONFIG_PARSER=toml
export LUIGI_CONFIG_PATH=/Users/ihowell/Projects/unluigi/example_configurations/local_test_config.toml
python3 unluigi/sched.py unluigi/test/test_workflow.py
# python3 unluigi/sched.py unluigi/workflows/final_metric_data.py
# python3 unluigi/sched.py unluigi/workflows/histories.py
