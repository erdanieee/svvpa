<?php
require_once('CONSTANTS.php');

function endsWith($haystack, $needle) {
	$length = strlen($needle);
	if ($length == 0) {
		return true;
	}
	return (substr($haystack, -$length) === $needle);
}

$type=htmlspecialchars($_GET["t"]);

$files=array();
foreach (new DirectoryIterator(MOTION_DIR) as $fileInfo) {
	if(!$fileInfo->isDot() && endsWith($fileInfo->getFilename(), $type)){
		$files[] = $fileInfo->getBasename();
	}
}

$zipname = '/tmp/imagenes_' . date("d-m-Y", time()) . '.zip';
$zip 		 = new ZipArchive;
$zip->open($zipname, ZipArchive::CREATE);
foreach ($files as $file) {
	$zip->addFile(MOTION_DIR . '/'.$file);
}
$zip->close();

header('Content-Type: application/zip');
header('Content-disposition: attachment; filename='.$zipname);
header('Content-Length: ' . filesize($zipname));
readfile($zipname);

unlink($zipname);
?>
