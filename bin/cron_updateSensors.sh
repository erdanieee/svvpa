#!/bin/bash


source $(dirname $0)/CONSTANTS.sh

function getMysqlVal(){ r="NULL"; if [[ "$1" ]]; then r="'$1'"; fi; echo $r; }
function getGoogleSpVal(){ r="nan"; if [[ "$1" ]]; then r="$1"; fi; echo ${r/\./\,}; }

cd ${BIN_DIR}

cpuTemp="$(sudo python readInternalTemp.sh)"
bmp180Pres="$(sudo python _readBmp180Press.py)"
bmp180Temp="$(sudo python _readBmp180Temp.py)"
dht22Val="$(sudo python _readDht22HrTemp.py)"
dht22Temp="$(echo $dht22Val|awk '{print $1}')"
dht22Hr="$(echo $dht22Val|awk '{print $2}')"

sqlStm=$(echo "insert into sensors (CPU_temp, BMP180_temp, BMP180_press, DHT22_temp, DHT22_HR) values ($(getMysqlVal $cpuTemp), $(getMysqlVal $bmp180Temp), $(getMysqlVal $bmp180Pres), $(getMysqlVal $dht22Temp), $(getMysqlVal $dht22Hr))")
echo $sqlStm

mysql -u ${MYSQL_USER} -p${MYSQL_PASS} ${MYSQL_DB} < <(echo $sqlStm)

python _updateGoogleSpreadsheetSensors.py $(getGoogleSpVal $cpuTemp) $(getGoogleSpVal $bmp180Temp) $(getGoogleSpVal $bmp180Pres) $(getGoogleSpVal $dht22Temp) $(getGoogleSpVal $dht22Hr)

