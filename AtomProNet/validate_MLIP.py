import os
import torch
import ase.io
import yaml

def find_file_by_extension(base_path, extension):
    """Recursively search for the first file with the given extension."""
    for root, _, files in os.walk(base_path):
        for file in files:
            if file.endswith(extension):
                return os.path.join(root, file)
    raise FileNotFoundError(f"No file with extension {extension} found in {base_path}")

def load_yaml(yaml_path):
    """Load the YAML configuration file."""
    with open(yaml_path, "r") as f:
        config = yaml.safe_load(f)
    return config

def load_model(pth_path):
    """Load the PyTorch model checkpoint."""
    checkpoint = torch.load(pth_path, map_location=torch.device("cpu"))
    return checkpoint

def create_ml_data(extxyz_path, original_dataset_indices, output_path="MLIP_evaluated_data.extxyz"):
    """Filter and save the evaluated data using the original dataset indices."""
    frames = ase.io.read(extxyz_path, index=":")
    selected_frames = [frames[idx] for idx in original_dataset_indices]
    ase.io.write(output_path, selected_frames)

def create_dft_data(extxyz_path, original_dataset_indices, output_path="DFT_data.extxyz"):
    """Save the initial DFT data corresponding to the original dataset indices."""
    frames = ase.io.read(extxyz_path, index=":")
    selected_frames = [frames[idx] for idx in original_dataset_indices]
    ase.io.write(output_path, selected_frames)

def main():
    # Get user input for base folder path
    base_path = input("Enter the path to the folder containing .pth, .yaml, and .extxyz files: ")

    # Locate files
    yaml_path = find_file_by_extension(base_path, ".yaml")
    pth_path = find_file_by_extension(base_path, ".pth")
    extxyz_path = find_file_by_extension(base_path, ".extxyz")
    
    # Load model and configuration data
    config = load_yaml(yaml_path)
    checkpoint = load_model(pth_path)
    
    # Extract original_dataset_index
    original_dataset_indices = checkpoint.get("original_dataset_index", None)
    if original_dataset_indices is None:
        raise ValueError("original_dataset_index not found in the model checkpoint.")
    
    # Generate MLIP_evaluated_data.extxyz
    create_ml_data(extxyz_path, original_dataset_indices)
    
    # Generate DFT_data.extxyz
    create_dft_data(extxyz_path, original_dataset_indices)

    print("Files DFT_data.extxyz and MLIP_evaluated_data.extxyz have been created.")

if __name__ == "__main__":
    main()
