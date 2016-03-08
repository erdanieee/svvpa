#!/bin/bash

source $(dirname $0)/CONSTANTS.sh
exec &> >(tee -a $LOG_FILE})

echo "[$(date)] $0: actualizando tráfico en ${VNSTAT_INTERFACE}"
sudo ${VNSTAT_BIN} -u -i ${VNSTAT_INTERFACE}
