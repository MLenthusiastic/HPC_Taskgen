#!/bin/sh -v
#PBS -e /mnt/home/amal01/Thesis/Codings/A
#PBS -o /mnt/home/amal01/Thesis/Codings/A
#PBS -q batch
#PBS -p 1000
#PBS -l nodes=1:ppn=1
#PBS -l mem=5gb
#PBS -l walltime=96:00:00

eval "$(conda shell.bash hook)"
source activate conda_env_01


cd /mnt/home/amal01/Thesis/Codings/A
python my_taskgen.py