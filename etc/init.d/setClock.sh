#! /bin/sh
### BEGIN INIT INFO
# Provides:          puestaEnHora 
# Required-Start:    $remote_fs $syslog $all 
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
  start|write)
	(
		exec 2> /tmp/rc.local.log      # send stderr from rc.local to a log file
	        exec 1>&2                      # send stdout to the same log file
	        set -x                         # tell sh to display commands before execution
		sleep 20
		hwclock -w --debug
		echo "done!"
	) &
	;;
  *)
	echo "Usage: $(basename $0) {read}" >&2
	exit 3
	;;
esac


