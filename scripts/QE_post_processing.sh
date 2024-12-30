#!/bin/bash

exec 2>error_from_bash.log  # Redirect standard error to a file for debugging

# Output files (centralized in the root folder)
output_dir=$(pwd)  # Save the starting directory for results
pos_file="$output_dir/pos.txt"
energy_file="$output_dir/energy-conv.txt"
force_file="$output_dir/forces.txt"
pos_force_file="$output_dir/pos-conv.txt"
stress_file="$output_dir/pressure_eV.txt"
lattice_file="$output_dir/lattice.txt"
symbols_file="$output_dir/symbols.txt"

# Clear previous output files
> "$pos_file"
> "$energy_file"
> "$force_file"
> "$stress_file"
> "$lattice_file"
> "$pos_force_file"
> "$symbols_file"


# Function to perform post-processing in a directory
process_directory() {
    local current_dir=$1
    echo "Processing directory: $current_dir"

    cd "$current_dir" || return

    # Check if Quantum Espresso output file (e.g., pw.out) exists and process it
    if [ -f "pw.out" ]; then
        #echo "Directory: $current_dir" >> "$energy_file"
        #echo "Directory: $current_dir" >> "$pos_file"
        #echo "Directory: $current_dir" >> "$force_file"
        #echo "Directory: $current_dir" >> "$stress_file"

    # Extract energy lines after "the Fermi energy is"
    FermiLines=$(grep -n "the Fermi energy is" pw.out | cut -d: -f1)  # Find all line numbers

    if [ -n "$FermiLines" ]; then  # Check if Fermi energy lines exist
        for LineNum in $FermiLines; do
            # Extract lines after the Fermi line and find the first energy line
            ENERGY_LINE=$(sed -n "$((LineNum + 1)),\$p" pw.out | grep -i "!" | head -n 1)
            if [ -n "$ENERGY_LINE" ]; then
                # Remove the '!' from the energy line
                ENERGY_LINE=$(echo "$ENERGY_LINE" | sed 's/!//')
                
                # Print the directory and energy line without the '!'
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
        # Extract only the force values starting after "=" and ignore the rest
        # Extract forces with directory headers
        sed -n '/Forces acting/,$p' pw.out | \
        awk -v dir="$current_dir" '
            BEGIN {
                # Set a flag to track when we are inside a section
                inside_section = 0;
            }
            /Forces acting/ {
                # New section starts
                print "Directory: " dir;
                inside_section = 1;
                next;
            }
            /correction/ {
                # End of the current section
                inside_section = 0;
                #print "";  # Add a blank line for separation
                next;
            }
            inside_section && /force =/ {
                # If inside a section, print the 7th, 8th, and 9th columns (forces)
                print $7, $8, $9;
            }
        ' > forces-conv.txt

        # Append the processed data to the main force file
        cat forces-conv.txt >> "$force_file"


        # Extract positions
        sed -n '/ATOMIC_POSITIONS/,/^$/p' pw.out | sed '/^$/d' > pos.txt
        cat pos.txt >> "$pos_file"


        paste pos.txt forces-conv.txt | awk -v dir="$current_dir" '
            {
                if ($1 == "ATOMIC_POSITIONS" && $2 == "(angstrom)") {
                    if (NR > 1) {
                        # Print the dashed line after the previous block
                        print "-----------------------------------------------------------------------------------";
                    }
                    # Print the directory, header, and separator before each new dataset
                    print "Directory: " dir;
                    print "POSITION                                       TOTAL-FORCE (Ry/au)";
                    print "-----------------------------------------------------------------------------------";
                } else {
                    # Ensure the numbers are printed with 10 decimal places and aligned correctly
                    # This approach will handle negative signs without misalignment
                    printf "%17s %17s %17s %17s %17s %17s\n", $2, $3, $4, $5, $6, $7;
                }
            }
            END {
                # Print the dashed line after the last block as well
                print "-----------------------------------------------------------------------------------";
            }
        ' >> "$pos_force_file"







        # Extract stress (with debugging)
        sed -n '/total   stress/ {n; p; n; p; n; p;}' pw.out | \
        awk -v dir="$current_dir" '{
            # Print the directory path only before the first row of each block
            if (NR % 3 == 1) {
                printf "Directory: %s\n", dir;
                printf "Total ";
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






        # Count the occurrences of "total stress" in pw.out
        stress_count=$(grep -c "total   stress" pw.out)

        if [ "$stress_count" -eq 0 ]; then
            echo "No 'total   stress' occurrences found in pw.out."
            exit 0
        fi

        # Extract symbols and their counts for each ATOMIC_POSITIONS section
        inside_atomic_positions=false
        declare -A symbol_counts
        symbol_order=()

        while read -r line; do
            # Detect the start of ATOMIC_POSITIONS
            if [[ "$line" =~ ^ATOMIC_POSITIONS[[:space:]]*\(angstrom\) ]]; then
                inside_atomic_positions=true
                # Reset symbol counts and order for the new section
                symbol_counts=()
                symbol_order=()
                continue
            fi

            # If we're inside the ATOMIC_POSITIONS section, process the symbols
            if $inside_atomic_positions; then
                # Stop processing once we reach the end of the section
                if [[ -z "$line" || "$line" =~ ^[[:space:]]*$ ]]; then
                    inside_atomic_positions=false

                    # Generate the symbols and counts strings in order of appearance
                    symbols_line=""
                    counts_line=""
                    for symbol in "${symbol_order[@]}"; do
                        symbols_line+="$symbol "
                        counts_line+="${symbol_counts[$symbol]} "
                    done

                    # Write the directory and current section's symbols/counts to the file
                    {
                        echo "Directory: $current_dir"
                        echo "Symbols:    $symbols_line"
                        echo "Counts:     $counts_line"
                        echo ""
                    } >> "$symbols_file"

                    continue
                fi

                # Extract the symbol (first column)
                symbol=$(echo "$line" | awk '{print $1}')
                if [[ -n "$symbol" ]]; then
                    if [[ -z "${symbol_counts[$symbol]}" ]]; then
                        symbol_order+=("$symbol") # Add symbol to order if not already present
                    fi
                    ((symbol_counts["$symbol"]++))
                fi
            fi
        done < pw.out

        echo "File $symbols_file has been created with entries from pw.out."




        inside_cell_parameters=false
        lattice_line=""

        while read -r line; do
            # Detect the start of CELL_PARAMETERS
            if [[ "$line" =~ ^CELL_PARAMETERS[[:space:]]*\(angstrom\) ]]; then
                inside_cell_parameters=true
                lattice_line="" # Reset the lattice line for the next entry
                continue
            fi

            # If we're inside the CELL_PARAMETERS section, process the next three lines
            if $inside_cell_parameters; then
                lattice_line="$lattice_line $line"

                # Check if we have read 3 lines (9 components)
                if [[ $(echo "$lattice_line" | awk '{print NF}') -eq 9 ]]; then
                    {
                        echo "$current_dir"
                        echo "$lattice_line"
                        #echo "" # Add a blank line for separation
                    } >> "$lattice_file"
                    inside_cell_parameters=false # Reset for the next occurrence
                fi
            fi
        done < pw.out

        echo "File $lattice_file has been created with lattice data."



    else
        echo "pw.out not found in $current_dir. Skipping."
    fi


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
