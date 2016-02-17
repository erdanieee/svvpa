#!/bin/bash

source ${CONFIG_DIR}CONSTANTS.sh

cd ${BIN_DIR}

cpuTemp="$(sudo ./readInternalTemp.sh)"
bmp180Pres="$(sudo ./_readBmp180Press.py)"
bmp180Temp="$(sudo ./_readBmp180Temp.py)"


dht22Val="$(sudo ./_readDht22HrTemp.py)"
dht22Temp="$(echo $dht22Val|awk '{print $1}')"
dht22Hr="$(echo $dht22Val|awk '{print $2}')"


[ "$cpuTemp" ] && cpuTemp="'$cpuTemp'" || cpuTemp="NULL"
[ "$bmp180Pres" ] && bmp180Pres="'$bmp180Pres'" || bmp180Pres="NULL"
[ "$bmp180Temp" ] && bmp180Temp="'$bmp180Temp'" || bmp180Temp="NULL"
[ "$dht22Temp" ] && dht22Temp="'$dht22Temp'" || dht22Temp="NULL"
[ "$dht22Hr" ] && dht22Hr="'$dht22Hr'" || dht22Hr="NULL"


echo $cpuTemp
echo $bmp180Pres
echo $bmp180Temp
echo $dht22Val
echo $dht22Temp
echo $dht22Hr
echo

mysql -u ${MYSQL_USER} -p${MYSQL_PASS} ${MYSQL_DB} < <(echo "insert into sensors (CPU_temp, BMP180_temp, BMP180_press, DHT22_temp, DHT22_HR) values ($cpuTemp, $bmp180Temp, $bmp180Pres, $dht22Temp, $dht22Hr)")

./_updateGoogleSpreadsheetSensors.py $cpuTemp $bmp180Temp $bmp180Pres $dht22Temp $dht22Hr

