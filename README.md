# Nanopore sequencing provides rapid and reliable insight into microbial profiles of Intensive Care Units
__Guilherme Marcelino Viana de Siqueira, Felipe Marcelo Pereira-dos-Santos, Rafael Silva-Rocha, María-Eugenia Guazzaroni__

In this repository we provide a custom pipeline for taxonomic assignment of long-read 16S sequencing. We have submitted this work in the Biorxiv (we'll update the link as soon as it is available)


## Usage

In Python, import the library provided in minion_analysis.py with the following command:

`import minion_analysis`

Next, provide paths in which demultiplexed sequencing files (.FASTQ) might be found. Assuming that we have our demultiplexed files for two sequencing runs in the subdirectories `Experiment1` and `Experiment2`, within a directory `experiment_data` in the user's Documents directory, the command would look like:
```
path = '/home/user/Documents/experiment_data'
lib = ['Experiment1', 'Experiment2']
```
The next steps automate the pipeline guppy_barcoder (for removing barcodes) -> NanoFilt -> Minimap2. The minimap2 step depends on the file refseq_16S.fa, that can be found in this repository

```
HC_analysis = minion_analysis.Analysis(path, lib)

HC_analysis.merge_files(cpus = 4)

HC_analysis.guppy_barcoder(cpus = 2)

HC_analysis.nanofilt(q = 7, cpus=2, just_filt = False)

HC_analysis.minimap(refseqpath = path, nanofilt_q = 7, cpus = 2)

HC_analysis.taxonomy(cpus = 2)
```

After processing the files, obtaining the read count for each resulting alignment files (.paf)can be done with the `alignment-parser.R` script.

``Rscript --vanilla ./alignment-parser.R [path] [lib(s)]``

For this, the `nametable.tsv` file (that relates NCBI accession numbers and species names)  should be located in a directory within the working environment.
