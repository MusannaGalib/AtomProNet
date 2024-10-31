import os
import subprocess
import shutil
from materials_fetcher import fetch_and_write_poscar  # Import the function from your materials_fetcher.py
from lattice import lattice
from pressure_eV import pressure_eV
from position_force import position_force
from energy import energy
from atom_symbol import atom_symbol
from combine import combine
from npz_to_extxyz import npz_to_extxyz

def process_and_run_script(input_folder):
    # Step 2: Process files or fetch materials data
    while True:
        print("\nChoose an option:")
        print("1. Fetch material data and create POSCAR files")
        print("2. Process the generated files with Python scripts")
        print("3. Exit")

        option = input("Enter your choice (1/2/3): ").strip()

        if option == '1':
            # Fetch material data and create POSCAR files
            api_key = input("Enter your Materials Project API key: ")
            query = input("Enter the material ID (e.g., mp-1234), compound formula (e.g., Al2O3), or elements (e.g., Li, O, Mn): ")
            
            create_supercell_option = input("Do you want to create supercells for all structures? (yes/no): ").lower() == 'yes'
            supercell_size = None
            if create_supercell_option:
                sizes = input("Enter the supercell size (e.g., 2 2 2): ")
                supercell_size = [int(x) for x in sizes.split()]

            fetch_and_write_poscar(api_key, query, create_supercell_option, supercell_size)

        elif option == '2':
            # Step 1: Set up paths and check for the Bash script
            input_folder_path = os.path.abspath(input_folder)
            script_dir = os.path.dirname(os.path.abspath(__file__))
            bash_script_path = os.path.join(script_dir, '..', 'scripts', 'hydrostatic_strain_post_processing.sh')

            if not os.path.exists(bash_script_path):
                print("Error: Bash script not found.")
                return

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

            print("Input folder path:", input_folder_path)

            # Process the generated files
            print("Starting Step 2: Processing files with Python scripts.")
            lattice_output_file = lattice(input_folder)
            pressure_eV_output_file = pressure_eV(input_folder)
            position_force_output_file = position_force(input_folder)
            energy_output_file = energy(input_folder)
            atom_symbol_output_file = atom_symbol(input_folder)
            combined_output_file = combine(input_folder)
            npz_to_extxyz_output_file = npz_to_extxyz(combined_output_file)

            print(f"Final output file directory from the workflow: {npz_to_extxyz_output_file}")

        elif option == '3':
            print("Exiting the program.")
            break

        else:
            print("Invalid option, please try again.")

if __name__ == "__main__":
    input_folder = input("Please enter the full path to the folder where the operations should be performed: ").strip()
    process_and_run_script(input_folder)
