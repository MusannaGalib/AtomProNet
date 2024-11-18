import os
import re
import random
import ase.io

def collect_indices(input_file, output_file):
    """Collect original_dataset_index values from parity.x and save them to an output file."""
    indices = set()
    with open(input_file, 'r') as infile:
        for line in infile:
            match = re.search(r"original_dataset_index\s*=\s*(\d+)", line)
            if match:
                index = int(match.group(1))
                indices.add(index)
    
    # Write the collected indices to the output file
    with open(output_file, 'w') as outfile:
        for index in sorted(indices):
            outfile.write(f"{index}\n")
    
    print(f"Total indices collected and saved to {output_file}: {len(indices)}")
    return indices

def load_indices_from_file(input_file):
    """Load indices from the collected indices file."""
    indices = set()
    with open(input_file, 'r') as infile:
        for line in infile:
            indices.add(int(line.strip()))
    return indices

def read_datasets(file_path):
    """Read all datasets from the extxyz file using ASE."""
    datasets = []
    for frame in ase.io.iread(file_path, format='extxyz'):
        datasets.append(frame)
    return datasets

def process_extxyz_file(input_file, indices_to_copy, output_file, validation_file):
    """Process the extxyz file to copy specified frames to a validation file and remove them from the original."""
    # Read all datasets from the input file
    datasets = read_datasets(input_file)
    
    # Separate datasets based on indices_to_copy
    datasets_to_copy = [frame for idx, frame in enumerate(datasets) if idx in indices_to_copy]
    remaining_datasets = [frame for idx, frame in enumerate(datasets) if idx not in indices_to_copy]
    
    # Save copied datasets to validation file
    ase.io.write(validation_file, datasets_to_copy, format='extxyz')
    print(f"Total datasets copied to {validation_file}: {len(datasets_to_copy)}")
    
    # Save remaining datasets to new output file
    ase.io.write(output_file, remaining_datasets, format='extxyz')
    print(f"Total datasets remaining in {output_file}: {len(remaining_datasets)}")

def split_train_test(input_file, folder_path):
    """Split the datasets in input_file into train and test files based on user input."""
    datasets = read_datasets(input_file)
    total_datasets = len(datasets)

    # Ask the user for the number of datasets to include in the train file
    num_train = int(input(f"Enter the number of datasets for train.extxyz (out of {total_datasets}): "))
    
    # Ensure the requested number is valid
    if num_train > total_datasets or num_train < 0:
        raise ValueError("The number of training datasets must be between 0 and the total number of datasets.")
    
    # Randomly shuffle and split the datasets
    random.shuffle(datasets)
    train_datasets = datasets[:num_train]
    test_datasets = datasets[num_train:]
    
    # Define output paths
    train_file = os.path.join(folder_path, 'train.extxyz')
    test_file = os.path.join(folder_path, 'test.extxyz')
    
    # Save the train and test datasets
    ase.io.write(train_file, train_datasets, format='extxyz')
    ase.io.write(test_file, test_datasets, format='extxyz')
    
    print(f"Total datasets in train file ({train_file}): {len(train_datasets)}")
    print(f"Total datasets in test file ({test_file}): {len(test_datasets)}")

# Ask the user for the folder path
folder_path = input("Enter the folder path containing MLIP_data.extxyz and parity.xyz: ").strip()

# Define file paths based on the user-specified folder
mlip_data_file = os.path.join(folder_path, 'MLIP_data.extxyz')
parity_file = os.path.join(folder_path, 'parity.xyz')
indices_file = os.path.join(folder_path, 'collected_indices.txt')
new_mlip_data_file = os.path.join(folder_path, 'MLIP_data_new.extxyz')
validation_file = os.path.join(folder_path, 'validation_dataset.xyz')

# Step 1: Collect and save indices from parity.xyz into collected_indices.txt
collect_indices(parity_file, indices_file)

# Step 2: Load the indices from the collected indices file
indices_to_copy = load_indices_from_file(indices_file)

# Debugging: print out the indices to copy after reading from collected_indices.txt
print(f"Collected indices from {indices_file}: {indices_to_copy}")

# Step 3: Process the extxyz file to copy specified data chunks and save to a validation dataset
process_extxyz_file(
    mlip_data_file,
    indices_to_copy,
    new_mlip_data_file,   # New output file with chunks removed
    validation_file       # Validation dataset file with copied chunks
)

# Step 4: Split the datasets in MLIP_data_new.extxyz into train and test files
split_train_test(new_mlip_data_file, folder_path)
