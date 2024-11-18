def combine(input_file):

    import numpy as np
    import os

    def combine_npz_files(file1, file2, file3, file4, file5, file6, output_file):
        # List of input files and corresponding keys
        files = [file1, file2, file3, file4, file5, file6]
        keys = ['positions', 'lattice', 'symbols', 'energies', 'forces', 'pressures']

        # Dictionary to store combined data
        combined_data = {}

        # Check each file and load if available
        for file, key in zip(files, keys):
            if os.path.exists(file):
                data = np.load(file)
                combined_data[key] = data[key]
            else:
                print(f"Warning: {file} is missing. Skipping this file.")

        # Save the combined data to a new npz file
        if combined_data:
            np.savez(output_file, **combined_data)
            print(f"Combined data saved to {output_file}.")
        else:
            print("No data to combine. All input files are missing.")

    # Usage
    combine_npz_files(
        "positions.npz",
        "lattice.npz",
        "symbols.npz",
        "energies.npz",
        "forces.npz",
        "pressures.npz",
        "Converted.npz",
    )

    return input_file
