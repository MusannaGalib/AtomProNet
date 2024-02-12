#!/bin/bash

# Post processing script for 2D strain
for EXX in `seq -0.05 0.01 0.05` # strain range in XX direction
do 
	cd strain_XX_$EXX
	for EYY in `seq -0.05 0.01 0.05` # strain range in YY direction
	do     
	     cd strain_YY_$EYY
	     for EZZ in `seq -0.05 0.01 0.05` # strain range in ZZ direction
	     do     
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
                sed -n '3,5p' CONTCAR | awk '{printf $1" "$2" "$3" "$4" "$5" "$6" "$7" "$8" "$9" "} END {print ""}' > lattice.txt
                echo "$EXX $EYY $EZZ" >> ../../../lattice.txt
                cat lattice.txt >> ../../../lattice.txt

                echo >> ../../../pos-conv.txt
	          cd ..
	          done
	cd ..
	done
cd ..
done
