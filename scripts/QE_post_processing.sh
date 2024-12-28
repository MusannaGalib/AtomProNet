#!/bin/bash

exec 2>error_from_bash.log  # Redirect standard error to a file for debugging

# Output files (centralized in the root folder)
output_dir=$(pwd)  # Save the starting directory for results
pos_file="$output_dir/pos-conv.txt"
energy_file="$output_dir/energy-conv.txt"
force_file="$output_dir/forces.txt"
stress_file="$output_dir/stress.txt"
lattice_file="$output_dir/lattice.txt"

# Clear previous output files
> "$pos_file"
> "$energy_file"
> "$force_file"
> "$stress_file"
> "$lattice_file"

# Function to perform post-processing in a directory
process_directory() {
    local current_dir=$1
    echo "Processing directory: $current_dir"

    cd "$current_dir" || return

    # Check if Quantum Espresso output file (e.g., pw.out) exists and process it
    if [ -f "pw.out" ]; then
        echo "Directory: $current_dir" >> "$energy_file"
        echo "Directory: $current_dir" >> "$pos_file"
        echo "Directory: $current_dir" >> "$force_file"
        echo "Directory: $current_dir" >> "$stress_file"

        # Extract energy
        ENERGY_LINE=$(grep -i "!" pw.out | tail -n 1)
        echo "$ENERGY_LINE" >> "$energy_file"

        # Extract forces
        sed -n '/Forces acting/,/Total force/p' pw.out > forces-conv.txt
        cat forces-conv.txt >> "$force_file"

        # Extract positions
        sed -n '/ATOMIC_POSITIONS/,/^$/p' pw.out | sed '/^$/d' > pos-conv.txt
        cat pos-conv.txt >> "$pos_file"

        # Extract stress
        sed -n '/total   stress/ {n; p; n; p; n; p;}' pw.out > stress-conv.txt
        cat stress-conv.txt >> "$stress_file"
    else
        echo "pw.out not found in $current_dir. Skipping."
    fi

    # Check if input structure file (e.g., input.in) exists and process it
    if [ -f "input.in" ]; then
        echo "Directory: $current_dir" >> "$lattice_file"

        # Extract lattice parameters
        sed -n '/CELL_PARAMETERS/,/^$/p' input.in | sed '/^$/d' > lattice-conv.txt
        cat lattice-conv.txt >> "$lattice_file"
    else
        echo "input.in not found in $current_dir. Skipping."
    fi

    cd - > /dev/null || return
}

# Recursive function to traverse all directories
traverse_directories() {
    local base_dir=$1

    for folder in "$base_dir"/*; do
        if [ -d "$folder" ]; then
            # If "pw.out" exists in the folder, process it
            if [ -f "$folder/pw.out" ]; then
                process_directory "$folder"
            fi

            # Recurse into subdirectories
            traverse_directories "$folder"
        fi
    done
}

# Start recursive processing
echo "Post-processing started at $(date)"
traverse_directories "$(pwd)"
echo "Post-processing completed at $(date)"
