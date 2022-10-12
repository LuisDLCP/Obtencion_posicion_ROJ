#!/bin/bash
# This script copies position files (*.pos) to a destination
# Previously these files are compressed 
FOLDER_HOME="/home/cesar/Desktop/luisd/scripts/"
FOLDER_SRC="${FOLDER_HOME}Obtencion_posicion/Output_files/"
FOLDER_SRC2="${FOLDER_HOME}Obtencion_posicion/Output_files/ToUpload/"
FOLDER_DST="${FOLDER_HOME}Main/Output_files/ToUpload/"

echo 'Compressing and moving pos files'

# Compressing files
gzip --force ${FOLDER_SRC}*pos ${FOLDER_SRC2}*pos 

# Moving files 
mv ${FOLDER_SRC2}*pos.gz ${FOLDER_DST}

echo 'Done!'
