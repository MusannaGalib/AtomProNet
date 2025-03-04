import os
import numpy as np
import matplotlib.pyplot as plt
import ase.io
import statsmodels.api as sm
import seaborn as sns
from scipy.stats import norm
from sklearn.metrics import r2_score
from sklearn.metrics import mean_absolute_error, mean_squared_error

# Checks if a file exists at the given path
def check_file_exists(file_path):
    return os.path.isfile(file_path)

# Gets the file path from the user if the file does not exist at the given path
def get_file_path(filename, prompt_message):
    file_path = filename
    if not check_file_exists(file_path):
        file_path = input(prompt_message)
        if not check_file_exists(file_path):
            raise FileNotFoundError(f"File {filename} not found.")
    return file_path

# Reads datasets from a file using ASE, supporting the 'extxyz' format
def read_datasets(file_path):
    datasets = []
    for frame in ase.io.iread(file_path, format='extxyz'):
        datasets.append(frame)
    return datasets

# Extracts a specific dataset from a list based on its index
def extract_dataset(original_datasets, index):
    if 0 <= index < len(original_datasets):
        return original_datasets[index]
    else:
        raise IndexError("Index out of range.")

    

# Plots parity between true and predicted values and optionally saves the data to files
def plot_parity(true_values, predicted_values, title, xlabel, ylabel, folder_path, data_save=True, save=True, confidence_level=0.95):
    # Create a 'plots' directory inside the user-defined folder path
    save_dir = os.path.join(folder_path, "plots")
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # Set up the figure layout
    fig = plt.figure(figsize=(6, 6), dpi=1200)
    grid = plt.GridSpec(4, 4, hspace=0, wspace=0)

    # Main parity plot
    ax_main = fig.add_subplot(grid[1:, :-1])
    ax_main.scatter(true_values, predicted_values, alpha=0.7, color='black', s=10)
    
    # Ensure the 45-degree line starts from (0, 0)
    min_val = min(min(true_values), min(predicted_values), 0)  # Include 0 in the minimum
    max_val = max(max(true_values), max(predicted_values))  # Find the max value in data

    
    # Plot the parity line
    ax_main.plot([min_val, max_val], [min_val, max_val], color="red", linestyle="--")

    # Calculate metrics
    r_squared = r2_score(true_values, predicted_values)
    mae = mean_absolute_error(true_values, predicted_values)
    rmse = np.sqrt(mean_squared_error(true_values, predicted_values))

    # Add metrics as text
    metrics_text = f"$R^2$ = {r_squared:.2f}\nMAE = {mae:.2f}\nRMSE = {rmse:.2f}"
    ax_main.text(0.05, 0.95, metrics_text, transform=ax_main.transAxes, fontsize=14, verticalalignment='top')

    ax_main.set_xlabel(xlabel, fontsize=16)
    ax_main.set_ylabel(ylabel, fontsize=16)

    # Set axis limits to include 0
    ax_main.set_xlim(min_val, max_val)
    ax_main.set_ylim(min_val, max_val)
    ax_main.tick_params(labelsize=12)

    if save:
        figure_save_path = os.path.join(save_dir, f"{title.replace(' ', '_')}.png")
        plt.savefig(figure_save_path, bbox_inches='tight')
        print(f"Figure saved to {figure_save_path}")
    plt.close()

    if data_save:
        true_values_path = os.path.join(save_dir, f"{title.replace(' ', '_')}_true_values.txt")
        predicted_values_path = os.path.join(save_dir, f"{title.replace(' ', '_')}_predicted_values.txt")
        np.savetxt(true_values_path, true_values, header='True Values', comments='')
        np.savetxt(predicted_values_path, predicted_values, header='Predicted Values', comments='')
        print(f"Data saved to {true_values_path} and {predicted_values_path}")


# Calculates the RMS of forces in each row
def calculate_rms_forces(forces):
    rms_forces = [np.sqrt(np.mean(f**2, axis=1)) for f in forces]
    return rms_forces

# Compares RMS forces between extracted and test datasets, plots the comparison, and saves the RMS force data
def compare_rms_forces(extracted_forces, test_forces, title, folder_path, save=True, data_save=True):
    save_dir = os.path.join(folder_path, "plots")
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # Calculate RMS forces
    rms_extracted = calculate_rms_forces(extracted_forces)
    rms_test = calculate_rms_forces(test_forces)

    # Debug lines to show the first RMS calculation for both true and trial
    print("Debug: First row of forces for extracted forces:")
    print(extracted_forces[0][0])  # Print the first row of forces from the first dataset
    print(f"RMS value for the first row of extracted forces: {rms_extracted[0][0]}")  # Print the RMS value for the first row

    print("Debug: First row of forces for test forces:")
    print(test_forces[0][0])  # Print the first row of forces from the first dataset
    print(f"RMS value for the first row of test forces: {rms_test[0][0]}")  # Print the RMS value for the first row

    # Concatenating RMS values
    true_rms_forces = np.concatenate(rms_extracted, axis=0)
    predicted_rms_forces = np.concatenate(rms_test, axis=0)

    plt.figure(figsize=(5, 4), dpi=1200)
    plt.scatter(true_rms_forces, predicted_rms_forces, alpha=0.7, color='black', s=10)
    
    # Compute unified axis limits similar to plot_parity
    min_val = min(true_rms_forces.min(), predicted_rms_forces.min(), 0)
    max_val = max(true_rms_forces.max(), predicted_rms_forces.max())
    plt.plot([min_val, max_val], [min_val, max_val], color='red')
    
    # Confidence interval calculation and plotting
    mean_true = np.mean(true_rms_forces)
    std_true = np.std(true_rms_forces)
    ci = 1.95 * std_true  # 80% confidence interval
    #plt.fill_between([true_rms_forces.min(), true_rms_forces.max()], [true_rms_forces.min() - ci, true_rms_forces.max() - ci], [true_rms_forces.min() + ci, true_rms_forces.max() + ci], color='lightblue', alpha=0.4)

    # Calculate metrics
    r_squared = r2_score(true_rms_forces, predicted_rms_forces)
    mae = mean_absolute_error(true_rms_forces, predicted_rms_forces)
    rmse = np.sqrt(mean_squared_error(true_rms_forces, predicted_rms_forces))

    # Add metrics as text
    metrics_text = f"$R^2$ = {r_squared:.3f}\nMAE = {mae:.3f}\nRMSE = {rmse:.3f}"
    plt.text(0.05, 0.85, metrics_text, ha='left', va='center', transform=plt.gca().transAxes, fontsize=14)

    plt.xlabel('True RMS Forces (eV/$\AA$)', fontsize=16)
    plt.ylabel('Predicted RMS Forces (eV/$\AA$)', fontsize=16)
    #plt.title(title, fontsize=14)
    
    # Set range limits for both axes using unified limits
    plt.xlim(min_val, max_val)
    plt.ylim(min_val, max_val)

    # Set aspect ratio
    plt.gca().set_aspect('auto')

    # Increase x and y tick label font size
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)

    plt.tight_layout()

    if save:
        figure_save_path = os.path.join(save_dir, f"{title.replace(' ', '_')}_rms_forces.png")
        plt.savefig(figure_save_path, bbox_inches='tight')
        print(f"Figure saved to {figure_save_path}")
    plt.close()
    if data_save:
        true_rms_forces_path = os.path.join(save_dir, f"{title.replace(' ', '_')}_true_rms_forces.txt")
        predicted_rms_forces_path = os.path.join(save_dir, f"{title.replace(' ', '_')}_predicted_rms_forces.txt")
        np.savetxt(true_rms_forces_path, true_rms_forces, header='True RMS Forces', comments='')
        np.savetxt(predicted_rms_forces_path, predicted_rms_forces, header='Predicted RMS Forces', comments='')
        print(f"RMS force data saved to {true_rms_forces_path} and {predicted_rms_forces_path}")








def plot_cumulative_distribution(true_values, predicted_values, folder_path, extracted_datasets, percentiles=[50, 80, 95], title='Cumulative Distribution of Energy Errors', save=False, data_save=False):
    """
    Plot the cumulative distribution of absolute errors between true values and predicted values.

    Parameters:
    - true_values: numpy array of true values
    - predicted_values: numpy array of predicted values
    - extracted_datasets: list of ASE Atoms objects representing datasets
    - percentiles: list of percentiles to annotate on the plot (default: [50, 80, 95])
    - title: title of the plot (default: 'Cumulative Distribution of Energy Errors')
    - save_dir: directory where the plot and data will be saved (default: 'plots')
    - save: boolean indicating whether to save the plot (default: False)
    - data_save: boolean indicating whether to save the data (default: False)
    """
    # Ensure the same number of datasets are used for atom_counts
    min_len = min(len(true_values), len(predicted_values), len(extracted_datasets))
    true_values = true_values[:min_len]
    predicted_values = predicted_values[:min_len]
    extracted_datasets = extracted_datasets[:min_len]

    # Extract atom counts for each dataset
    atom_counts = np.array([len(frame) for frame in extracted_datasets])

    # Calculate the absolute errors normalized by atom counts
    errors = np.abs(true_values - predicted_values) / atom_counts

    # Check if all errors are zero
    if np.all(errors == 0):
        print("\033[95mGood News! 0% error, no cumulative energy error plot needed!\033[0m")
        return

    # Sort the errors
    sorted_errors = np.sort(errors)

    # Compute the cumulative distribution
    cumulative = np.arange(1, len(sorted_errors) + 1) / len(sorted_errors) * 100

    # Find the error values at specified percentiles
    percentile_values = [np.percentile(sorted_errors, p) for p in percentiles]

    # Plot the cumulative distribution
    plt.figure(figsize=(5, 4), dpi=1200)
    plt.plot(sorted_errors, cumulative, color='orange', linewidth=2)

    # Add horizontal dashed lines for specified percentiles and markers at intersections
    for p, v in zip(percentiles, percentile_values):
        plt.axhline(
            y=p,
            xmin=0,
            xmax=(np.log10(v) - np.log10(sorted_errors.min())) / (np.log10(sorted_errors.max()) - np.log10(sorted_errors.min())),
            color='lightblue',
            linestyle='--',
        )
        plt.annotate(f'{v:.2f}', xy=(v, p), xytext=(v * 2.0, p), fontsize=12, ha='center',
                     bbox=dict(facecolor='none', edgecolor='none', boxstyle='round,pad=0.2'))
        plt.scatter([v], [p], color='lightblue', s=50, edgecolor='black', zorder=5)  # Circular marker

    # Set x and y scales
    plt.xscale('log')
    plt.yscale('linear')

    # Add labels and title
    plt.xlabel('Energy error (eV/ atom)', fontsize=16)
    plt.ylabel('Cumulative (%)', fontsize=16)
    # plt.title(title)

    # Increase x and y tick label font size
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)

    # Show the plot
    plt.tight_layout()

    # Set the x-axis limit to avoid overlapping with annotations
    plt.xlim(sorted_errors.min(), sorted_errors.max() * 3.0)  # Adjust multiplier as needed

    if save:
        save_dir = os.path.join(folder_path, "plots")
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        figure_save_path = os.path.join(save_dir, f"{title.replace(' ', '_')}.png")
        plt.savefig(figure_save_path, bbox_inches='tight')
        print(f"Figure saved to {figure_save_path}")
    plt.close()

    if data_save:
        true_values_path = os.path.join(save_dir, f"{title.replace(' ', '_')}_true_values.txt")
        predicted_values_path = os.path.join(save_dir, f"{title.replace(' ', '_')}_predicted_values.txt")
        atom_counts_path = os.path.join(save_dir, f"{title.replace(' ', '_')}_atom_counts.txt")

        np.savetxt(true_values_path, true_values, header='True Values', comments='')
        np.savetxt(predicted_values_path, predicted_values, header='Predicted Values', comments='')
        np.savetxt(atom_counts_path, atom_counts, header='Atom Counts', comments='')

        print(f"Data saved to {true_values_path}, {predicted_values_path}, and {atom_counts_path}")

    plt.show()





def flatten_list(nested_list):
    """
    Flatten a nested list to a 1D list.
    """
    if isinstance(nested_list[0], list) or isinstance(nested_list[0], np.ndarray):
        return [item for sublist in nested_list for item in sublist]
    return nested_list



def plot_cumulative_distribution_rms_forces(
    extracted_forces, test_forces, folder_path, percentiles=[50, 80, 95], title='Cumulative Distribution of Force Errors', save=False, data_save=False
):
    # Calculate RMS forces
    rms_extracted = calculate_rms_forces(extracted_forces)
    rms_test = calculate_rms_forces(test_forces)

    # Debug: Print the type and first few elements of the RMS forces
    print(f"rms_extracted type: {type(rms_extracted)}, first elements: {rms_extracted[:1]}")
    print(f"rms_test type: {type(rms_test)}, first elements: {rms_test[:1]}")

    # Flatten the lists if necessary
    rms_extracted = flatten_list(rms_extracted)
    rms_test = flatten_list(rms_test)

    # Convert lists to numpy arrays
    rms_extracted = np.array(rms_extracted, dtype=float)
    rms_test = np.array(rms_test, dtype=float)

    # Debug: Print the shapes and types after conversion
    print(f"rms_extracted shape: {rms_extracted.shape}, dtype: {rms_extracted.dtype}")
    print(f"rms_test shape: {rms_test.shape}, dtype: {rms_test.dtype}")

    # Calculate the absolute errors
    errors = np.abs(rms_extracted - rms_test)  # 80 atoms in the alumina

    # Check if all errors are zero
    if np.all(errors == 0):
        print("\033[95mGood News! 0% force error, no cumulative force error plot needed!\033[0m")
        return

    # Sort the errors
    sorted_errors = np.sort(errors)

    # Compute the cumulative distribution
    cumulative = np.arange(1, len(sorted_errors) + 1) / len(sorted_errors) * 100

    # Find the error values at specified percentiles
    percentile_values = [np.percentile(sorted_errors, p) for p in percentiles]

    # Plot the cumulative distribution
    plt.figure(figsize=(5, 4), dpi=1200)
    plt.plot(sorted_errors, cumulative, color='orange', linewidth=2)

    # Add horizontal dashed lines for specified percentiles and markers at intersections
    for p, v in zip(percentiles, percentile_values):
        plt.axhline(
            y=p,
            xmin=0,
            xmax=(np.log10(v) - np.log10(sorted_errors.min())) / (np.log10(sorted_errors.max()) - np.log10(sorted_errors.min())),
            color='lightblue',
            linestyle='--',
        )
        plt.annotate(f'{v:.3f}', xy=(v, p), xytext=(v * 2.8, p), fontsize=12, ha='center',
                     bbox=dict(facecolor='none', edgecolor='none', boxstyle='round, pad=0.4'))
        plt.scatter([v], [p], color='lightblue', s=50, edgecolor='black', zorder=5)  # Circular marker

    # Set x and y scales
    plt.xscale('log')
    plt.yscale('linear')

    # Add labels and title
    plt.xlabel('Force error (eV/$\AA$)', fontsize=16)
    plt.ylabel('Cumulative (%)', fontsize=16)
    
    # Increase x and y tick label font size
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    
    plt.tight_layout()

    # Set the x-axis limit to avoid overlapping with annotations
    plt.xlim(sorted_errors.min(), sorted_errors.max() * 3.0)  # Adjust multiplier as needed

    # Save the plot and data if required
    save_dir = os.path.join(folder_path, "plots")
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    if save:
        figure_save_path = os.path.join(save_dir, f"{title.replace(' ', '_')}.png")
        plt.savefig(figure_save_path, bbox_inches='tight')
        print(f"Figure saved to {figure_save_path}")
    plt.close()

    if data_save:
        true_values_path = os.path.join(save_dir, f"{title.replace(' ', '_')}_true_values.txt")
        predicted_values_path = os.path.join(save_dir, f"{title.replace(' ', '_')}_predicted_values.txt")
        np.savetxt(true_values_path, rms_extracted, header='True RMS Values', comments='')
        np.savetxt(predicted_values_path, rms_test, header='Predicted RMS Values', comments='')
        print(f"Data saved to {true_values_path} and {predicted_values_path}")








def main(folder_path=None):
    if not folder_path:  # If no folder path is provided, ask the user
        folder_path = input("Enter the folder path: ").strip() or "."
    else:
        print(f"Using provided folder path: {folder_path}")
    original_file_name = input("Enter the original dataset name: ").strip()
    test_file_name = input("Enter the validation dataset name: ").strip()

    # Ensure we have a valid folder path
    if not os.path.isdir(folder_path):
        raise NotADirectoryError(f"Provided folder path does not exist: {folder_path}")

    # Getting file paths
    original_file_path = os.path.join(folder_path, original_file_name)
    test_file_path = os.path.join(folder_path, test_file_name)

    # Reading datasets
    original_datasets = ase.io.read(original_file_path, index=":")
    test_datasets = ase.io.read(test_file_path, index=":")

    # Extract datasets or set as test_datasets
    extracted_datasets = []
    dataset_counter = 0
    has_original_index = any('original_dataset_index' in frame.info for frame in test_datasets)

    if has_original_index:
        for frame in test_datasets:
            if 'original_dataset_index' in frame.info:
                index = frame.info['original_dataset_index']
                dataset_counter += 1
                print(f"Extracting dataset {dataset_counter} using original_dataset_index: {index}")
                extracted_datasets.append(original_datasets[index])
    else:
        print("No 'original_dataset_index' found in test_datasets. Using original_datasets as extracted_datasets.")
        extracted_datasets = original_datasets

    # Save extracted datasets
    output_file_path = os.path.join(folder_path, 'extracted_datasets.extxyz')
    ase.io.write(output_file_path, extracted_datasets, format='extxyz')
    print(f"Extracted datasets have been saved to {output_file_path}")

    # Extract forces
    def get_forces(frame):
        if 'MACE_forces' in frame.arrays:
            return frame.arrays['MACE_forces']
        return frame.get_forces()

    extracted_forces = [get_forces(frame) for frame in extracted_datasets]
    test_forces = [get_forces(frame) for frame in test_datasets]


    # Comparing RMS forces
    compare_rms_forces(extracted_forces, test_forces, 'RMS Force Comparison Plot', folder_path)

   # Extract energies safely (first checks 'energy', then 'MACE_energy')
    def get_potential_energy(frame):
        # Check multiple potential keys for energy
        for key in ['energy', 'MACE_energy', 'potential_energy', 'total_energy']:
            if key in frame.info:
                return frame.info[key]
        # Fallback to ASE's built-in method
        try:
            return frame.get_potential_energy()
        except Exception:
            return np.nan
        
    # Extract energies for comparison
    extracted_energies = np.array([get_potential_energy(frame) for frame in extracted_datasets])
    test_energies = np.array([get_potential_energy(frame) for frame in test_datasets])

    # Ensure both energy arrays have the same length for plotting
    min_len = min(len(extracted_energies), len(test_energies))
    extracted_energies = extracted_energies[:min_len]
    test_energies = test_energies[:min_len]

    # Compare energies
    plot_parity(extracted_energies, test_energies, 'Energy Parity Plot', 'True Energies (eV)', 'Predicted Energies (eV)', folder_path)

    # Plot cumulative distributions
    plot_cumulative_distribution(extracted_energies, test_energies, folder_path, extracted_datasets, save=True, data_save=True)
    plot_cumulative_distribution_rms_forces(extracted_forces, test_forces, folder_path, save=True, data_save=True)

if __name__ == "__main__":
    main()

