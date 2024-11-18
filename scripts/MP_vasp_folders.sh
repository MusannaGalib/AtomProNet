#!/bin/bash

get_directory() {
    read -p "$1" dir
    # Convert Windows paths to Unix style by replacing backslashes with forward slashes
    dir=$(echo "$dir" | sed 's/\\/\//g')
    echo "$dir"
}

# Ask for the folder containing POSCAR files
poscar_folder=$(get_directory "Enter the path to the folder containing POSCAR files: ")

# Ask for the folder containing the four required files (INCAR, KPOINTS, POTCAR, vasp_jobsub.sh)
files_folder=$(get_directory "Enter the path to the folder containing INCAR, KPOINTS, POTCAR, and vasp_jobsub.sh files: ")

# Debug: Print the converted paths
echo "POSCAR folder path: $poscar_folder"
echo "Files folder path: $files_folder"

# Define paths for the required files from the specified folder
incar_file="$files_folder/INCAR"
kpoints_file="$files_folder/KPOINTS"
potcar_file="$files_folder/POTCAR"
vasp_jobsub_file="$files_folder/vasp_jobsub.sh"

# Debug: Print the file paths to verify correctness
echo "INCAR file path: $incar_file"
echo "KPOINTS file path: $kpoints_file"
echo "POTCAR file path: $potcar_file"
echo "vasp_jobsub.sh file path: $vasp_jobsub_file"

# Check if all required files exist in the folder and print which file is missing
missing_files=()
if [[ ! -f "$incar_file" ]]; then
    missing_files+=("INCAR")
fi
if [[ ! -f "$kpoints_file" ]]; then
    missing_files+=("KPOINTS")
fi
if [[ ! -f "$potcar_file" ]]; then
    missing_files+=("POTCAR")
fi
if [[ ! -f "$vasp_jobsub_file" ]]; then
    missing_files+=("vasp_jobsub.sh")
fi

# If there are missing files, display them
if [[ ${#missing_files[@]} -gt 0 ]]; then
    echo "The following required files are missing in the specified folder:"
    for file in "${missing_files[@]}"; do
        echo "- $file"
    done
    exit 1
fi

# Iterate over all POSCAR files in the specified folder
for poscar_path in "$poscar_folder"/*_POSCAR; do
    # Extract the material ID from the filename
    base_filename=$(basename "$poscar_path")
    material_id=$(echo "$base_filename" | cut -d'_' -f1) # Extracts "mp-XXXXX" part

    # Create the corresponding folder for the material ID
    material_folder="$poscar_folder/$material_id"
    mkdir -p "$material_folder"

    # Move the POSCAR file to the new folder and rename it to "POSCAR"
    mv "$poscar_path" "$material_folder/POSCAR"

    # Copy additional files to the material folder
    cp "$incar_file" "$material_folder/"
    cp "$kpoints_file" "$material_folder/"
    cp "$potcar_file" "$material_folder/"
    cp "$vasp_jobsub_file" "$material_folder/"

    echo "Processed $material_id and organized files into $material_folder"
done

echo "All POSCAR files have been processed and organized!"
