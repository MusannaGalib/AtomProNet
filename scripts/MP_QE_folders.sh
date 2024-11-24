#!/bin/bash

# Define folder paths
script_folder=$(dirname "$(realpath "$0")")
structure_folder="$script_folder"
parent_folder=$(dirname "$structure_folder")

# Define filenames for QE job submission script and input template
qe_jobsub_file="$parent_folder/qe_jobsub.sh"
input_template_file="$parent_folder/input_template.in"

# Generate the QE job submission script in the parent folder
if [[ ! -f "$qe_jobsub_file" ]]; then
    cat <<EOL > "$qe_jobsub_file"
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

mpirun  QE_PATH/bin/pw.x < input > output
EOL
    echo "Generated 'qe_jobsub.sh' in the parent folder."
fi

# Generate the QE input template file in the parent folder
if [[ ! -f "$input_template_file" ]]; then
    cat <<EOL > "$input_template_file"
&control
    calculation = 'scf',
    prefix = 'PREFIX',
    pseudo_dir = './',
    outdir = './out',
    verbosity = 'high',
/
&system
    ibrav = 0,
    nat = NAT_VALUE,
    ntyp = NTYP_VALUE,
    ecutwfc = 40.0,
    ecutrho = 400.0,
/
&electrons
    conv_thr = 1.0d-8,
    mixing_beta = 0.7,
/
ATOMIC_SPECIES
SPECIES_PLACEHOLDER
ATOMIC_POSITIONS crystal
POSITION_PLACEHOLDER
K_POINTS automatic
4 4 4 0 0 0
EOL
    echo "Generated 'input_template.in' in the parent folder."
fi

# Check for the presence of structure files
structure_files=("$structure_folder"/*_POSCAR)
if [[ ! -e "${structure_files[0]}" ]]; then
    echo "No POSCAR files found in $structure_folder"
    exit 1
fi

# Ensure the user updates the files before rerunning the script
echo "Please review and modify 'qe_jobsub.sh' and 'input_template.in' in the parent folder if necessary."
echo "After making changes, rerun this script to organize files into respective folders."
exit 0

# Function to parse POSCAR and extract atomic data
parse_poscar() {
    local poscar_path="$1"
    local output_folder="$2"

    nat=$(sed -n '7p' "$poscar_path" | awk '{sum=0; for(i=1; i<=NF; i++) sum+=$i; print sum}')
    atomic_species=$(sed -n '6p' "$poscar_path" | awk '{for(i=1; i<=NF; i++) print $i}')
    positions=$(sed -n '9,$p' "$poscar_path")

    atomic_species_section=""
    for species in $atomic_species; do
        atomic_species_section+="$species $species.upf 1.0\n"
    done

    sed -e "s/NAT_VALUE/$nat/" \
        -e "s/NTYP_VALUE/$(echo "$atomic_species" | wc -w)/" \
        -e "s/SPECIES_PLACEHOLDER/$atomic_species_section/" \
        -e "s/POSITION_PLACEHOLDER/$positions/" \
        "$input_template_file" > "$output_folder/input.in"
}

# Process each POSCAR file
for structure_path in "$structure_folder"/*_POSCAR; do
    base_filename=$(basename "$structure_path")
    folder_name=$(echo "$base_filename" | sed 's/_POSCAR.*//')
    material_folder="$structure_folder/$folder_name"

    mkdir -p "$material_folder"
    mv "$structure_path" "$material_folder/structure"

    # Copy qe_jobsub.sh and UPF files to the material folder
    cp "$qe_jobsub_file" "$material_folder/"
    cp "$structure_folder"/*.upf "$material_folder/" 2>/dev/null || true

    # Generate input.in file for the folder
    parse_poscar "$material_folder/structure" "$material_folder"

    echo "Processed $folder_name and organized files into $material_folder"
done

echo "All POSCAR files have been processed and organized successfully!"
