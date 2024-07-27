#!/bin/bash

# Function to process each .vue file
process_vue_files() {
    local file="$1"
    # Check if the first line matches "<script setup lang="ts">"
    first_line=$(head -n 1 "$file")
    if [[ "$first_line" == '<script setup lang="ts">' ]]; then
        echo "File: $file - OK"
    else
        echo "File: $file - First line does not match '<script setup lang=\"ts\">'"
    fi
}

# Main function to iterate through subdirectories and find .vue files
check_vue_files() {
    local dir="$1"
    # Iterate over .vue files
    while IFS= read -r -d '' file; do
        process_vue_files "$file"
    done < <(find "$dir" -type f -name "*.vue" -print0)
}

# Check .vue files in current directory and subdirectories
check_vue_files .