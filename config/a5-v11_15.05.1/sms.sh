#!/bin/sh
# $1 RECEIVED
# $2 filename


aux=$(egrep -i From $2|egrep '(620579969)|(679878862)')


if [[ "$aux" ]]
then
  rm $2
  date >> /root/sms_shutdown
  (echo -e "GET /reboot.php\r\n"|nc 192.168.1.10 80) && reboot -f  

else
  echo "banned $2" >> /root/sms_shutdown
  cat $2 >> /root/sms_shutdown
  echo >> /root/sms_shutdown
  rm $2
fi

