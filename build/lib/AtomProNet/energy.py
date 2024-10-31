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

    # Iterate through lines and extract relevant information
    for line in lines:
        # Split the line into words
        words = line.split()
        if words and words[0] == 'energy' and words[1] == 'without' and words[2] == 'entropy=':
            energy_values.append([float(words[3])])

    # Save the lists to a .npz file
    if  energy_values:
        np.savez('energies.npz', energies=np.array(energy_values))
    else:
        print("No energy values found.")


    return input_file











