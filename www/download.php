<?php
require_once('CONSTANTS.php');


function endsWith($haystack, $needle) {
    // search forward starting from end minus needle length characters
    return $needle === "" || (($temp = strlen($haystack) - strlen($needle)) >= 0 && strpos($haystack, $needle, $temp) !== false);
}


$file = MOTION_DIR . htmlspecialchars($_GET["n"]);

$contentType="image/jpg";
if (endsWith($file, "mp4")) {
	$contentType="video/mp4";
}

if (! $file) {
	die('file not found'); //Or do something 
} else {
	header("Cache-Control: public");
	header("Content-Description: File Transfer");
	header("Content-Disposition: attachment; filename=".basename($file));
	//header("Content-Type: application/zip");
	header("Content-Type: ".$contentType);
	header("Content-Transfer-Encoding: binary");
	// Read the file from disk
	readfile($file); 
}
?> 
