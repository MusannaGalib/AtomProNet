from nequip_converter import convert_npz_to_extxyz, convert_vasp_to_extxyz
import os
import numpy as np

# Define the paths for the test data files
TEST_DATA_DIR = os.path.dirname(__file__)
ALUMINA_NPZ_FILE = os.path.join(TEST_DATA_DIR, 'alumina_pure.npz')
OUTCAR_FILE = os.path.join(TEST_DATA_DIR, 'OUTCAR')

def test_convert_npz_to_extxyz():
    # Print statement for debugging: indicating the start of this test function
    print("Running test: test_convert_npz_to_extxyz")

    # Call the conversion function from the package to convert 'alumina_pure.npz' to 'output_xyz.xyz'
    convert_npz_to_extxyz(ALUMINA_NPZ_FILE, 'output_xyz.xyz')

    # Additional tests (assertions) can be added here to validate the functionality of the conversion

def test_convert_vasp_to_extxyz():
    # Print statement for debugging: indicating the start of this test function
    print("Running test: test_convert_vasp_to_extxyz")

    # Check if the OUTCAR file exists before attempting conversion
    assert os.path.exists(OUTCAR_FILE), "OUTCAR file does not exist."

    # Call the conversion function from the package to convert 'OUTCAR' to 'output_xyz.xyz'
    convert_vasp_to_extxyz(OUTCAR_FILE, 'output_xyz.xyz')

    # Additional tests (assertions) can be added here to validate the functionality of the conversion

# Execute the test functions when this script is run directly
if __name__ == "__main__":
    test_convert_npz_to_extxyz()
    test_convert_vasp_to_extxyz()
