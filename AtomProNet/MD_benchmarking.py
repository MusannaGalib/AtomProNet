import os
import json
from MD_benchmarking_input_validation import validate_repetitions, validate_potentials
from file_management import (
    create_main_directory,
    create_folders_and_files,
    submit_all_minimization_jobs,
    submit_all_npt_jobs,
)
from config import VALID_POTENTIALS
from file_conversion import convert_to_lammps_data
from plotting import plot_npt_performance

def is_lammps_data_file(file_path):
    try:
        with open(file_path, "r") as f:
            first_line = f.readline().strip()
            # Check if the first line contains the word "LAMMPS"
            return "LAMMPS" in first_line
    except Exception as e:
        print(f"Error checking file format: {e}")
        return False

def has_charges(file_path):
    try:
        with open(file_path, "r") as f:
            in_atoms_section = False
            for line in f:
                if "Atoms" in line:  # Look for the "Atoms" section
                    in_atoms_section = True
                    next(f)  # Skip the line after "Atoms"
                    continue
                if in_atoms_section:
                    if line.strip() == "":  # End of Atoms section
                        break
                    # Check if the atom line has at least 6 columns (id, type, charge, x, y, z)
                    if len(line.split()) >= 6:
                        return True  # Charges are present
            return False  # No charges found
    except Exception as e:
        print(f"Error checking for charges: {e}")
        return False

def get_main_dir():
    while True:
        main_dir = input("Enter the path to the main directory (or leave blank to use the current directory): ").strip()
        if not main_dir:
            main_dir = os.getcwd()  # Use the current directory if no path is provided
        if os.path.exists(main_dir):
            return main_dir
        else:
            print(f"Error: The directory '{main_dir}' does not exist. Please enter a valid path.")

def find_potentials_and_repetitions(main_dir):
    potentials = []
    repetitions = set()  # Use a set to avoid duplicates

    # Scan the main directory for potential folders
    for potential in VALID_POTENTIALS:
        potential_dir = os.path.join(main_dir, potential.upper())
        if os.path.exists(potential_dir):
            potentials.append(potential)
            # Scan the potential directory for repetition folders
            for repetition in os.listdir(potential_dir):
                repetition_path = os.path.join(potential_dir, repetition)
                if os.path.isdir(repetition_path):
                    repetitions.add(repetition)

    # Convert the set of repetitions to a sorted list
    repetitions = sorted(list(repetitions), key=lambda x: tuple(map(int, x.split('x'))))

    return potentials, repetitions

def main():
    print("Welcome to the LAMMPS Computational Performance Setup Tool!")
    
    while True:
        # Present options to the user
        print("\nPlease select an option:")
        print("1. Create folders, generate input files, and copy submission scripts.")
        print("2. Submit all minimization jobs.")
        print("3. Submit all NPT relaxation jobs.")
        print("4. Plot computational performance.")
        print("5. Exit.")
        
        option = input("Enter your choice (1, 2, 3, 4, or 5): ").strip()
        
        if option not in ["1", "2", "3", "4", "5"]:
            print("Error: Invalid option. Please enter 1, 2, 3, 4, or 5.")
            continue
        
        # Handle Option 1
        if option == "1":
            # Get the path to the main directory
            main_dir = input("Enter the path to the main directory (or leave blank to use the current directory): ").strip()
            if not main_dir:
                main_dir = os.getcwd()  # Use the current directory if no path is provided
            os.makedirs(main_dir, exist_ok=True)  # Create the directory if it doesn't exist
            
            # Get and validate unit cell repetitions
            repetitions = input("Enter the unit cell repetitions you want (separated by spaces, e.g., '1 3 5 7 10'): ").split()
            validate_repetitions(repetitions)
            
            # Get and validate interatomic potentials
            potentials = input(f"Enter the interatomic potentials ({', '.join(VALID_POTENTIALS)}) separated by spaces: ").lower().split()
            validate_potentials(potentials)
            
            # Get path to unit cell file
            path_to_unit_cell = input("Enter the path to the unit cell file: ")
            if not os.path.exists(path_to_unit_cell):
                print(f"Error: The file '{path_to_unit_cell}' does not exist.")
                exit(1)
            
            # Check if the file is in LAMMPS data format
            if not is_lammps_data_file(path_to_unit_cell):
                print("The input file is not in LAMMPS data format.")
                convert_choice = input("Do you want to convert it to LAMMPS data format? (yes/no): ").strip().lower()
                if convert_choice == "yes":
                    # Determine if charges are needed
                    requires_charges = any(potential in ["comb3", "reaxff"] for potential in potentials)
                    requires_no_charges = any(potential in ["allegro", "mace"] for potential in potentials)
                    
                    # Generate LAMMPS data file with charges (if needed)
                    if requires_charges:
                        lammps_data_file_with_charges = os.path.join(os.path.dirname(path_to_unit_cell), "lammps_data_file_with_charges.data")
                        elements = input("Enter the elements (e.g., 'Al O'): ").split()
                        charges = {}
                        for element in elements:
                            charge = input(f"Enter the charge for element {element}: ")
                            charges[element] = float(charge)
                        
                        # Convert the file to LAMMPS data format with charges
                        converted_file_with_charges = convert_to_lammps_data(path_to_unit_cell, lammps_data_file_with_charges, charges)
                        if not converted_file_with_charges:
                            print("Failed to convert the file with charges. Exiting.")
                            exit(1)
                    
                    # Generate LAMMPS data file without charges (if needed)
                    if requires_no_charges:
                        lammps_data_file_no_charges = os.path.join(os.path.dirname(path_to_unit_cell), "lammps_data_file_no_charges.data")
                        
                        # Convert the file to LAMMPS data format without charges
                        converted_file_no_charges = convert_to_lammps_data(path_to_unit_cell, lammps_data_file_no_charges, charges=None)
                        if not converted_file_no_charges:
                            print("Failed to convert the file without charges. Exiting.")
                            exit(1)
                    
                    # Update the path_to_unit_cell based on the selected potentials
                    if requires_charges and requires_no_charges:
                        print("Generated two LAMMPS data files: one with charges and one without.")
                        # Use the file with charges for comb3/reaxff and the file without charges for allegro/mace
                        path_to_unit_cell = {
                            "with_charges": converted_file_with_charges,
                            "without_charges": converted_file_no_charges
                        }
                    elif requires_charges:
                        path_to_unit_cell = converted_file_with_charges
                    elif requires_no_charges:
                        path_to_unit_cell = converted_file_no_charges
                else:
                    print("Skipping file conversion. Using the original file.")
            else:
                print("The input file is already in LAMMPS data format.")
            
            # Check if charges are required and if the file has charges
            requires_charges = any(potential in ["comb3", "reaxff"] for potential in potentials)
            if requires_charges and not has_charges(path_to_unit_cell):
                print("The selected potentials (comb3, reaxff) require charges, but the LAMMPS data file does not include charges.")
                charge_option = input("Do you want to (1) provide a path to a LAMMPS file with charges, or (2) convert the current file to include charges? (1/2): ").strip()
                if charge_option == "1":
                    path_to_unit_cell_with_charges = input("Enter the path to the LAMMPS data file with charges: ")
                    if not os.path.exists(path_to_unit_cell_with_charges):
                        print(f"Error: The file '{path_to_unit_cell_with_charges}' does not exist.")
                        exit(1)
                    path_to_unit_cell = path_to_unit_cell_with_charges
                elif charge_option == "2":
                    lammps_data_file_with_charges = os.path.join(os.path.dirname(path_to_unit_cell), "lammps_data_file_with_charges.data")
                    elements = input("Enter the elements (e.g., 'Al O'): ").split()
                    charges = {}
                    for element in elements:
                        charge = input(f"Enter the charge for element {element}: ")
                        charges[element] = float(charge)
                    
                    # Convert the file to LAMMPS data format with charges
                    converted_file_with_charges = convert_to_lammps_data(path_to_unit_cell, lammps_data_file_with_charges, charges)
                    if not converted_file_with_charges:
                        print("Failed to convert the file with charges. Exiting.")
                        exit(1)
                    path_to_unit_cell = converted_file_with_charges
                else:
                    print("Invalid option. Exiting.")
                    exit(1)
            
            # Get elements (if not already provided for charges)
            if 'elements' not in locals():
                elements = input("Enter the elements (e.g., 'Al O'): ").split()
            
            # Create folders, generate input files, and copy submission scripts
            create_folders_and_files(main_dir, potentials, repetitions, path_to_unit_cell, elements)
        
        # Handle Option 2
        elif option == "2":
            # Get the path to the main directory
            main_dir = get_main_dir()
            
            # Submit all minimization jobs
            submit_all_minimization_jobs(main_dir)
        
        # Handle Option 3
        elif option == "3":
            # Get the path to the main directory
            main_dir = get_main_dir()
            
            # Submit all NPT relaxation jobs
            submit_all_npt_jobs(main_dir)
        
        # Handle Option 4
        elif option == "4":
            # Get the path to the main directory
            main_dir = get_main_dir()
            
            # Automatically find potentials and repetitions
            potentials, repetitions = find_potentials_and_repetitions(main_dir)
            if not potentials:
                print("Error: No potentials found in the main directory.")
                continue
            if not repetitions:
                print("Error: No repetitions found in the main directory.")
                continue
            
            print(f"Found potentials: {', '.join(potentials)}")
            print(f"Found repetitions: {', '.join(repetitions)}")
            
            # Plot NPT relaxation performance
            plot_npt_performance(main_dir, potentials, repetitions)
        
        # Handle Option 5
        elif option == "5":
            print("Exiting the program. Goodbye!")
            break

if __name__ == "__main__":
    main()
