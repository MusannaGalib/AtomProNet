from ase.io import read
import numpy as np
import os

def convert_to_lammps_data(input_file, output_file, charges=None):
    """
    Converts a non-LAMMPS file (e.g., XYZ, POSCAR) to LAMMPS data format, including charges.

    Args:
        input_file (str): Path to the input file.
        output_file (str): Path to the output LAMMPS data file.
        charges (dict): Dictionary of charges for each element. Keys are element symbols, values are charges.
                        If None, charges will not be included.

    Returns:
        str: Path to the output file if successful, None otherwise.
    """
    try:
        # Read the input file using ASE
        atoms = read(input_file)

        # Automatically determine the order of elements based on their first occurrence
        unique_elements = []
        for atom in atoms:
            if atom.symbol not in unique_elements:
                unique_elements.append(atom.symbol)

        # Create a mapping from element to atom type based on the order of first occurrence
        element_to_type = {element: i + 1 for i, element in enumerate(unique_elements)}

        # If charges are provided, assign them to the atoms
        if charges is not None:
            # Create a new array to store charges
            charges_array = np.zeros(len(atoms))
            for i, atom in enumerate(atoms):
                element = atom.symbol
                if element in charges:
                    charges_array[i] = charges[element]
                else:
                    charges_array[i] = 0.0  # Default charge if not specified

            # Add charges to the Atoms object
            atoms.set_initial_charges(charges_array)

        # Write the atoms object to a LAMMPS data file manually
        with open(output_file, "w") as f:
            # Write LAMMPS header
            f.write("# LAMMPS data file written by OVITO Basic 3.9.2\n\n")
            f.write(f"{len(atoms)} atoms\n")
            f.write(f"{len(unique_elements)} atom types\n\n")  # Use the number of unique elements

            # Write box dimensions
            cell = atoms.get_cell()
            f.write(f"0.0 {cell[0, 0]} xlo xhi\n")
            f.write(f"0.0 {cell[1, 1]} ylo yhi\n")
            f.write(f"0.0 {cell[2, 2]} zlo zhi\n\n")

            # Write Atoms section
            if charges is not None:
                f.write("Atoms  # charge\n\n")
            else:
                f.write("Atoms\n\n")

            for i, atom in enumerate(atoms):
                # Assign atom types based on the order of first occurrence
                atom_type = element_to_type[atom.symbol]
                if charges is not None:
                    charge = atom.charge
                    f.write(f"{i+1} {atom_type} {charge} {atom.position[0]} {atom.position[1]} {atom.position[2]}\n")
                else:
                    f.write(f"{i+1} {atom_type} {atom.position[0]} {atom.position[1]} {atom.position[2]}\n")

        print(f"Converted {input_file} to LAMMPS data format: {output_file}")
        return output_file
    except Exception as e:
        print(f"Error converting file: {e}")
        return None