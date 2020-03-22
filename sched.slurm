#!/bin/sh
#SBATCH --array=0-2
#SBATCH --mem-per-cpu=32768
#SBATCH --time=7-0
#SBATCH --job-name=LuigiWorker
#SBATCH --partition=batch,choueiry
#SBATCH --error=/work/[group]/[user]/sched_logs/sched_%a.err
#SBATCH --output=/work/[group]/[user]/sched_logs/sched_%a.out

./resources/crane_cpu.sh $@
