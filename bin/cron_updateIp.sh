#!/bin/bash

source $(dirname $0)/CONSTANTS.sh
touch ${LOG_FILE}; exec &> >(tee -a ${LOG_FILE})

echo "[$(date)] $0: Updating svvpa.duckdns.org"
echo url="https://www.duckdns.org/update?domains=${DUCKDNS_DOMAIN}&token=${DUCKDNS_TOKEN}&ip=" | curl -k -K -
r1=$?
echo

echo "[$(date)] $0: Saving ip to $(basename ${CURRENT_IP_FILE})"
ip=$(wget "http://ipecho.net/plain" -qO -)
r2=$?

if [[ $r2 -eq 0 ]]
then
  echo "[$(date)] $0: OK"
else
  echo "[$(date)] $0: ERROR!"
fi


echo "[$(date)] $0: Uploading IP file to Google Drive"
echo "http://${DUCKDNS_DOMAIN}.duckdns.org:${APACHE_PORT}" > ${CURRENT_IP_FILE} 
echo "http://$ip:${APACHE_PORT}" >> ${CURRENT_IP_FILE}
${RCLONE_BIN} --config ${RCLONE_CONFIG} copy ${CURRENT_IP_FILE} google:SVVPA/ 2>&1
r3=$?

if [[ $r1 -eq 0 && $r2 -eq 0  && $r3 -eq 0 ]]
then
  echo
  echo "[$(date)] $0: Ip actualizada correctamente. Este servidor se puede acceder desde $(cat ${CURRENT_IP_FILE})"
else
  echo "[$(date)] $0: Hubo errores. Por favor, revisa los parámetros y si los sitios web están funcionando"
  exit 1		
fi
