<?php
require_once('../config/CONSTANTS.php');

$image = MOTION_DIR . '/' . htmlspecialchars($_GET["n"]) . '.' . MOTION_IMAGE_EXT;
$video = MOTION_DIR . '/' . htmlspecialchars($_GET["n"]) . '.' . MOTION_VIDEO_EXT;
$back  = htmlspecialchars($_GET["b"]);

try {
	unlink($video);
} catch (Exception $e) {}

try {
	unlink($image);
} catch (Exception $e) {}

if ($back){
	header( 'Location: /'.$back ) ;
} else {
	header( 'Location: /index.php' ) ;
}

die();

?>
