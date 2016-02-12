<?php
	$tempDir="/tmp/motion/";
	$targetDir="/var/www/motion/";	
	$id=htmlspecialchars($_GET["id"]);
	
	while ( file_exists($tempDir . $id . ".avi") ){
		sleep(10);
	}
	

?>
