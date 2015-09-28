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
	$name = htmlspecialchars($_GET["n"]);
	$path = "motion";
	list($y, $m, $d, $H, $M, $S, $p, $n, $J, $w, $h) = split ("_", $name);
?>


<!DOCTYPE html>
<html lang="es">
	<head>
		<meta charset="UTF-8">
		<title>SVVPA</title>
		<meta http-equiv="content-type" content="text/html; charset=utf-8" />
		<meta name="description" content="" />
		<meta name="keywords" content="" />
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
			<header id="header">
				<h1><a href="index.html">SVVPA</a></h1>
				<nav id="nav">
					<ul>
						<li><a href="index.php">Inicio</a></li>
						<li><a href="imagenes.php">Capturas</a></li>
						<li><a href="life.php">Directo</a></li>
						<li><a href="sensors.php?h=2,3">Sensores</a></li>
						<li><a href="ajustes.php" class="button special">Ajustes</a></li>
					</ul>
				</nav>
			</header>





		<!-- Main -->
			<section id="main" class="wrapper">
				<div class="container">				
						<div class="12u 12u$(medium)">							
<?php
								$isImage=file_exists ("motion/".$name.".jpg");
                                                                $isVideo=file_exists ("motion/".$name.".mp4");

								echo "<h3>$d $meses[$m] $y</h3>";
								echo "<span class=\"image fit\">";
								if ($isVideo && $isImage){
									echo "<video width=\"100%\" controls poster=\"$path/$name.jpg\" preload=\"none\" autoplay>";
									echo "<source src=\"$path/$name.mp4\" type=\"video/mp4\">";
									echo "</video>";
								} elseif ($isVideo){
									echo "<video width=\"100%\" controls preload=\"none\" autoplay>";
                                                                        echo "<source src=\"$path/$name.mp4\" type=\"video/mp4\">";
                                                                        echo "</video>";
								} elseif ($isImage){
									echo "<img src=\"$path/$name.jpg\" />";
								}
								echo "</span>";
								echo "<ul class=\"actions\">";

								if ($isImage){
									echo "<li><a href=\"download.php?n=$name.jpg\" class=\"button icon fa-download\">Imagen</a></li>";
								}

								if ($isVideo){									
									echo "<li><a href=\"download.php?n=$name.mp4\" class=\"button icon fa-download\">Vídeo</a></li>";
								}
								echo "<li><a href=\"delete.php/?n=$name&b=imagenes.php\" class=\"button icon special fa-remove\">Borrar</a></li>";
								echo "</ul>";
								#echo "</section>";
								echo "</div>";
?>									
							
						<section class="6u(medium) 12u$(xsmall) profile">
						       <p><span class="left"><i class="icon rounded fa-info"></i></span> Para visualizar el vídeo en <strong>pantalla completa</strong> pulsa sobre el icono <i class="icon fa-arrows-alt"></i> que está situado en la parte inferior derecha del vídeo.</p>
                                                </section>	

							</div>

						</div>				
	
					</div>
				</div>
			</section>






		<!-- Footer -->
			<footer id="footer">
				<div class="container">
					<div class="row">
						<div class="8u 12u$(medium)">
							<ul class="copyright">
								<li>&copy;SVVPA 2015. Todos los derechos reservados.</li>
								<li>Diseño: Er Danié</li>
								<li>Instalación: Pae, Andrex y Er Danié</li>
							</ul>
						</div>
					</div>
				</div>
			</footer>

	</body>
</html>
