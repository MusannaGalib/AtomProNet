#!/bin/bash

#SBATCH --account=def-mponga
#SBATCH --ntasks=128
#SBATCH --mem-per-cpu=10G
#SBATCH --time=01:00:00
#SBATCH --job-name=allegro_minimization
#SBATCH --output=output.txt
#SBATCH --error=error.txt




# Change to the directory where the job submission script is located
cd ../LAMMPS_comp_perf/ALLEGRO/6x6x6

# Run LAMMPS
mpiexec -np 128 /home/mewael/lammps-2Aug2023/build/lmp_mpi  -in in.minimization
