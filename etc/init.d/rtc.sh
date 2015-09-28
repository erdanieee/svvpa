#! /bin/sh
### BEGIN INIT INFO
# Provides:          skeleton
# Required-Start:    $remote_fs $syslog
# Required-Stop:     $remote_fs $syslog
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Example initscript
# Description:       This file should be used to construct scripts to be
#                    placed in /etc/init.d.
### END INIT INFO

# Author: Foo Bar <foobar@baz.org>
#
# Please remove the "Author" lines above and replace them
# with your own name if you copy and modify this script.

# Do NOT "set -e"

# PATH should only include /usr/* if it runs after the mountnfs.sh script
PATH=/sbin:/usr/sbin:/bin:/usr/bin
DESC="gestiona el módulo RTC"


case "$1" in
  start)
	echo ds3231 0x68 > /sys/class/i2c-adapter/i2c-1/new_device
	;;
  stop)
	echo 0x68 > /sys/class/i2c-adapter/i2c-1/delete_device
	;;
  status)
	hwclock -r
	;;
  *)
	echo "Usage: $(basename $0) {start|stop|status|restart|force-reload}" >&2
	exit 3
	;;
esac


