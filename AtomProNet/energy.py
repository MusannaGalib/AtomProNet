def energy(input_file):

    import numpy as np
    import os

    # Read the data from the text file
    #with open('F:/Research/ML/package/AtomProNet/trial/energy-conv_pure.txt', 'r') as file:
    #    lines = file.readlines()

    # Get the absolute path of the input file
    input_file_path = os.path.join(input_file, 'energy-conv.txt')

    # Read the data from the text file
    with open(input_file_path, 'r') as file:
        lines = file.readlines()

    # Initialize lists to store parsed data
    energy_values = []

    # Flag to track if 'energy without entropy' was found
    found_energy_without_entropy = False

    # Iterate through lines and extract relevant information
    for line in lines:
        # Split the line into words
        words = line.split()
        if words and len(words) >= 3:
            # First search for 'energy without entropy='
            if words[0] == 'energy' and words[1] == 'without' and words[2] == 'entropy=':
                energy_values.append([float(words[3])])
                found_energy_without_entropy = True
            # If 'energy without entropy' is not found, search for 'total energy'
            elif words[0] == 'total' and words[1] == 'energy':
                energy_values.append([float(words[3])])

    # If no energy value was found with 'energy without entropy', use 'total energy'
    if not found_energy_without_entropy and not energy_values:
        print("No 'energy without entropy' found, falling back to 'total energy'.")

    # Save the lists to a .npz file
    if energy_values:
        np.savez('energies.npz', energies=np.array(energy_values))
    else:
        print("No energy values found.")

    return input_file
