#!/bin/bash

fileIn=$1
dirOut=$2

if [[ $# -eq 2 ]]
then
	logger "$(basename $0) DEBUG $@"

	if [[ ! -e $fileIn || ! -f $fileIn ]]
	then
		logger "$0 - ERROR! Archivo de origen no existe o es un directorio: $fileIn"
		exit 1
	fi

	if [[ ! -d $dirOut ]]
        then
                logger "$0 - ERROR! El directorio de destino no existe: $dirOut"
        	exit 1
        fi

	chmod 775 $fileIn
	mv $fileIn $dirOut
	

else
	logger "$0 ERROR! Invalid number of arguments: $#"
	exit 1
fi	
