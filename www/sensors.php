<?php
$servername = "localhost";
$username = "temp";
$password = "readtemperature";
$dbname = "svvpa";
$bmp180Temp = [];
$bmp180Press = [];
$dht22Temp = [];
$dht22HR = [];

date_default_timezone_set('UTC');

// Create connection
$conn = mysqli_connect($servername, $username, $password, $dbname);
// Check connection
if (mysqli_connect_errno())
  {
  echo "Failed to connect to MySQL: " . mysqli_connect_error();
  }

$sql = "SELECT date, CPU_temp, BMP180_temp, BMP180_press, DHT22_temp, DHT22_HR FROM sensors";
//$result = $conn->query($sql);
if ($result=mysqli_query($conn, $sql)){
///	while ($row=mysql_fetch_array($result,MYSQLI_ASSOC)) {
	foreach( $result as $row ) {
   		extract($row);
			
   		$dt = new DateTime($date);
		$datetime = $dt->format('U')*1000;

		if(!empty($CPU_temp)){ 		$cpuTemp[]     = "[$datetime, $CPU_temp]";}
		if(!empty($BMP180_temp)){ 	$bmp180Temp[]  = "[$datetime, $BMP180_temp]";}
		if(!empty($BMP180_press)){ 	$bmp180Press[] = "[$datetime, $BMP180_press]";}
		if(!empty($DHT22_temp)){ 	$dht22Temp[]   = "[$datetime, $DHT22_temp]";} 
		if(!empty($DHT22_HR)){ 		$dht22HR[]     = "[$datetime, $DHT22_HR]";} 
	}
}

$conn->close();


//Elige qué columnas ocultar por defecto.
$hideSeries = json_decode('[' . $_GET["h"] . ']', true);
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
<!--		<META HTTP-EQUIV="PRAGMA" CONTENT="NO-CACHE">-->
		<meta http-equiv="content-type" content="text/html; charset=utf-8" />
		<meta name="description" content="" />
		<meta name="keywords" content="" />
		<!--[if lte IE 8]><script src="js/html5shiv.js"></script><![endif]-->
		<script src="js/jquery.min.js"></script>
		<script src="js/skel.min.js"></script>
		<script src="js/skel-layers.min.js"></script>
		<script src="js/init.js"></script>
		<script src="js/highstock.js"></script>
		<script src="js/modules/exporting.js"></script>
		<script src="js/themes/grid-light.js"></script>
		<link rel="shortcut icon" type="image/x-icon" href="images/favicon.png" />
		<noscript>
			<link rel="stylesheet" href="css/skel.css" />
			<link rel="stylesheet" href="css/style.css" />
			<link rel="stylesheet" href="css/style-xlarge.css" />
		</noscript>
<script>
$( document ).ready(function() {
        // Create the chart
        $('#myChart').highcharts('StockChart', {
            rangeSelector :  {
                buttons : [{
                    type : 'hour',
                    count : 1,
                    text : '1h'
                }, {
                    type : 'day',
                    count : 1,
                    text : '1d'
                }, {
                    type : 'day',
                    count : 3,
                    text : '3d'
                }, {
                    type : 'week',
                    count : 1,
                    text : '7d'
                }, {
                    type : 'month',
                    count : 1,
                    text : '1m'
                }, {
                    type : 'month',
                    count : 3,
                    text : '3m'
                }, {
                    type : 'month',
                    count : 6,
                    text : '6m'
                }, {
                    type : 'year',
                    count : 1,
                    text : '12m'
                }, {
                    type : 'all',
                    count : 1,
                    text : 'Todo'
                }],
                selected : 3 
            },

	    colors: ['#0033FF','#00CC00','#CCCC00','#FF3300','#FF99CC'],		

            title : {
                text : 'Sensores'
            }, 

	    subtitle: {
    		text: 'Sensores internos y externos de la RPi'
	    },

	    navigator : {
		enabled : false
	    },

	    yAxis: [{
                title: {
                    text: '%HR',
		    align: 'high',
		    offset: 15,
		    rotation: 0
                },
		showEmpty: false,
                tickWidth: 1,
                tickLength: 8,
                tickPosition: 'outside',
                lineWidth: 2,
		offset : 10,
		opposite: false,
		//max: 100,
		minRange: 0-100 
            }, {
                title: {
                    text: 'ºC',
                    align: 'high',
                    offset: 20,
                    rotation: 0
                },
		showEmpty: false,
                tickWidth: 1,
                tickLength: 8,
                tickPosition: 'outside',
                lineWidth: 2,
		offset: 10,
                opposite: true 
            }, {
                title: {
                    text: 'mmHg',
                    align: 'high',
                    offset: 10,
                    rotation: 0
                },
		showEmpty: false,
		tickWidth: 1,
                tickLength: 8,
                tickPosition: 'outside',
                lineWidth: 2,
		opposite: false
            }],

	    legend : { 
            	borderRadius: 0,
            	borderColor: 'silver',
            	enabled: true,
            	margin: 30,
            	itemMarginTop: 2,
            	itemMarginBottom: 2,
            	layout: 'vertical'
          },

	    tooltip: {
		valueDecimals: 1
	    }, 

            series : [{
		type : 'spline',
                name : 'Humedad Revaliva (%)',
                data : [<?php echo join($dht22HR, ',') ?>],
		yAxis: 0,
		lineWidth:4 
            }, {
                type : 'spline',
                name : 'Temperatura exterior(ºC)',
                data : [<?php echo join($dht22Temp, ',') ?>],
                yAxis: 1,
                lineWidth:4
            }, {
                type : 'spline',
                name : 'Temperatura en la caja (ºC)',
                data : [<?php echo join($bmp180Temp, ',') ?>],
                yAxis: 1,
                lineWidth:4
            }, {
                type : 'spline',
                name : 'Temperatura CPU (ºC)',
                data : [<?php echo join($cpuTemp, ',') ?>],
                yAxis: 1,
                lineWidth:4
            }, {
                name: 'Presión atmosférica (mmHg)',
		type : 'spline',
                data: [<?php echo join($bmp180Press, ',') ?>],
                yAxis: 2,
		lineWidth:4
		//dashStyle: 'dash'
            }]
        });

	var chart = $('#myChart').highcharts();
	var hideSeries = <?php echo json_encode($hideSeries); ?>;
	for (var i=0; i<hideSeries.length; i++){
		chart.series[hideSeries[i]].hide();
	}

});
</script>
	</head>
	<body>
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
				<div class="container style1">
						<section>
							<div id="myChart" style="height: 500px; "></div>
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


	</body>
</html>
