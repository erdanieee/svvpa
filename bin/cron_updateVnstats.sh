#!/bin/bash

source $(dirname $0)/CONSTANTS.sh
exec &> >(tee -a $LOG_FILE})

sudo ${VNSTAT_BIN} -u -i ${VNSTAT_INTERFACE}
