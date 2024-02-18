#!/bin/bash
root_path=$(pwd)

for cij in $(ls -F | grep /$)
do
  cd "${root_path}/${cij}"

  for s in strain_*
  do
    cd "${root_path}/${cij}/${s}"
    current_directory=$(pwd)
    echo "${current_directory}"

    # Create vaspjob_sub.sh in the current folder
    cat <<EOF > vaspjob_sub.sh
#!/bin/bash
#SBATCH --account=def-mponga
#SBATCH --ntasks=1
#SBATCH --mem-per-cpu=3500M
#SBATCH --job-name=Alumina_strain_80_atoms
#SBATCH --time=1:00:00
#SBATCH --output=output.out
#SBATCH --error=error.err
#SBATCH --mail-type=end

module load nixpkgs/16.09 intel/2018.3 intelmpi/2018.3.222 vasp/6.1.0

srun vasp_std
EOF

    # Run sbatch on the created vaspjob_sub.sh file
    sbatch vaspjob_sub.sh

    # Move back to the parent directory
    cd "${root_path}/${cij}"
  done
done
