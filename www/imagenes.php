<?php
require_once('CONSTANTS.php');

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
	if(preg_match("/^([0-9]+_)+[0-9]+.jpg$/", $fileInfo->getBasename())){
		$file = $fileInfo->getBasename('.' . MOTION_IMAGE_EXT);
        list($y, $m, $d, $H, $M, $S, $p, $n, $i, $J, $w, $h, $t) = explode ("_", $file);        
		$key= $y . $m . $d . $H . $M . $S;

		$filesByName[] = array(
			"sorting" => $key,
			"name"		=> $file,
			"year"		=> $y,
			"month"		=> $m,
			"day"		=> $d
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
		<script>
			var selected=[];
			var selecting=false;

		function deleteAll(){
			if (confirm('Se va a proceder a borrar todos los vídeos e imágenes. ¿Realmente deseas continuar?')) {
				$("#deleteAllForm").submit();
			}
		}

		function toggleSelection(){
			selecting=!selecting;
			$("#downloadButton").addClass("disabled");			
			$("#deleteButton").addClass("disabled");


			if (selecting){
				selection=[]				
				$("#modeButton").removeClass("fa-check");
				$("#modeButton").addClass("fa-eye");
				$("#modeButton").text("Volver al modo visualización");
	
			} else {
				$("#modeButton").addClass("fa-check");
				$("#modeButton").removeClass("fa-eye");				
				$("#modeButton").text("Activar modo selección");
				$('[name=imagelink]').css("border-color","white");
			}
		}

		function deleteSelected(){
			$("#deleteSelected_n").val(selected.join(":"));
			if (confirm('Se van a borrar los vídeos e imágenes seleccionados (' + selected.length + '). ¿Realmente deseas continuar?')) {
				$("#deleteSelected").submit();
			}
		}


		// Handler for .ready() called.
		$(function() {
			$('[name=imagelink]').click(function() {
  				if (!selecting){
					return true;
			
				} else {
					id=$( this ).attr( "title" );
					
					if ($.inArray(id, selected)!=-1){
						selected.splice( $.inArray(id, selected), 1 );	//remove item
						$( this ).css("border-color","white");
						if (selected.length==0){
							$("#downloadButton").addClass("disabled");			
							$("#deleteButton").addClass("disabled");
						}

					} else {
						selected.push(id);					
						$( this ).css("border-color","#ff0000");
						$("#downloadButton").removeClass("disabled");			
						$("#deleteButton").removeClass("disabled");			
					}

					return false;
				}	
			});
		});
		
		</script>


	</head>

	<body>
		<!-- Header -->
		<?php require 'header.php'; ?>


		<!-- Main -->
		<section id="main" class="wrapper">
			<div class="container">
				<header class="major">
					<h2>Capturas</h2>
				</header>

				<h2>Información</h2>
				<p>Esta sección contiene una previsualización de los mejores momentos de cada vídeo. Esto permite hacerte una idea de lo que se ha grabado, y evitar así visualizar vídeos que solo tengan pequeños movimientos de hojas. Que no es por no visualizarlos... que si hay que visualizarlos se visualizan, pero visualizar los vídeos pa ná es tontería. <br> Para ver los vídeos simplemente haz <strong>click</strong> en la imagen. Para borrar varias capturas al mismo tiempo, activa el <strong>modo selección</strong> y selecciona las imágenes pulsando sobre ellas. Recuerda que NO es necesario borrarlas, ya que se hace de forma automática. Si quieres conservar algún vídeo/captura, es recomendable descargarlo a tu ordenador o subirlo a google Drive, ya que la tarjeta de memoria del SVVPA puede fallar en cualquier momento.</p>


				<div class="12u$"> 
					<ul class="actions">
						<li><span id="modeButton" class="button icon fa-check" onclick="toggleSelection()">Activar modo selección</span></li>
						<!--<li><span id="downloadButton"  class="disabled button icon fa-download" onclick="downloadSelected()">Descargar selección</span></li>-->
						<li><span id="deleteButton" class="disabled button icon fa-remove" onclick="deleteSelected()">Borrar seleccionados</span></li>
<!--						<li><a href="downloadAll.php?t=<?php echo MOTION_IMAGE_EXT?>&amp;b=imagenes.php" class="button icon fa-download">Descargar todas las imágenes</a></li>
						<li><a href="downloadAll.php?t=<?php echo MOTION_VIDEO_EXT?>&amp;b=imagenes.php" class="button icon special fa-download"><i class="icon fa-warning"></i> Descargar todos los vídeos</a></li> -->
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

							echo "<h3>".$file["year"]."</h3>\n";
							echo "<h2>".$meses[$file["month"]]."</h2>\n";
							echo "<div class=\"box alt\">\n";
							echo "<div class=\"row 50% uniform\">\n";
							$first=0;
							$year=$file["year"];
							$month=$file["month"];
						}

						if ($i++ % 2) {
							echo "<div class=\"6u 12u$(medium)\">\n";
						} else {
							echo "<div class=\"6u$ 12u$(medium)\">\n";
						}
						#echo "<section class=\"box\">";	
						#echo "<i class=\"icon fa-trash\">";	
						echo "<span title=\"$name\" name=\"imagelink\" class=\"image fit\">\n";
						echo "<a href=\"view.php?n=".$file["name"]."\">\n";	
						if (file_exists (MOTION_DIR . $name . "." . MOTION_IMAGE_EXT)){
							echo "<img src=\"".basename(MOTION_DIR)."/$name." . MOTION_IMAGE_EXT . "\"/>\n";
						} else{
							echo "<img width=\"50%\" src=\"images/video.jpg\" />\n";
						}							

						echo "</a>\n";
						echo "</span>\n";
						echo "</div>\n";
#							echo "</div>\n";
#							echo "</div>\n";
					}
					?>
						</div>
					</div>
				</section>
			</div>
		</section>

		<?php require 'footer.php'; ?>

		<form id="deleteSelected" action="delete.php">
			<input type="hidden" id="deleteSelected_n" name="n" value=""/>	
			<input type="hidden" id="deleteSelected_b" name="b" value="imagenes.php"/>			
		</form> 

		<form id="deleteAllForm" action="deleteAll.php">
			<input type="hidden" id="t" name="t" value="all"/>
			<input type="hidden" id="b" name="b" value="imagenes.php"/>
		</form>



	</body>
</html>
