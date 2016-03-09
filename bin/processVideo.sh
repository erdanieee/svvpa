#!/bin/bash

source $(dirname $0)/CONSTANTS.sh
touch ${LOG_FILE}; exec &> >(tee -a ${LOG_FILE})

fileIn=$1

if [[ $# -eq 1 ]]
then
	echo "[$(date)] $0: Procesando vídeo $fileIn"

	if [[ ! -e $fileIn || ! -f $fileIn ]]
	then
		echo "[$(date)] $0: ERROR! Archivo de origen no existe o es un directorio: $fileIn"
		exit 1
	fi

	mkdir -p ${MOTION_DIR} 2>/dev/null

	echo "[$(date)] $0: Convirtiendo vídeo a formato .${MOTION_VIDEO_EXT}"
	fileOut=${MOTION_DIR}${fileIn/\.${MOTION_VIDEO_EXT_RAW}/\.${MOTION_VIDEO_EXT}}
	#TODO: usar avconv (see http://www.thehelloworldprogram.com/web-development/encode-video-and-audio-for-html5-with-avconv/)
	${FFMPEG_BIN} -i $fileIn -preset ultrafast -y ${fileOut}	

	if [[ ! -e $fileOut || ! -f $fileOut ]]
	then
		echo "[$(date)] $0: ERROR! La conversión del archivo $fileIn ha fallado"
		exit 1
	fi

	echo "[$(date)] $0: borrando vídeo original"
	chmod 664 $fileOut
	rm -f $fileIn 

else
	echo "[$(date)] $0: ERROR! Invalid number of arguments: $#"
exit 1
fi
