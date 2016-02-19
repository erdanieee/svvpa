#!/bin/bash

source $(dirname $0)/CONSTANTS.sh

fileIn=$1

if [[ $# -eq 1 ]]
then
	logger "$(basename $0) DEBUG $@"

	if [[ ! -e $fileIn || ! -f $fileIn ]]
	then
		logger "$0 - ERROR! Archivo de origen no existe o es un directorio: $fileIn"
		exit 1
	fi

	mkdir -p ${MOTION_DIR} 2>/dev/null

	#send file by email
	./_sendEmailImage.py $fileIn

	#move file to www
	chmod 664 $fileIn
	mv $fileIn ${MOTION_DIR}

else
	logger "$0 ERROR! Invalid number of arguments: $#"
	exit 1
fi	
