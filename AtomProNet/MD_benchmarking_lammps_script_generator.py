import os
import textwrap

LAMMPS_MINIMIZATION_TEMPLATE = textwrap.dedent("""
##-----------INITIALIZATION---------- ##
units           {units}
atom_style      {atom_style}
boundary        p p p
atom_modify     map yes
newton          on
read_data       {unit_cell_path}
replicate       {repetition} {repetition} {repetition}

##-----------MASS INFORMATION---------- ##
{mass_commands}

##-----------INTERATOMIC POTENTIAL---------- ##
pair_style      {pair_style}
pair_coeff      * * {potential_path} {elements}
neighbor        2.0 bin
neigh_modify    delay 10 check yes

## ----------ENERGY/FORCE MINIMIZATION---------- ##
{fix_min}
min_modify      dmax 0.01
minimize        1e-25 1e-25 5000 10000

## ----------DUMP DATA FILE---------- ##
write_data      {output_file}
""")

LAMMPS_NPT_RELAXATION_TEMPLATE = textwrap.dedent("""
##-----------INITIALIZATION---------- ##
units           {units}
atom_style      {atom_style}
boundary        p p p
atom_modify     map yes
newton          on
read_data       {input_data_file}

##-----------MASS INFORMATION---------- ##
{mass_commands}

##-----------INTERATOMIC POTENTIAL---------- ##
pair_style      {pair_style}
pair_coeff      * * {potential_path} {elements}
neighbor        2.0 bin
neigh_modify    delay 10 check yes

##-----------THERMO SETTINGS---------- ##
thermo          1
thermo_style    custom step lx ly lz press pxx pyy pzz pe temp
timestep        {timestep}

##-----------NPT RELAXATION---------- ##
{fix_npt}

##-----------OUTPUT TO FILE---------- ##
variable        time equal time
fix             comp_perf all ave/time 1 1 1 v_time file {output_file}

run             100000000
""")

POTENTIAL_SETTINGS = {
    "allegro": {
        "units": "metal",
        "atom_style": "atomic",
        "pair_style": "allegro",
        "fix_min": "fix 1 all box/relax iso 0.0 vmax 0.001",
        "fix_npt": "fix 1 all npt temp 300.0 300.0 0.001 iso 0 0 0.01",
        "timestep": "0.0001",
    },
    "mace": {
        "units": "metal",
        "atom_style": "atomic",
        "pair_style": "mace no_domain_decomposition",
        "fix_min": "fix 1 all box/relax iso 0.0 vmax 0.001",
        "fix_npt": "fix 1 all npt temp 300.0 300.0 0.001 iso 0 0 0.01",
        "timestep": "0.0001",
    },
    "comb3": {
        "units": "metal",
        "atom_style": "charge",
        "pair_style": "comb3 polar_off",
        "fix_min": "fix 1 all nvt temp 300.0 300.0 0.1\nrun 1\nfix 2 all qeq/comb 1 0.0001 file fq.out\nrun 5\nunfix 1\nfix 3 all box/relax aniso 0.0 vmax 0.001",
        "fix_npt": "fix 1 all npt temp 300.0 300.0 0.001 iso 0 0 0.01\nfix 2 all qeq/comb 1 0.0001 file fq.out",
        "timestep": "0.0001",
    },
    "reaxff": {
        "units": "real",
        "atom_style": "charge",
        "pair_style": "reaxff NULL",
        "fix_min": "fix 1 all box/relax iso 0.0 vmax 0.001\nfix 2 all qeq/reaxff 1 0.0 10.0 0.0001 reaxff",
        "fix_npt": "fix 1 all npt temp 300.0 300.0 1 iso 0 0 10\nfix 2 all qeq/reaxff 1 0.0 10.0 0.0001 reaxff",
        "timestep": "0.1",
    },
}

def generate_minimization_script(folder_name, potential, unit_cell_path, repetition, elements, masses, potential_path, allegro_precision=None):
    script_path = os.path.join(folder_name, "in.minimization")
    
    # Get potential-specific settings
    settings = POTENTIAL_SETTINGS.get(potential)
    if not settings:
        raise ValueError(f"Unsupported potential: {potential}")
    
    # Prepare the output file name
    output_file = f"{potential}_min_{repetition}x{repetition}x{repetition}.data"
    
    # Update pair_style for Allegro based on precision
    if potential == "allegro" and allegro_precision:
        settings["pair_style"] = f"allegro{allegro_precision}{allegro_precision}"
    
    # Generate mass commands
    mass_commands = "\n".join([f"mass {i+1} {masses[element]}" for i, element in enumerate(elements)])
    
    # Fill the template with the appropriate values
    script_content = LAMMPS_MINIMIZATION_TEMPLATE.format(
        units=settings["units"],
        atom_style=settings["atom_style"],
        unit_cell_path=unit_cell_path,
        repetition=repetition,
        pair_style=settings["pair_style"],
        potential_path=potential_path,
        elements=" ".join(elements),
        fix_min=settings["fix_min"],
        output_file=output_file,
        mass_commands=mass_commands,
    )
    
    # Write the script to the file
    with open(script_path, "w") as f:
        f.write(script_content)
    
    print(f"Created LAMMPS minimization script: {script_path}")

def generate_npt_relaxation_script(folder_name, potential, repetition, elements, masses, potential_path, allegro_precision=None):
    script_path = os.path.join(folder_name, "in.npt_relaxation")
    
    # Get potential-specific settings
    settings = POTENTIAL_SETTINGS.get(potential)
    if not settings:
        raise ValueError(f"Unsupported potential: {potential}")
    
    # Prepare the input data file name (from minimization output)
    input_data_file = f"{potential}_min_{repetition}x{repetition}x{repetition}.data"
    
    # Prepare the output file name
    output_file = f"{potential}_comp_perf_{repetition}x{repetition}x{repetition}.txt"
    
    # Update pair_style for Allegro based on precision
    if potential == "allegro" and allegro_precision:
        settings["pair_style"] = f"allegro{allegro_precision}{allegro_precision}"
    
    # Generate mass commands
    mass_commands = "\n".join([f"mass {i+1} {masses[element]}" for i, element in enumerate(elements)])
    
    # Fill the template with the appropriate values
    script_content = LAMMPS_NPT_RELAXATION_TEMPLATE.format(
        units=settings["units"],
        atom_style=settings["atom_style"],
        input_data_file=input_data_file,
        pair_style=settings["pair_style"],
        potential_path=potential_path,
        elements=" ".join(elements),
        timestep=settings["timestep"],
        fix_npt=settings["fix_npt"],
        output_file=output_file,
        mass_commands=mass_commands,  # Add mass commands
    )
    
    # Write the script to the file
    with open(script_path, "w") as f:
        f.write(script_content)
    
    print(f"Created LAMMPS NPT relaxation script: {script_path}")
