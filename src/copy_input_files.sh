#!/bin/bash
# This program obtains:
#   - MeasEpoch2
#   - ChannelStatus
# data from an SBF file 
# -------------------------------
INPUT_PATH='/media/cesar/Septentrio02/Binary/'
OUTPUT_PATH='/home/cesar/Desktop/luisd/scripts/Obtencion_posicion/Input_files/Data_set/'
COMPARE_PATH1='/media/cesar/Septentrio02/ISMR/'
COMPARE_PATH2='/home/cesar/Desktop/luisd/scripts/Obtencion_posicion/Input_files/Data_NMEA/'

FOLDERS=`diff -q ${COMPARE_PATH1} ${COMPARE_PATH2} | grep Only | grep ${COMPARE_PATH1} | awk '{print $4}'`

if [[ -z $FOLDERS ]]
then 
  echo "There isn't any new NMEA file yet!"
else
  echo "The new files are:"
  echo $FOLDERS
  for FOLDER in $FOLDERS
  do
    cp ${INPUT_PATH}${FOLDER}/*1 ${OUTPUT_PATH} 
    mkdir ${COMPARE_PATH2}${FOLDER}
  done
  echo "All NMEA files were copied sucesfully!"
fi

