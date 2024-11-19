import os
import subprocess
import shutil
import pymatgen
import mp_api
from AtomProNet.lattice import lattice
from AtomProNet.pressure_eV import pressure_eV
from AtomProNet.position_force import position_force
from AtomProNet.energy import energy
from AtomProNet.atom_symbol import atom_symbol
from AtomProNet.combine import combine
from AtomProNet.npz_to_extxyz import npz_to_extxyz
from AtomProNet.materials_project import fetch_and_write_poscar  # Import the function from your materials_fetcher.py

def process_and_run_script(input_folder):
    while True:
        print("\nChoose an option:")
        print("1. Data from Materials Project")
        print("2. Pre-processing for DFT simulation")
        print("3. Pre-processing for Neural Network")
        print("3. Post-processing")
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
            query = input("Enter the material ID (e.g., mp-1234), compound formula (e.g., Al2O3), or elements (e.g., Li, O, Mn): ")
            
            create_supercell_option = input("Do you want to create supercells for all structures? (yes/no): ").lower() == 'yes'
            supercell_size = None
            if create_supercell_option:
                sizes = input("Enter the supercell size (e.g., 2 2 2): ")
                supercell_size = [int(x) for x in sizes.split()]

            if create_supercell_option:
                fetch_and_write_poscar(api_key, query, input_folder, create_supercell_option, supercell_size)
            else:
                fetch_and_write_poscar(api_key, query, input_folder, create_supercell_option)

                

        

        elif option == '2':
                while True:
                    print("Options:")
                    print("1: Copy and run MP_vasp_folders.sh")
                    print("2: Copy and run job_submission.sh")
                    print("q: Quit")
                    option = input("Enter your choice: ").strip()

                    if option == '1':
                        # Ask for the folder containing POSCAR files
                        poscar_folder = input("Enter the full path to the folder containing POSCAR files: ").strip()
                        poscar_folder = os.path.abspath(poscar_folder)

                        if not os.path.isdir(poscar_folder):
                            print(f"Error: The provided path '{poscar_folder}' is not a valid directory.")
                            continue

                        # Check for required files one level above the POSCAR folder
                        parent_folder = os.path.dirname(poscar_folder)
                        required_files = ["INCAR", "KPOINTS", "POTCAR", "vasp_jobsub.sh"]

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

                    elif option == '2':
                        # Ask for the folder containing POSCAR files
                        poscar_folder = input("Enter the full path to the folder containing POSCAR files: ").strip()
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

                    elif option == 'q':
                        print("Exiting.")
                        break

                    else:
                        print("Invalid option. Please try again.")




        elif option == '3':
            input_folder_path = os.path.abspath(input_folder)           
            script_dir = os.path.dirname(os.path.abspath(__file__))     
            bash_script_path = os.path.join(script_dir, '..', 'scripts', 'hydrostatic_strain_post_processing.sh')  

            if not os.path.exists(bash_script_path):
                print("Error: Bash script not found.")
                return

            run_step1 = input("Do you want to run the first step (execute hydrostatic_strain_post_processing.sh)? (yes/no): ").strip().lower()
            
            if run_step1 == 'yes':       
                try:                                           
                    shutil.copy(bash_script_path, input_folder_path)
                    print("Bash script copied successfully.")
                except Exception as e:
                    print(f"Error copying Bash script: {e}")
                    return

                os.chdir(input_folder_path)                       
                try:                                              
                    subprocess.run(['bash', 'hydrostatic_strain_post_processing.sh'], capture_output=True, text=True, check=True)
                    print("Bash script executed successfully.")
                except subprocess.CalledProcessError as e:
                    print(f"Error executing Bash script: {e}")
                    return
            else:
                print("Skipping the first step and proceeding to step 2.")
            
            print("Input folder path:", input_folder_path)   
            
            os.chdir(input_folder)
            print("Starting Step 2: Processing files with Python scripts.")


            try:
                lattice_output_file = lattice(input_folder)
                print(f"Lattice processing completed: {lattice_output_file}")
            except Exception as e:
                print(f"Error in lattice processing: {e}")

            try:
                pressure_eV_output_file = pressure_eV(input_folder)
                print(f"Pressure (eV) processing completed: {pressure_eV_output_file}")
            except Exception as e:
                print(f"Error in pressure (eV) processing: {e}")

            try:
                position_force_output_file = position_force(input_folder)
                print(f"Position and force processing completed: {position_force_output_file}")
            except Exception as e:
                print(f"Error in position and force processing: {e}")

            try:
                energy_output_file = energy(input_folder)
                print(f"Energy processing completed: {energy_output_file}")
            except Exception as e:
                print(f"Error in energy processing: {e}")

            try:
                atom_symbol_output_file = atom_symbol(input_folder)
                print(f"Atom symbol processing completed: {atom_symbol_output_file}")
            except Exception as e:
                print(f"Error in atom symbol processing: {e}")

            combined_output_file = combine(input_folder)
            npz_to_extxyz_output_file = npz_to_extxyz(combined_output_file)


            print(f"Final output file directory from the workflow: {npz_to_extxyz_output_file}") 

        elif option == '4':
            print("Exiting the program.")
            break

        else:
            print("Invalid option, please try again or type 'exit' to return to the main menu.")

if __name__ == "__main__":
    input_folder = input("Please enter the full path to the folder where the operations should be performed: ").strip()
    process_and_run_script(input_folder)
