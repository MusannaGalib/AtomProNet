def atom_symbol(input_file):


    import numpy as np


    # Create the array with atomic numbers
    Al_count = 8  #Al
    O_count = 12   #O


    # Create an array with 'Na' symbols followed by other elements
    atom_array = np.concatenate([np.full(Al_count, 'Al'), np.full(O_count, 'O')])


    # Save the array as an npz file
    np.savez('symbols.npz', symbols=atom_array)


    return input_file
