#!/bin/bash

# Get the current script location (assumes the script is copied to the POSCAR folder by the wrapper)
script_folder=$(dirname "$(realpath "$0")")
poscar_folder="$script_folder"
parent_folder=$(dirname "$poscar_folder")  # Parent directory (where required files are located)

# Debug: Print paths for verification
echo "POSCAR folder path: $poscar_folder"
echo "Parent folder path: $parent_folder"

# Define paths for required files in the parent folder
incar_file="$parent_folder/INCAR"
kpoints_file="$parent_folder/KPOINTS"
potcar_file="$parent_folder/POTCAR"
vasp_jobsub_file="$parent_folder/vasp_jobsub.sh"

# Check for missing required files
missing_files=()
if [[ ! -f "$incar_file" ]]; then missing_files+=("INCAR"); fi
if [[ ! -f "$kpoints_file" ]]; then missing_files+=("KPOINTS"); fi
if [[ ! -f "$potcar_file" ]]; then missing_files+=("POTCAR"); fi
if [[ ! -f "$vasp_jobsub_file" ]]; then missing_files+=("vasp_jobsub.sh"); fi

# Exit if any required files are missing
if [[ ${#missing_files[@]} -gt 0 ]]; then
    echo "The following required files are missing in the parent folder:"
    for file in "${missing_files[@]}"; do
        echo "- $file"
    done
    exit 1
fi

# Process each POSCAR file in the POSCAR folder
for poscar_path in "$poscar_folder"/*_POSCAR; do
    # Skip if no POSCAR files are found
    if [[ ! -f "$poscar_path" ]]; then
        echo "No POSCAR files found in the folder: $poscar_folder"
        exit 1
    fi

    # Extract the material ID (e.g., "mp-XXXXX") from the filename
    base_filename=$(basename "$poscar_path")
    material_id=$(echo "$base_filename" | cut -d'_' -f1)  # Extracts "mp-XXXXX" part

    # Create a folder for the material ID within the POSCAR folder
    material_folder="$poscar_folder/$material_id"
    mkdir -p "$material_folder"

    # Move the POSCAR file to the new folder and rename it to "POSCAR"
    mv "$poscar_path" "$material_folder/POSCAR"

    # Copy the required files from the parent folder into the material folder
    cp "$incar_file" "$material_folder/"
    cp "$kpoints_file" "$material_folder/"
    cp "$potcar_file" "$material_folder/"
    cp "$vasp_jobsub_file" "$material_folder/"

    echo "Processed $material_id and organized files into $material_folder"
done

echo "All POSCAR files have been processed and organized successfully!"
