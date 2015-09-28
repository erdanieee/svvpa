<?php
function endsWith($haystack, $needle) {
	$length = strlen($needle);
        if ($length == 0) {
        	return true;
        }
        return (substr($haystack, -$length) === $needle);
}

function human_filesize($bytes, $decimals = 2) {
  $sz = 'BKMGTP';
  $factor = floor((strlen($bytes) - 1) / 3);
  return sprintf("%.{$decimals}f", $bytes / pow(1024, $factor)) . @$sz[$factor];
}

function getSize($files){
	$size=0;
	foreach ($files as $f){
		$size+=filesize($f);	
	}
	return human_filesize($size,0);
}


$motionImages=array();
$motionVideos=array();
$motionOthers=array();
foreach (new DirectoryIterator("motion") as $fileInfo) {
        if(!$fileInfo->isDot()){
		if(endsWith($fileInfo->getFilename(), '.jpg')){
	                $motionImages[] = "motion/" . $fileInfo->getFilename();
		}elseif(endsWith($fileInfo->getFilename(), '.mp4')){
                        $motionVideos[] = "motion/" . $fileInfo->getFilename();
                }else{
			$motionOthers[] = "motion/" . $fileInfo->getFilename();
		}
        }	
}

$motionImagesSize=getSize($motionImages);
$motionVideosSize=getSize($motionVideos);
$motionOthersSize=getSize($motionOthers);




?>









<!DOCTYPE html>
<!--
	Transit by TEMPLATED
	templated.co @templatedco
	Released for free under the Creative Commons Attribution 3.0 license (templated.co/license)
-->
<html lang="en">
	<head>
		<meta charset="UTF-8">
		<title>SVVPA</title>
		<!--<META HTTP-EQUIV="PRAGMA" CONTENT="NO-CACHE">-->
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

<script type="text/javascript">
<!--


var oldTime = new Date (<?php echo (time()*1000); ?>);
function updateClock (){
  var currentTime = new Date (oldTime.getTime()+1000);
  oldTime = currentTime;

  var currentHours = currentTime.getHours ( );
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

function getDate(){
	var today = new Date();
	var dd = today.getDate();
	var mm = today.getMonth()+1; //January is 0!
	var yyyy = today.getFullYear();

	if(dd<10) {
	    dd='0'+dd;
	} 

	if(mm<10) {
	    mm='0'+mm;
	} 

	return yyyy+'/'+mm+'/'+dd;
}

function setDate(){
	var pattern = /^[0-9]{4}\/[0-9]{2}\/[0-9]{2}$/;

	var date = prompt("Introduce la nueva fecha en formato yyyy/mm/dd. P.e.: 1981/08/21", getDate());
	if ( pattern.test(date)) {
	    $("#dateField").val(date.replace(/\//g, ""));
	    $("#changeDateForm").submit();	
	}
}

function getTime(){
        var today = new Date();
        var hh = today.getHours();
        var mm = today.getMinutes();
        var ss = today.getSeconds();

        if(hh<10) {
            hh='0'+hh;
        }

        if(mm<10) {
            mm='0'+mm;
        }

	if(ss<10) {
            ss='0'+ss;
        }

        return hh+':'+mm+':'+ss;
}

function setTime(){
        var pattern = /^[0-9]{2}:[0-9]{2}:[0-9]{2}$/;
        
        var time = prompt("Introduce la nueva hora en formato HH:MM:SS. P.e.: 17:30:00", getTime());
        if (pattern.test(time)) {
            $("#timeField").val(time);
            $("#changeTimeForm").submit();      
        }   
} 

function checkShutdown(){
	if (confirm('Se va a proceder a apagar el sistema. Para volver a iniciarlo, es necesario quitar y volver a poner la alimentación. ¿Realmente deseas apagar el sistema?')) {
    		$("#shutdownForm").submit();
	}
}


// -->
</script>


	<body onload="updateClock(); setInterval('updateClock()', 1000 )">

		<!-- Header -->
			<header id="header">
				<h1><a href="index.php">El Cárabo</a></h1>
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
			<section id="main" class="wrapper ">
				<div class="container">

					<header class="major">
						<h2>Ajustes</h2>
					</header>


					<!-- Table -->
						<section>
							<div class="table-wrapper">
								<table>
									<thead>
										<tr>
											<th>Descripción</th>
											<th>Estado</th>
											<th></th>
										</tr>
									</thead>
									<tbody>
										<tr>
											<td>Espacio total disponible</td>
											<td><?php echo number_format((disk_free_space("/") / disk_total_space("/") * 100),1) . "% (~" . human_filesize(disk_free_space("/"),0).")";?></td>
											<td></td>
										</tr>
										<tr>
											<td>Total imágenes</td>
											<td><?php echo (count($motionImages) . " (" . $motionImagesSize . ")"); ?></td>
                                                                                        <td><a href="deleteAll.php?t=jpg&b=ajustes.php" class="button icon small fa-remove">Purgar</a></td>										
										</tr>
										<tr>
											<td>Total vídeos</td>
											<td><?php echo (count($motionVideos) . " (" . $motionVideosSize . ")"); ?></td>
                                                                                        <td><a href="deleteAll.php?t=mp4&b=ajustes.php" class="button icon small fa-remove">Pu    rgar</a></td>
										</tr>
										<tr>
											<td>Otros archivos</td>
											<td><?php echo (count($motionOthers) . " (" . $motionOthersSize . ")"); ?></td>
                                                                                        <td></td>
										</tr>
                                                                                <tr>
                                                                                        <td>Carpeta <i>/tmp/motion</i></td>
                                                                                        <td><?php echo (human_filesize(exec("du -sb /tmp/motion|awk '{print $1}'"),0)) ?></td>
                                                                                        <td></td>
                                                                                </tr>
										<tr>
                	                                                 		<td>Fecha</td>
		                                                                        <td><?php echo date("d/m/Y", time());?></td>
                                                                                        <td><a href="#" class="button icon small fa-edit" onclick="setDate();">Cambiar</a></td>
                                		                                </tr>
                        	                		                <tr>
                                                                		        <td>Hora</td>
	                                                                	        <td id="clock">&nbsp;</td>
                                                                                        <td><a href="#" class="button icon small fa-edit" onclick="setTime();">Cambiar</a></td>
		                                                                </tr>
                		                                                <tr>
                                		                                        <td>Temperatura RPI</td>
                                                	                        	<td><?php $t=exec('cat /sys/class/thermal/thermal_zone0/temp') / 1000; echo number_format($t,1);?>ºC</td>
                                                                                        <td><a href="/sensors.php?h=0,1,4" class="button icon small fa-eye">ver</a></td>
                                                        		        </tr>
									</tbody>
								</table>
							</div>
						</section>
 <section>
                                                        <ul class="actions">
								<li><a href="<?php echo ('http://'.$_SERVER['HTTP_HOST'].':8080')?>" class="button icon fa-gear" >Ajustes avanzados</a></li>
                                                                <li><a href="/reboot.php" class="button special icon fa-power-off">Reiniciar sistema</a></li>
								<li><a href="#" class="button special icon fa-power-off" onclick="checkShutdown();"><i class="icon fa-warning"></i> Apagar sistema</a></li>
                                                        </ul>
                                                </section>



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




<form id="changeDateForm" action="changeDate.php">
  <input type="hidden" id="dateField" name="dateField">
</form>
<form id="changeTimeForm" action="changeTime.php">
  <input type="hidden" id="timeField" name="timeField">
</form>
<form id="shutdownForm" action="shutdown.php"></form>

	</body>
</html>
