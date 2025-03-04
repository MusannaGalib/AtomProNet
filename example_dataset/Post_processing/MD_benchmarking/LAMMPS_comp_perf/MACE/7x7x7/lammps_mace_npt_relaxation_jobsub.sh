#!/bin/bash

#SBATCH --account=def-mponga
#SBATCH --ntasks=1
#SBATCH --mem=192000M
#SBATCH --time=01:00:00
#SBATCH --job-name=mace_npt_relaxation
#SBATCH --output=output.txt
#SBATCH --error=error.txt
#SBATCH --gpus-per-node=v100l:1

module load cmake cuda cudnn

# Change to the directory where the job submission script is located
cd ../LAMMPS_comp_perf/MACE/7x7x7

# Run LAMMPS
mpiexec -np 1 /home/mewael/scratch/lammps_MACE_GPU/build/lmp -k on g 1 -sf kk -in in.npt_relaxation
