#!/bin/sh

iface_wifi='wlan0'
iface_3g='wan3'
test_ip='8.8.8.8'


#$1 - interface
testConn(){
    if [[ "$1" ]]
    then
        ping -c 1 -q -w 10 -I $1 $test_ip
        ret=$?
    else
        ping -c 1 -q -w 10 $test_ip
        ret=$?
    fi
    return $ret
}

start3g(){
    echo "starting 3g"
    usbmode -s
    ifup $iface_3g
}

stop3g(){
    echo "stoping 3g"
    ifdown $iface_3g
}


#test connection
testConn
if [[ $? == "0" ]]
then
    testConn $iface_wifi
    if [[ $? == "0" ]]
    then
        stop3g 
    else
	echo "nothing to do"
    fi

else
    stop3g
    sleep 5
    start3g    
fi

