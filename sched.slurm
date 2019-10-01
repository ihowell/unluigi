#!/bin/sh
#SBATCH --mem-per-cpu=4096
#SBATCH --job-name=LuigiScheduler
#SBATCH --partition=batch
#SBATCH --error=/work/[groupname]/[username]/sched_logs/job.%J.err
#SBATCH --output=/work/[groupname]/[username]/sched_logs/job.%J.out

module load python/3.7
pip install --user -r requirements.txt
export PATH=$PATH:/home/[groupname]/[username]/.local/bin

export LUIGI_CONFIG_PARSER=toml
export LUIGI_CONFIG_PATH=$1
python3 ./unl_luigi/sched.py ${@:2}
