#!/bin/sh

# Define project paths and variables
MAIN_TEX="thesis.tex"
SECTIONS_FOLDER="chapters"
DEST_FOLDER="AllImagesForUse"
IMAGE_FOLDER="AllStaticFile"
BIB_FILE="bib/References.bib"
IMG_CONVERTER="imgconverter.sh"
KILL_SCRIPT="kill.sh"

# Check if required tools are installed
for cmd in xelatex convert inkscape fswatch biber; do
    if ! command -v "$cmd" > /dev/null 2>&1; then
        echo "Error: $cmd not found. Please install it."
        exit 1
    fi
done

# Ensure main LaTeX file exists
if [ ! -f "$MAIN_TEX" ]; then
    echo "Error: $MAIN_TEX not found in $(pwd)."
    exit 1
fi

# Function to clean old files and compile a fresh document
compile_pdf() {
    echo "Running cleanup script ($KILL_SCRIPT)..."
    if [ -f "$KILL_SCRIPT" ]; then
        ./"$KILL_SCRIPT"
    fi

    echo "Cleaning old compiled files..."
    rm -f thesis.pdf thesis.aux thesis.log thesis.bbl thesis.blg thesis.out thesis.toc thesis.bcf thesis.run.xml *.synctex.gz

    echo "Compiling $MAIN_TEX..."
    if xelatex -interaction=nonstopmode "$MAIN_TEX"; then
        echo "First XeLaTeX pass complete."

        if [ -f "${MAIN_TEX%.tex}.bcf" ]; then
            biber "${MAIN_TEX%.tex}"
            echo "Biber processing completed."
        else
            echo "Warning: Biber skipped (bcf file missing)."
        fi

        xelatex -interaction=nonstopmode "$MAIN_TEX"
        xelatex -interaction=nonstopmode "$MAIN_TEX"
        echo "PDF successfully compiled: thesis.pdf"
    else
        echo "Error: XeLaTeX compilation failed. Check logs."
    fi
}

# Initial compilation
compile_pdf

# Start local HTTP server
nohup python3 -m http.server 8000 > /dev/null 2>&1 &
echo "Serving current directory at http://localhost:8000 (press Ctrl+C to stop)."

# Watch for changes and recompile
echo "Watching for changes in .tex files, chapters, images, and bibliography..."

fswatch -0 "$MAIN_TEX" "$SECTIONS_FOLDER" "$DEST_FOLDER" "$IMAGE_FOLDER" "$BIB_FILE" | while IFS= read -r -d "" event; do
    echo "Detected change: $event"
    
    if echo "$event" | grep -E "^($DEST_FOLDER|$IMAGE_FOLDER)/"; then
        echo "Image file change detected. Running image conversion..."
        if [ -f "$IMG_CONVERTER" ]; then
            ./"$IMG_CONVERTER"
        fi
    fi

    compile_pdf
done

# # Define project paths and variables
# MAIN_TEX="thesis.tex"
# OUTPUT_FOLDER="output"
# SECTIONS_FOLDER="chapters"
# DEST_FOLDER="AllImagesForUse"
# BIB_FILE="bib/References.bib"
# IMG_CONVERTER="imgconverter.sh"

# # Ensure output folder exists
# mkdir -p "$OUTPUT_FOLDER"

# # Copy all necessary files (excluding output folder itself)
# rsync -av --exclude="$OUTPUT_FOLDER" ./ "$OUTPUT_FOLDER/"
# echo "All files copied to '$OUTPUT_FOLDER'."

# # Check if required tools are installed
# for cmd in xelatex convert inkscape fswatch biber; do
#     if ! command -v "$cmd" > /dev/null 2>&1; then
#         echo "Error: $cmd not found. Please install it."
#         exit 1
#     fi
# done

# # Ensure the main LaTeX file exists
# if [ ! -f "$OUTPUT_FOLDER/$MAIN_TEX" ]; then
#     echo "Error: $MAIN_TEX not found in '$OUTPUT_FOLDER'. Ensure it exists."
#     exit 1
# fi

# # Run killport.sh to free up port 8000 (if exists)
# if [ -f "./killport.sh" ]; then
#     chmod +x "./killport.sh"
#     ./killport.sh
# else
#     echo "Warning: killport.sh not found. Skipping port cleanup."
# fi

# # Initial image conversion
# if [ -f "./$IMG_CONVERTER" ]; then
#     chmod +x "./$IMG_CONVERTER"
#     ./"$IMG_CONVERTER"
#     cp -ru "$DEST_FOLDER" "$OUTPUT_FOLDER/"
#     rm -rf "$DEST_FOLDER"
#     echo "Initial image conversion done."
# else
#     echo "Warning: $IMG_CONVERTER not found. Skipping image conversion."
# fi

# # Compile PDF inside OUTPUT_FOLDER
# (
#   cd "$OUTPUT_FOLDER" || exit
#   rm -f "thesis.pdf"

#   echo "Starting XeLaTeX compilation..."
#   if xelatex -interaction=nonstopmode "$MAIN_TEX"; then
#     echo "First XeLaTeX pass complete."

#     if [ -f "${MAIN_TEX%.tex}.bcf" ]; then
#       biber "${MAIN_TEX%.tex}"
#       echo "Biber completed."
#     else
#       echo "Warning: Biber skipped (bcf file missing)."
#     fi

#     xelatex -interaction=nonstopmode "$MAIN_TEX"
#     xelatex -interaction=nonstopmode "$MAIN_TEX"
#     echo "Final XeLaTeX pass complete."
#   else
#     echo "Error: XeLaTeX failed. Check logs."
#     exit 1
#   fi
# )
# echo "PDF compilation complete. Output: $OUTPUT_FOLDER/thesis.pdf"

# # Start the server from OUTPUT_FOLDER
# (
#   cd "$OUTPUT_FOLDER" || exit
#   nohup python3 -m http.server 8000 > /dev/null 2>&1 &
# )
# echo "Serving '$OUTPUT_FOLDER' at http://localhost:8000 (press Ctrl+C to stop)."

# # Watch for changes and recompile (POSIX-friendly)
# fswatch -0 . | while IFS= read -r event; do
#     echo "Detected change: $event"
#     rsync -av --exclude="$OUTPUT_FOLDER" ./ "$OUTPUT_FOLDER/"
    
#     # Recompile PDF
#     (
#       cd "$OUTPUT_FOLDER" || exit
#       rm -f "thesis.pdf"
#       xelatex -interaction=nonstopmode "$MAIN_TEX"
#       biber "${MAIN_TEX%.tex}"
#       xelatex -interaction=nonstopmode "$MAIN_TEX"
#       xelatex -interaction=nonstopmode "$MAIN_TEX"
#     )
#     echo "Recompiled thesis.pdf"
# done

# # Define project paths and variables
# MAIN_TEX="thesis.tex"
# OUTPUT_FOLDER="output"
# SECTIONS_FOLDER="chapters"
# DEST_FOLDER="AllImagesForUse"
# BIB_FILE="bib/References.bib"
# IMG_CONVERTER="imgconverter.sh"

# # Clean and recreate output folder
# rm -rf "$OUTPUT_FOLDER"
# mkdir -p "$OUTPUT_FOLDER"
# echo "Done: OUTPUT_FOLDER: '$OUTPUT_FOLDER' Deleted and Recreated."

# # Check if required tools are installed
# for cmd in xelatex convert inkscape fswatch biber; do
#     if ! command -v $cmd &> /dev/null; then
#         echo "Error: $cmd not found. Please install it."
#         exit 1
#     fi
# done

# # Ensure helper scripts exist and are executable
# for script in "killport.sh" "$IMG_CONVERTER"; do
#     if [ ! -f "$script" ]; then
#         echo "Error: $script not found in $(pwd). Please ensure the file exists."
#         exit 1
#     fi
#     chmod +x "$script"
# done

# # Ensure main LaTeX file exists
# if [ ! -f "$MAIN_TEX" ]; then
#     echo "Error: $MAIN_TEX not found in $(pwd). Please ensure the file exists."
#     exit 1
# fi

# # Move necessary LaTeX files to the output folder
# cp -r "$SECTIONS_FOLDER" "$OUTPUT_FOLDER/"
# cp "$MAIN_TEX" "$OUTPUT_FOLDER/"
# if [ -f "$BIB_FILE" ]; then
#     cp "$BIB_FILE" "$OUTPUT_FOLDER/"
# fi
# echo "All necessary LaTeX files copied to $OUTPUT_FOLDER."

# # Run killport.sh to free up port 8000
# ./killport.sh

# # Convert images before compilation
# ./"$IMG_CONVERTER"

# # Move converted images to output folder
# cp -r "$DEST_FOLDER" "$OUTPUT_FOLDER/"
# # Remove DEST_FOLDER from root directory after moving
# rm -rf "$DEST_FOLDER"
# echo "Converted images moved to output folder and original DEST_FOLDER removed."

# # Change to output directory before compilation
# cd "$OUTPUT_FOLDER"

# # Run LaTeX multiple times for correct compilation
# xelatex -interaction=nonstopmode "thesis.tex"
# biber "thesis"
# xelatex -interaction=nonstopmode "thesis.tex"
# xelatex -interaction=nonstopmode "thesis.tex"

# echo "Compilation complete. Output: thesis.pdf"

# # Start the server from the output folder
# nohup python3 -m http.server 8000 > /dev/null 2>&1 &
# echo "Serving $OUTPUT_FOLDER at http://localhost:8000 (press Ctrl+C to stop)"

# # Watch for changes and automate
# fswatch -0 "../$SECTIONS_FOLDER" "../$MAIN_TEX" | while read -d "" event; do
#     echo "Detected change: $event"
#     if [[ "$event" == *"$SECTIONS_FOLDER"* ]]; then
#         echo "Image change detected. Reprocessing images..."
#         ../"$IMG_CONVERTER"
#         cp -r "../$DEST_FOLDER" "../$OUTPUT_FOLDER/"
#         rm -rf "../$DEST_FOLDER"
#     fi
#     if [[ "$event" == *".tex" ]]; then
#         echo "LaTeX file change detected. Recompiling..."
#         cd "../$OUTPUT_FOLDER"
#         xelatex -interaction=nonstopmode "thesis.tex"
#         biber "thesis"
#         xelatex -interaction=nonstopmode "thesis.tex"
#         xelatex -interaction=nonstopmode "thesis.tex"
#         echo "Recompilation complete."
#         cd ..
#     fi
# done


# # Define project paths and variables
# MAIN_TEX="thesis.tex"
# OUTPUT_FOLDER="output"
# SRC_FOLDER="AllStaticFile"
# SECTIONS_FOLDER="chapters"
# DEST_FOLDER="AllImagesForUse"
# BIB_FILE="bib/References.bib"
# IMG_CONVERTER="imgconverter.sh"

# # Clean and recreate output folder
# rm -rf "$OUTPUT_FOLDER"
# mkdir -p "$OUTPUT_FOLDER"
# echo "Done: OUTPUT_FOLDER: '$OUTPUT_FOLDER' Deleted and Recreated."

# # Check if required tools are installed
# for cmd in xelatex convert inkscape fswatch biber; do
#     if ! command -v $cmd &> /dev/null; then
#         echo "Error: $cmd not found. Please install it."
#         exit 1
#     fi
# done

# # Ensure helper scripts exist and are executable
# for script in "killport.sh" "$IMG_CONVERTER"; do
#     if [ ! -f "$script" ]; then
#         echo "Error: $script not found in $(pwd). Please ensure the file exists."
#         exit 1
#     fi
#     chmod +x "$script"
# done

# # Ensure main LaTeX file exists
# if [ ! -f "$MAIN_TEX" ]; then
#     echo "Error: $MAIN_TEX not found in $(pwd). Please ensure the file exists."
#     exit 1
# fi

# # Move all necessary files to the output folder
# cp -r "$SRC_FOLDER" "$OUTPUT_FOLDER/"
# cp -r "$SECTIONS_FOLDER" "$OUTPUT_FOLDER/"
# cp "$MAIN_TEX" "$OUTPUT_FOLDER/"
# if [ -f "$BIB_FILE" ]; then
#     cp "$BIB_FILE" "$OUTPUT_FOLDER/"
# fi
# echo "All necessary files copied to $OUTPUT_FOLDER."

# # Run killport.sh to free up port 8000
# ./killport.sh

# # Convert images before compilation
# ./"$IMG_CONVERTER"

# # Move converted images to output folder
# cp -r "$DEST_FOLDER" "$OUTPUT_FOLDER/"

# # Change to output directory before compilation
# cd "$OUTPUT_FOLDER"

# # Run LaTeX multiple times for correct compilation
# xelatex -interaction=nonstopmode "thesis.tex"
# biber "thesis"
# xelatex -interaction=nonstopmode "thesis.tex"
# xelatex -interaction=nonstopmode "thesis.tex"

# echo "Compilation complete. Output: thesis.pdf"

# # Start the server from the output folder
# nohup python3 -m http.server 8000 > /dev/null 2>&1 &
# echo "Serving $OUTPUT_FOLDER at http://localhost:8000 (press Ctrl+C to stop)"

# # Watch for changes and automate
# fswatch -0 "../$SRC_FOLDER" "../$MAIN_TEX" "../$SECTIONS_FOLDER" | while read -d "" event; do
#     echo "Detected change: $event"
#     if [[ "$event" == *"$SRC_FOLDER"* ]]; then
#         echo "Image change detected. Reprocessing images..."
#         ../"$IMG_CONVERTER"
#         cp -r "../$DEST_FOLDER" "../$OUTPUT_FOLDER/"
#     fi
#     if [[ "$event" == *".tex" ]]; then
#         echo "LaTeX file change detected. Recompiling..."
#         cd "../$OUTPUT_FOLDER"
#         xelatex -interaction=nonstopmode "thesis.tex"
#         biber "thesis"
#         xelatex -interaction=nonstopmode "thesis.tex"
#         xelatex -interaction=nonstopmode "thesis.tex"
#         echo "Recompilation complete."
#         cd ..
#     fi
# done


# # Define project paths and variables
# MAIN_TEX="thesis.tex"
# OUTPUT_FOLDER="output"
# SRC_FOLDER="AllStaticFile"
# SECTIONS_FOLDER="chapters"
# DEST_FOLDER="AllImagesForUse"
# BIB_FILE="bib/References.bib"
# IMG_CONVERTER="imgconverter.sh"

# # Clean and recreate output folder
# rm -rf "$OUTPUT_FOLDER"
# mkdir -p "$OUTPUT_FOLDER"
# echo "Done: OUTPUT_FOLDER: '$OUTPUT_FOLDER' Deleted and Recreated."

# # Check if required tools are installed
# for cmd in xelatex convert inkscape fswatch biber; do
#     if ! command -v $cmd &> /dev/null; then
#         echo "Error: $cmd not found. Please install it."
#         exit 1
#     fi
# done

# # Ensure helper scripts exist and are executable
# for script in "killport.sh" "$IMG_CONVERTER"; do
#     if [ ! -f "$script" ]; then
#         echo "Error: $script not found in $(pwd). Please ensure the file exists."
#         exit 1
#     fi
#     chmod +x "$script"
# done

# # Ensure main LaTeX file exists
# if [ ! -f "$MAIN_TEX" ]; then
#     echo "Error: $MAIN_TEX not found in $(pwd). Please ensure the file exists."
#     exit 1
# fi

# # Move all necessary files to the output folder
# cp -r "$SRC_FOLDER" "$OUTPUT_FOLDER/"
# cp -r "$SECTIONS_FOLDER" "$OUTPUT_FOLDER/"
# cp "$MAIN_TEX" "$OUTPUT_FOLDER/"
# if [ -f "$BIB_FILE" ]; then
#     cp "$BIB_FILE" "$OUTPUT_FOLDER/"
# fi
# echo "All necessary files copied to $OUTPUT_FOLDER."

# # Run killport.sh to free up port 8000
# ./killport.sh

# # Convert images before compilation
# ./"$IMG_CONVERTER"

# # Move converted images to output folder
# cp -r "$DEST_FOLDER" "$OUTPUT_FOLDER/"

# # Change to output directory before compilation
# cd "$OUTPUT_FOLDER"

# # Run LaTeX multiple times for correct compilation
# xelatex -interaction=nonstopmode "thesis.tex"
# biber "thesis"
# xelatex -interaction=nonstopmode "thesis.tex"
# xelatex -interaction=nonstopmode "thesis.tex"

# echo "Compilation complete. Output: thesis.pdf"

# # Start the server from the output folder
# nohup python3 -m http.server 8000 > /dev/null 2>&1 &
# echo "Serving $OUTPUT_FOLDER at http://localhost:8000 (press Ctrl+C to stop)"

# # Watch for changes and automate
# fswatch -0 "../$SRC_FOLDER" "../$MAIN_TEX" "../$SECTIONS_FOLDER" | while read -d "" event; do
#     echo "Detected change: $event"
#     if [[ "$event" == *"$SRC_FOLDER"* ]]; then
#         echo "Image change detected. Reprocessing images..."
#         ../"$IMG_CONVERTER"
#         cp -r "../$DEST_FOLDER" "../$OUTPUT_FOLDER/"
#     fi
#     if [[ "$event" == *".tex" ]]; then
#         echo "LaTeX file change detected. Recompiling..."
#         cd "../$OUTPUT_FOLDER"
#         xelatex -interaction=nonstopmode "thesis.tex"
#         biber "thesis"
#         xelatex -interaction=nonstopmode "thesis.tex"
#         xelatex -interaction=nonstopmode "thesis.tex"
#         echo "Recompilation complete."
#         cd ..
#     fi
# done




# # Define project paths and variables
# OUTPUT_FOLDER="output"

# rm -rf "$OUTPUT_FOLDER"
# echo "Done: OUTPUT_FOLDER: '$OUTPUT_FOLDER' Deleted."
# IMG_CONVERTER="imgconverter.sh"

# # Define ignored files
# IGNORED_FILES=(".DS_Store" ".gitignore" ".git" "Thumbs.db") # Add more files as needed

# PROJECT_DIR=$(pwd)
# MAIN_TEX="thesis.tex"
# SRC_FOLDER="AllStaticFile"
# DEST_FOLDER="AllImagesForUse"

# # Create output folder if it doesn't exist
# mkdir -p "$OUTPUT_FOLDER"

# # Check if required tools are installed
# if ! command -v xelatex &> /dev/null; then
#     echo "Error: xelatex (TeX Live) not found. Please install it."
#     exit 1
# fi

# if ! command -v convert &> /dev/null; then
#     echo "Error: ImageMagick (convert) not found. Please install it."
#     exit 1
# fi

# if ! command -v inkscape &> /dev/null; then
#     echo "Error: Inkscape not found. Please install it."
#     exit 1
# fi

# if ! command -v fswatch &> /dev/null; then
#     echo "Error: fswatch not found. Please install it with 'brew install fswatch'."
#     exit 1
# fi

# # Ensure killport.sh and imgconverter.sh exist and are executable
# if [ ! -f "killport.sh" ]; then
#     echo "Error: killport.sh not found in $PROJECT_DIR. Please ensure the file exists."
#     exit 1
# fi

# chmod +x "killport.sh"

# if [ ! -f "$IMG_CONVERTER" ]; then
#     echo "Error: $IMG_CONVERTER not found in $PROJECT_DIR. Please ensure the file exists."
#     exit 1
# fi
# chmod +x "$IMG_CONVERTER"

# # Check if thesis.tex exists
# if [ ! -f "$MAIN_TEX" ]; then
#     echo "Error: $MAIN_TEX not found in $PROJECT_DIR. Please ensure the file exists."
#     exit 1
# fi

# # Run killport.sh to free up port 8000
# echo "Checking and killing process on port 8000..."
# ./killport.sh

# # Initial conversion and compilation
# echo "Performing initial conversion and compilation..."
# ./"$IMG_CONVERTER"
# xelatex -interaction=nonstopmode -output-directory="$OUTPUT_FOLDER" "$PROJECT_DIR/$MAIN_TEX"  # Compile directly to output folder
# echo "Initial compilation complete. Output: $OUTPUT_FOLDER/$MAIN_TEX.pdf"

# # Start the server from the output folder
# echo "Serving $OUTPUT_FOLDER at http://localhost:8000 (press Ctrl+C to stop)"
# (cd "$OUTPUT_FOLDER" && python3 -m http.server 8000 &) &

# # Watch for changes and automate
# echo "Watching for changes in $PROJECT_DIR and $SRC_FOLDER..."
# fswatch -0 "$PROJECT_DIR" "$SRC_FOLDER" | while read -d "" event; do
#     echo "Detected change: $event"
    
#     # Check if the changed file is in the ignored list
#     IGNORE=false
#     for ignored in "${IGNORED_FILES[@]}"; do
#         if [[ "$event" == *"$ignored" ]]; then
#             echo "Ignoring change to $ignored"
#             IGNORE=true
#             break
#         fi
#     done
    
#     # Proceed only if not ignored
#     if [ "$IGNORE" = false ]; then
#         # Check if the change is in SRC_FOLDER (new or updated images)
#         if [[ "$event" == *"$SRC_FOLDER"* ]]; then
#             echo "Change detected in $SRC_FOLDER. Converting images..."
#             ./"$IMG_CONVERTER"
#         fi
        
#         # Check if the change affects .tex files
#         if [[ "$event" == *".tex" ]]; then
#             echo "Change detected in .tex file. Recompiling..."
#             xelatex -interaction=nonstopmode -output-directory="$OUTPUT_FOLDER" "$PROJECT_DIR/$MAIN_TEX"  # Compile directly to output folder
#             echo "Recompilation complete. Output: $OUTPUT_FOLDER/$MAIN_TEX.pdf"
#         fi
#     fi
# done