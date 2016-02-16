#!/bin/bash

if [ -z "${APACHE_DIR}" ]
then
	echo "ERROR: No se ha cargado la librería de variables env.sh!!!"
	exit 1
fi


cd ${APACHE_DIR}/bin

cpuTemp="$(sudo ./readInternalTemp.sh)"
bmp180Pres="$(sudo ./readBmp180Press.py)"
bmp180Temp="$(sudo ./readBmp180Temp.py)"


dht22Val=$(sudo ./readDht22HrTemp.py)
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

mysql -u temp -preadtemperature svvpa < <(echo "insert into sensors (CPU_temp, BMP180_temp, BMP180_press, DHT22_temp, DHT22_HR) values ($cpuTemp, $bmp180Temp, $bmp180Pres, $dht22Temp, $dht22Hr)")

./updateGoogleSpreadsheetSensors.py $cpuTemp $bmp180Temp $bmp180Pres $dht22Temp $dht22Hr

#echo "insert into sensors (CPU_temp, BMP180_temp, BMP180_press, DHT22_temp, DHT22_HR) values ($cpuTemp, $bmp180Temp, $bmp180Pres, $dht22Temp, $dht22Hr)"