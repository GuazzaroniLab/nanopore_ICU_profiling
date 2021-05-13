#!/usr/bin/env Rscript


# This script takes as arguments paths to directories containing .paf files generated in
# the previous step of our pipeline and returns .tsv files with read counts for each
# assigned species

# Depends on:
# - a 16S rRNA RefSeq table present in the path /ncbi/nametable.tsv 

# Arguments:
# - path: the absolute path to the parent folder containing different libs (e.g. ~/Documents/)
# - lib: the prefix used to generate directories in the previous step (e.g. experiment1)

# Loading the required packages

if (!require(pafr)) {
  install.packages("pafr")
  suppressPackageStartupMessages(library(pafr, quietly = TRUE))
} else {
  suppressPackageStartupMessages(library(pafr, quietly = TRUE))
}

if (!require(tidyverse)) {
  install.packages("tidyverse")
  suppressPackageStartupMessages(library(tidyverse, quietly = TRUE))
} else {
  suppressPackageStartupMessages(library(tidyverse, quietly = TRUE))
}

# Reading the arguments provided in the command-line

args <- commandArgs(trailingOnly = TRUE)

path <- args[1]
lib <- args[2]

# importing the refseq 16S rRNA database

name_table <- read_tsv(file = paste(path, "/ncbi/nametable.tsv", sep = ''), col_names = TRUE, col_types = c(col_character(), col_character()))

# Looping over the files in the provided paths and parsing the .paf files

for (libs in lib) {  
  
  file_list <- list.files(path = paste(path, "/", libs, "/Files_barcodes/", libs, "_minimap/", sep = ''))
  file_list <- file_list[file_list != 'tables']
  
  for (files in file_list) {
    
    message("Starting analysis")
    input_file <- paste(path, "/", libs, "/Files_barcodes/", libs, "_minimap/", files, sep = '')
    output_file <- paste(path, "/", libs, "/Files_barcodes/", libs, "_minimap/tables/", files, sep = '')
    
    paf <- read_paf(file = input_file, tibble = TRUE)
    
    paf_count <- paf %>%
      filter(mapq != 0 & nmatch > 1000) %>% # PLACE TO LOOK FOR IF TUNING THE STRICTNESS OF THE SCRIPT
      mutate(species = map_chr(.$tname, ~ {idx <- match(.x, name_table$accession)
      return(name_table$name[idx])}
      )) %>%
      group_by(species) %>%
      tally(sort = TRUE)
      
    # saving the final table
    output_name <- paste0(output_file, "_taxCount.tsv")
    message("Writing output")
    write_tsv(x = paf_count, file = output_name)
  
  }
}
