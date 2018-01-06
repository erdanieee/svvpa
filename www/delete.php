<?php
require_once('CONSTANTS.php');

/* if started from commandline, wrap parameters to $_POST and $_GET */
if (!isset($_SERVER["HTTP_HOST"])) {
  parse_str($argv[1], $_GET);
  parse_str($argv[1], $_POST);
}

$capturesID = explode(":", htmlspecialchars($_GET["n"]));
$back  = htmlspecialchars($_GET["b"]);

var_dump($capturesID);

try {
	foreach ($capturesID as $id){
		$image = MOTION_DIR . $id . '.' . MOTION_IMAGE_EXT;	
		$video = MOTION_DIR . $id . '.' . MOTION_VIDEO_EXT;
		unlink($video);
		unlink($image);
	}
} catch (Exception $e) {
	echo 'Caught exception: ',  $e->getMessage(), "\n";	
}

if ($back){
	header( 'Location: /'.$back ) ;
} else {
	header( 'Location: /index.php' ) ;
}

die();

?>
