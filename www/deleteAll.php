<?php
require_once('CONSTANTS.php');

function endsWith($haystack, $needle) {
	$length = strlen($needle);
	if ($length == 0) {
		return true;
	}
	return (substr($haystack, -$length) === $needle);
}

$back = htmlspecialchars($_GET["b"]);
$type	= htmlspecialchars($_GET["t"]);	#all to delete all files in motion directory

foreach (new DirectoryIterator(MOTION_DIR) as $fileInfo) {
	if(!$fileInfo->isDot() && ($type=="all" ||  endsWith($fileInfo->getFilename(), $type))){
		try {
			unlink(MOTION_DIR . $fileInfo->getBasename());
		} catch (Exception $e) {}
	}
}

if ($back){
	header( 'Location: /'.$back ) ;
} else {
	header( 'Location: /index.php' ) ;
}

die();

?>
