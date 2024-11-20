import re
import numpy as np
import os


def position_force(input_file):
    # Function to extract data blocks between dashed lines
    def extract_all_data(content):
        blocks = []
        current_block = []
        in_data_block = False

        for line in content:
            # Detect dashed lines
            if re.match(r'\s*-{5,}', line):  # Match 5 or more dashes
                if in_data_block:
                    blocks.append(current_block)
                    current_block = []
                    in_data_block = False
                else:
                    in_data_block = True
            elif in_data_block and re.search(r'^\s*\d', line):  # Ensure numeric lines
                current_block.append(line.strip())

        if current_block:  # Append the last block
            blocks.append(current_block)
        return blocks

    # Function to convert a block to positions and forces
    def process_block(block):
        positions = []
        forces = []
        for line in block:
            values = list(map(float, line.split()))
            # First three columns are positions, next three are forces
            positions.append(values[:3])
            forces.append(values[3:6])
        return positions, forces

    # Get the absolute path of the input file
    input_file_path = os.path.join(input_file, 'pos-conv.txt')

    # Read the data from the text file
    if not os.path.exists(input_file_path):
        raise FileNotFoundError(f"File not found: {input_file_path}")

    with open(input_file_path, 'r') as file:
        content = file.readlines()

    # Extract all data blocks
    data_blocks = extract_all_data(content)

    all_positions = []
    all_forces = []

    for block in data_blocks:
        positions, forces = process_block(block)
        all_positions.append(positions)
        all_forces.append(forces)

    # Save all positions and forces to .npz files
    np.savez(os.path.join(input_file, 'positions.npz'), positions=all_positions)
    np.savez(os.path.join(input_file, 'forces.npz'), forces=all_forces)

    # Print the number of tables
    print(f"Number of tables in positions.npz: {len(all_positions)}")
    print(f"Number of tables in forces.npz: {len(all_forces)}")

    return input_file














# ----------------- Legacy Version -------------------------
# def position_force(input_file):

#     import re
#     import numpy as np
#     import os

#     # Function to extract data between dash lines
#     def extract_data(lines):
#         start_index = None
#         end_index = None

#         # Iterate through the lines to find the dash lines
#         for i, line in enumerate(lines):
#             if re.match(r'\s*-{80,}', line):
#                 if start_index is not None:
#                     end_index = i
#                     break
#                 else:
#                     # Skip two lines after the dash line
#                     start_index = i + 1  

#         # If dash lines are found, return the data between them
#         if start_index is not None and end_index is not None:
#             return lines[start_index:end_index]
#         else:
#             return []

#     # Function to convert data to nested list
#     def convert_data_to_nested_list(data):
#         nested_table = []

#         # Iterate through the data and split into positions and forces
#         for line in data:
#             values = list(map(float, line))
#             nested_table.append(values)

#         return nested_table

#     # Read the entire file
#     #with open('F:/Research/ML/package/AtomProNet/trial/pos-conv_pure.txt', 'r') as file:
#     #    content = file.readlines()

#     # Get the absolute path of the input file
#     input_file_path = os.path.join(input_file, 'pos-conv.txt')

#     # Read the data from the text file
#     with open(input_file_path, 'r') as file:
#         content = file.readlines()

#     # Split content into tables based on empty lines
#     tables = re.split(r'\n\s*\n', ''.join(content))

#     # Print the number of tables directly from the txt file
#     #print(f"Number of tables directly from the txt file: {len(tables)}")


#     # Combine all positions and forces
#     all_positions = []
#     all_forces = []

#     # Iterate over tables and extract data between dash lines
#     for i, table in enumerate(tables):
#         lines = table.split('\n')
#         data = extract_data(lines)

#         if data:
#             # Append data to all_positions and all_forces
#             all_positions.append(convert_data_to_nested_list([line.split()[:3] for line in data]))
#             all_forces.append(convert_data_to_nested_list([line.split()[3:] for line in data]))



#     # Save all positions and forces to single npz files
#     np.savez('positions.npz', positions=all_positions)
#     np.savez('forces.npz', forces=all_forces)


#     # Print the number of tables after concatenation for each .npz file
#     print(f"Number of tables in positions.npz after concatenation: {len(all_positions)}")
#     print(f"Number of tables in forces.npz after concatenation: {len(all_positions)}")



#     return input_file