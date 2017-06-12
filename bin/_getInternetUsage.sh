#!/bin/bash
#Imprime los MB gastados en el mes para la interfaz de red

source $(dirname $0)/CONSTANTS.sh
sqlStm=$(echo "select sum(bytes)/1000000 from (select bytes from internetUsage where YEAR(date) = YEAR(NOW()) and MONTH(date) = MONTH(NOW())) s;")
mysql -u ${MYSQL_USER} -p${MYSQL_PASS} ${MYSQL_DB} --skip-column-names < <(echo $sqlStm)
