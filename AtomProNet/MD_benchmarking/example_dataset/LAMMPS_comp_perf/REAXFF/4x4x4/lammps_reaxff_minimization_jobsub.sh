#!/bin/bash

#SBATCH --account=def-mponga
#SBATCH --ntasks=1
#SBATCH --mem-per-cpu=10G
#SBATCH --time=01:00:00
#SBATCH --job-name=reaxff_minimization
#SBATCH --output=output.txt
#SBATCH --error=error.txt




# Change to the directory where the job submission script is located
cd /scratch/mewael/Testing/REAXFF/4x4x4

# Run LAMMPS
mpiexec -np 1 /home/mewael/lammps-17Apr2024/src/lmp_mpi  -in in.minimization
