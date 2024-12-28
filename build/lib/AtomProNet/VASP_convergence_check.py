#module load  intel-oneapi-compilers/2023.1.0
#module load python/3.11.6
#module load gcc/5.5.0  openblas/0.3.15
#module load  py-numpy/1.20.3
#module load py-matplotlib/3.4.2


import os
import re
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from matplotlib.ticker import MaxNLocator

# Ask for the directory path where the OUTCAR file is located
directory_path = input("Please provide the directory where the OUTCAR file is located: ").strip()

# Construct the full path to the OUTCAR file
outcar_file = os.path.join(directory_path, "OUTCAR")


# Define output file paths in the same directory as OUTCAR
output_dir = os.path.dirname(outcar_file)
position_file = os.path.join(output_dir, "position_total_force.txt")
stress_file = os.path.join(output_dir, "stress.txt")
energy_file = os.path.join(output_dir, "energy_ionic_step.txt")

# Function to extract data from OUTCAR
def extract_data(pattern, outcar_file, output_file, skip_lines=None, end_pattern="total drift"):
    with open(outcar_file, "r") as file, open(output_file, "w") as out:
        capture = False
        for line in file:
            if re.search(pattern, line):
                capture = True
                if skip_lines:
                    [next(file) for _ in range(skip_lines)]
            if capture:
                out.write(line)
                if re.search(end_pattern, line) or line.strip() == "":
                    capture = False

# Extract relevant data from OUTCAR
extract_data(r"POSITION", outcar_file, position_file, skip_lines=1)
extract_data(r"in kB", outcar_file, stress_file)


def extract_energy_data(outcar_file, output_file, energy_pattern, next_line_condition):
    with open(outcar_file, "r") as file, open(output_file, "w") as out:
        lines = file.readlines()
        
        for i, line in enumerate(lines):
            if re.search(energy_pattern, line):
                # Check within the next few lines for the dashes and the condition
                for j in range(i + 1, min(i + 10, len(lines))):
                    if re.search(r"^-{20,}", lines[j]):
                        for k in range(j + 1, min(j + 10, len(lines))):
                            if re.search(next_line_condition, lines[k]):
                                out.write(line)
                                break
                        break

# Extract energy without entropy data with the specified condition
extract_energy_data(outcar_file, energy_file, 
                    energy_pattern=r"energy without entropy", 
                    next_line_condition=r"average \(electrostatic\) potential at core")


# Load extracted data using np.loadtxt
try:
    with open(position_file, "r") as f:
        lines = f.readlines()
except Exception as e:
    print(f"Error loading data: {e}. Please check the file paths.")
    exit()

# Process the position_total_force.txt file
rms_forces_per_step = []
step_count = 0

positions = []
forces = []

# Loop through the lines and extract positions and forces
for line in lines:
    if "POSITION" in line:
        if forces:  # If there's data collected, process the previous step
            forces_array = np.array(forces)
            rms_forces = np.sqrt(np.sum(forces_array ** 2, axis=1))  # RMS force for each atom
            mean_rms_force = np.mean(rms_forces)  # Mean RMS force for the step
            rms_forces_per_step.append(mean_rms_force)
            forces = []  # Reset for the next step
        step_count += 1  # Increment ionic relaxation step count
    elif "total drift" in line:
        continue
    else:
        data = line.split()
        if len(data) == 6:
            force = [float(data[3]), float(data[4]), float(data[5])]
            forces.append(force)

# Process the final step
if forces:
    forces_array = np.array(forces)
    rms_forces = np.sqrt(np.sum(forces_array ** 2, axis=1))
    mean_rms_force = np.mean(rms_forces)
    rms_forces_per_step.append(mean_rms_force)

# Plot Mean RMS Force vs Ionic Relaxation Step
plt.figure(figsize=(7, 5))
plt.plot(range(1, step_count + 1), rms_forces_per_step, '#FF8C00', label='Mean RMS Force')
plt.grid(False)
plt.xlabel('Ionic Relaxation Step', fontsize=14, fontweight='normal')
plt.ylabel('Mean RMS Force (eV/Å)', fontsize=14, fontweight='normal')
plt.legend(loc='upper right',fontsize=14, borderaxespad=0., frameon=False)
plt.gca().tick_params(axis='both', which='major', labelsize=14)
# Dynamically determine the x-axis ticks
plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True, nbins=10))  # Show up to 10 evenly spaced ticks


# Add inset showing the last 10 ionic steps
if step_count >= 10:
    ax_inset = inset_axes(plt.gca(), width="30%", height="30%", loc='center right')
    inset_x = range(step_count - 9, step_count + 1)
    inset_y = rms_forces_per_step[-10:]
    ax_inset.plot(inset_x, inset_y, '#800080', label='Last 10 Steps')
    ax_inset.set_title('', fontsize=10)
    ax_inset.tick_params(axis='both', which='major', labelsize=10)
    ax_inset.grid(False)  # No grid lines in the inset
    

# Save the plot with 1200 dpi resolution
output_plot_path = os.path.join(output_dir, "mean_rms_force_plot.png")
plt.savefig(output_plot_path, dpi=1200, bbox_inches='tight')

print(f"Plot saved at: {output_plot_path}")





# Step 1: Count number of atoms from position_total_force.txt
def count_atoms(position_file):
    with open(position_file, "r") as f:
        lines = f.readlines()
        atom_count = 0
        counting = False
        for line in lines:
            if "POSITION" in line:
                counting = True
                atom_count = 0
            elif "total drift" in line:
                if counting:
                    return atom_count
            elif counting:
                if len(line.split()) == 6:
                    atom_count += 1
    return atom_count

num_atoms = count_atoms(position_file)
print(f"Number of atoms: {num_atoms}")

# Step 2: Extract energies from energy_ionic_step.txt and compute log10(ΔE)
def compute_log_delta_e(energy_file, num_atoms):
    energies = []
    with open(energy_file, "r") as f:
        for line in f:
            match = re.search(r"energy without entropy\s*=\s*([-\d.]+)", line)
            if match:
                energies.append(float(match.group(1)))
    
    delta_es = [abs(energies[i] - energies[i - 1]) / num_atoms for i in range(1, len(energies))]
    log_delta_es = np.log10([de if de > 0 else 1e-10 for de in delta_es])  # Add small offset to zero values

        
    return log_delta_es

log_delta_es = compute_log_delta_e(energy_file, num_atoms)

# Step 3: Extract external pressures from stress.txt
def extract_pressures(stress_file):
    pressures = []
    with open(stress_file, "r") as f:
        for line in f:
            match = re.search(r"external pressure\s*=\s*([-\d.]+)", line)
            if match:
                pressures.append(float(match.group(1)))
    return pressures

pressures = extract_pressures(stress_file)

# Ensure the lengths of pressures and log_delta_es match
num_steps = min(len(pressures), len(log_delta_es))
pressures = pressures[:num_steps]
log_delta_es = log_delta_es[:num_steps]
steps = list(range(1, num_steps + 1))

# Plot External Pressure and log10(ΔE) on dual Y-axes
fig, ax1 = plt.subplots(figsize=(7, 5))

# Plot External Pressure (Left Y-Axis)
ax1.plot(steps, pressures, color='#FF8C00', label='External Pressure (kB)')
ax1.set_xlabel('Ionic Relaxation Step', fontsize=14, fontweight='normal')
ax1.set_ylabel('External Pressure (kB)', color='#FF8C00', fontsize=14, fontweight='normal')
ax1.tick_params(axis='y', labelcolor='#FF8C00')
# Change the left and right spines color to deep orange
ax1.grid(False)


# Plot log10(ΔE) (Right Y-Axis)
ax2 = ax1.twinx()
ax2.plot(steps, log_delta_es, color='#800080', label='$\log_{10}(\Delta E) \, (\mathrm{eV/atom})$')
ax2.set_ylabel(r'$\log_{10}(\Delta E) \, (\mathrm{eV/atom})$', color='#800080', fontsize=14, fontweight='normal')
ax2.tick_params(axis='y', labelcolor='#800080')

# Dynamically determine the x-axis ticks
ax1.xaxis.set_major_locator(MaxNLocator(integer=True, nbins=10))  # Show up to 10 evenly spaced ticks


# Set the left spine color and tick color for ax1
ax1.spines['left'].set_color('#FF8C00')
ax1.spines['left'].set_linewidth(1)
ax1.tick_params(axis='y', color='#FF8C00', labelcolor='#FF8C00')

# Set the right spine color and tick color for ax2
ax2.spines['right'].set_color('#800080')
ax2.spines['right'].set_linewidth(1)
ax2.tick_params(axis='y', color='#800080', labelcolor='#800080')

# Remove the left spine of ax2 to prevent overlap
ax2.spines['left'].set_visible(False)

# Set the top and bottom spines for ax1
ax1.spines['top'].set_color('black')
ax1.spines['top'].set_linewidth(1)
ax1.spines['bottom'].set_color('black')
ax1.spines['bottom'].set_linewidth(1)



# Title and Legend
fig.legend(loc='upper right', fontsize=12, bbox_to_anchor=(0.90, 0.88), borderaxespad=0., frameon=False)

# Save the plot with 1200 dpi resolution
output_plot_path = os.path.join(output_dir, "pressure_energy_plot.png")
plt.savefig(output_plot_path, dpi=1200, bbox_inches='tight')

print(f"Plot saved at: {output_plot_path}")

