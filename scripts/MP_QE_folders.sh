#!/bin/bash

# Get the current script location (assumes the script is copied to the POSCAR folder by the wrapper)
script_folder=$(dirname "$(realpath "$0")")
parent_folder=$(dirname "$script_folder")  # Parent directory (where input_template.in and qe_jobsub.sh are created)

# Debug: Print paths for verification
echo "Script folder: $script_folder"
echo "Parent folder: $parent_folder"

# Define paths for required template files in the parent folder
input_template_file="$parent_folder/input_template.in"
qe_jobsub_file="$parent_folder/qe_jobsub.sh"

# Generate input_template.in if it doesn't exist
if [[ ! -f "$input_template_file" ]]; then
    cat > "$input_template_file" <<EOL
&control
    calculation = 'scf',
    restart_mode = 'from_scratch',
    pseudo_dir = './',
    outdir = './tmp/'
/
&system
    ibrav = 0,
    nat = 0,    ! This will be replaced with the atom count
    ntyp = 0,   ! This will be replaced with the unique atom types count
    ecutwfc = 40,
    ecutrho = 320,
/
&electrons
    diagonalization = 'david',
    conv_thr = 1.0d-8,
    mixing_beta = 0.7,
/
CELL_PARAMETERS angstrom
! Replace with cell parameters
ATOMIC_SPECIES
! Replace with species info
ATOMIC_POSITIONS angstrom
! Replace with atomic positions
K_POINTS automatic
4 4 4 0 0 0
EOL
    echo "Generated 'input_template.in' in the parent folder."
fi

# Generate qe_jobsub.sh if it doesn't exist
if [[ ! -f "$qe_jobsub_file" ]]; then
    cat > "$qe_jobsub_file" <<EOL
#!/bin/bash
#PBS -l walltime=60:00:00,select=1:ncpus=32:ompthreads=1:mpiprocs=32:mem=180gb
#PBS -N JobName
#PBS -A ex-mponga1-1
#PBS -o output.txt
#PBS -e error.txt

################################################################################

module load gcc/9.1.0
module load intel-mkl/2019.3.199
module load openmpi/3.1.4
module load fftw/3.3.8-mpi3.1.4

cd \$PBS_O_WORKDIR

mpirun QE_PATH/bin/pw.x < input > output
EOL
    echo "Generated 'qe_jobsub.sh' in the parent folder."
fi

# Search for POSCAR files in the current script folder
structure_files=($(find "$script_folder" -type f -name "*_POSCAR"))

# Check if no structure files are found
if [[ ${#structure_files[@]} -eq 0 ]]; then
    echo "No structure files found in $script_folder"
    exit 1
fi

# Process each POSCAR file in the folder
for poscar_path in "${structure_files[@]}"; do
    # Extract the folder name from the filename (everything before "_POSCAR")
    base_filename=$(basename "$poscar_path")
    folder_name=$(echo "$base_filename" | sed 's/_POSCAR.*//')  # Extracts the prefix before "_POSCAR"

    # Create a folder for the extracted folder name within the script folder
    material_folder="$script_folder/$folder_name"
    mkdir -p "$material_folder"

    # Move the POSCAR file to the new folder and rename it to "POSCAR"
    mv "$poscar_path" "$material_folder/POSCAR"

    # Copy the required files from the parent folder into the material folder
    cp "$input_template_file" "$material_folder/input.in"
    cp "$qe_jobsub_file" "$material_folder/"

    echo "Processed $folder_name and organized files into $material_folder"
done

echo "All POSCAR files have been processed and organized successfully!"
