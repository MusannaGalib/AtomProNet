import os
from mp_api.client import MPRester
from pymatgen.core.structure import Structure
from pymatgen.core.lattice import Lattice

def construct_poscar_from_structure(structure, input_folder, filename="POSCAR"):
    # Construct the path to the VASP_files directory within the input folder
    directory = os.path.join(input_folder, "VASP_files")
    
    # Ensure the directory exists
    if not os.path.exists(directory):
        os.makedirs(directory)
        
    # Full file path to save the POSCAR file
    filepath = os.path.join(directory, filename)
    print(f"Saving POSCAR file to: {filepath}")  # Debugging statement
    
    # Constructs a POSCAR file from a given structure object
    with open(filepath, 'w') as f:
        f.write("Generated using mp-api\n")
        f.write("1.0\n")
        for vec in structure.lattice.matrix:
            f.write(f"{' '.join(map(str, vec))}\n")
        species = [site.specie.symbol for site in structure.sites]
        unique_species = sorted(set(species), key=species.index)
        f.write(" ".join(unique_species) + "\n")
        f.write(" ".join([str(species.count(s)) for s in unique_species]) + "\n")
        f.write("Direct\n")
        for site in structure.sites:
            f.write(f"{' '.join(map(str, site.frac_coords))}\n")

def create_supercell(structure, supercell_size):
    pymatgen_structure = Structure(
        lattice=Lattice(structure.lattice.matrix),
        species=[site.specie for site in structure.sites],
        coords=[site.frac_coords for site in structure.sites],
        coords_are_cartesian=False
    )
    supercell = pymatgen_structure.make_supercell(supercell_size)
    return supercell




def fetch_and_write_poscar(api_key, query, input_folder, create_supercell_option, supercell_size=None):

    print(f"Called with: api_key={api_key}, query={query}, input_folder={input_folder}, create_supercell_option={create_supercell_option}, supercell_size={supercell_size}")    
  
    with MPRester(api_key) as mpr:
        if query.startswith("mp-"):
            # Querying by material ID
            material_id = query
            structure = mpr.get_structure_by_material_id(material_id)
            if structure:
                print(f"Structure for material ID {material_id} fetched successfully.")
                construct_poscar_from_structure(structure, input_folder, f"{material_id}_POSCAR")
                print(f"POSCAR file for {material_id} has been generated.")
                
                # Create supercell if option is enabled
                if create_supercell_option and supercell_size:
                    supercell = create_supercell(structure, supercell_size)
                    supercell_filename = f"{material_id}_supercell_POSCAR"
                    construct_poscar_from_structure(supercell, input_folder, supercell_filename)
                    print(f"Supercell POSCAR file for {material_id} has been generated and saved as {supercell_filename}.")
        
        elif "," in query:
            # Querying by a comma-separated list of elements
            elements = [elem.strip().capitalize() for elem in query.split(',')]
            try:
                summaries = mpr.materials.summary.search(elements=elements)
                for summary in summaries:
                    material_id = summary.material_id
                    structure = mpr.get_structure_by_material_id(material_id)
                    if structure:
                        construct_poscar_from_structure(structure, input_folder, f"{material_id}_POSCAR")
                        print(f"POSCAR file for {material_id} has been generated.")
                        
                        # Create supercell if option is enabled
                        if create_supercell_option and supercell_size:
                            supercell = create_supercell(structure, supercell_size)
                            supercell_filename = f"{material_id}_supercell_POSCAR"
                            construct_poscar_from_structure(supercell, input_folder, supercell_filename)
                            print(f"Supercell POSCAR file for {material_id} has been generated and saved as {supercell_filename}.")
            except Exception as e:
                print(f"Error during bulk search: {e}")
        
        else:
            # Querying by compound formula
            formula = query
            try:
                summaries = mpr.materials.summary.search(formula=formula)
                for summary in summaries:
                    material_id = summary.material_id
                    structure = mpr.get_structure_by_material_id(material_id)
                    if structure:
                        construct_poscar_from_structure(structure, input_folder, f"{material_id}_POSCAR")
                        print(f"POSCAR file for {material_id} has been generated.")
                        
                        # Create supercell if option is enabled
                        if create_supercell_option and supercell_size:
                            supercell = create_supercell(structure, supercell_size)
                            supercell_filename = f"{material_id}_supercell_POSCAR"
                            construct_poscar_from_structure(supercell, input_folder, supercell_filename)
                            print(f"Supercell POSCAR file for {material_id} has been generated and saved as {supercell_filename}.")
            except Exception as e:
                print(f"Error during formula-based search: {e}")

if __name__ == "__main__":
    input_folder = input("Please enter the full path to the folder where the operations should be performed: ").strip()
    default_api_key = "H5zmHxuvPs9LKyABNRQmUsj0ROBYs5C4"
    user_api_key = input("Enter your Materials Project API key (press Enter to use default): ")
    api_key = user_api_key if user_api_key.strip() != "" else default_api_key
    query = input("Enter the material ID (e.g., mp-1234), compound formula (e.g., Al2O3), or elements (e.g., Li, O, Mn) for bulk download: ")
    
    # Ask once if supercells should be created for all structures
    create_supercell_option = input("Do you want to create supercells for all structures? (yes/no): ").lower() == 'yes'
    supercell_size = None
    if create_supercell_option:
        sizes = input("Enter the supercell size (e.g., 2 2 2): ")
        supercell_size = [int(x) for x in sizes.split()]
    
    # Call the function
    if create_supercell_option:
        fetch_and_write_poscar(api_key, query, input_folder, create_supercell_option, supercell_size)
    else:
        fetch_and_write_poscar(api_key, query, input_folder, create_supercell_option)