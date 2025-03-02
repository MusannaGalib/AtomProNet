from ase.io import read
import numpy as np
import os

def convert_to_lammps_data(input_file, output_file, charges=None):
    try:
        # Read the input file using ASE
        atoms = read(input_file)

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
            f.write(f"{len(set(atoms.get_chemical_symbols()))} atom types\n\n")

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
                # Assign atom types based on element (1 for the first element, 2 for the second, etc.)
                atom_type = list(set(atoms.get_chemical_symbols())).index(atom.symbol) + 1
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
