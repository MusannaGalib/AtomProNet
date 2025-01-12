import os
import subprocess
import shutil
import pymatgen
import mp_api
import numpy as np
# from AtomProNet.lattice import lattice
# from AtomProNet.pressure_eV import pressure_eV
# from AtomProNet.position_force import position_force
# from AtomProNet.energy import energy
# from AtomProNet.atom_symbol import atom_symbol
# from AtomProNet.combine import combine
# from AtomProNet.npz_to_extxyz import npz_to_extxyz
# from AtomProNet.materials_project import fetch_and_write_poscar  # Import the function from your materials_fetcher.py
# from AtomProNet.split import split




def process_and_run_script(input_folder):
    while True:
        print("\nChoose an option:")
        print("1. Data from Materials Project")
        print("2. Pre-processing for DFT simulation")
        print("3. Pre-processing for Neural Network")
        print("4. Post-processing")
        print("Type 'exit' to return to the main menu.")

        option = input("Enter your choice (1/2/3/4 or 'exit'): ").strip()

        # Check for 'exit' option
        if option.lower() == 'exit':
            print("Exiting to the main menu.")
            break

        if option == '1':
            input_folder_path = os.path.abspath(input_folder) 
            os.chdir(input_folder)          
            default_api_key = "H5zmHxuvPs9LKyABNRQmUsj0ROBYs5C4"
            user_api_key = input("Enter your Materials Project API key (press Enter to use default): ")
            api_key = user_api_key if user_api_key.strip() != "" else default_api_key
            query = input("Enter the material ID (e.g., mp-1938, mp-1001790), compound formula (e.g., Al2O3), or elements (e.g., Li, O, Mn): ")
            
            create_supercell_option = input("Do you want to create supercells for all structures? (yes/no): ").lower() == 'yes'
            supercell_size = None
            if create_supercell_option:
                sizes = input("Enter the supercell size (e.g., 2 2 2): ")
                supercell_size = [int(x) for x in sizes.split()]

            from AtomProNet.materials_project import fetch_and_write_poscar  # Import the function from your materials_fetcher.py
            if create_supercell_option:
                fetch_and_write_poscar(api_key, query, input_folder, create_supercell_option, supercell_size)
            else:
                fetch_and_write_poscar(api_key, query, input_folder, create_supercell_option)

                

        

        elif option == '2':
            while True:
                print("Options:")
                print("1: VASP")
                print("2: Quantum ESPRESSO")
                print("q: Quit")
                sub_option = input("Enter your choice: ").strip()

                if sub_option == '1':  # VASP Job Submission
                    while True:
                        print("VASP Options:")
                        print("1: Prepare VASP job submission folders")
                        print("2: VASP job submission")
                        print("3: Post-processing of VASP jobs")
                        print("4: Convergence check of VASP jobs")
                        print("q: Quit")
                        option = input("Enter your choice: ").strip()

                        if option == '1':
                            while True:
                                print("\nOption 1: POSCAR File Operations")
                                print("1. Enter the full path to the folder containing multiple POSCAR files")
                                print("2. Do you want to strain hydrostatically one POSCAR structure")
                                print("3. Do you want to strain volumetrically one POSCAR structure")
                                print("q. Quit")

                                sub_option = input("Enter your choice: ").strip()

                                if sub_option == '1':
                                    # Logic for processing multiple POSCAR files
                                    poscar_folder = input("Enter the full path to the folder containing POSCAR files: ").strip()
                                    poscar_folder = os.path.abspath(poscar_folder)

                                    if not os.path.isdir(poscar_folder):
                                        print(f"Error: The provided path '{poscar_folder}' is not a valid directory.")
                                        continue

                                    # Check for required files one level above the POSCAR folder
                                    parent_folder = os.path.dirname(poscar_folder)
                                    required_files = ["INCAR", "KPOINTS", "vasp_jobsub.sh"]

                                    missing_files = [file for file in required_files if not os.path.exists(os.path.join(parent_folder, file))]

                                    if missing_files:
                                        print("The following required files are missing in the specified parent folder:")
                                        for file in missing_files:
                                            print(f"- {file}")
                                        print("Please place these files in the parent folder and try again.")
                                        continue

                                    # Path to the bash script
                                    script_dir = os.path.dirname(os.path.abspath(__file__))
                                    bash_script_path = os.path.join(script_dir, '..', 'scripts', 'MP_vasp_folders.sh')

                                    if not os.path.exists(bash_script_path):
                                        print(f"Error: The bash script '{bash_script_path}' was not found.")
                                        continue

                                    # Copy the bash script to the POSCAR folder
                                    try:
                                        shutil.copy(bash_script_path, poscar_folder)
                                        print(f"Copied {bash_script_path} to {poscar_folder}")
                                    except IOError as e:
                                        print(f"Error copying the bash script: {e}")
                                        continue

                                    # Run the bash script from the POSCAR folder
                                    try:
                                        print("Running MP_vasp_folders.sh...")
                                        subprocess.run(['bash', './MP_vasp_folders.sh'], cwd=poscar_folder, check=True, text=True)
                                        print("Bash script executed successfully.")
                                    except subprocess.CalledProcessError as e:
                                        print(f"Error executing bash script: {e}")
                                        continue

                                elif sub_option == '2':
                                    # Logic for hydrostatic strain
                                        script_dir = os.path.dirname(os.path.abspath(__file__))
                                        hydrostatic_script_path = os.path.join(script_dir, '..', 'scripts', 'hydrostatic_strain.sh')

                                        if not os.path.exists(hydrostatic_script_path):
                                            print(f"Error: The hydrostatic strain script '{hydrostatic_script_path}' was not found.")
                                            continue

                                        # Ask for the directory where the script will be copied
                                        target_folder = input("Enter the full path to the folder to copy the hydrostatic strain script: ").strip()
                                        target_folder = os.path.abspath(target_folder)

                                        if not os.path.isdir(target_folder):
                                            print(f"Error: The provided path '{target_folder}' is not a valid directory.")
                                            continue

                                        # Copy the hydrostatic strain script to the target folder
                                        try:
                                            shutil.copy(hydrostatic_script_path, target_folder)
                                            print(f"Copied {hydrostatic_script_path} to {target_folder}")
                                        except IOError as e:
                                            print(f"Error copying the script: {e}")
                                            continue

                                        # Ask the user if they want to modify the EXX range
                                        update_range = input("Do you want to modify the EXX range in the script? (yes/no): ").strip().lower()

                                        if update_range == 'yes':
                                            # Ask for the new range values
                                            print("Enter the new range for EXX:")
                                            try:
                                                exx_start = float(input("Start (e.g., -0.05): "))
                                                exx_step = float(input("Step size (e.g., 0.01): "))
                                                exx_end = float(input("End (e.g., 0.05): "))
                                            except ValueError:
                                                print("Error: Please enter valid numerical values for the range.")
                                                continue

                                            # Path to the copied script in the target folder
                                            target_script_path = os.path.join(target_folder, 'hydrostatic_strain.sh')

                                            # Modify the EXX range in the copied script
                                            try:
                                                with open(target_script_path, 'r') as file:
                                                    script_content = file.read()

                                                # Dynamically create the EXX range string and sanitize it
                                                exx_range = f"for EXX in $(seq {exx_start} {exx_step} {exx_end})"
                                                exx_range = exx_range.replace('\r', '').replace('\n', '') + '\n'  # Ensure no carriage returns and add Unix-style newline

                                                # Replace the default range with the sanitized EXX range
                                                updated_content = script_content.replace(
                                                    'for EXX in $(seq -0.05 0.01 0.05)',
                                                    exx_range.strip()  # Strip any unintended whitespace
                                                )

                                                # Write the updated script back to the target file
                                                with open(target_script_path, 'w') as file:
                                                    file.write(updated_content)

                                                print(f"Updated EXX range in {target_script_path}")
                                            except IOError as e:
                                                print(f"Error updating the script: {e}")
                                                continue

                                        # Ask the user if they want to execute the script
                                        execute = input("Do you want to execute the hydrostatic strain script now? (yes/no): ").strip().lower()

                                        if execute == 'yes':
                                            try:
                                                with open(target_script_path, 'r', encoding='utf-8') as file:
                                                    script_content = file.read()

                                                # Replace Windows-style line endings (\r\n) with Unix-style (\n)
                                                script_content = script_content.replace('\r\n', '\n')

                                                with open(target_script_path, 'w', encoding='utf-8', newline='\n') as file:
                                                    file.write(script_content)

                                                print(f"Fixed line endings in {target_script_path} using Python.")
                                            except IOError as e:
                                                print(f"Error fixing line endings: {e}")


                                            try:
                                                subprocess.run(['bash', './hydrostatic_strain.sh'], cwd=target_folder, check=True, text=True)
                                                print("Hydrostatic strain script executed successfully.")
                                            except subprocess.CalledProcessError as e:
                                                print(f"Error executing the hydrostatic strain script: {e}")


                                elif sub_option == '3':
                                    # Logic for volumetric strain
                                    script_dir = os.path.dirname(os.path.abspath(__file__))
                                    volumetric_script_path = os.path.join(script_dir, '..', 'scripts', 'volumetric_strain.sh')

                                    if not os.path.exists(volumetric_script_path):
                                        print(f"Error: The volumetric strain script '{volumetric_script_path}' was not found.")
                                        continue

                                    # Ask for the directory where the script will be copied
                                    target_folder = input("Enter the full path to the folder to copy the volumetric strain script: ").strip()
                                    target_folder = os.path.abspath(target_folder)

                                    if not os.path.isdir(target_folder):
                                        print(f"Error: The provided path '{target_folder}' is not a valid directory.")
                                        continue

                                    # Copy the volumetric strain script to the target folder
                                    try:
                                        shutil.copy(volumetric_script_path, target_folder)
                                        print(f"Copied {volumetric_script_path} to {target_folder}")
                                    except IOError as e:
                                        print(f"Error copying the script: {e}")
                                        continue

                                    # Prompt the user to update the script
                                    print("The volumetric strain script has been copied.")
                                    print("Please update the script to include the correct POSCAR file before execution.")
                                    execute = input("Do you want to execute the volumetric strain script now? (yes/no): ").strip().lower()

                                    if execute == 'yes':
                                        try:
                                            subprocess.run(['bash', './volumetric_strain.sh'], cwd=target_folder, check=True, text=True)
                                            print("Volumetric strain script executed successfully.")
                                        except subprocess.CalledProcessError as e:
                                            print(f"Error executing the volumetric strain script: {e}")

                                elif sub_option == 'q':
                                    print("Exiting POSCAR operations.")
                                    break

                                else:
                                    print("Invalid option. Please try again.")



                        elif option == '2':
                            # Logic for copying and running job_submission.sh (VASP)
                            poscar_folder = input("Enter the full path to the folder to submit jobs: ").strip()
                            poscar_folder = os.path.abspath(poscar_folder)

                            if not os.path.isdir(poscar_folder):
                                print(f"Error: The provided path '{poscar_folder}' is not a valid directory.")
                                continue

                            # Path to the job_submission.sh script
                            script_dir = os.path.dirname(os.path.abspath(__file__))
                            bash_script_path = os.path.join(script_dir, '..', 'scripts', 'job_submission.sh')

                            if not os.path.exists(bash_script_path):
                                print(f"Error: The bash script '{bash_script_path}' was not found.")
                                continue

                            # Copy the bash script to the POSCAR folder
                            try:
                                shutil.copy(bash_script_path, poscar_folder)
                                print(f"Copied {bash_script_path} to {poscar_folder}")
                            except IOError as e:
                                print(f"Error copying the bash script: {e}")
                                continue

                            # Run the bash script from the POSCAR folder
                            try:
                                print("Running job_submission.sh...")
                                subprocess.run(['bash', './job_submission.sh'], cwd=poscar_folder, check=True, text=True)
                                print("Bash script executed successfully.")
                            except subprocess.CalledProcessError as e:
                                print(f"Error executing bash script: {e}")
                                continue

                        elif option == '3':
                            # Logic for copying and running post_processing.sh (VASP)
                            completed_job_folder = input("Enter the full path to the folder to post-process: ").strip()
                            completed_job_folder = os.path.abspath(completed_job_folder)

                            if not os.path.isdir(completed_job_folder):
                                print(f"Error: The provided path '{completed_job_folder}' is not a valid directory.")
                                continue

                            # Path to the post_processing.sh script
                            script_dir = os.path.dirname(os.path.abspath(__file__))
                            bash_script_path = os.path.join(script_dir, '..', 'scripts', 'post_processing.sh')

                            if not os.path.exists(bash_script_path):
                                print(f"Error: The bash script '{bash_script_path}' was not found.")
                                continue

                            # Copy the bash script to the folder
                            try:
                                shutil.copy(bash_script_path, completed_job_folder)
                                print(f"Copied {bash_script_path} to {completed_job_folder}")
                            except IOError as e:
                                print(f"Error copying the bash script: {e}")
                                continue

                            # Run the bash script from the folder
                            try:
                                print("Running post_processing.sh...")
                                subprocess.run(['bash', './post_processing.sh'], cwd=completed_job_folder, check=True, text=True)
                                print("Bash script executed successfully.")
                            except subprocess.CalledProcessError as e:
                                print(f"Error executing bash script: {e}")
                                continue

                        elif option == '4':
                            # Get the absolute path of the script's directory
                            script_dir = os.path.dirname(os.path.abspath(__file__))  # This gets the folder where the wrapper script is located
                            script_path = os.path.join(script_dir, "VASP_convergence_check.py")  # Build the full path to VASP_convergence_check.py
                            
                            # Print the script path for debugging
                            print(f"Looking for script at: {script_path}")
                            
                            # Check if the script exists
                            if not os.path.exists(script_path):
                                print(f"Error: '{script_path}' not found.")
                                return  # Exit if the script is not found
                            
                            # Run the script to extract and plot data from OUTCAR
                            subprocess.run(["python", script_path])  # Run the full path of the script


                        elif option == 'q':
                            print("Exiting VASP options.")
                            break

                        else:
                            print("Invalid option. Please try again.")

                elif sub_option == '2':  # Quantum ESPRESSO Job Submission
                    while True:
                        print("Quantum ESPRESSO Options:")
                        print("1: Prepare Quantum ESPRESSO job submission folders")
                        print("2: Quantum ESPRESSO job submission")
                        print("3: Post-processing of Quantum ESPRESSO jobs")
                        print("q: Quit")
                        option = input("Enter your choice: ").strip()

                        if option == '1':
                            # Logic for copying and running MP_qe_folders.sh
                            qe_folder = input("Enter the full path to the folder containing QE input files: ").strip()
                            qe_folder = os.path.abspath(qe_folder)

                            if not os.path.isdir(qe_folder):
                                print(f"Error: The provided path '{qe_folder}' is not a valid directory.")
                                continue

                            # Path to the QE folder preparation script
                            script_dir = os.path.dirname(os.path.abspath(__file__))
                            bash_script_path = os.path.join(script_dir, '..', 'scripts', 'MP_QE_folders.sh')

                            if not os.path.exists(bash_script_path):
                                print(f"Error: The bash script '{bash_script_path}' was not found.")
                                continue

                            # Copy the bash script to the folder
                            try:
                                shutil.copy(bash_script_path, qe_folder)
                                print(f"Copied {bash_script_path} to {qe_folder}")
                            except IOError as e:
                                print(f"Error copying the bash script: {e}")
                                continue

                            # Run the bash script from the folder
                            try:
                                print("Running MP_qe_folders.sh...")
                                subprocess.run(['bash', './MP_QE_folders.sh'], cwd=qe_folder, check=True, text=True)
                                print("Bash script executed successfully.")
                            except subprocess.CalledProcessError as e:
                                print(f"Error executing bash script: {e}")
                                continue

                        elif option == '2':
                            # Logic for copying and running qe_job_submission.sh
                            qe_folder = input("Enter the full path to the folder to submit QE jobs: ").strip()
                            qe_folder = os.path.abspath(qe_folder)

                            if not os.path.isdir(qe_folder):
                                print(f"Error: The provided path '{qe_folder}' is not a valid directory.")
                                continue

                            # Path to the QE job submission script
                            script_dir = os.path.dirname(os.path.abspath(__file__))
                            bash_script_path = os.path.join(script_dir, '..', 'scripts', 'job_submission.sh')

                            if not os.path.exists(bash_script_path):
                                print(f"Error: The bash script '{bash_script_path}' was not found.")
                                continue

                            # Copy the bash script to the folder
                            try:
                                shutil.copy(bash_script_path, qe_folder)
                                print(f"Copied {bash_script_path} to {qe_folder}")
                            except IOError as e:
                                print(f"Error copying the bash script: {e}")
                                continue

                            # Run the bash script from the folder
                            try:
                                print("Running qe_job_submission.sh...")
                                subprocess.run(['bash', './job_submission.sh'], cwd=qe_folder, check=True, text=True)
                                print("Bash script executed successfully.")
                            except subprocess.CalledProcessError as e:
                                print(f"Error executing bash script: {e}")
                                continue

                        elif option == '3':
                            # Logic for copying and running qe_post_processing.sh
                            completed_qe_folder = input("Enter the full path to the folder to post-process QE jobs: ").strip()
                            completed_qe_folder = os.path.abspath(completed_qe_folder)

                            if not os.path.isdir(completed_qe_folder):
                                print(f"Error: The provided path '{completed_qe_folder}' is not a valid directory.")
                                continue

                            # Path to the QE post-processing script
                            script_dir = os.path.dirname(os.path.abspath(__file__))
                            bash_script_path = os.path.join(script_dir, '..', 'scripts', 'QE_post_processing.sh')

                            if not os.path.exists(bash_script_path):
                                print(f"Error: The bash script '{bash_script_path}' was not found.")
                                continue

                            # Copy the bash script to the folder
                            try:
                                shutil.copy(bash_script_path, completed_qe_folder)
                                print(f"Copied {bash_script_path} to {completed_qe_folder}")
                            except IOError as e:
                                print(f"Error copying the bash script: {e}")
                                continue

                            # Run the bash script from the folder
                            try:
                                print("Running qe_post_processing.sh...")
                                subprocess.run(['bash', './QE_post_processing.sh'], cwd=completed_qe_folder, check=True, text=True)
                                print("Bash script executed successfully.")
                            except subprocess.CalledProcessError as e:
                                print(f"Error executing bash script: {e}")
                                continue

                        elif option == 'q':
                            print("Exiting Quantum ESPRESSO options.")
                            break

                        else:
                            print("Invalid option. Please try again.")

                elif sub_option == 'q':
                    print("Exiting job submission options.")
                    break

                else:
                    print("Invalid option. Please try again.")





        elif option == '3':
            input_folder_path = os.path.abspath(input_folder)           
            script_dir = os.path.dirname(os.path.abspath(__file__))     

            # Ask the user if they want to execute the post-processing script
            run_step1 = input("Do you want to run the first step (execute post-processing script)? (yes/no): ").strip().lower()
            
            if run_step1 == 'yes':
                # Ask the user whether it's for VASP or Quantum ESPRESSO
                while True:
                    print("Select the system for post-processing:")
                    print("1. VASP")
                    print("2. Quantum ESPRESSO")
                    system_choice = input("Enter your choice (1/2): ").strip()

                    if system_choice == '1':  # VASP
                        print("Select the extraction type for VASP:")
                        print("1. Extract ionic last step (Self-Consistent simulations)")
                        print("2. Extract all ionic steps (Ab-initio MD)")
                        vasp_choice = input("Enter your choice (1/2): ").strip()

                        if vasp_choice == '1':
                            bash_script_path = os.path.join(script_dir, '..', 'scripts', 'post_processing.sh')
                            print(f"Using script: {bash_script_path}")
                            break
                        elif vasp_choice == '2':
                            bash_script_path = os.path.join(script_dir, '..', 'scripts', 'AIMD_post_processing.sh')
                            print(f"Using script: {bash_script_path}")
                            break
                        else:
                            print("Invalid choice. Please select 1 or 2 for VASP.")
                            continue

                    elif system_choice == '2':  # Quantum ESPRESSO
                        bash_script_path = os.path.join(script_dir, '..', 'scripts', 'QE_post_processing.sh')
                        print(f"Using script: {bash_script_path}")
                        break
                    else:
                        print("Invalid choice. Please select 1 for VASP or 2 for Quantum ESPRESSO.")
                        continue

                if not os.path.exists(bash_script_path):
                    print("Error: Bash script not found.")
                    return

                # Copy the selected script to the input folder
                try:                                           
                    shutil.copy(bash_script_path, input_folder_path)
                    print(f"Bash script '{os.path.basename(bash_script_path)}' copied successfully.")
                except Exception as e:
                    print(f"Error copying Bash script: {e}")
                    return

                # Change directory to the input folder and execute the script
                os.chdir(input_folder_path)                       
                try:                                              
                    subprocess.run(['bash', os.path.basename(bash_script_path)], capture_output=True, text=True, check=True)
                    print(f"Bash script '{os.path.basename(bash_script_path)}' executed successfully.")
                except subprocess.CalledProcessError as e:
                    print(f"Error executing Bash script: {e}")
                    return
            else:
                print("Skipping the first step and proceeding to step 2.")

        
        

            input_folder_path = input("Enter the path to the input folder: ").strip()
            if not os.path.exists(input_folder_path):
                print(f"Error: Input folder path '{input_folder_path}' does not exist.")
                exit()

            # Step 1: Run the organize.py script in the input folder path
            wrapper_dir = os.path.dirname(os.path.abspath(__file__))  # Current wrapper script directory
            organize_script_path = os.path.join(wrapper_dir, "organize.py")

            if not os.path.exists(organize_script_path):
                print(f"Error: organize.py not found at {organize_script_path}.")
                exit()

            print(f"Executing organize.py to process initial directories in {input_folder_path}...")
            try:
                subprocess.run(['python', organize_script_path, input_folder_path], check=True)
                print("organize.py executed successfully.")
            except subprocess.CalledProcessError as e:
                print(f"Error executing organize.py: {e}")
                exit()

            # Check if `processed_data` folder exists
            processed_data_path = os.path.join(input_folder_path, "processed_data")
            required_files = [
                "symbols.txt",
                "pos-conv.txt",
                "lattice.txt",
                "pressure_eV.txt",
                "energy-conv.txt",
            ]

            concatenated_npz = []
            concatenated_extxyz = []

            if os.path.exists(processed_data_path):
                print(f"Found processed_data folder. Processing subdirectories in {processed_data_path}...")
                for root, dirs, files in os.walk(processed_data_path):
                    # Process folders containing all required files
                    if all(file in files for file in required_files):
                        print(f"Processing folder: {root}")
                        os.chdir(root)
                        try:
                            from AtomProNet.lattice import lattice
                            lattice_output_file = lattice(root)
                            print(f"Lattice processing completed: {lattice_output_file}")

                            from AtomProNet.pressure_eV import pressure_eV
                            pressure_eV_output_file = pressure_eV(root)
                            print(f"Pressure (eV) processing completed: {pressure_eV_output_file}")

                            from AtomProNet.position_force import position_force
                            position_force_output_file = position_force(root)
                            print(f"Position and force processing completed: {position_force_output_file}")

                            from AtomProNet.energy import energy
                            energy_output_file = energy(root)
                            print(f"Energy processing completed: {energy_output_file}")

                            from AtomProNet.atom_symbol import atom_symbol
                            atom_symbol_output_file = atom_symbol(root)
                            print(f"Atom symbol processing completed: {atom_symbol_output_file}")

                            from AtomProNet.combine import combine
                            from AtomProNet.npz_to_extxyz import npz_to_extxyz
                            combined_output_file = combine(root)
                            extxyz_output_file = npz_to_extxyz(combined_output_file)
                            print(f"Final output file: {extxyz_output_file}")

                            concatenated_npz.append(combined_output_file)
                            concatenated_extxyz.append(extxyz_output_file)

                        except Exception as e:
                            print(f"Error while processing {root}: {e}")
                    else:
                        print(f"Required files missing in {root}. Skipping.")


            else:
                print(f"No processed_data folder found. Checking required files in base directory: {input_folder_path}")
                if all(os.path.exists(os.path.join(input_folder_path, file)) for file in required_files):
                    print(f"All required files found in base directory. Processing...")
                    try:
                        os.chdir(input_folder_path)
                        from AtomProNet.lattice import lattice
                        lattice_output_file = lattice(input_folder_path)
                        print(f"Lattice processing completed: {lattice_output_file}")

                        from AtomProNet.pressure_eV import pressure_eV
                        pressure_eV_output_file = pressure_eV(input_folder_path)
                        print(f"Pressure (eV) processing completed: {pressure_eV_output_file}")

                        from AtomProNet.position_force import position_force
                        position_force_output_file = position_force(input_folder_path)
                        print(f"Position and force processing completed: {position_force_output_file}")

                        from AtomProNet.energy import energy
                        energy_output_file = energy(input_folder_path)
                        print(f"Energy processing completed: {energy_output_file}")

                        from AtomProNet.atom_symbol import atom_symbol
                        atom_symbol_output_file = atom_symbol(input_folder_path)
                        print(f"Atom symbol processing completed: {atom_symbol_output_file}")

                        from AtomProNet.combine import combine
                        from AtomProNet.npz_to_extxyz import npz_to_extxyz
                        combined_output_file = combine(input_folder_path)
                        extxyz_output_file = npz_to_extxyz(combined_output_file)
                        print(f"Final output file: {extxyz_output_file}")

                        # Save the final combined files as the result directly
                        converted_npz_file = os.path.join(input_folder_path, "Converted.npz")
                        converted_extxyz_file = os.path.join(input_folder_path, "Converted.extxyz")

                        if os.path.isfile(combined_output_file):
                            os.rename(combined_output_file, converted_npz_file)
                            print(f"Generated Converted.npz at: {converted_npz_file}")

                        if os.path.isfile(extxyz_output_file):
                            os.rename(extxyz_output_file, converted_extxyz_file)
                            print(f"Generated Converted.extxyz at: {converted_extxyz_file}")

                        # Directly assign converted_extxyz_file to a variable for further use
                        final_extxyz_file = converted_extxyz_file

                    except Exception as e:
                        print(f"Error while processing base directory: {e}")
                        exit()  # Exit if an error occurs in base directory processing
                else:
                    print(f"Required files missing in base directory. Cannot process.")
                    exit()

            # Step 3: Concatenate all npz and extxyz files
            if concatenated_npz:
                concatenated_npz = [f for f in concatenated_npz if os.path.isfile(f)]
                concatenated_npz_file = os.path.join(input_folder_path, "Converted.npz")
                combined_data = {}
                for file in concatenated_npz:
                    data = np.load(file, allow_pickle=True)
                    for key in data.keys():
                        if key not in combined_data:
                            combined_data[key] = []
                        combined_data[key].extend(data[key])
                np.savez(concatenated_npz_file, **combined_data)
                print(f"All .npz files concatenated into: {concatenated_npz_file}")

            if concatenated_extxyz:
                concatenated_extxyz = [f for f in concatenated_extxyz if os.path.isfile(f)]
                concatenated_extxyz_file = os.path.join(input_folder_path, "Converted.extxyz")
                with open(concatenated_extxyz_file, 'w') as outfile:
                    for file in concatenated_extxyz:
                        with open(file, 'r') as infile:
                            outfile.write(infile.read())
                print(f"All .extxyz files concatenated into: {concatenated_extxyz_file}")
                final_extxyz_file = concatenated_extxyz_file  # Assign concatenated file for further use
            else:
                print("No .extxyz files were generated. Skipping concatenation.")

            # Ensure split is only performed if `final_extxyz_file` exists
            if 'final_extxyz_file' in locals() and os.path.exists(final_extxyz_file):
                from AtomProNet.split import split
                split_dataset = split(input_folder_path)
                print(f"Final split dataset directory from the workflow: {split_dataset}")
            else:
                print("No final extxyz file found. Cannot proceed with splitting.")

                    

        elif option == '4':
            print("\nPost-Processing Options:")
            print("1. Post-Processing of MLIP")
            print("2. Post-Processing of LAMMPS")
            post_processing_option = input("Select an option (1 or 2): ").strip()

            if post_processing_option == '1':
                print("\nStarting MLIP Post-Processing...")
                
                # Import the necessary function from the MLIP post-processing module
                from AtomProNet.MLIP_post_processing import main as mlip_post_processing_main
                
                try:
                    # Call the main function for MLIP post-processing
                    mlip_post_processing_main(None)
                except Exception as e:
                    print(f"An error occurred during MLIP post-processing: {e}")

            elif post_processing_option == '2':
                print("\nStarting LAMMPS Post-Processing...")

            else:
                print("Invalid option. Please select either 1 or 2.")

            #break

        else:
            print("Invalid option, please try again or type 'exit' to return to the main menu.")

if __name__ == "__main__":
    input_folder = input("Please enter the full path to the folder where the operations should be performed: ").strip()
    process_and_run_script(input_folder)
