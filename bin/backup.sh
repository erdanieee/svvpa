#!/bin/bash

source $(dirname $0)/CONSTANTS.sh

mkdir ~/backup 2>/dev/null
tar -zcvf ~/backup/www-`date +%Y%m%d`.tar.gz --exclude=${MOTION_DIR} ${APACHE_DIR}

