#!/bin/bash

source $(dirname $0)/CONSTANTS.sh
touch ${LOG_FILE}; exec &> >(tee -a ${LOG_FILE})


case $1 in
	shutdown)
	python _sendEmailShutdown.py
	RETVAL=$?
	;;
 
	startup)
	python _sendEmailStartup.py
	RETVAL=$?
	;;
 
	*)
 	echo "[$(date)] $0: Comando '$1' no reconocido"	
	RETVAL=99
	esac

exit ${RETVAL}

