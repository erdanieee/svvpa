#!/bin/bash

source $(dirname $0)/CONSTANTS.sh
touch ${LOG_FILE}; exec &> >(tee -a ${LOG_FILE})

mkdir ~/backup 2>/dev/null
f=~/backup/www-`date +%Y%m%d`.tar.gz
echo "[$(date)] $0: guardando copia de seguridad en $f"
tar -zcvf $f --exclude=${MOTION_DIR} ${APACHE_DIR}

