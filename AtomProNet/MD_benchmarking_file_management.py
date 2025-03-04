import os
import subprocess
import shutil
from MD_benchmarking_lammps_script_generator import generate_minimization_script, generate_npt_relaxation_script

# Global variables to store user inputs
ACCOUNT = None
LAMMPS_EXECUTABLES = {}

def create_main_directory():
    """
    Creates the main directory for LAMMPS computational performance results.

    Returns:
        str: Path to the main directory.
    """
    main_dir = "LAMMPS_computational_performance"
    os.makedirs(main_dir, exist_ok=True)
    return main_dir

def create_potential_directories(main_dir, potential):
    """
    Creates a directory for the specified potential inside the main directory.

    Args:
        main_dir (str): Path to the main directory.
        potential (str): Name of the potential (e.g., "allegro", "mace").

    Returns:
        str: Path to the potential directory.
    """
    pot_dir = os.path.join(main_dir, potential.upper())
    os.makedirs(pot_dir, exist_ok=True)
    return pot_dir

JOB_SUBMISSION_TEMPLATE = """#!/bin/bash

#SBATCH --account={account}
#SBATCH --ntasks={ntasks}
{cpu_directive}
#SBATCH --time={time}
#SBATCH --job-name={job_name}
#SBATCH --output={output_file}
#SBATCH --error={error_file}
{gpu_directive}

{additional_commands}

# Change to the directory where the job submission script is located
cd {folder_name}

# Run LAMMPS
mpiexec -np {ntasks} {lammps_executable} {gpu_flags} -in {input_file}
"""

def get_account():
    """
    Prompts the user to input the account for job submission.

    Returns:
        str: The account to use for job submission.
    """
    global ACCOUNT
    if ACCOUNT is None:
        ACCOUNT = input("Enter the account for job submission (e.g., def-mponga): ").strip()
    return ACCOUNT

def get_lammps_executable(potential):
    """
    Prompts the user to input the LAMMPS executable for the specified potential.

    Args:
        potential (str): The interatomic potential (e.g., "allegro", "mace").

    Returns:
        str: Path to the LAMMPS executable.
    """
    global LAMMPS_EXECUTABLES
    if potential not in LAMMPS_EXECUTABLES:
        LAMMPS_EXECUTABLES[potential] = input(f"Enter the path to the LAMMPS executable for {potential}: ").strip()
    return LAMMPS_EXECUTABLES[potential]

def get_minimization_time():
    """
    Prompts the user to set the time for minimization jobs.

    Returns:
        str: The time for minimization jobs (e.g., "01:00:00").
    """
    print("For minimization jobs, you can set the time:")
    print("(a) Use the default value of 1 hour (01:00:00).")
    print("(b) Enter a custom time (e.g., 02:00:00 for 2 hours).")
    choice = input("Enter your choice (a/b): ").strip().lower()
    if choice == "a":
        return "01:00:00"
    elif choice == "b":
        return input("Enter the custom time (e.g., 02:00:00): ").strip()
    else:
        print("Invalid choice. Using the default value of 1 hour.")
        return "01:00:00"

def generate_job_submission_script(folder_name, potential, job_type, repetition, cpu_directive, universal_ntasks=None, lammps_executable=None):
    """
    Generates a job submission script for the specified potential and job type.

    Args:
        folder_name (str): Path to the folder where the script will be saved.
        potential (str): The interatomic potential (e.g., "allegro", "mace").
        job_type (str): The type of job ("minimization" or "npt_relaxation").
        repetition (int): Number of unit cell repetitions.
        cpu_directive (str): CPU directive for the job (e.g., "#SBATCH --mem-per-cpu=10G").
        universal_ntasks (int): Universal ntasks value for NPT relaxation (optional).
        lammps_executable (str): Path to the LAMMPS executable for the potential.
    """
    # Convert the folder_name to an absolute path
    folder_name = os.path.abspath(folder_name)

    # Use universal_ntasks for NPT relaxation if provided
    if job_type == "npt_relaxation" and universal_ntasks is not None:
        ntasks = universal_ntasks
    else:
        # Ask the user for the number of tasks (ntasks) for minimization or if universal_ntasks is not provided
        while True:
            try:
                ntasks = int(input(f"Enter the number of tasks (ntasks) for {potential} {job_type} at {repetition}x{repetition}x{repetition}: "))
                if ntasks > 0:
                    break
                else:
                    print("Error: ntasks must be a positive integer. Please try again.")
            except ValueError:
                print("Error: Invalid input. Please enter a valid integer for ntasks.")

    # Override ntasks and cpu_directive for MACE
    if potential == "mace":
        ntasks = 1
        cpu_directive = "#SBATCH --mem=192000M"

    # Define job-specific settings
    account = get_account()
    if lammps_executable is None:
        lammps_executable = get_lammps_executable(potential)
    if job_type == "minimization":
        time = get_minimization_time()
    elif job_type == "npt_relaxation":
        time = "01:00:00"  # Fixed at 1 hour for NPT relaxation
        print("Note: The time for NPT relaxation jobs is set to 1 hour to compute simulation time per computational time (ps/hr).")

    if potential == "allegro":
        gpu_directive = ""
        gpu_flags = ""
        additional_commands = ""
    elif potential == "mace":
        gpu_directive = "#SBATCH --gpus-per-node=v100l:1"
        gpu_flags = "-k on g 1 -sf kk"  # Add GPU flags for MACE
        additional_commands = "module load cmake cuda cudnn"
    elif potential == "comb3":
        gpu_directive = ""
        gpu_flags = ""
        additional_commands = ""
    elif potential == "reaxff":
        gpu_directive = ""
        gpu_flags = ""
        additional_commands = ""
    else:
        raise ValueError(f"Unsupported potential: {potential}")
    
    # Define job name and input file
    if job_type == "minimization":
        job_name = f"{potential}_minimization"
        input_file = "in.minimization"
    elif job_type == "npt_relaxation":
        job_name = f"{potential}_npt_relaxation"
        input_file = "in.npt_relaxation"
    else:
        raise ValueError(f"Unsupported job type: {job_type}")
    
    # Define output and error files
    output_file = "output.txt"
    error_file = "error.txt"
    
    # Fill the template with the appropriate values
    script_content = JOB_SUBMISSION_TEMPLATE.format(
        account=account,
        ntasks=ntasks,
        cpu_directive=cpu_directive,
        time=time,
        job_name=job_name,
        output_file=output_file,
        error_file=error_file,
        gpu_directive=gpu_directive,
        additional_commands=additional_commands,
        np=ntasks,
        lammps_executable=lammps_executable,
        gpu_flags=gpu_flags,  # Pass GPU flags to the template
        input_file=input_file,
        folder_name=folder_name,  # Pass the absolute path to the template
    )
    
    # Write the script to the file
    script_path = os.path.join(folder_name, f"lammps_{potential}_{job_type}_jobsub.sh")
    with open(script_path, "w") as f:
        f.write(script_content)
    
    print(f"Created job submission script: {script_path}")

def get_masses_from_user(elements):
    """
    Prompts the user to input the atomic mass for each element.

    Args:
        elements (list): List of element symbols (e.g., ["Al", "O"]).

    Returns:
        dict: A dictionary mapping element symbols to their masses.
    """
    masses = {}
    for element in elements:
        while True:
            try:
                mass = float(input(f"Enter the atomic mass for element {element}: "))
                masses[element] = mass
                break
            except ValueError:
                print("Invalid input. Please enter a numeric value for the mass.")
    return masses

def create_folders_and_files(main_dir, potentials, repetitions, path_to_unit_cell, elements, potential_paths, lammps_executables):
    """
    Creates folders, generates input files, and copies submission scripts.

    Args:
        main_dir (str): Path to the main directory.
        potentials (list): List of selected potentials (e.g., ["allegro", "mace", "comb3", "reaxff"]).
        repetitions (list): List of unit cell repetitions (e.g., ["1", "5", "10"]).
        path_to_unit_cell (str or dict): Path to the unit cell file or dictionary with "with_charges" and "without_charges" paths.
        elements (list): List of elements (e.g., ["Al", "O"]).
        potential_paths (dict): Dictionary mapping each potential to its file path.
        lammps_executables (dict): Dictionary mapping each potential to its LAMMPS executable path.
    """
    # Get atomic masses from the user
    print("\nPlease enter the atomic masses for the following elements:")
    masses = get_masses_from_user(elements)

    # Ask the user for a universal ntasks value for NPT relaxation
    universal_ntasks = None
    while True:
        try:
            universal_ntasks = int(input("Enter the universal number of tasks (ntasks) for NPT relaxation: "))
            if universal_ntasks > 0:
                break
            else:
                print("Error: ntasks must be a positive integer. Please try again.")
        except ValueError:
            print("Error: Invalid input. Please enter a valid integer for ntasks.")

    # Define cpu_directive for minimization and NPT relaxation
    minimization_cpu_directive = "#SBATCH --mem-per-cpu=10G"  # Example: 10G memory per CPU for minimization
    npt_cpu_directive = "#SBATCH --mem-per-cpu=200G"  # Example: 20G memory per CPU for NPT relaxation

    for pot in potentials:
        pot_dir = create_potential_directories(main_dir, pot)
        
        # Get path to the potential file from the potential_paths dictionary
        potential_path = potential_paths[pot]
        
        # Get path to the LAMMPS executable from the lammps_executables dictionary
        lammps_executable = lammps_executables[pot]
        
        # If the potential is Allegro, ask for precision
        if pot == "allegro":
            while True:
                allegro_precision = input("Is Allegro 32 or 64 precision? (Enter 32 or 64): ")
                if allegro_precision in ["32", "64"]:
                    break
                print("Error: Invalid precision. Please enter 32 or 64.")
        else:
            allegro_precision = None
        
        for rep in repetitions:
            folder_name = os.path.join(pot_dir, f"{rep}x{rep}x{rep}")
            os.makedirs(folder_name, exist_ok=True)
            
            # Determine the correct data file path
            if isinstance(path_to_unit_cell, dict):
                # Use the file with charges for comb3/reaxff and the file without charges for allegro/mace
                if pot in ["comb3", "reaxff"]:
                    data_file_path = path_to_unit_cell["with_charges"]
                else:
                    data_file_path = path_to_unit_cell["without_charges"]
            else:
                data_file_path = path_to_unit_cell
            
            # Generate job submission scripts with user-defined ntasks
            generate_job_submission_script(
                folder_name=folder_name,
                potential=pot,
                job_type="minimization",
                repetition=rep,
                cpu_directive=minimization_cpu_directive,
                lammps_executable=lammps_executable,
            )
            generate_job_submission_script(
                folder_name=folder_name,
                potential=pot,
                job_type="npt_relaxation",
                repetition=rep,
                cpu_directive=npt_cpu_directive,
                universal_ntasks=universal_ntasks,  # Pass the universal ntasks value
                lammps_executable=lammps_executable,
            )
            
            # Generate minimization script
            generate_minimization_script(
                folder_name=folder_name,
                potential=pot,
                unit_cell_path=data_file_path,
                repetition=int(rep),
                elements=elements,
                masses=masses,  # Pass the masses to the script generator
                potential_path=potential_path,
                allegro_precision=allegro_precision,
            )
            
            # Generate NPT relaxation script
            generate_npt_relaxation_script(
                folder_name=folder_name,
                potential=pot,
                repetition=int(rep),
                elements=elements,
                masses=masses,  # Pass the masses to the script generator
                potential_path=potential_path,
                allegro_precision=allegro_precision,
            )
    
    print("All folders, input files, and submission scripts have been created.")

def submit_minimization_job(folder_name, potential):
    """
    Submits the LAMMPS minimization job using sbatch.

    Args:
        folder_name (str): Path to the folder containing the job submission script.
        potential (str): The interatomic potential (e.g., "allegro", "mace").
    """
    job_script = os.path.join(folder_name, f"lammps_{potential}_minimization_jobsub.sh")
    if not os.path.exists(job_script):
        print(f"Warning: Minimization job submission script not found in {folder_name}.")
        return
    
    try:
        # Run sbatch command
        result = subprocess.run(["sbatch", job_script], check=True, text=True, capture_output=True)
        print(f"Submitted minimization job for {potential}: {result.stdout.strip()}")
    except subprocess.CalledProcessError as e:
        print(f"Error submitting minimization job for {potential}: {e.stderr}")

def submit_npt_job(folder_name, potential):
    """
    Submits the LAMMPS NPT relaxation job using sbatch.

    Args:
        folder_name (str): Path to the folder containing the job submission script.
        potential (str): The interatomic potential (e.g., "allegro", "mace").
    """
    job_script = os.path.join(folder_name, f"lammps_{potential}_npt_relaxation_jobsub.sh")
    if not os.path.exists(job_script):
        print(f"Warning: NPT relaxation job submission script not found in {folder_name}.")
        return
    
    try:
        # Run sbatch command
        result = subprocess.run(["sbatch", job_script], check=True, text=True, capture_output=True)
        print(f"Submitted NPT relaxation job for {potential}: {result.stdout.strip()}")
    except subprocess.CalledProcessError as e:
        print(f"Error submitting NPT relaxation job for {potential}: {e.stderr}")

def submit_all_minimization_jobs(main_dir):
    """
    Submits all minimization jobs by discovering folders and scripts in the main directory.

    Args:
        main_dir (str): Path to the main directory.
    """
    submit = input("Do you want to submit all minimization jobs? (yes/no): ").lower()
    if submit != "yes":
        print("Minimization jobs were not submitted.")
        return

    # Traverse the main directory
    for potential in os.listdir(main_dir):
        potential_dir = os.path.join(main_dir, potential)
        if os.path.isdir(potential_dir):
            for repetition_folder in os.listdir(potential_dir):
                repetition_dir = os.path.join(potential_dir, repetition_folder)
                if os.path.isdir(repetition_dir):
                    # Look for the minimization job submission script
                    job_script = os.path.join(repetition_dir, f"lammps_{potential.lower()}_minimization_jobsub.sh")
                    if os.path.exists(job_script):
                        try:
                            # Submit the job using sbatch
                            result = subprocess.run(["sbatch", job_script], check=True, text=True, capture_output=True)
                            print(f"Submitted minimization job for {potential} at {repetition_folder}: {result.stdout.strip()}")
                        except subprocess.CalledProcessError as e:
                            print(f"Error submitting minimization job for {potential} at {repetition_folder}: {e.stderr}")
                    else:
                        print(f"Warning: Minimization job submission script not found in {repetition_dir}.")

    print("All minimization jobs have been submitted.")

def submit_all_npt_jobs(main_dir):
    """
    Submits all NPT relaxation jobs by discovering folders and scripts in the main directory.

    Args:
        main_dir (str): Path to the main directory.
    """
    submit = input("Do you want to submit all NPT relaxation jobs? (yes/no): ").lower()
    if submit != "yes":
        print("NPT relaxation jobs were not submitted.")
        return

    # Traverse the main directory
    for potential in os.listdir(main_dir):
        potential_dir = os.path.join(main_dir, potential)
        if os.path.isdir(potential_dir):
            for repetition_folder in os.listdir(potential_dir):
                repetition_dir = os.path.join(potential_dir, repetition_folder)
                if os.path.isdir(repetition_dir):
                    # Look for the NPT relaxation job submission script
                    job_script = os.path.join(repetition_dir, f"lammps_{potential.lower()}_npt_relaxation_jobsub.sh")
                    if os.path.exists(job_script):
                        try:
                            # Submit the job using sbatch
                            result = subprocess.run(["sbatch", job_script], check=True, text=True, capture_output=True)
                            print(f"Submitted NPT relaxation job for {potential} at {repetition_folder}: {result.stdout.strip()}")
                        except subprocess.CalledProcessError as e:
                            print(f"Error submitting NPT relaxation job for {potential} at {repetition_folder}: {e.stderr}")
                    else:
                        print(f"Warning: NPT relaxation job submission script not found in {repetition_dir}.")

    print("All NPT relaxation jobs have been submitted.")
