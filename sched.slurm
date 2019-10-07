#!/bin/sh
#SBATCH --mem-per-cpu=4096
#SBATCH --job-name=LuigiScheduler
#SBATCH --partition=batch

module load python/3.7

if [ -d "/path/to/dir" ]; then
    pip install --target $WORK/luigi_env/ virtualenv
    saved_pwd=$(pwd)
    cd $WORK/luigi_env
    python -m virtualenv .
    source ./bin/activate
    cd $saved_pwd
    pip install -r requirements.txt
    pip install -e .
else
    source $WORK/luigi_env/bin/activate
fi

export LUIGI_CONFIG_PARSER=toml
export LUIGI_CONFIG_PATH=$1
python3 ./unl_luigi/sched.py ${@:2}


# sbatch sched.slurm <LUIGI_CONFIG_PATH> <CREATE_TASKS_MODULE_PATH>
