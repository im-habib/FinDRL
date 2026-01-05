#!/bin/bash

# Define source and destination directories
src_folder="AllStaticFile"
dest_folder="AllImagesForUse"

# Create the destination folder if it doesn't exist
mkdir -p "$dest_folder"

# Check if required tools are installed
if ! command -v convert &> /dev/null; then
    echo "Error: ImageMagick (convert) not found. Please install it."
    exit 1
fi

if ! command -v inkscape &> /dev/null; then
    echo "Error: Inkscape not found. Please install it."
    exit 1
fi

# Loop through all supported image files in the source folder
for file in "$src_folder"/*.{png,jpg,jpeg,svg}; do
    if [[ -f "$file" ]]; then
        # Extract the base filename without extension
        filename=$(basename "$file" | cut -d. -f1)
        
        # Define the output PDF path
        output_file="$dest_folder/$filename.pdf"

        # Check if the PDF already exists and compare timestamps
        if [[ ! -f "$output_file" || "$file" -nt "$output_file" ]]; then
            echo "Converting $file to $output_file..."
            case "${file##*.}" in
                png|jpg|jpeg)
                    convert "$file" "$output_file"
                    ;;
                svg)
                    inkscape "$file" --export-filename="$output_file"
                    ;;
            esac
        else
            echo "Skipping $file - already up to date."
        fi
    fi
done

echo "Image conversion complete."