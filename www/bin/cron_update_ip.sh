#!/bin/bash

if [[ -z "$CURRENT_IP_FILE" || -z "${DUCKDNS_TOKEN}" ]]
then
	echo "Error!! No se ha cargado el archivo fuente con todas las variables!!!"
	exit 1
fi

echo "Updating svvpa.duckdns.org"
echo url="https://www.duckdns.org/update?domains=${DUCKDNS_DOMAIN}&token=${DUCKDNS_TOKEN}&ip=" | curl -k -K -
r1=$?
echo

echo "Saving ip to ${CURRENT_IP_FILE}"
ip=$(wget "http://ipecho.net/plain" -qO -)
r2=$?

if [[ $r2 -eq 0 ]]
then
  echo "OK"
else
  echo "ERROR!"
fi


echo "Uploading IP file to Google Drive"
echo "http://${DUCKDNS_DOMAIN}.duckdns.org:${APACHE_PORT}" > ${CURRENT_IP_PATH}${CURRENT_IP_FILE} 
echo "http://$ip:${APACHE_PORT}" >> ${CURRENT_IP_PATH}${CURRENT_IP_FILE}
${RCLONE_BIN} copy ${CURRENT_IP_PATH}${CURRENT_IP_FILE} google:SVVPA/ 2>&1
r3=$?

if [[ $r1 -eq 0 && $r2 -eq 0  && $r3 -eq 0 ]]
then
  echo
  echo "Ip actualizada correctamente. Este servidor se puede acceder desde $(cat ${CURRENT_IP_PATH}${CURRENT_IP_FILE})"
else
  echo "Hubo errores. Por favor, revisa los parámetros y si los sitios web están funcionando"
  exit 1		
fi