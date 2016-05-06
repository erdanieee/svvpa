#!/bin/bash
#Imprime los Mb gastados en el mes para la interfaz de red


source $(dirname $0)/CONSTANTS.sh
#touch ${LOG_FILE}; exec &> >(tee -a ${LOG_FILE})

sudo ${VNSTAT_BIN} -u -i ${VNSTAT_INTERFACE} 2>&1 > /dev/null
${VNSTAT_BIN} --dumpdb -i ${VNSTAT_INTERFACE}|egrep 'm;0'|awk -F";" '{print $6+$7}'

