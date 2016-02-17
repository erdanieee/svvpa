#!/bin/bash

source ${CONFIG_DIR}CONSTANTS.sh

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

	mdir -p $dirOut 2>/dev/null

	fileOut=${dirOut}"/"$(basename $fileIn)
	fileOut=${fileOut/.${MOTION_IMAGE_EXT}/.${MOTION_VIDEO_EXT}}
	#TODO: usar avconv (see http://www.thehelloworldprogram.com/web-development/encode-video-and-audio-for-html5-with-avconv/)
	${FFMPEG_BIN} -i $fileIn -preset ultrafast -y ${fileOut}	

	if [[ ! -e $fileOut || ! -f $fileOut ]]
	then
		logger "$0 - ERROR! La conversión del archivo $fileIn ha fallado"
		exit 1
	fi

	chmod 666 $fileOut
	rm -f $fileIn 

else
	logger "$0 ERROR! Invalid number of arguments: $#"
exit 1
fi
