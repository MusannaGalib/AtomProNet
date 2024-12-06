#!/bin/bash
#SBATCH --account=st-mponga1-1
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --mem=3G
#SBATCH --time=10:00:00
#SBATCH --job-name=Alumina_4_4_4
#SBATCH --output=output.txt
#SBATCH --error=error.txt
   

################################################################################
module load gcc
module load intel-mkl
module load openmpi
module load fftw

export LD_LIBRARY_PATH=/arc/software/spack-2024/opt/spack/linux-rocky9-skylake_avx512/gcc-9.4.0/fftw-3.3.9-d7h6oztbr3jgmalhhroq2hqpqeufza53/lib:$LD_LIBRARY_PATH

cd $PBS_O_WORKDIR
pwd

mpirun -n $SLURM_NTASKS /home/galibubc/scratch/musanna/software/vasp.6.3.0_july_2024/bin/vasp_std 



