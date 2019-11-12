#!/bin/sh

module load compiler/gcc/8.2
module load boost/1.67

export LUIGI_CONFIG_PARSER=toml
export LUIGI_CONFIG_PATH=/home/ihowell/blackhole/externalTools/luigi/example_configurations/zebra_config.toml
nohup python3 unluigi/sched.py unluigi/workflows/generate_final_metric_data.py &
