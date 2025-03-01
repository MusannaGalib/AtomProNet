import os
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import glob

# Define the time units for each LAMMPS units setting
LAMMPS_UNITS_TO_TIME = {
    "metal": "ps",  # metal units use picoseconds (ps)
    "real": "fs",   # real units use femtoseconds (fs)
}

def extract_last_time_from_file(file_path):
    """
    Extracts the last recorded time from the NPT relaxation output file.

    Args:
        file_path (str): Path to the output file.

    Returns:
        float: The last recorded time, or None if the file is empty or the format is invalid.
    """
    try:
        with open(file_path, "r") as f:
            lines = f.readlines()
            
            # Check if the file is empty
            if not lines:
                print(f"Warning: File {file_path} is empty.")
                return None

            # Get the last non-empty line
            last_line = None
            for line in reversed(lines):
                if line.strip():  # Skip empty lines
                    last_line = line.strip()
                    break

            if not last_line:
                print(f"Warning: No valid data found in {file_path}.")
                return None

            # Split the last line into columns
            columns = last_line.split()
            if len(columns) < 2:
                print(f"Warning: Invalid format in {file_path}. Expected at least 2 columns, found {len(columns)}.")
                return None

            # Extract the time (second column)
            try:
                last_time = float(columns[1])  # Time is the second column
                return last_time
            except ValueError:
                print(f"Warning: Could not convert time value to float in {file_path}.")
                return None

    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return None

def get_lammps_units(folder_name, potential):
    """
    Extracts the LAMMPS units setting from the input script.

    Args:
        folder_name (str): Path to the folder containing the LAMMPS input script.
        potential (str): The interatomic potential (e.g., "allegro", "mace", "reaxff").

    Returns:
        str: The LAMMPS units setting (e.g., "metal", "real").
    """
    input_script = os.path.join(folder_name, f"in.npt_relaxation")
    try:
        with open(input_script, "r") as f:
            for line in f:
                if line.strip().startswith("units"):
                    return line.strip().split()[1]  # Extract the units setting
        print(f"Warning: Could not find 'units' setting in {input_script}. Defaulting to 'metal'.")
        return "metal"  # Default to metal units if not found
    except Exception as e:
        print(f"Error reading LAMMPS input script: {e}")
        return "metal"  # Default to metal units if there's an errors

def get_ntasks_from_script(folder_name):
    """
    Extracts the ntasks value from the NPT relaxation job submission script.
    """
    script_path = os.path.join(folder_name, "lammps_*_npt_relaxation_jobsub.sh")
    script_files = glob.glob(script_path)
    if not script_files:
        print(f"Warning: No NPT relaxation job submission script found in {folder_name}.")
        return None

    with open(script_files[0], "r") as f:
        for line in f:
            if line.strip().startswith("#SBATCH --ntasks="):
                return int(line.strip().split("=")[1])
    return None

def plot_npt_performance(main_dir, potentials, repetitions):
    """
    Plots the last recorded time for NPT relaxation for all selected potentials.
    """
    # Set Seaborn style for better aesthetics
    sns.set(style="whitegrid", palette="deep", font_scale=1.2)
    plt.figure(figsize=(10, 6))  # Adjust figure size if needed

    # Get the universal ntasks value from the first NPT script
    first_potential_dir = os.path.join(main_dir, potentials[0].upper(), repetitions[0])
    ntasks = get_ntasks_from_script(first_potential_dir)
    if ntasks is None:
        print("Warning: Could not determine ntasks value. Using default title.")
        plt.title("Computational Performance (Log-Log Plot)")
    else:
        plt.title(f"Computational Performance (Log-Log Plot) - CPUs={ntasks}")

    plt.xlabel(r"Number of unit cell repetitions ($\gamma$)")
    plt.ylabel("Simulation time per computational time (ps/hr)")

    has_data = False  # Flag to check if any data is found

    # Process MACE last
    if "mace" in potentials:
        potentials.remove("mace")
        potentials.append("mace")  # Move MACE to the end of the list

    # Store equations for later placement
    equations = []

    for potential in potentials:
        times = []
        valid_repetitions = []

        for rep in repetitions:
            # Extract the numerical value from the repetition string (e.g., "1x1x1" → 1)
            rep_value = int(rep.split('x')[0])  # Split on 'x' and take the first part

            folder_name = os.path.join(main_dir, potential.upper(), f"{rep}")
            output_file = os.path.join(folder_name, f"{potential}_comp_perf_{rep}.txt")
            
            if not os.path.exists(output_file):
                print(f"Warning: Output file not found for {potential} at {rep}.")
                continue

            last_time = extract_last_time_from_file(output_file)
            if last_time is not None:
                # Get the LAMMPS units setting
                lammps_units = get_lammps_units(folder_name, potential)
                # Convert time to ps if necessary
                if LAMMPS_UNITS_TO_TIME.get(lammps_units, "ps") == "fs":
                    last_time /= 1000  # Convert fs to ps
                times.append(last_time)
                valid_repetitions.append(rep_value)  # Use the numerical value
            else:
                print(f"Warning: No valid time found for {potential} at {rep}.")

        # Debugging: Check if times is empty
        if not times:
            print(f"Warning: No data found for {potential}. Skipping plot.")
            continue

        # Plot the data for this potential using log-log (only markers, no lines)
        has_data = True
        # Plot the markers and store the plot object to retrieve the color
        marker_plot = plt.loglog(valid_repetitions, times, marker='o', linestyle='', label=potential.upper())
        color = marker_plot[0].get_color()  # Get the color of the markers

        # Fit a linear line to the log-log data (if at least 2 points are available)
        if len(times) >= 2:
            log_reps = np.log10(valid_repetitions)
            log_times = np.log10(times)
            coefficients = np.polyfit(log_reps, log_times, 1)  # Linear fit (degree 1)
            slope, intercept = coefficients

            # Generate the fitted line
            fitted_log_times = slope * log_reps + intercept
            plt.plot(valid_repetitions, 10**fitted_log_times, '--', color=color)  # Use the same color as markers

            # Store the equation for later placement
            equation = f"$\\log_{{10}}(t^{{\\mathrm{{{potential.upper()}}}}}) = {slope:.2f} \\cdot \\log_{{10}}(\\gamma) + {intercept:.2f}$"
            equations.append(equation)
        else:
            # Print a message if there are insufficient data points for fitting
            print(f"Warning: Insufficient data points for {potential}. At least 2 points are required for fitting.")

    if not has_data:
        print("Error: No performance data found for any potential or repetition.")
        return

    # Set the x-axis range dynamically based on the min and max of the repetitions
    if repetitions:
        rep_values = [int(rep.split('x')[0]) for rep in repetitions]  # Convert repetitions to integers
        x_min = min(rep_values)
        x_max = max(rep_values)
        
        # Extend x_max to 100% of x_max + x_max (i.e., 2 * x_max)
        x_max_extended = 2 * x_max  # Set x_max_extended to twice the value of x_max
        plt.xlim(x_min, x_max_extended)  # Set x-axis range dynamically

        # Control the number of x-axis ticks
        if x_max_extended - x_min > 10:  # If the range is large, space out the ticks
            tick_step = max(1, (x_max_extended - x_min) // 10)  # Ensure at least 1 tick per step
            plt.xticks(range(x_min, x_max_extended + 1, tick_step))  # Set ticks with spacing
        else:
            plt.xticks(range(x_min, x_max_extended + 1))  # Use all ticks for small ranges

    # Add legend (only markers, no fitted lines)
    legend = plt.legend(title="Interatomic Potential", bbox_to_anchor=(1.05, 1), loc='upper left')

    # Position the equations inside the plot area with proper vertical spacing
    if equations:
        # Calculate the starting y-position for the equations (inside the plot area)
        y_start = 0.5  # Start near the top of the plot
        vertical_spacing = 0.08  # Adjust this value to control the spacing between equations

        for i, equation in enumerate(equations):
            # Place each equation below the previous one with vertical spacing
            plt.text(1.02, y_start - i * vertical_spacing, equation, transform=plt.gca().transAxes, fontsize=10,
                     verticalalignment='top', bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.5'))

    # Add grid
    plt.grid(True, which="both", ls="--")

    # Save and show the plot
    plt.tight_layout()  # Adjust layout to prevent overlap
    plot_path = os.path.join(main_dir, "computational_performance_plot.png")
    plt.savefig(plot_path, dpi=300, bbox_inches="tight")
    plt.show()

    print(f"Performance plot saved to {plot_path}")
