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

# Function to generate input_template.in
generate_input_template() {
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
    occupations = 'smearing',
    smearing = 'gaussian',
    degauss = 0.02
/
&electrons
    diagonalization = 'david',
    conv_thr = 1.0d-8,
    mixing_beta = 0.7,
/
CELL_PARAMETERS angstrom
CELL_PLACEHOLDER
ATOMIC_SPECIES
SPECIES_PLACEHOLDER
ATOMIC_POSITIONS angstrom
POSITION_PLACEHOLDER
K_POINTS automatic
4 4 4 0 0 0
EOL
    echo "Generated 'input_template.in' in the parent folder."
}

# Function to generate qe_jobsub.sh
generate_qe_jobsub() {
    cat > "$qe_jobsub_file" <<EOL
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

cd $PBS_O_WORKDIR
cd $SLURM_SUBMIT_DIR


mpirun /scratch/st-mponga1-1/musanna/software/q-e/bin/pw.x < input.in > output.out
EOL
    echo "Generated 'qe_jobsub.sh' in the parent folder."
}

# Check for input_template.in and prompt if it exists
if [[ -f "$input_template_file" ]]; then
    echo "The file 'input_template.in' already exists. Do you want to replace it? (y/n)"
    read -r response
    if [[ "$response" == "y" || "$response" == "Y" ]]; then
        generate_input_template
        echo "The file 'input_template.in' has been replaced."
        echo "Do you want to modify 'input_template.in' before proceeding? (y/n)"
        read -r modify_response
        if [[ "$modify_response" == "y" || "$modify_response" == "Y" ]]; then
            nano "$input_template_file"  # Replace `nano` with your preferred editor
        fi
    else
        echo "Using existing 'input_template.in'."
    fi
else
    generate_input_template
fi

# Check for qe_jobsub.sh and prompt if it exists
if [[ -f "$qe_jobsub_file" ]]; then
    echo "The file 'qe_jobsub.sh' already exists. Do you want to replace it? (y/n)"
    read -r response
    if [[ "$response" == "y" || "$response" == "Y" ]]; then
        generate_qe_jobsub
        echo "The file 'qe_jobsub.sh' has been replaced."
        echo "Do you want to modify 'qe_jobsub.sh' before proceeding? (y/n)"
        read -r modify_response
        if [[ "$modify_response" == "y" || "$modify_response" == "Y" ]]; then
            nano "$qe_jobsub_file"  # Replace `nano` with your preferred editor
        fi
    else
        echo "Using existing 'qe_jobsub.sh'."
    fi
else
    generate_qe_jobsub
fi

# Confirm whether to continue generating job submission folders
echo "Do you want to continue to copy the files and generate job submission folders? (y/n)"
read -r continue_response
if [[ "$continue_response" != "y" && "$continue_response" != "Y" ]]; then
    echo "Exiting without generating job submission folders."
    exit 0
fi

# Search for POSCAR files in the current script folder
structure_files=($(find "$script_folder" -type f -name "*_POSCAR"))

# Check if no structure files are found
if [[ ${#structure_files[@]} -eq 0 ]]; then
    echo "No structure files found in $script_folder"
    exit 1
fi

# Function to parse POSCAR and generate the input file
parse_poscar_to_input() {
    local poscar_file="$1"
    local input_file="$2"
    local material_folder="$3"

    # Extract cell parameters
    cell_parameters=$(sed -n '3,5p' "$poscar_file")

    # Extract atomic species and counts
    atom_types=$(sed -n '6p' "$poscar_file")
    atom_counts=$(sed -n '7p' "$poscar_file")
    nat=$(echo "$atom_counts" | awk '{sum=0; for(i=1; i<=NF; i++) sum+=$i; print sum}')
    ntyp=$(echo "$atom_types" | wc -w)

    # Generate ATOMIC_SPECIES section and copy corresponding UPF files
    atomic_species=""
    missing_potentials=()
    for species in $atom_types; do
        species=$(echo "$species" | xargs)  # Trim whitespace
        echo "Looking for UPF file for species: '$species'"
        
        # Use case-insensitive find to match UPF files
        # Use exact word matching for species in UPF filenames
        upf_file=$(find "$parent_folder" -type f -regextype posix-extended -iregex ".*[/_]+${species}[._].*upf" | head -n 1)

        
        if [[ -z "$upf_file" ]]; then
            echo "UPF file for species '$species' not found."
            missing_potentials+=("$species")
        else
            echo "Found UPF file: $upf_file"
            cp "$upf_file" "$material_folder/"
            upf_filename=$(basename "$upf_file")
            atomic_species+="$species 1.0 $upf_filename\n"
        fi
    done


    # Warn if any UPF files are missing
    if [[ ${#missing_potentials[@]} -gt 0 ]]; then
        echo -e "\033[31mWarning: The following pseudopotentials are missing for $material_folder:\033[0m"
        for species in "${missing_potentials[@]}"; do
            echo -e "\033[31m- $species\033[0m"
        done
    fi

    # Extract atomic positions and format them with atom types
    positions=$(awk -v types="$atom_types" -v counts="$atom_counts" '
        BEGIN {
            split(types, typeArray);  # Split atom types into an array
            split(counts, countArray);  # Split atom counts into an array
            atomIndex = 1;
        }
        NR >= 9 {  # Start reading positions from line 9
            for (i = 1; i <= length(typeArray); i++) {  # Loop over each atom type
                for (j = 1; j <= countArray[i]; j++) {  # Repeat based on atom count
                    printf "%s  %s\n", typeArray[i], $0;  # Prepend atom type to position
                    atomIndex++;
                    getline;  # Read the next position line
                }
            }
        }
    ' "$poscar_file")

    # Replace placeholders directly into the template
    awk -v nat="$nat" -v ntyp="$ntyp" \
        -v cell_parameters="$cell_parameters" \
        -v atomic_species="$atomic_species" \
        -v positions="$positions" \
        '{
            gsub(/nat = 0,/, "nat = " nat ",");
            gsub(/ntyp = 0,/, "ntyp = " ntyp ",");
            gsub(/CELL_PLACEHOLDER/, cell_parameters);
            gsub(/SPECIES_PLACEHOLDER/, atomic_species);
            gsub(/POSITION_PLACEHOLDER/, positions);
            print;
        }' "$input_template_file" > "$input_file"
}

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
    cp "$qe_jobsub_file" "$material_folder/"

    # Generate the input file for Quantum Espresso
    parse_poscar_to_input "$material_folder/POSCAR" "$material_folder/input.in" "$material_folder"

    echo "Processed $folder_name and organized files into $material_folder"
done

echo "All POSCAR files have been processed and organized successfully!"
