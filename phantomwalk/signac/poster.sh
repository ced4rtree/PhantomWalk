#!/usr/bin/env sh

#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --gres=gpu:1
#SBATCH -t 00-05:00:00
#SBATCH -o poster-slurm.out
#SBATCH --error=poster-slurm.err
#SBATCH -J 1.5M_UA
#SBATCH -c 2
#SBATCH -N 1
#SBATCH -p gpu-v100

source ~/miniforge3/etc/profile.d/conda.sh
conda activate phantomwalk-dev
python poster.py
