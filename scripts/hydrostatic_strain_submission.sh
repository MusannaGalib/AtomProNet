#!/bin/bash

# Submission script for hydrostatic strain

# Define strain range in XX direction (can be modified by the user)
start=-0.05
increment=0.01
end=0.05

# Automatically calculate the total number of jobs based on the sequence parameters
total_jobs=$(echo "scale=0; ($end - $start) / $increment + 1" | bc)

echo "Total number of jobs to be submitted: $total_jobs"

# Store the absolute path of the top-level directory
top_dir=$(pwd)

# Check if last_job.txt exists to resume from the last job, otherwise issue a warning
if [ ! -f "$top_dir/last_job.txt" ]; then
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
    counter=$(cat "$top_dir/last_job.txt")
    echo "Resuming from job number $counter."
fi

# Define maximum jobs per submission run
max_jobs=4000
submitted_jobs=0

# Define delay duration in seconds
submission_delay=0.05

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

  # Stop if maximum allowed jobs are submitted
  if (( submitted_jobs >= max_jobs )); then
      echo -e "\033[35mReached the job submission limit of $max_jobs. Submitting terminated.\033[0m"
      echo -e "\033[35mLast submitted job: $((job_index - 1))\033[0m"
      echo -e "\033[35mNext submission will start from job $job_index\033[0m"
      echo $((job_index - 1)) > "$top_dir/last_job.txt"
      break
  fi


  # Format EXX to always have four decimal places for consistency
  formatted_EXX=$(printf "%.4f" $EXX)

  # Debug message for tracking
  echo "Debug: Simulation $job_index - EXX=$formatted_EXX, EYY=$formatted_EXX, EZZ=$formatted_EXX"   

  # Navigate into the required directories and submit jobs
  if cd "strain_XX_$formatted_EXX" && \
     cd "strain_YY_$formatted_EXX" && \
     cd "strain_ZZ_$formatted_EXX"; then

    # Submit the job and capture the output
    sbatch_output=$(sbatch vasp_jobsub.sh)
    if [[ $sbatch_output == *"Submitted batch job"* ]]; then
        echo "Job $job_index submitted successfully: $sbatch_output"
        submitted_jobs=$((submitted_jobs + 1))
    else
        echo -e "\033[31mJob $job_index submission failed. Stopping submission process.\033[0m"
        echo -e "\033[35mLast submitted job: $((job_index-1))\033[0m"
        echo -e "\033[35mNext submission will start from job $job_index\033[0m"
        echo $((job_index-1)) > "$top_dir/last_job.txt"
        break
    fi

    cd "$top_dir"  # Return to the top-level directory
  else
    echo -e "\033[31mDirectory structure not found for EXX=$formatted_EXX. Skipping job submission.\033[0m"
    cd "$top_dir"  # Return to the top-level directory in case of failure
  fi

  # Save the last submitted job number to last_job.txt in the top-level directory
  echo $job_index > "$top_dir/last_job.txt"

  # Introduce a small delay after each job submission
  sleep $submission_delay

  # If the counter reaches the total number of jobs, stop
  if (( job_index >= total_jobs )); then
    echo "All jobs have been submitted."
    break
  fi
done





#scancel $(seq 2974787 2974937)
