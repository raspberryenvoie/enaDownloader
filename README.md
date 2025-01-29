# enaDownloader

Download an entire study accession from the European Nucleotide Archive (ENA)

## I. Usage

### A. Download structure

These scripts download files in a separate folder, generate their md5 and output it to a `checksum.md5` file.

### B. ENA Downloader

```bash
python enaDownloader.py <filename>
```
The supplied file should contain one valid study accession code per line (e. g. `PRJNA603343`).

> The python script downloads the files in BAM format if they are available; otherwise, it will download them in FASTQ format.


### C. Direct link download

```bash
./directDownloader <filename>
```

The supplied file should contain one valid link per line.
