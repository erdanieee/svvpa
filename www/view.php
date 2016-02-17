<?php 
	require_once(CONFIG_DIR . 'CONSTANTS.php');

	$meses = [
		"01" => "Enero",
		"02" => "Febrero",
		"03" => "Marzo",
		"04" => "Abril",
		"05" => "Mayo",
		"06" => "Junio",
		"07" => "Julio",
		"08" => "Agosto",
		"09" => "Septiembre",
		"10" => "Octubre",
		"11" => "Noviembre",
		"12" => "Diciembre"];	
	$name = htmlspecialchars($_GET["n"]);
	list($y, $m, $d, $H, $M, $S, $p, $n, $J, $w, $h) = split ("_", $name);
?>


<!DOCTYPE html>
<html lang="es">
	<head>
		<?php require 'meta.php'; ?>
		<!--[if lte IE 8]><script src="js/html5shiv.js"></script><![endif]-->
		<script src="js/jquery.min.js"></script>
		<script src="js/skel.min.js"></script>
		<script src="js/skel-layers.min.js"></script>
		<script src="js/init.js"></script>
		<link rel="shortcut icon" type="image/x-icon" href="images/favicon.png" />
		<noscript>
			<link rel="stylesheet" href="css/skel.css" />
			<link rel="stylesheet" href="css/style.css" />
			<link rel="stylesheet" href="css/style-xlarge.css" />
		</noscript>
	</head>

	<body>
	<?php require 'header.php'; ?>

	<!-- Main -->
	<section id="main" class="wrapper">
		<div class="container">				
			<div class="12u 12u$(medium)">							
				<?php
				$isImage=file_exists (MOTION_DIR . $name . "." . MOTION_IMAGE_EXT);
				$isVideo=file_exists (MOTION_DIR . $name . "." . MOTION_VIDEO_EXT);

				echo "<h3>$d $meses[$m] $y</h3>";
				echo "<span class=\"image fit\">";
				if ($isVideo && $isImage){
					echo "<video width=\"100%\" controls poster=\"".MOTION_DIR."$name.".MOTION_IMAGE_EXT."\" preload=\"none\" autoplay>";
					echo "<source src=\"".MOTION_DIR."$name.".MOTION_VIDEO_EXT."\" type=\"video/mp4\">";
					echo "</video>";

				} elseif ($isVideo){
					echo "<video width=\"100%\" controls preload=\"none\" autoplay>";
					echo "<source src=\"".MOTION_DIR."$name.".MOTION_VIDEO_EXT."\" type=\"video/mp4\">";
					echo "</video>";

				} elseif ($isImage){
					echo "<img src=\"".MOTION_DIR."$name.".MOTION_IMAGE_EXT."\" />";
				}

				echo "</span>";
				echo "<ul class=\"actions\">";

				if ($isImage){
					echo "<li><a href=\"download.php?n=$name.".MOTION_IMAGE_EXT."\" class=\"button icon fa-download\">Imagen</a></li>";
				}

				if ($isVideo){									
				echo "<li><a href=\"download.php?n=$name.".MOTION_VIDEO_EXT."\" class=\"button icon fa-download\">Vídeo</a></li>";
				}
				echo "<li><a href=\"delete.php/?n=$name&amp;b=imagenes.php\" class=\"button icon special fa-remove\">Borrar</a></li>";
				echo "</ul>";
				#echo "</section>";
				?>									
			</div>
			<section class="6u(medium) 12u$(xsmall) profile">
				<p><span class="left"><i class="icon rounded fa-info"></i></span> Para visualizar el vídeo en <strong>pantalla completa</strong> pulsa sobre el icono <i class="icon fa-arrows-alt"></i> que está situado en la parte inferior derecha del vídeo.</p>
			</section>	
		</div>			
	</section>
	
	<?php require 'footer.php'; ?>

	</body>
</html>
