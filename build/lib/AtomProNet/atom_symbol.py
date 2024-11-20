import os
import numpy as np

def atom_symbol(input_folder):
    # Initialize an empty list to store the expanded symbols
    expanded_symbols = []

    # Define the path to symbols.txt
    symbols_file = os.path.join(input_folder, "symbols.txt")
    if not os.path.exists(symbols_file):
        print(f"Error: The file {symbols_file} does not exist.")
        return None

    # Read and process the symbols.txt file
    with open(symbols_file, 'r') as file:
        lines = file.readlines()

    symbols, counts = [], []
    for line in lines:
        if "Symbols:" in line:
            # Parse symbols
            symbols = line.split(":")[1].strip().split()
        elif "Counts:" in line:
            # Parse counts
            counts = list(map(int, line.split(":")[1].strip().split()))

            # Ensure symbols and counts match
            if len(symbols) == len(counts):
                expanded_structure = [symbol for symbol, count in zip(symbols, counts) for _ in range(count)]
                expanded_symbols.append(expanded_structure)
            else:
                print("Mismatch between symbols and counts!")
                return None

    # Convert expanded symbols to a 2D NumPy array with dtype=str
    if expanded_symbols:
        expanded_symbols_array = np.array(expanded_symbols, dtype=str)

        # Save the expanded symbols into a .npz file
        npz_save_path = os.path.join(input_folder, "symbols.npz")
        np.savez(npz_save_path, symbols=expanded_symbols_array)

        print(f"Symbols saved to {npz_save_path}")
        return npz_save_path
    else:
        print("No symbols to save.")
        return None














# def atom_symbol(input_folder):
#     import numpy as np
#     import os

#     # Prompt the user for the atomic symbols and counts
#     atom_array = []

#     while True:
#         symbol = input("Enter the atomic symbol (e.g., Al, O, N) or type 'done' to finish: ").strip()
#         if symbol.lower() == 'done':
#             break

#         try:
#             count = int(input(f"Enter the count of {symbol} atoms: ").strip())
#             atom_array.extend([symbol] * count)
#         except ValueError:
#             print("Please enter a valid integer for the count.")

#     # Convert to numpy array
#     atom_array = np.array(atom_array)

#     # Save the array as an npz file in the specified input folder
#     save_path = os.path.join(input_folder, 'symbols.npz')
#     np.savez(save_path, symbols=atom_array)

#     print(f"Symbols saved to {save_path}")
#     return save_path






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