#!/bin/bash

# Get the script's directory
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# List of full paths to the folders to process
folders=("/home/galibubc/scratch/ML_LAMMPS/vasp_simulations/hydrostatic_strain/Alumina/Alumina_strain_-0.05_0.01_0.05"
 "/home/galibubc/scratch/ML_LAMMPS/vasp_simulations/hydrostatic_strain/Alumina_Al_O_vacancy/Alumina_strain_-0.05_0.01_0.05"
 "/home/galibubc/scratch/ML_LAMMPS/vasp_simulations/hydrostatic_strain/Alumina_Al_vacancy/Alumina_strain_-0.05_0.01_0.05"
 "/home/galibubc/scratch/ML_LAMMPS/vasp_simulations/hydrostatic_strain/Alumina_O_vacancy/Alumina_strain_-0.05_0.01_0.05")

# Output file path
output_file="$script_dir/energytable_vacform.txt"

# Ensure the output file is empty before appending
echo -n > "$output_file"

# Add a line at the beginning of the file with the last two folders from each path
for folder_path in "${folders[@]}"; do
    last_two_folders=$(echo "$folder_path" | awk -F '/' '{print $(NF-1)"/"$(NF)}')
    echo -n "$last_two_folders  " >> "$output_file"
done
echo "" >> "$output_file"

# Header for the output file
echo "Strain_XX Strain_YY Strain_ZZ Energy_Value" >> "$output_file"

# Post processing script for 2D strain
for EXX in $(seq -0.05 0.01 0.05); do 
    for folder_path in "${folders[@]}"; do
        cd "$folder_path"

        # Ensure the strain_XX, strain_YY, and strain_ZZ folders exist
        if [ -d "strain_XX_$EXX" ] && [ -d "strain_XX_$EXX/strain_YY_$EXX" ] && [ -d "strain_XX_$EXX/strain_YY_$EXX/strain_ZZ_$EXX" ]; then
            cd "strain_XX_$EXX/strain_YY_$EXX/strain_ZZ_$EXX"

            # Add energy lines to the main output file
            # Extract lines containing "energy without entropy=" and get only the last occurrence
            ENERGY_LINE=$(grep "energy  without entropy=" OUTCAR | tail -n 1)

            # Extract the numerical value after "energy without entropy="
            ENERGY_VALUE=$(echo "$ENERGY_LINE" | awk '{print $7}')

            # Debug statements
            echo "Current directory: $(pwd)"
            echo "Attempting to access: $(pwd)/OUTCAR"
            echo "DEBUG: ENERGY_VALUE=$ENERGY_VALUE"   

            # Print the desired information in a single line and append to the main output file
            echo -n "$(printf "% .2f" $EXX) $(printf "% .2f" $EXX) $(printf "% .2f" $EXX) $(printf "% .2f" $ENERGY_VALUE)" >> "$output_file"

            if [ "${folder_path}" != "${folders[-1]}" ]; then
                echo -n "  " >> "$output_file"
            fi

            cd "$script_dir"
        else
            echo "Directories strain_XX_$EXX, strain_YY_$EXX, or strain_ZZ_$EXX not found in $folder_path"
        fi
    done
    echo "" >> "$output_file"
done
# Add a column for the difference in energies (8th column - 4th column)
awk -v N=20 'NR==1 {print $1, $2, $3, "Vacancy_energy_" $(NF-1)}; NR>2 {printf "%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\n", $1, $2, $3, $8 - $4 * (N-2)/N, $12 - $4 * (N-1)/N, $16 - $4 * (N-1)/N}' OFS="\t" "$output_file" > "$script_dir/vacuum_formation_energy.txt"

# vacancy formation energy, E_vf=E_f -[(N-1)/N ]*E_i 
#N = 20;  total number of atoms in the cell before the vacancy
# E_f, E_i, the final energy after the atom is removed from the cell, the initial energy before the atom was removed
