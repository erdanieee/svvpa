#!/bin/bash

. CONSTANTS.sh

mkdir ~/backup 2>/dev/null
tar -zcvf ~/backup/www-`date +%Y%m%d`.tar.gz --exclude=${MOTION_DIR} $dir

