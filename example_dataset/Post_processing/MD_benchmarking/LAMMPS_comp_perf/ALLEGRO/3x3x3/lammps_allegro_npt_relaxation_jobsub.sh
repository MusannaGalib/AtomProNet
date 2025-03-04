#!/bin/bash

#SBATCH --account=def-mponga
#SBATCH --ntasks=1
#SBATCH --mem-per-cpu=200G
#SBATCH --time=01:00:00
#SBATCH --job-name=allegro_npt_relaxation
#SBATCH --output=output.txt
#SBATCH --error=error.txt




# Change to the directory where the job submission script is located
cd ../LAMMPS_comp_perf/ALLEGRO/3x3x3

# Run LAMMPS
mpiexec -np 1 /home/mewael/lammps-2Aug2023/build/lmp_mpi  -in in.npt_relaxation
