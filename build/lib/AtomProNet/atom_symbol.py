#def atom_symbol(input_file):

#    import numpy as np

    # Create the array with atomic numbers
#    Al_count = 8  #Al
#    O_count = 12   #O


    # Create an array with 'Al' symbols followed by other elements
#    atom_array = np.concatenate([np.full(Al_count, 'Al'), np.full(O_count, 'O')])


    # Save the array as an npz file
#    np.savez('symbols.npz', symbols=atom_array)


#    return input_file

def atom_symbol(input_folder):
    import numpy as np
    import os

    # Prompt the user for the atomic symbols and counts
    atom_array = []

    while True:
        symbol = input("Enter the atomic symbol (e.g., Al, O, N) or type 'done' to finish: ").strip()
        if symbol.lower() == 'done':
            break

        try:
            count = int(input(f"Enter the count of {symbol} atoms: ").strip())
            atom_array.extend([symbol] * count)
        except ValueError:
            print("Please enter a valid integer for the count.")

    # Convert to numpy array
    atom_array = np.array(atom_array)

    # Save the array as an npz file in the specified input folder
    save_path = os.path.join(input_folder, 'symbols.npz')
    np.savez(save_path, symbols=atom_array)

    print(f"Symbols saved to {save_path}")
    return save_path
