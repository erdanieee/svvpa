#!/bin/bash
#Imprime los bytes enviados y recibidos durante el mes en curso

if [[ $# -gt 0 ]]
then
    source $(dirname $0)/CONSTANTS.sh

    cd ${BIN_DIR}

    b_adjust=$1
    b_current=$( ./_getInternetUsage.sh );
    b_diff=$( echo $b_adjust - $b_current |bc )

    echo $b_diff

    sleep 1     #necesario para que no haya duplicación de PRIMARY_KEY, ya que _getInternetUsage actualiza la tabla
    sqlStm=$(echo "insert into internetUsage (bytes_out) values ($b_diff)")
    mysql -u ${MYSQL_USER} -p${MYSQL_PASS} ${MYSQL_DB} < <(echo $sqlStm)

else
    echo "USAGE $(basename $0)  <setToTotalBytes>"
    exit
fi


