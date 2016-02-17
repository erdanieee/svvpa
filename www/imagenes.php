<?php
require_once(CONFIG_DIR . 'CONSTANTS.php');

$filesByName = array();
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

function endsWith($haystack, $needle) {
	$length = strlen($needle);
	if ($length == 0) {
		return true;
	}
	return (substr($haystack, -$length) === $needle);
}




foreach (new DirectoryIterator(MOTION_DIR) as $fileInfo) {
	if(!$fileInfo->isDot() && ( endsWith($fileInfo->getFilename(),'.' . MOTION_IMAGE_EXT))){
		$file = $fileInfo->getBasename('.' . MOTION_IMAGE_EXT);
		list($y, $m, $d, $H, $M, $S, $p, $n, $J, $w, $h) = split ("_", $file);
		$key= $y . $m . $d . $H . $M . $S;

		$filesByName[] = array(
			"sorting" => $key,
			"name"		=> $file,
			"year"		=> $y,
			"month"		=> $m,
			"day"			=> $d
		);
	}
}

arsort($filesByName);
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
		<!-- Header -->
		<?php require 'header.php'; ?>

		<script>
		function deleteAll(){
			if (confirm('Se va a proceder a borrar todos los vídeos e imágenes. ¿Realmente deseas continuar?')) {
				$("#deleteAllForm").submit();
			}
		}
		</script>

		<!-- Main -->
		<section id="main" class="wrapper">
			<div class="container">
				<header class="major">
					<h2>Capturas</h2>
				</header>

				<h2>Información</h2>
				<p>Esta sección contiene una previsualización de los mejores momentos de cada vídeo. Esto permite hacerte una idea de lo que se ha grabado, y evitar así visualizar vídeos que solo tengan pequeños movimientos de hojas. Que no es por no visualizarlos... que si hay que visualizarlos se visualizan, pero visualizar los vídeos pa ná es tontería. Para ver los vídeos simplemente haz <strong>click</strong> en la imagen.</p>


				<div class="12u$"> 
					<ul class="actions">
						<li><a href="downloadAll.php?t=<?php echo MOTION_IMAGE_EXT?>&amp;b=imagenes.php" class="button icon fa-download">Descargar todas las imágenes</a></li>
						<li><a href="downloadAll.php?t=<?php echo MOTION_VIDEO_EXT?>&amp;b=imagenes.php" class="button icon special fa-download"><i class="icon fa-warning"></i> Descargar todos los vídeos</a></li>
						<li><a href="#" class="button icon fa-remove special" onclick="deleteAll()"><i class="icon fa-warning"></i> Borrar todo</a></li>
					</ul>
				</div>


				<!-- Image -->
				<section>
					<?php
					$i		= 1;
					$year	= "";
					$month= "";
					$first= 1;
					foreach($filesByName as $file){
						$name = $file["name"];

						if ($file["year"]!=$year || $file["month"]!=$month){
							if(!$first){
								echo "</div></div>";
							}						

							echo "<h3>".$file["year"]."</h3>";
							echo "<h2>".$meses[$file["month"]]."</h2>";
							echo "<div class=\"box alt\">";
							echo "<div class=\"row 50% uniform\">";
							$first=0;
							$year=$file["year"];
							$month=$file["month"];
						}


						if ($i++ % 2) {
							echo "<div class=\"6u 12u$(medium)\">";
						} else {
							echo "<div class=\"6u$ 12u$(medium)\">";
						}
						#echo "<section class=\"box\">";	
						echo "<span class=\"image fit\">";
						echo "<a href=\"view.php?n=".$file["name"]."\">";	
						if (file_exists (MOTION_DIR . $name . "." . MOTION_IMAGE_EXT)){
							echo "<img src=\"".MOTION_DIR."$name." . MOTION_IMAGE_EXT . "\"/>";
						} else{
							echo "<img width=\"50%\" src=\"images/video.jpg\" />";
						}
						echo "</a></span></div>";
					}
					?>
				</section>
			</div>
		</section>

		<?php require 'footer.php'; ?>

		<form id="deleteAllForm" action="deleteAll.php">
			<input type="hidden" id="t" name="t" value="all"/>
			<input type="hidden" id="b" name="b" value="imagenes.php"/>
		</form>

	</body>
</html>
