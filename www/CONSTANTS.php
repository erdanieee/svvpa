<?php

#define user/pass MYSQL. Debe tener permisos SELECT
define("MYSQL_USER","web");
define("MYSQL_PASS", "readSensors");
define('MYSQL_DB', "svvpa");
define('MYSQL_SERVER','localhost');

define('MOTION_DIR','motion');
define('MOTION_IMAGE_EXT','jpg');
define('MOTION_VIDEO_EXT','mp4');
define('MOTION_TEMP_DIR','/tmp/motion');
define('MOTION_VIDEO_EXT_RAW','avi');

define('RCLONE_BIN','/home/dan/software/rclone-v1.27-linux-amd64/rclone');

?>
