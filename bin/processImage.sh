#!/bin/bash

source $(dirname $0)/CONSTANTS.sh
exec &> >(tee -a $LOG_FILE})

fileIn=$1

if [[ $# -eq 1 ]]
then
	echo "[$(date)] $0: Procesando archivo $fileIn"

	if [[ ! -e $fileIn || ! -f $fileIn ]]
	then
		echo "[$(date)] $0: ERROR! Archivo de origen no existe o es un directorio: $fileIn"
		exit 1
	fi

	mkdir -p ${MOTION_DIR} 2>/dev/null

	#send file by email
	echo "[$(date)] $0: enviando imagen por email"
	python _sendEmailImage.py $fileIn

	#move file to www
	echo "[$(date)] $0: Moviendo $fileIn a ${MOTION_DIR}"
	chmod 664 $fileIn
	mv $fileIn ${MOTION_DIR}$(basename $fileIn)
	
else
	echo "[$(date)] $0: ERROR! Invalid number of arguments: $#"
	exit 1
fi	
