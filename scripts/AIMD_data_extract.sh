#!/bin/bash

# Find all directories containing OUTCAR files
for DIRECTORY in $(find . -type d -name "alumina_*"); do
    echo "Currently working in directory: ${DIRECTORY}"
    cd "${DIRECTORY}"

    # Check if files exist and delete them if they do
    if [ -f pos-conv.txt ]; then
        rm pos-conv.txt
    fi

    if [ -f energy-conv.txt ]; then
        rm energy-conv.txt
    fi

    if [ -f pressure_eV.txt ]; then
        rm pressure_eV.txt
    fi

    if [ -f lattice.txt ]; then
        rm lattice.txt
    fi

    # Check if OUTCAR file exists
    if [ -f "OUTCAR" ]; then
        # Extract data from OUTCAR
		sed -n '/POSITION/,/total drift/ {/POSITION/{s/^/\n0.0 0.0 0.0\n/}; p}' OUTCAR > ../pos-conv.txt   #0.0 0.0 0.0 indicates no strain in the cell and needed for python package
		echo "$EXX $EYY $EZZ" >> ../pos-conv.txt


        # Add energy lines to separate file
        ENERGY_LINE=$(grep "energy  without entropy=" OUTCAR)
        echo "$ENERGY_LINE" >> ../energy-conv.txt

        # Add the line before "in kB" to a separate file
        TOTAL_LINE=$(grep -B1 "in kB" OUTCAR | grep -v "in kB")
        echo "$TOTAL_LINE" >> ../pressure_eV.txt

		# Extract lines 3, 4, and 5 from the CONTCAR file and save in lattice.txt
		# Repeat the following command 20000 times
		for ((i=1; i<=10; i++)); do   #change this line depending on AIMD steps
			# Add 0.0 0.0 0.0 once before each block of data
			echo "0.0 0.0 0.0" >> ../lattice.txt
			sed -n '3,5p' CONTCAR | awk '{printf $1" "$2" "$3" "$4" "$5" "$6" "$7" "$8" "$9" "} END {print ""}' >> ../lattice.txt
		done


    else
        echo "Error: OUTCAR file not found in directory: ${DIRECTORY}"
    fi
    cd ..
done
