#!/bin/sh

device="radio0"
keepAlive=/root/keep_wifi_alive


if [[ $# -lt 1 ]]
then
    echo "USAGE $(basename $0): <start|stop|status>"
    exit 1
fi


#case $(uci get wireless.$device.disabled) in
case $1 in
    stop)
        wifi down $device
        uci set wireless.$device.disabled=1
        echo "Wifi disabled"
    ;;
    start|restart)
        uci set wireless.$device.disabled=0
        wifi up $device
        echo "Wifi enabled"
    ;;
    status)
	ret=$(wifi status|grep up|egrep -o '(true)|(false)')
	($ret && echo enabled) || echo disabled
    ;;
esac

exit 0
