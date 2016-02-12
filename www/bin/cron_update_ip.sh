#!/bin/bash

echo "Updating svvpa.duckdns.org"
echo url="https://www.duckdns.org/update?domains=svvpa&token=b4d602f7-a21f-442d-a8da-a6bff50795f3&ip=" | curl -k -K -
r1=$?


echo
echo "Saving ip to current_ip.txt"
wget "http://ipecho.net/plain" -qO current_ip.txt
r2=$?

if [ $r2 ]
then
  echo "OK"
else
  echo "ERROR!"
fi


if [[ $r1 && $r2 ]]
then
  echo
  echo "Ip actualizada correctamente. Este servidor se puede acceder desde http://svvpa.duckdns.org o en http://$(cat current_ip.txt)"
else
  echo "Hubo errores. Por favor, revisa los parámetros y si los sitios web están funcionando"
  exit 1		
fi
