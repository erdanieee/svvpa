#!/bin/bash

source $(dirname $0)/CONSTANTS.sh
exec &> >(tee -a $LOG_FILE})

python _diskSpaceControl.py
