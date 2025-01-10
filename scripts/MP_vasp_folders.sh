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

    # Extract the folder name from the filename (everything before "_POSCAR")
    base_filename=$(basename "$poscar_path")
    folder_name=$(echo "$base_filename" | sed 's/_POSCAR.*//')  # Extracts the prefix before "_POSCAR"

    # Create a folder for the extracted folder name within the POSCAR folder
    material_folder="$poscar_folder/$folder_name"
    mkdir -p "$material_folder"

    # Move the POSCAR file to the new folder and rename it to "POSCAR"
    mv "$poscar_path" "$material_folder/POSCAR"

    # Copy the required files from the parent folder into the material folder
    cp "$incar_file" "$material_folder/"
    cp "$kpoints_file" "$material_folder/"
    cp "$vasp_jobsub_file" "$material_folder/"

    # Extract atom types from the 6th line of the POSCAR file
    atom_types=$(sed -n '6p' "$material_folder/POSCAR" | awk '{print $1,$2,$3,$4}' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
    atom_list=($atom_types)

    # Create a new POTCAR file by concatenating atom-specific POTCAR files
    missing_potcar_atoms=()
    : > "$material_folder/POTCAR"  # Clear any existing POTCAR file in the folder
    for atom in "${atom_list[@]}"; do
        atom_potcar="$parent_folder/POTCAR_$atom"
        if [[ -f "$atom_potcar" ]]; then
            cat "$atom_potcar" >> "$material_folder/POTCAR"
        else
            missing_potcar_atoms+=("$atom")
        fi
    done

    # Check for missing POTCAR files
    if [[ ${#missing_potcar_atoms[@]} -gt 0 ]]; then
        echo -e "\033[31mWarning: The following POTCAR files are missing in the parent folder for $folder_name:\033[0m"
        for atom in "${missing_potcar_atoms[@]}"; do
            echo -e "\033[31m- POTCAR_$atom\033[0m"
        done
    else
        echo "POTCAR file created successfully for $folder_name."
    fi

    echo "Processed $folder_name and organized files into $material_folder"
done

echo "All POSCAR files have been processed and organized successfully!"
