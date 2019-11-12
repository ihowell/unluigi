#!/bin/sh

export LUIGI_CONFIG_PARSER=toml
export LUIGI_CONFIG_PATH=/Users/ihowell/Projects/blackhole/externalTools/luigi/example_configurations/local_config.toml
# python3 unluigi/sched.py unluigi/workflows/generate_final_metric_data.py
python3 unluigi/sched.py unluigi/workflows/generate_histories.py
