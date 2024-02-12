def combine(input_file):

    import numpy as np

    def combine_npz_files(file1, file2, file3, file4, file5, file6, output_file):
        # Load the data from the first npz file
        data1 = np.load(file1)
        array1 = data1['positions']

        data2 = np.load(file2)
        array2 = data2['lattice']


        # Load the data from the third npz file
        data3 = np.load(file3)
        array2d = data3['symbols']

        # Load the data from the fourth npz file
        data4 = np.load(file4)
        array3d = data4['energies']

        # Load the data from the fourth npz file
        data5 = np.load(file5)
        array1d = data5['forces']

        # Load the data from the fourth npz file
        data6 = np.load(file6)
        array4d = data6['pressures']

        

        # Create a new dictionary to store the combined data
        combined_data = {'positions': array1, 'lattice': array2, 'symbols': array2d, 'energies': array3d, 'forces': array1d, 'pressures': array4d}

        # Save the combined data to a new npz file
        np.savez(output_file, **combined_data)

    # usage
    combine_npz_files("positions.npz", "lattice.npz", "symbols.npz", "energies.npz", "forces.npz", "pressures.npz",  "Converted.npz")

    return input_file