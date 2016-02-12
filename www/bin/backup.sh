#!/bin/bash

dir=${APACHE_DIR}

if [ -z "$dir" ]
then
	dir="../"
fi

mkdir ~/backup 2>/dev/null
tar -zcvf ~/backup/www-`date +%Y%m%d`.tar.gz --exclude='motion' $dir

