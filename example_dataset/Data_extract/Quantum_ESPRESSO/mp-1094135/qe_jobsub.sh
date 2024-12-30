#!/bin/bash
#SBATCH --account=st-mponga1-1
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=4
#SBATCH --mem=4G
#SBATCH --time=1:00:00
#SBATCH --job-name=Quantum_ESPRESSO
#SBATCH --output=output.txt
#SBATCH --error=error.txt

################################################################################

module load gcc
module load openmpi
module load fftw


mpirun /scratch/st-mponga1-1/musanna/software/q-e/bin/pw.x -in input.in > pw.out
