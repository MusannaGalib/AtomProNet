import os
import json
from MD_benchmarking_input_validation import validate_repetitions, validate_potentials
from MD_benchmarking_file_management import (
    create_main_directory,
    create_folders_and_files,
    submit_all_minimization_jobs,
    submit_all_npt_jobs,
)
from MD_benchmarking_config import VALID_POTENTIALS
from MD_benchmarking_file_conversion import convert_to_lammps_data
from MD_benchmarking_plotting import plot_npt_performance
from MD_benchmarking_file_management import get_account

def is_lammps_data_file(file_path):
    """
    Checks if the file is in LAMMPS data format by searching for the word "LAMMPS" in the first line.

    Args:
        file_path (str): Path to the file.

    Returns:
        bool: True if the file is in LAMMPS data format, False otherwise.
    """
    try:
        with open(file_path, "r") as f:
            first_line = f.readline().strip()
            # Check if the first line contains the word "LAMMPS"
            return "LAMMPS" in first_line
    except Exception as e:
        print(f"Error checking file format: {e}")
        return False

def has_charges(file_path):
    """
    Checks if the LAMMPS data file includes charges in the Atoms section.

    Args:
        file_path (str): Path to the LAMMPS data file.

    Returns:
        bool: True if the file includes charges, False otherwise.
    """
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

def add_charges_to_lammps_data(input_file, output_file, charges):
    """
    Adds charges to a LAMMPS data file by directly modifying the Atoms section.

    Args:
        input_file (str): Path to the input LAMMPS data file.
        output_file (str): Path to the output LAMMPS data file with charges.
        charges (dict): Dictionary of charges for each element. Keys are element symbols, values are charges.
    """
    try:
        with open(input_file, "r") as f:
            lines = f.readlines()

        # Find the start of the Atoms section
        atoms_section_index = -1
        for i, line in enumerate(lines):
            if "Atoms" in line:
                atoms_section_index = i
                break

        if atoms_section_index == -1:
            print(f"Error: Could not find 'Atoms' section in {input_file}.")
            return None

        # Process the Atoms section
        new_lines = lines[:atoms_section_index + 2]  # Include the "Atoms" line and the blank line after it
        for line in lines[atoms_section_index + 2:]:
            if line.strip() == "":  # End of Atoms section
                break
            parts = line.split()
            if len(parts) >= 5:  # Ensure the line has at least id, type, x, y, z
                atom_id = parts[0]
                atom_type = parts[1]
                x = parts[2]
                y = parts[3]
                z = parts[4]
                element = get_element_from_type(atom_type)  # Map atom type to element
                charge = charges.get(element, 0.0)  # Default charge if element not in charges
                new_line = f"{atom_id} {atom_type} {charge} {x} {y} {z}\n"
                new_lines.append(new_line)

        # Write the modified file
        with open(output_file, "w") as f:
            f.writelines(new_lines)

        print(f"Added charges to LAMMPS data file: {output_file}")
        return output_file
    except Exception as e:
        print(f"Error adding charges to LAMMPS data file: {e}")
        return None

def get_element_from_type(atom_type):
    """
    Maps atom type to element (for simplicity, assumes type 1 is Al and type 2 is O).

    Args:
        atom_type (str): Atom type (e.g., "1", "2").

    Returns:
        str: Element symbol (e.g., "Al", "O").
    """
    if atom_type == "1":
        return "Al"
    elif atom_type == "2":
        return "O"
    else:
        return "X"  # Unknown element

def get_main_dir():
    """
    Prompts the user to provide the path to the main directory.

    Returns:
        str: Path to the main directory.
    """
    while True:
        main_dir = input("Enter the path to the main directory (or leave blank to use the current directory): ").strip()
        if not main_dir:
            main_dir = os.getcwd()  # Use the current directory if no path is provided        
        if not os.path.exists(main_dir):
            try:
                os.makedirs(main_dir)  # Create the directory if it doesn't exist
                print(f"Directory '{main_dir}' did not exist and has been created.")
            except OSError as e:
                print(f"Error: Could not create directory '{main_dir}'. {e}")
                continue
        return main_dir

def get_unit_cell_file():
    """
    Prompts the user to provide the path to the unit cell file.

    Returns:
        str: Path to the unit cell file.
    """
    while True:
        path_to_unit_cell = input("Enter the path to the unit cell file: ")
        if os.path.exists(path_to_unit_cell):
            return path_to_unit_cell
        else:
            print(f"Error: The file '{path_to_unit_cell}' does not exist. Please enter a valid path.")

def get_potential_paths(potentials):
    """
    Prompts the user to provide the path to the potential file for each selected potential.

    Args:
        potentials (list): List of selected potentials (e.g., ["allegro", "mace", "comb3", "reaxff"]).

    Returns:
        dict: Dictionary mapping each potential to its file path.
    """
    potential_paths = {}
    for potential in potentials:
        while True:
            potential_path = input(f"Enter the path to the {potential.upper()} interatomic potential: ")
            if os.path.exists(potential_path):
                potential_paths[potential] = potential_path
                break
            else:
                print(f"Error: The file '{potential_path}' does not exist. Please enter a valid path.")
    return potential_paths

def get_lammps_executables(potentials):
    """
    Prompts the user to provide the path to the LAMMPS executable for each selected potential.

    Args:
        potentials (list): List of selected potentials (e.g., ["allegro", "mace", "comb3", "reaxff"]).

    Returns:
        dict: Dictionary mapping each potential to its LAMMPS executable path.
    """
    lammps_executables = {}
    for potential in potentials:
        while True:
            lammps_executable = input(f"Enter the path to the LAMMPS executable for {potential.upper()}: ")
            if os.path.exists(lammps_executable):
                lammps_executables[potential] = lammps_executable
                break
            else:
                print(f"Error: The file '{lammps_executable}' does not exist. Please enter a valid path.")
    return lammps_executables

def find_potentials_and_repetitions(main_dir):
    """
    Automatically discovers the potentials and repetitions from the directory structure.

    Args:
        main_dir (str): Path to the main directory.

    Returns:
        tuple: A tuple containing two lists: (potentials, repetitions).
    """
    potentials = []
    repetitions = []

    # Traverse the main directory to find potentials
    for potential in os.listdir(main_dir):
        potential_dir = os.path.join(main_dir, potential)
        if os.path.isdir(potential_dir):
            potentials.append(potential.lower())  # Ensure lowercase for consistency

            # Traverse the potential directory to find repetitions
            for repetition_folder in os.listdir(potential_dir):
                repetition_dir = os.path.join(potential_dir, repetition_folder)
                if os.path.isdir(repetition_dir):
                    # Use the full repetition folder name (e.g., "1x1x1")
                    if repetition_folder not in repetitions:
                        repetitions.append(repetition_folder)

    # Sort repetitions numerically based on the first part (e.g., "1x1x1" → "1")
    repetitions = sorted(repetitions, key=lambda x: int(x.split("x")[0]))

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
            main_dir = get_main_dir()
            # Prompt the user for the account once
            from MD_benchmarking_file_management import get_account
            get_account()
            # Get and validate unit cell repetitions
            while True:
                repetitions = input("Enter the unit cell repetitions you want (separated by spaces, e.g., '1 3 5 7 10'): ").split()
                try:
                    validate_repetitions(repetitions)
                    break
                except ValueError as e:
                    print(e)
            
            # Get and validate interatomic potentials
            while True:
                potentials = input(f"Enter the interatomic potentials ({', '.join(VALID_POTENTIALS)}) separated by spaces: ").lower().split()
                try:
                    validate_potentials(potentials)
                    break
                except ValueError as e:
                    print(e)
            
            # Get paths to potential files
            potential_paths = get_potential_paths(potentials)
            
            # Get paths to LAMMPS executables
            lammps_executables = get_lammps_executables(potentials)
            
            # Get path to unit cell file
            path_to_unit_cell = get_unit_cell_file() 

            # Check if the file is in LAMMPS data format
            if not is_lammps_data_file(path_to_unit_cell):
                print("The input file is not in LAMMPS data format.")
                while True:
                    convert_choice = input("Do you want to convert it to LAMMPS data format? (yes/no): ").strip().lower()
                    if convert_choice in ["yes", "no"]:
                        break
                    else:
                        print("Error: Invalid choice. Please enter 'yes' or 'no'.")
                
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
                            while True:
                                try:
                                    charge = float(input(f"Enter the charge for element {element}: "))
                                    charges[element] = charge
                                    break
                                except ValueError:
                                    print("Error: Invalid input. Please enter a numeric value for the charge.")
                        
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

            # Check if the file is in LAMMPS data format
            if is_lammps_data_file(path_to_unit_cell):
                print("The input file is already in LAMMPS data format.")
                
                # Determine if charges are needed
                requires_charges = any(potential in ["comb3", "reaxff"] for potential in potentials)
                requires_no_charges = any(potential in ["allegro", "mace"] for potential in potentials)
                
                # If charges are required for any potential, check if the file has charges
                if requires_charges:
                    if not has_charges(path_to_unit_cell):
                        print("The selected potentials (comb3, reaxff) require charges, but the LAMMPS data file does not include charges.")
                        while True:
                            charge_option = input("Do you want to (1) provide a path to a LAMMPS file with charges, or (2) add charges to the current file? (1/2): ").strip()
                            if charge_option in ["1", "2"]:
                                break
                            else:
                                print("Error: Invalid option. Please enter 1 or 2.")
                        
                        if charge_option == "1":
                            # Ask the user to provide a LAMMPS file with charges
                            while True:
                                path_to_unit_cell_with_charges = input("Enter the path to the LAMMPS data file with charges: ")
                                if os.path.exists(path_to_unit_cell_with_charges):
                                    break
                                else:
                                    print(f"Error: The file '{path_to_unit_cell_with_charges}' does not exist. Please enter a valid path.")
                            
                            # Update the path_to_unit_cell dictionary
                            path_to_unit_cell = {
                                "with_charges": path_to_unit_cell_with_charges,
                                "without_charges": path_to_unit_cell  # Original file without charges
                            }
                        elif charge_option == "2":
                            # Add charges to the current LAMMPS data file
                            lammps_data_file_with_charges = os.path.join(os.path.dirname(path_to_unit_cell), "lammps_data_file_with_charges.data")
                            elements = input("Enter the elements (e.g., 'Al O'): ").split()
                            charges = {}
                            for element in elements:
                                while True:
                                    try:
                                        charge = float(input(f"Enter the charge for element {element}: "))
                                        charges[element] = charge
                                        break
                                    except ValueError:
                                        print("Error: Invalid input. Please enter a numeric value for the charge.")
                            
                            # Add charges to the LAMMPS data file
                            add_charges_to_lammps_data(path_to_unit_cell, lammps_data_file_with_charges, charges)
                            if not os.path.exists(lammps_data_file_with_charges):
                                print("Failed to add charges to the LAMMPS data file. Exiting.")
                                exit(1)
                            
                            # Update the path_to_unit_cell dictionary
                            path_to_unit_cell = {
                                "with_charges": lammps_data_file_with_charges,
                                "without_charges": path_to_unit_cell  # Original file without charges
                            }
                    else:
                        # The file already has charges, so we can use it for comb3/reaxff
                        path_to_unit_cell = {
                            "with_charges": path_to_unit_cell,
                            "without_charges": path_to_unit_cell  # Use the same file for allegro/mace (charges will be ignored)
                        }
                else:
                    # No charges are required, so use the original file for all potentials
                    path_to_unit_cell = path_to_unit_cell
            else:
                print("The input file is not in LAMMPS data format.")
                # Handle non-LAMMPS file conversion (not relevant to this case)
            
            # Get elements (if not already provided for charges)
            if 'elements' not in locals():
                elements = input("Enter the elements (e.g., 'Al O'): ").split()
            
            # Create folders, generate input files, and copy submission scripts
            create_folders_and_files(main_dir, potentials, repetitions, path_to_unit_cell, elements, potential_paths, lammps_executables)
        
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
