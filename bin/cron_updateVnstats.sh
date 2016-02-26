#!/bin/bash

source $(dirname $0)/CONSTANTS.sh

sudo ${VNSTAT_BIN} -u -i ${VNSTAT_INTERFACE}
