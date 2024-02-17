#!/bin/bash

# Get the directory where the bash script exists
script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$script_dir"

# Load necessary modules
module load gnuplot

# Loop through each folder containing OSZICAR files
for folder in */; do
    # Navigate to the folder containing OSZICAR files
    cd "$folder"

    # Extract the folder name
    folder_name="${folder%/}"

    # Initialize variables for data and plot filenames
    data_filename="data_${folder_name}.txt"
    plot_filename="plot_${folder_name}.jpg"

    # Loop through each OSZICAR file
    for file in *OSZICAR; do
        echo "Processing $file"

        # Extract and print data
        awk '/T=/ && /E=/ {printf "%.1f %s %s\n", $1 * 0.5, $3, $7}' "$file" >> "../$data_filename"   # Timestep 0.5 fs
    done

    echo "Data extraction completed for folder $folder_name."

    # Plotting with gnuplot
    gnuplot -e "set terminal jpeg; set key left; set xlabel 'Time (fs)'; \
                set ylabel 'Temperature (K)'; set y2label 'Energy (eV)'; \
                set ytics nomirror; set y2tics; \
                set title 'Plot for $folder_name'; \
                set style data lines; \
                plot '../$data_filename' using 1:2 title 'Temperature (K)' axes x1y1, \
                     '' using 1:3 title 'Energy (eV)' axes x1y2" > "../$plot_filename"

    echo "Plot generated for folder $folder_name."

    # Move back to the parent directory
    cd ..
done

echo "All data extraction and plotting completed."
