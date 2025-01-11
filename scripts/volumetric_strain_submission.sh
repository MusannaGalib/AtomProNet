#!/bin/bash

#Submission script for 2D strain

for EXX in `seq -0.05 0.01 0.05` # strain range in XX direction
do 
	cd strain_XX_$EXX
	for EYY in `seq -0.05 0.01 0.05` # strain range in YY direction
	do     
	     cd strain_YY_$EYY
	     for EZZ in `seq -0.05 0.01 0.05` # strain range in ZZ direction
	     do     
	          cd strain_ZZ_$EZZ
                   sbatch vasp_jobsub.sh
	          cd ..
	          done
	cd ..
	done
cd ..
done
 


