def lattice(input_file):

    import numpy as np
    import os

    # Read the data from the text file
    #with open('F:/Research/ML/package/AtomProNet/trial/lattice_pure.txt', 'r') as file:
    #    lines = file.readlines()

    # Get the absolute path of the input file
    input_file_path = os.path.join(input_file, 'lattice.txt')

        # Ask the user if the sample is strained in 2 or 3 directions
    while True:
        try:
            strain_directions = int(input("Enter the number of directions the sample is strained in (2 or 3): ").strip())
            if strain_directions in [2, 3]:
                break
            else:
                print("Please enter 2 or 3.")
        except ValueError:
            print("Invalid input. Please enter a number (2 or 3).")

    # Define the expected length based on user input
    expected_length = 3 if strain_directions == 3 else 2

    # Read the data from the text file
    with open(input_file_path, 'r') as file:
        lines = file.readlines()

    # Initialize lists to store parsed data
    lattice_parameters = []

    # Iterate through lines and extract lattice parameters
    for i in range(0, len(lines), 2):
        # Extract the index and lattice parameters
        index_line = lines[i].split()

        # Check if the index line has the correct number of values
        if len(index_line) == expected_length:              #3 for -0.05 -0.05 -0.05   2 for -0.05 -0.05
            # Check if there are enough lines remaining
            if i + 1 < len(lines):
                # Extract the lattice parameters
                params_line_1 = lines[i + 1].split()

                # Check if the lines have the correct number of values
                if len(params_line_1) == 9:
                    # Combine the lines into a single list of 11 values
                    lattice_params = [float(value) for value in params_line_1]

                    # Append the values to the list
                    lattice_parameters.append(lattice_params)
                else:
                    print(f"Ignoring invalid lines starting at index {i}:\n{lines[i]}{lines[i+1]}")
            else:
                print(f"Skipping incomplete set of lattice parameters at index {i}:\n{lines[i]}")
        else:
            print(f"Ignoring invalid index line at index {i}:\n{lines[i]}")

    # Convert the list to a numpy array
    lattice_array = np.array(lattice_parameters)

    # Reshape the array to have the appropriate number of columns
    lattice_array = lattice_array.reshape((len(lattice_array), 9))

    output_file = 'lattice.npz'
    # Save the array to an npz file with the desired filename
    if lattice_array.size > 0:
        np.savez('lattice.npz', lattice=lattice_array)
        print(f"{len(lattice_array)} rows of lattice parameters added to the table.")
    else:
        print("No valid lattice parameters found.")

    return input_file