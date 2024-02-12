#!/bin/bash

# Submission script for hydrostatic strain
# Initialize counter
counter=0

# Initialize list to keep track of restarted jobs
restarted_jobs=()

for EXX in $(seq -0.2 0.0001 0.2) # strain range in XX direction
do 
  ((counter++))
  cd strain_XX_$EXX
  EYY=$EXX
  EZZ=$EXX
  echo "Debug: Simulation $counter - EXX=$EXX, EYY=$EYY, EZZ=$EZZ"   
  
  cd strain_YY_$EYY
    
  cd strain_ZZ_$EZZ
  
  # Check if the line "General timing and accounting informations for this job:" is present in OUTCAR
  if grep -q "General timing and accounting informations for this job:" OUTCAR; then
    echo "Job already completed successfully."
  else
    echo "Resubmitting job with 10-hour time limit."
    sed -i 's/#SBATCH --time=3:00:00/#SBATCH --time=10:00:00/' vasp_job.sh  # Change the time limit in vasp_job.sh
    sbatch vasp_job.sh
    restarted_jobs+=("strain_XX_$EXX/strain_YY_$EYY/strain_ZZ_$EZZ")  # Add the restarted job to the list
  fi
  
  cd ..
  cd ..
  cd ..
done

# Print the list of restarted jobs
echo "Restarted Jobs:"
for job in "${restarted_jobs[@]}"; do
  echo "- $job"
done
