<?php 
require_once('CONSTANTS.php');
?>

<html>
	<head>
		<?php require 'meta.php'; ?>
	</head>

	<body>
	<?php
		$id=htmlspecialchars($_GET["id"]);
		while ( file_exists(MOTION_TEMP_DIR . $id . "." . MOTION_VIDEO_EXT_RAW) ){
			sleep(10);
		}
	
		echo '<h5>Transfiriendo imagen...</h5>';
		ob_flush();
		flush();
		echo '<pre>';
		system(RCLONE_BIN . ' --config '. RCLONE_CONFIG .' copy ' . MOTION_DIR . $id . "." . MOTION_IMAGE_EXT . " google:SVVPA/imagenes 2>&1", $out1);	
		echo '</pre>';

	//	echo '<br><br>';	

		echo '<h5>Transfiriendo video...</h5>';
		ob_flush();
		flush();
		echo '<pre>';
		system(RCLONE_BIN . ' --config '. RCLONE_CONFIG .' copy ' . MOTION_DIR . $id . "." . MOTION_VIDEO.EXT . " google:SVVPA/videos 2>&1", $out2);
		echo '</pre>';
		echo '<br>';	
		if ($out1==0 && $out2==0){
			echo '<h3>Google Drive sincronizado correctamente!!</h3>';
		} else{
			echo '<h3 style="color:red">¡Ha habido algún problema al sincronizar los archivos. Inténtalo de nuevo más tarde y si sigue fallando contacta con Er Danié!</h3>';
		}
		ob_flush();
		flush();	
	?>

	</body>
</html>
