<?php 
require_once('CONSTANTS.php'); 
?>

<!DOCTYPE html>
<html lang="es">
	<head>
		<?php require 'meta.php'; ?>
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

		<script type="text/javascript">
			function updateClock () {
				var currentTime 	 = new Date ( );
				var currentHours 	 = currentTime.getHours ( );
				var currentMinutes = currentTime.getMinutes ( );
				var currentSeconds = currentTime.getSeconds ( );

				// Pad the minutes and seconds with leading zeros, if required
				currentMinutes = ( currentMinutes < 10 ? "0" : "" ) + currentMinutes;
				currentSeconds = ( currentSeconds < 10 ? "0" : "" ) + currentSeconds;

				// Compose the string for display
				var currentTimeString = currentHours + ":" + currentMinutes + ":" + currentSeconds;

				// Update the time display
				$("#clock").html(currentTimeString);
			}
		</script>
	</head>

	<body class="landing" onload="updateClock(); setInterval('updateClock()', 1000 )">
		<?php require 'header.php'; ?>

		<!-- Banner -->
		<section id="banner">
			<h2>Bienvenido a SVVPA</h2>
			<p>El Sistema de Video Vigilancia del Puto Amo</p>				
		</section>

		<!-- One -->
		<section id="one" class="wrapper style1 special" name="one">
			<div class="container">
				<header class="major">
					<h2>Últimas capturas</h2>
				</header>
				<div class="row 150%">
					<?php
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


					$filesByName	= array();
					$filesByChange= array();
					foreach (new DirectoryIterator(MOTION_DIR) as $fileInfo) {
						if(!$fileInfo->isDot() && endsWith($fileInfo->getFilename(),'.' . MOTION_VIDEO_EXT)){
							$file =  $fileInfo->getBasename('.' . MOTION_VIDEO_EXT);
							list($y, $m, $d, $H, $M, $S, $p, $n, $J, $w, $h, $t) = split ("_", $file);

							$filesByName[] = array(
							"sorting" => $y . $m . $d . $H . $M . $S,
							"name"		=> $file,
							"fecha"		=> $d . " " .$meses[$m] ." " . $y ,
							"hora"		=> $H . ":" . $M
							);

							$filesByChange[] = array(
							"sorting"	=> $p,
							"name"		=> $file,
							"fecha"		=> $d . " " .$meses[$m] ." " . $y ,
							"hora"    => $H . ":" . $M
							);
						}
					}

					arsort($filesByName);
					//var_dump($filesByName);
					$i=1;
					foreach($filesByName as $f){
						$name 	= $f["name"];
						$fecha	= $f["fecha"];
						$hora		= $f["hora"];

						if ($i++ % 3) {
							echo "<div class=\"4u 12u$(medium)\">";
						} else {
							echo "<div class=\"4u$ 12u$(medium)\">";	
						}

						echo "<section class=\"box\">";									
						echo "<h3>$fecha</h3>";
						echo "<h5>$hora</h5>";
						#echo "<h5>$name</h5>";
						echo "<div class=\"12u$\">";
						echo "<span class=\"image fit\">";
						if(file_exists (MOTION_DIR . $name . "." . MOTION_IMAGE_EXT)){
							echo "<video width=\"100%\" controls poster=\"".basename(MOTION_DIR)."/$name." . MOTION_IMAGE_EXT . "\" preload=\"none\">";
						}else{
							echo "<video width=\"100%\" controls preload=\"none\">";
						}
						echo "<source src=\"".basename(MOTION_DIR)."/$name." . MOTION_VIDEO_EXT . "\" type=\"video/mp4\">";
						echo "</video></span></div>";

						echo "<ul class=\"actions\">";
						echo "<li><a href=\"download.php/?n=$name.".MOTION_VIDEO_EXT."\" class=\"button icon fa-download\">Descargar</a></li>";
						echo "<li><a href=\"delete.php/?n=$name&b=index.php#one\" class=\"button icon fa-remove\">Borrar</a></li>";
						echo "</ul>";
						echo "</section>";
						echo "</div>";

						if ($i>3){
							break;
						}
					}
					?>
				</div>
			</div>
		</section>

	
		<section id="two" class="wrapper style1 special" name="two">
			<div class="container">
				<header class="major">
					<h2>Mayores movimientos detectados</h2>
				</header>
				<div class="row 150%">
					<?php
					arsort($filesByChange);		#reverse order
					$i=1;
					foreach($filesByChange as $file){
						$name 	= $file["name"];
						$fecha  = $file["fecha"];
						$hora		= $file["hora"];

						if ($i++ % 3) {
							echo "<div class=\"4u 12u$(medium)\">";
						} else {
							echo "<div class=\"4u$ 12u$(medium)\">";	
						}

						echo "<section class=\"box\">";									
						echo "<h3>".$file["sorting"]." píxeles</h3>";								
						echo "<h5>$fecha $hora</h5>";								
						echo "<div class=\"12u$\">";
						echo "<span class=\"image fit\">";
						if(file_exists (MOTION_DIR.$name.".".MOTION_IMAGE_EXT)){
							echo "<video width=\"100%\" controls poster=\"".basename(MOTION_DIR)."/$name.".MOTION_IMAGE_EXT."\" preload=\"none\">";
						}else{
							echo "<video width=\"100%\" controls preload=\"none\">";
						}
						echo "<source src=\"".basename(MOTION_DIR)."/$name.".MOTION_VIDEO_EXT."\" type=\"video/mp4\">";
						echo "</video></span></div>";
						echo "<ul class=\"actions\">";
						echo "<li><a href=\"download.php/?n=$name.".MOTION_VIDEO_EXT."\" class=\"button icon fa-download\">Descargar</a></li>";
						echo "<li><a href=\"delete.php/?n=$name&b=index.php#two\" class=\"button icon fa-remove\">Borrar</a></li>";
						echo "</ul>";
						echo "</section>";
						echo "</div>";

						if ($i>3)break;
					}
					?>
				</div>
			</div>
		</section>



		<!-- Three -->
		<section id="three" class="wrapper style3 special">
			<div class="container">
				<header class="major">
					<h2>Estado actual</h2>
				</header>
			</div>
			<div class="container 50%">
				<div class="table-wrapper">
					<table>
						<thead>
							<tr>
								<th>Descripción</th>
								<th>Estado</th>
							</tr>
						</thead>
						<tbody>
							<tr>
								<td>Espacio disponible</td>
								<td><?php echo number_format((disk_free_space("/") / disk_total_space("/") * 100),2);?>%</td>
							</tr>
							<tr>
								<td>Fecha</td>
								<td><?php echo date("d/m/Y", time());?></td>
							</tr>
							<tr>
								<td>Hora</td>
								<td id="clock">&nbsp;</td>
							</tr>
							<tr>
								<td>Temperatura RPI</td>
								<td><?php system(BIN_DIR.'_readInternalTemp.sh');?>ºC</td>
							</tr>
						</tbody>
					</table>
				</div>
			</div>
		</section>

		<?php require 'footer.php'; ?>

	</body>
</html>
