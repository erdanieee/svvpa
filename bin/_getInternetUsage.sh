#!/bin/bash
#Imprime los bytes enviados y recibidos durante el mes en curso

source $(dirname $0)/CONSTANTS.sh
sqlStm=$(echo "select (sum(bytes_in)+sum(bytes_out)) from (select bytes_in, bytes_out from internetUsage where YEAR(date) = YEAR(NOW()) and MONTH(date) = MONTH(NOW())) s;")

sudo /usr/sbin/service SVVPA-service update_internetUsage 2>&1 >/dev/null
mysql -u ${MYSQL_USER} -p${MYSQL_PASS} ${MYSQL_DB} --skip-column-names < <(echo $sqlStm)
