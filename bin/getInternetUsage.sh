#!/bin/bash
#Imprime los Mb gastados en el mes para la interfaz de red


source $(dirname $0)/CONSTANTS.sh

${VNSTAT_BIN} --dumpdb -i ${VNSTAT_INTERFACE}|egrep 'm;0'|awk -F";" '{print $4+$5}'
