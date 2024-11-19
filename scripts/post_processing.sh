#!/bin/bash

exec 2>error_from_bash.log  # Redirect standard error to a file for debugging

# Output files (centralized in the root folder)
output_dir=$(pwd)  # Save the starting directory for results
pos_file="$output_dir/pos-conv.txt"
energy_file="$output_dir/energy-conv.txt"
pressure_file="$output_dir/pressure_eV.txt"
lattice_file="$output_dir/lattice.txt"

# Clear previous output files
> "$pos_file"
> "$energy_file"
> "$pressure_file"
> "$lattice_file"

# Function to perform post-processing in a directory
process_directory() {
    local current_dir=$1
    echo "Processing directory: $current_dir"

    cd "$current_dir" || return

    # Check if OUTCAR exists and process it
    if [ -f "OUTCAR" ]; then
        sed -n '/POSITION/,/total drift/ p' OUTCAR > pos-conv.txt
        echo "Directory: $current_dir" >> "$pos_file"
        cat pos-conv.txt >> "$pos_file"

        # Extract energy lines
        ENERGY_LINE=$(grep "energy  without entropy=" OUTCAR | tail -n 1)
        echo "Directory: $current_dir" >> "$energy_file"
        echo "$ENERGY_LINE" >> "$energy_file"

        # Extract pressure data
        TOTAL_LINE=$(grep -B1 "in kB" OUTCAR | grep -v "in kB" | tail -n 1)
        echo "Directory: $current_dir" >> "$pressure_file"
        echo "$TOTAL_LINE" >> "$pressure_file"
    else
        echo "OUTCAR not found in $current_dir. Skipping."
    fi

    # Check if CONTCAR exists and process it
    if [ -f "CONTCAR" ]; then
        sed -n '3,5p' CONTCAR | awk '{printf $1" "$2" "$3" "$4" "$5" "$6" "$7" "$8" "$9" "} END {print ""}' > lattice.txt
        echo "Directory: $current_dir" >> "$lattice_file"
        cat lattice.txt >> "$lattice_file"
    else
        echo "CONTCAR not found in $current_dir. Skipping."
    fi

    cd - > /dev/null || return
}

# Recursive function to traverse all directories
traverse_directories() {
    local base_dir=$1

    for folder in "$base_dir"/*; do
        if [ -d "$folder" ]; then
            # If "OUTCAR" or "CONTCAR" exists in the folder, process it
            if [ -f "$folder/OUTCAR" ] || [ -f "$folder/CONTCAR" ]; then
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
