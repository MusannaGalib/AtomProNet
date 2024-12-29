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
        #echo "Directory: $current_dir" >> "$energy_file"
        echo "Directory: $current_dir" >> "$pos_file"
        echo "Directory: $current_dir" >> "$force_file"
        #echo "Directory: $current_dir" >> "$stress_file"

        # Extract energy lines after "the Fermi energy is"
        FermiLines=$(grep -n "the Fermi energy is" pw.out | cut -d: -f1)  # Find all line numbers

        if [ -n "$FermiLines" ]; then  # Check if Fermi energy lines exist
            for LineNum in $FermiLines; do
                # Extract lines after the Fermi line and find the first energy line
                ENERGY_LINE=$(sed -n "$((LineNum + 1)),\$p" pw.out | grep -i "!" | head -n 1)
                if [ -n "$ENERGY_LINE" ]; then
                    echo "Directory: $current_dir" >> "$energy_file"
                    echo "$ENERGY_LINE" >> "$energy_file"
                else
                    echo "No energy line found after Fermi energy in $current_dir/pw.out."
                fi
            done
        else
            echo "No 'the Fermi energy is' line found in $current_dir/pw.out. Skipping energy extraction."
        fi



        # Extract forces
        sed -n '/Forces acting/,/Total force/p' pw.out > forces-conv.txt
        cat forces-conv.txt >> "$force_file"

        # Extract positions
        sed -n '/ATOMIC_POSITIONS/,/^$/p' pw.out | sed '/^$/d' > pos-conv.txt
        cat pos-conv.txt >> "$pos_file"


        # Extract stress (with debugging)
        sed -n '/total   stress/ {n; p; n; p; n; p;}' pw.out | \
        awk -v dir="$current_dir" '{
            # Print the directory path only before the first row of each block
            if (NR % 3 == 1) {
                print "Directory: " dir;
            }
            
            # Print the first 3 columns of each row on the same line
            printf "%s %s %s ", $1, $2, $3;

            row_count++;
            if (row_count % 3 == 0) {
                # After 3 rows, print a newline
                print "";
            }
        } END {
            # If not a multiple of 3, print a newline
            if (row_count % 3 != 0) print "";
        }' > stress-conv.txt

        # Save the stress values to the main file with directory path
        if [ -s stress-conv.txt ]; then  # Check if the file is not empty
            #echo "Directory: $current_dir" >> "$stress_file"
            cat stress-conv.txt >> "$stress_file"
        else
            echo "No stress data found for $current_dir" >> "$stress_file"
        fi


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
