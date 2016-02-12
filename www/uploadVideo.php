<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
</head>
<body>

<?php
	$targetDir=system('echo $PWD') . "/motion/";	
	$id=htmlspecialchars($_GET["id"]);
	
	while ( file_exists(getenv("MOTION_TEMP_DIR") . $id . ".avi") ){
		sleep(10);
	}
	
	echo '<h5>Transfiriendo imagen...</h5>';
	echo '<pre>';
	system(getenv("RCLONE_BIN") . ' copy ' . $targetDir . $id . ".jpg" . " google:SVVPA/imagenes 2>&1", $out1);	
	echo '</pre>';

//	echo '<br><br>';	

	echo '<h5>Transfiriendo video...</h5>';
	echo '<pre>';
	system(getenv("RCLONE_BIN") . ' copy ' . $targetDir . $id . ".mp4" . " google:SVVPA/videos 2>&1", $out2);
	echo '</pre>';

	echo '<br>';	
	if ($out1==0 && $out2==0){
		echo '<h3>Google Drive sincronizado correctamente!!</h3>';
	} else{
		echo '<h3 style="color:red">¡Ha habido algún problema al sincronizar los archivos. Inténtalo de nuevo más tarde y si sigue fallando contacta con Er Danié!</h3>';
	}
	
?>

</body>
</html>
