#!/bin/sh
#SBATCH --mem-per-cpu=8192
#SBATCH --job-name=LuigiScheduler
#SBATCH --partition=scott
#SBATCH --time=7-00:00:00

module load python/3.7

if [ ! -d "./env" ]; then
    pip install --target ./env/ virtualenv
    cd ./env
    python -m virtualenv .
    cd ..
    source ./env/bin/activate
    pip install -r requirements.txt
    pip install -e .
else
    source ./env/bin/activate
fi

export LUIGI_CONFIG_PARSER=toml
export LUIGI_CONFIG_PATH=$1
python3 ./unluigi/sched.py ${@:2}


# sbatch sched.slurm <LUIGI_CONFIG_PATH> <CREATE_TASKS_MODULE_PATH>
