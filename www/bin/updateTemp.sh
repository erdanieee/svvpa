#!/bin/bash

mysql -u temp -preadtemperature svvpa < <(echo "insert into temp (temp) values ($(echo "scale=2; $(cat /sys/class/thermal/thermal_zone0/temp) / 1000"|bc)) ")
