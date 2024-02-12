#!/bin/bash

#Submission script for hydrostatic strain
# Initialize counter
counter=0

for EXX in `seq -0.2 0.0001 0.2` # strain range in XX direction
do 
((counter++))
	cd strain_XX_$EXX
    EYY=$EXX
    EZZ=$EXX
  echo "Debug: Simulation $counter - EXX=$EXX, EYY=$EYY, EZZ=$EZZ"   
	     cd strain_YY_$EYY
    
	          cd strain_ZZ_$EZZ
                   sbatch vasp_job.sh
	          cd ..	          
	     cd ..	
cd ..
done
 


