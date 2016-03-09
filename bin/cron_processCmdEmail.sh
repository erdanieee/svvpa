#!/bin/bash

source $(dirname $0)/CONSTANTS.sh
exec &> >(tee -a {$LOG_FILE})

echo "[$(date)] $0: Procensando comando email"
python _processCmdEmail.py 
