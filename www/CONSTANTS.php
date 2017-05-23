<?php

$v=array(
	'MYSQL_USER',
	'MYSQL_PASS',
	'MYSQL_DB',
	'SVVPA_DIR',
	'BIN_DIR',
	'CONFIG_DIR',
	'APACHE_DIR',
	'MOTION_DIR',
	'MOTION_IMAGE_EXT',
	'MOTION_VIDEO_EXT',
	'MOTION_TEMP_DIR',
	'MOTION_VIDEO_EXT_RAW',
	'RCLONE_BIN',
	'RCLONE_CONFIG');

for ($i=0; $i<count($v); $i++){
	define("$v[$i]", exec("bash -c 'source ../bin/CONSTANTS.sh; echo \$$v[$i]'"));
}

define('MYSQL_SERVER','localhost');

?>
