#!/bin/bash

exec 2>error_from_bash.log  # Redirect standard error to a file for debugging

# Output files (centralized in the root folder)
output_dir=$(pwd)  # Save the starting directory for results
pos_file="$output_dir/pos-conv.txt"
energy_file="$output_dir/energy-conv.txt"
pressure_file="$output_dir/pressure_eV.txt"
lattice_file="$output_dir/lattice.txt"
symbols_file="$output_dir/symbols.txt"

# Clear previous output files
> "$pos_file"
> "$energy_file"
> "$pressure_file"
> "$lattice_file"
> "$symbols_file"

# Initialize folder counter
counter=0

# Function to perform post-processing in a directory
process_directory() {
    local current_dir=$1
    ((counter++))  # Increment counter
    echo "Processing folder #$counter: $current_dir"  # Debug line

    cd "$current_dir" || return

	# Check if OUTCAR exists and process it
	if [ -f "OUTCAR" ]; then
		awk -v dir="$current_dir" '
			/POSITION/,/total drift/ {
				if ($0 ~ /POSITION/) { print "Directory: " dir }
				print
			}
		' OUTCAR >> "$pos_file"
		
		# Extract energy lines and append directory for each energy line
		grep "energy  without entropy=" OUTCAR | while read -r ENERGY_LINE; do
			echo "Directory: $current_dir" >> "$energy_file"
			echo "$ENERGY_LINE" >> "$energy_file"
		done

		# Extract pressure data and append directory for each pressure block
		grep -B1 "in kB" OUTCAR | grep -v -e "in kB" -e "^--$" | while read -r TOTAL_LINE; do
			echo "Directory: $current_dir" >> "$pressure_file"
			echo "$TOTAL_LINE" >> "$pressure_file"
		done

	else
		echo "OUTCAR not found in $current_dir. Skipping."
	fi




	# Check if OUTCAR exists and process it
	if [ -f "OUTCAR" ]; then
		# Extract all lattice vector blocks and format them
		awk '/direct lattice vectors/,/length of vectors/ {
			if ($1 ~ /^[0-9\-\.]/) print $1, $2, $3;
		}' OUTCAR | awk 'NR % 3 == 0 { printf "%s\n", $0; } NR % 3 != 0 { printf "%s ", $0; }' > lattice_temp.txt

		# Add directory name before each block
		while IFS= read -r line; do
			echo "Directory: $current_dir" >> "$lattice_file"
			echo "$line" >> "$lattice_file"
		done < lattice_temp.txt

		# Clean up temporary file
		rm lattice_temp.txt
	else
		echo "OUTCAR not found in $current_dir. Skipping."
	fi





	if [ -f "CONTCAR" ] && [ -f "OUTCAR" ]; then
		# Read the 6th and 7th lines from the CONTCAR file
		atom_symbols=$(sed -n '6p' "$current_dir/CONTCAR")
		atom_counts=$(sed -n '7p' "$current_dir/CONTCAR")
		
		# Count occurrences of "POSITION TOTAL-FORCE (eV/Angst)" in OUTCAR
		occurrences=$(grep -c "POSITION                                       TOTAL-FORCE (eV/Angst)" "$current_dir/OUTCAR")
		
		# Append directory, symbols, and counts for each occurrence
		for ((i = 1; i <= occurrences; i++)); do
			echo "Directory: $current_dir" >> "$symbols_file"
			echo "Symbols: $atom_symbols" >> "$symbols_file"
			echo "Counts: $atom_counts" >> "$symbols_file"
			echo "" >> "$symbols_file"
		done
	else
		echo "CONTCAR or OUTCAR not found in $current_dir. Skipping."
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
echo "Processed $counter folders in total."  # Final counter output
echo "Post-processing completed at $(date)"
