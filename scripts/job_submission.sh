#!/bin/bash

# Submission script for hydrostatic strain with recursive directory traversal and logging.

# Set the default maximum number of jobs to submit in one run
max_jobs=${1:-999}  # User can override via the first script argument
submitted_jobs=0    # Counter for submitted jobs
total_jobs=0        # Total jobs found

# Check if last_job.txt exists to resume from the last job
if [ -f last_job.txt ]; then
    counter=$(cat last_job.txt)
    echo "Resuming from job number $counter."
else
    echo "Starting fresh. No 'last_job.txt' found."
    counter=0
fi

# Initialize log file
log_file="job_submission.log"
echo "Job submission started at $(date)" > "$log_file"

# Function to recursively traverse directories and submit jobs
submit_jobs_recursive() {
    local current_dir=$1

    # Loop through all items in the current directory
    for item in "$current_dir"/*; do
        if [ -d "$item" ]; then
            cd "$item" || continue

            # Find all .sh files in the current directory
            sh_files=($(find . -maxdepth 1 -type f -name "*.sh"))

            # Submit each .sh file as a job
            for sh_file in "${sh_files[@]}"; do
                # Increment total job counter
                ((total_jobs++))

                # Skip jobs already submitted
                if (( total_jobs <= counter )); then
                    continue
                fi

                # Submit the job and capture the output
                sbatch_output=$(sbatch "$sh_file")
                if [[ $sbatch_output == *"Submitted batch job"* ]]; then
                    echo "Job $total_jobs submitted successfully: $sbatch_output"
                    echo "[$(date)] Job $total_jobs submitted successfully in folder: $item with script: $sh_file" >> "$log_file"
                    submitted_jobs=$((submitted_jobs + 1))
                else
                    echo "Job $total_jobs submission failed: $sbatch_output"
                    echo "[$(date)] Job $total_jobs submission failed in folder: $item with script: $sh_file" >> "$log_file"
                    continue  # Proceed to the next job despite failure
                fi

                # Save the last submitted job number to last_job.txt
                echo $total_jobs > "$script_folder/last_job.txt"

                # Stop if the maximum allowed jobs have been submitted
                if (( submitted_jobs >= max_jobs )); then
                    echo "Reached the job submission limit of $max_jobs. Stopping."
                    return 0
                fi
            done

            # Recurse into subdirectories
            submit_jobs_recursive "$item"

            cd ..  # Return to the previous directory
        fi
    done
}

# Get the current script directory
script_folder=$(dirname "$(realpath "$0")")
cd "$script_folder" || exit 1

# Start recursive job submission
submit_jobs_recursive "$script_folder"

# Final output
echo "Total jobs found: $total_jobs"
echo "Total jobs submitted in this run: $submitted_jobs"
echo "Job submission completed at $(date)" >> "$log_file"

if (( submitted_jobs < max_jobs )); then
    echo "All available jobs have been submitted."
else
    echo "You may rerun the script to continue submitting remaining jobs."
fi
