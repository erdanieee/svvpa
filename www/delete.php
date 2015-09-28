<?php
$image = 'motion/' . htmlspecialchars($_GET["n"]) . '.jpg';
$video = 'motion/' . htmlspecialchars($_GET["n"]) . '.mp4';
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
