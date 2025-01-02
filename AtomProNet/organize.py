import os

# Functions for `symbols.txt` processing
def parse_symbols(file_path):
    """Extract all Counts: entries from symbols.txt."""
    counts_list = []
    directories = []
    with open(file_path, 'r') as f:
        current_dir = None
        for line in f:
            if line.startswith("Directory:"):
                current_dir = line.split(":", 1)[1].strip()
                directories.append(current_dir)
            elif line.startswith("Counts:"):
                counts = tuple(map(int, line.split(":")[1].strip().split()))
                counts_list.append((current_dir, counts))
    return counts_list

def find_changes_in_counts(counts_list):
    """Identify when Counts: changes and at which Directory."""
    changes = []
    previous_counts = None
    for idx, (directory, counts) in enumerate(counts_list):
        if previous_counts is not None and counts != previous_counts:
            changes.append((idx + 1, directory, previous_counts, counts))  # Record index and change details
        previous_counts = counts
    return changes

def process_symbols_file(file_path):
    """Process symbols.txt to detect and log changes in Counts."""
    print(f"Processing symbols.txt: {file_path}")
    counts_list = parse_symbols(file_path)
    if not counts_list:
        print("No Counts found in symbols.txt.")
        return []
    
    changes = find_changes_in_counts(counts_list)
    print(f"Total Directories Processed: {len(counts_list)}")
    print("\nDetected changes in Counts:")
    for change in changes:
        index, directory, old_counts, new_counts = change
        print(f"- Change at Directory {index}:")
        print(f"  Directory: {directory}")
        print(f"  Counts changed from {old_counts} to {new_counts}")
    
    return changes

# Functions for `pos-conv.txt` processing
def parse_pos_conv(file_path):
    """Parse pos-conv.txt to extract datasets and row counts, ensuring proper handling of directories."""
    datasets = []
    current_dir = None
    current_rows = 0
    in_dataset = False  # Flag to track if we're inside a dataset block

    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith("Directory:"):
                # Save the current dataset count before transitioning to a new directory
                if current_dir and in_dataset:
                    datasets.append((current_dir, current_rows))
                    current_rows = 0
                    in_dataset = False
                current_dir = line.split(":", 1)[1].strip()
            elif line.startswith("----"):
                # Toggle the dataset state when encountering dashed lines
                if in_dataset and current_rows > 0:
                    datasets.append((current_dir, current_rows))
                    current_rows = 0
                in_dataset = not in_dataset
            elif in_dataset and line:  # Count rows only if inside a dataset
                current_rows += 1

    # Append the last dataset if any rows remain
    if current_dir and current_rows > 0:
        datasets.append((current_dir, current_rows))
    
    return datasets

def find_dataset_changes(datasets):
    """Detect changes in row counts between datasets."""
    changes = []
    previous_rows = None

    for idx, (directory, row_count) in enumerate(datasets):
        if previous_rows is not None and row_count != previous_rows:
            changes.append((idx + 1, directory, previous_rows, row_count))  # Record index and change details
        previous_rows = row_count

    return changes

def process_pos_conv_file(file_path):
    """Process pos-conv.txt to detect dataset row count changes."""
    print(f"Processing pos-conv.txt: {file_path}")
    datasets = parse_pos_conv(file_path)
    
    if not datasets:
        print("No datasets found in pos-conv.txt.")
        return
    
    changes = find_dataset_changes(datasets)
    print(f"Total Directories Processed: {len(datasets)}")
    print("\nDetected changes in dataset row counts:")
    for change in changes:
        index, directory, old_rows, new_rows = change
        print(f"- Change at Directory {index}:")
        print(f"  Directory: {directory}")
        print(f"  Dataset row counts changed from {old_rows} to {new_rows}")

# Function to copy directory contents dynamically based on ranges
def copy_directory_contents_dynamic(base_dir, changes, output_dir):
    """Copy contents for ranges derived from changes in Counts."""
    files_to_process = [
        "symbols.txt",
        "pos-conv.txt",
        "lattice.txt",
        "pressure_eV.txt",
        "energy-conv.txt",
    ]

    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Collect all unique Counts types from changes
    counts_types = set(f"{change[2][0]}_{change[2][1]}" for change in changes)

    # Create base folders for each Counts type
    for counts_type in counts_types:
        counts_folder = os.path.join(output_dir, f"counts_{counts_type}")
        if not os.path.exists(counts_folder):
            os.makedirs(counts_folder)

    for file_name in files_to_process:
        source_file = os.path.join(base_dir, file_name)
        if not os.path.exists(source_file):
            print(f"{file_name} not found in {base_dir}. Skipping...")
            continue

        # Read the source file
        with open(source_file, 'r') as f:
            lines = f.readlines()

        # Identify and copy relevant ranges
        for i in range(len(changes) - 1):
            start_dir = changes[i][0]
            end_dir = changes[i + 1][0] - 1
            counts_type = f"{changes[i][3][0]}_{changes[i][3][1]}"
            counts_folder = os.path.join(output_dir, f"counts_{counts_type}")

            subfolder = os.path.join(counts_folder, f"directory_{start_dir}_{end_dir}")
            if not os.path.exists(subfolder):
                os.makedirs(subfolder)
            new_file_path = os.path.join(subfolder, file_name)
            with open(new_file_path, 'w') as new_file:
                current_dir_number = 0
                copy_lines = False

                for line in lines:
                    if line.startswith("Directory:"):
                        current_dir_number += 1
                        if start_dir <= current_dir_number <= end_dir:
                            copy_lines = True
                        else:
                            copy_lines = False

                    if copy_lines:
                        new_file.write(line)

            print(f"Filtered content for range {start_dir}-{end_dir} written to {new_file_path}")

# Main script
base_directory = "/home/galibubc/scratch/musanna/AtomProNet/AtomProNet-main/example_dataset/Data_generation/Quantum_ESPRESSO/VASP_files_LiO2"
processed_directory = os.path.join(base_directory, "processed_data")

# Process symbols.txt to get ranges
symbols_file = os.path.join(base_directory, "symbols.txt")
if os.path.exists(symbols_file):
    changes = process_symbols_file(symbols_file)
    if changes:
        copy_directory_contents_dynamic(base_directory, changes, processed_directory)
else:
    print(f"symbols.txt not found in the directory: {base_directory}")

# Process pos-conv.txt
pos_conv_file = os.path.join(base_directory, "pos-conv.txt")
if os.path.exists(pos_conv_file):
    process_pos_conv_file(pos_conv_file)
else:
    print(f"pos-conv.txt not found in the directory: {base_directory}")
