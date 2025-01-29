#!/bin/bash
## Usage: ./directDownload.sh <filename>
## <filename> contains one download link per line

### Initial checks
if [[ -z "$1" ]]; then
    echo 'Usage ./directDownload.sh <filename>'
fi

if [[ ! -f "$1" ]]; then
    echo "$1 not found"
    exit 1
fi

### File download
while IFS="" read -r p || [ -n "$p" ]; do
    folder_name="$(echo "$p" | sed 's|https://||; s|/|_|g')"
    mkdir "$folder_name"
    cd "$folder_name" || exit

    # Check if the URL points to a file or a directory
    if [[ "$p" == */ ]]; then
        # If the p ends with a '/', treat it as a directory
        wget -nv -r -l1 --no-parent "$p"
    else
        # Otherwise, treat it as a file
        wget -nv "$p"
    fi

    # Create or clear the output file
    >'checksum.md5'
    # Find all files and generate their MD5 checksums
    find . -type f -exec md5sum {} \; >>'checksum.md5'
    echo "checksum.md5 has been created"
    cd ..
done <"$1"
