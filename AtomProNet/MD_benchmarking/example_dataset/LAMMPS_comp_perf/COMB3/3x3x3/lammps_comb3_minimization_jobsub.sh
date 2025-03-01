#!/bin/bash

#SBATCH --account=def-mponga
#SBATCH --ntasks=128
#SBATCH --mem-per-cpu=10G
#SBATCH --time=01:00:00
#SBATCH --job-name=comb3_minimization
#SBATCH --output=output.txt
#SBATCH --error=error.txt




# Change to the directory where the job submission script is located
cd ../LAMMPS_comp_perf/COMB3/3x3x3

# Run LAMMPS
mpiexec -np 128 /home/mewael/lammps-29Aug2024/src/lmp_mpi  -in in.minimization
