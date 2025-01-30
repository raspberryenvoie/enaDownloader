#!/usr/bin/env python3
## Usage: python enaDownloader.py <filename>
## <filename> contains one study accession code per line
import json
## Added comment
import requests
import os
import sys
import hashlib
from datetime import datetime
import time
import random

downloadCounts = 1

def download_json(accession):
    # Construct the URL
    url = f"https://www.ebi.ac.uk/ena/portal/api/filereport?accession={accession}&result=read_run&fields=study_accession,sample_accession,experiment_accession,run_accession,tax_id,scientific_name,fastq_ftp,submitted_ftp,sra_ftp,bam_ftp&format=json&download=true&limit=0"

    # Download the JSON data
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses
        json_data = response.json()  # Parse the JSON response
        printLog("JSON data downloaded successfully: " + accession)
        return json_data
    except requests.exceptions.RequestException as e:
        printLog(f"Error downloading JSON data: {e}")
        return

def printLog(message):
    print("" + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " " + message, flush=True)

# Function to download a file
def download_file(url, folder, filename):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raise an error for bad responses
        md5_hash = hashlib.md5()  # Create an MD5 hash object
        file = os.path.join(folder, filename)
        with open(file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                md5_hash.update(chunk)  # Update the hash with the chunk
        # Get the hexadecimal digest of the MD5 hash
        md5sum = md5_hash.hexdigest()
        
        # Append the MD5 checksum to 
        md5_file = os.path.join(folder, 'checksum.md5')
        with open(md5_file, 'a') as checksum_file:
            checksum_file.write(f"{md5sum}  {filename}\n")  # Format: <md5sum>  <filename>

        printLog(f"Downloaded: {filename} with MD5: {md5sum}")

        # Wait to mitigate the ENA browser rate limit
        time.sleep(random.uniform(1, 3))  # Wait between 1 and 3 seconds
        printLog("Waiting between 1 and 3 seconds to start next download")

        global downloadCounts  # Necessary to modify the global variable
        downloadCounts += 1    # Increment the global variable
        if downloadCounts == 50:
            downloadCounts = 1
            printLog("Pausing for 30 seconds...")
            time.sleep(30)

    except Exception as e:
        printLog(f"Failed to download {url}: {e}")

def download_files(urls, folder):
    download_urls = urls.split(';')
    # Download each file
    for url in download_urls:
        filename = url.split('/')[-1]  # Extract the filename from the URL
        download_file("https://" + url, folder, filename)

def downloadFromJson(data):
# Iterate through each entry in the JSON data
    for entry in data:
        study_accession = entry.get('study_accession')

        # Create a directory for the study_accession if it doesn't exist
        if study_accession:
            os.makedirs(study_accession, exist_ok=True)

        # Check if bam_ftp has a value
        bam_ftp = entry.get('bam_ftp')
        fastq_ftp = entry.get('fastq_ftp')

        if bam_ftp:
            download_files(bam_ftp, study_accession)
        elif fastq_ftp:
            download_files(fastq_ftp, study_accession)
        else:
            printLog(f"No files to download for run_accession: {entry['run_accession']}")

def main():
    # Check if the filename is provided as an argument
    if len(sys.argv) != 2:
        printLog("Usage: python enaDownloader.py <filename>")
        sys.exit(1)

    # Get the filename from the command-line argument
    filename = sys.argv[1]

    try:
        # Open the file and iterate over each line
        with open(filename, 'r') as file:
            for line in file:
                # Strip whitespace and print the line
                json_data = download_json(line.strip())
                downloadFromJson(json_data)
    except FileNotFoundError:
        printLog(f"Error: The file '{filename}' was not found.")
    except Exception as e:
        printLog(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
