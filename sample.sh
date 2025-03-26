#!/bin/bash
#SBATCH -N 1 # Number of nodes requested
#SBATCH --ntasks-per-node=8
#SBATCH -t 0-05:00:00 # Runtime
#SBATCH --mem=40000 # Memory per node in MB (see also --mem-per-cpu)
#SBATCH -p gpu_test
#SBATCH --gres=gpu:2
#SBATCH -o slurm-%j.out # Standard out goes to this file
#SBATCH -e slurm-%j.err # Standard err goes to this filehostname

source ~/anaconda3/etc/profile.d/conda.sh
scratch
cd nf_flare_cg/coarse-graining-AL
conda activate coarse_graining
python -m main.train_sample --config ./main/configs/aldp_AL.yaml
# python -m main.torch_test
