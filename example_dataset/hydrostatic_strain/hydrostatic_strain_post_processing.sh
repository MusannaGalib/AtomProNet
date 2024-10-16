#!/bin/bash

exec 2>error_from_bash.log  # Redirect standard error to a file


# Initialize counter
counter=0

# Post processing script for hydrostatic strain
for EXX in $(seq -0.003 0.001 0.003); do
    if [ "$EXX" = "0.000" ]; then
        EXX="-0.000"
    fi
((counter++))
cd strain_XX_$EXX 
  # Strain range in YY direction  
  cd strain_YY_$EXX  
  # Strain range in ZZ direction 
  EYY=$EXX
  EZZ=$EXX
  echo "Debug: Simulation $counter - EXX=$EXX, EYY=$EYY, EZZ=$EZZ"   
	          cd strain_ZZ_$EZZ
                sed -n '/POSITION/,/total drift/ p' OUTCAR > pos-conv.txt
                echo "$EXX $EYY $EZZ" >> ../../../pos-conv.txt
                cat pos-conv.txt >> ../../../pos-conv.txt

                # Add energy lines to separate file
                # Extract lines containing "energy without entropy=" and get only the last occurrence
                ENERGY_LINE=$(grep "energy  without entropy=" OUTCAR | tail -n 1)
                echo "$EXX $EYY $EZZ" >> ../../../energy-conv.txt
                echo "$ENERGY_LINE" >> ../../../energy-conv.txt
        
                # Add the line before "in kB" to a separate file
                TOTAL_LINE=$(grep -B1 "in kB" OUTCAR | grep -v "in kB" | tail -n 1)
                echo "$EXX $EYY $EZZ" >> ../../../pressure_eV.txt
                echo "$TOTAL_LINE" >> ../../../pressure_eV.txt  

                # Extract lines 3, 4, and 5 from the CONTCAR file and save in lattice.txt
                #sed -n '3,5p' CONTCAR > lattice.txt
                sed -n '3,5p' CONTCAR | awk '{printf $1" "$2" "$3" "$4" "$5" "$6" "$7" "$8" "$9" "} END {print ""}'  > lattice.txt
                echo "$EXX $EYY $EZZ" >> ../../../lattice.txt
                cat lattice.txt >> ../../../lattice.txt

                echo >> ../../../pos-conv.txt
	          cd ..
	          
	cd ..
	
cd ..
done
