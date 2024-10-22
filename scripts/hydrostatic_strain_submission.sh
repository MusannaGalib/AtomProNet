#!/bin/bash

# Submission script for hydrostatic strain

# Define strain range in XX direction (can be modified by the user)
start=-0.1
increment=0.0001
end=0.1

# Automatically calculate the total number of jobs based on the sequence parameters
total_jobs=$(echo "scale=0; ($end - $start) / $increment + 1" | bc)

echo "Total number of jobs to be submitted: $total_jobs"

# Check if last_job.txt exists to resume from the last job, otherwise issue a warning
if [ ! -f last_job.txt ]; then
    echo "Warning: 'last_job.txt' not found. You are about to submit jobs starting from 1."
    read -p "Do you want to proceed? (yes/no): " user_input

    if [ "$user_input" != "yes" ]; then
        echo "Aborting job submission."
        exit 1
    else
        counter=0
    fi
else
    # Initialize the counter from last job
    counter=$(cat last_job.txt)
    echo "Resuming from job number $counter."
fi

# Set a maximum limit for job submission in one run (e.g., 999 jobs)
max_jobs=999
submitted_jobs=0

# Skip the first 'counter' values in the sequence to resume correctly
job_index=0
for EXX in $(seq $start $increment $end) # strain range in XX direction
do 
  # Increment the job index to track the sequence
  ((job_index++))

  # Skip jobs that were already submitted in previous runs
  if (( job_index <= counter )); then
    continue
  fi

  # If we have already submitted the max allowed jobs for this run, stop
  if (( submitted_jobs >= max_jobs )); then
    echo "Reached the job submission limit of $max_jobs. Stopping the script."
    break
  fi

  # Format EXX to always have four decimal places for consistency
  formatted_EXX=$(printf "%.4f" $EXX)

  # Debug message for tracking
  echo "Debug: Simulation $job_index - EXX=$formatted_EXX, EYY=$formatted_EXX, EZZ=$formatted_EXX"   

  # Navigate into the required directories and submit jobs
  cd strain_XX_$formatted_EXX
    EYY=$formatted_EXX
    EZZ=$formatted_EXX
    cd strain_YY_$EYY
    cd strain_ZZ_$EZZ

    # Submit the job and capture the output
    sbatch_output=$(sbatch vasp_job.sh)
    if [[ $sbatch_output == *"Submitted batch job"* ]]; then
        echo "Job $job_index submitted successfully: $sbatch_output"
        submitted_jobs=$((submitted_jobs + 1))  # Increment submitted jobs counter
    else
        echo "Job $job_index submission failed: $sbatch_output"
        break
    fi

    cd ..
    cd ..
  cd ..

  # Save the last submitted job number to last_job.txt
  echo $job_index > last_job.txt

  # If the counter reaches the total number of jobs, stop
  if (( job_index >= total_jobs )); then
    echo "All jobs have been submitted."
    break
  fi

done



#scancel $(seq 2974787 2974937)


#Submission script for hydrostatic strain
# Initialize counter
#counter=0

#for EXX in `seq -0.2 0.0001 0.2` # strain range in XX direction
#do 
#((counter++))
#	cd strain_XX_$EXX
#    EYY=$EXX
#    EZZ=$EXX
#  echo "Debug: Simulation $counter - EXX=$EXX, EYY=$EYY, EZZ=$EZZ"   
#	     cd strain_YY_$EYY
#    
#	          cd strain_ZZ_$EZZ
#                   sbatch vasp_job.sh
#	          cd ..	          
#	     cd ..	
#cd ..
#done
 


