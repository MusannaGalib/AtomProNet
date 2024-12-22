def pressure_eV(input_file):


    import numpy as np
    import os

    # Read the data from the text file
    #with open('F:/Research/ML/package/AtomProNet/trial/pressure_eV_pure.txt', 'r') as file:
    #    lines = file.readlines()

    # Get the absolute path of the input file
    input_file_path = os.path.join(input_file, 'pressure_eV.txt')

    # Read the data from the text file
    with open(input_file_path, 'r') as file:
        lines = file.readlines()

    # Initialize lists to store parsed data
    pressure_values = []

    # Iterate through lines and extract relevant information
    for i in range(len(lines)):
        # Check if the line starts with "Total"
        if lines[i].strip().startswith('Total'):
            # Extract the 6 columns following "Total"
            total_pressure_values = [float(value) for value in lines[i].split()[1:7]]

            # Append the values to the list
            pressure_values.append(total_pressure_values)

    # Save the lists to a .npz file
    if pressure_values:
        np.savez('pressures.npz', pressures=np.array(pressure_values))
        print(f"{len(pressure_values)} lines added to the table.")
    else:
        print("No 'Total' lines found.")


    return input_file