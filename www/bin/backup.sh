#!/bin/bash

mkdir ~/backup 2>/dev/null
tar -zcvf ~/backup/www-`date +%Y%m%d`.tar.gz --exclude='motion' /var/www

