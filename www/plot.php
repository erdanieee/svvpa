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

$sql = "SELECT date, CPU_temp, BMP180_temp, DHT22_temp FROM sensors";
//$result = $conn->query($sql);
if ($result=mysqli_query($conn, $sql)){
///	while ($row=mysql_fetch_array($result,MYSQLI_ASSOC)) {
	foreach( $result as $row ) {
   		extract($row);
			
   		$dt = new DateTime($date);
		$datetime = $dt->format('U')*1000;

		$BMP180_temp  = empty($BMP180_temp) ? 'null' : $BMP180_temp;
		$DHT22_temp   = empty($DHT22_temp) ? 'null' : $DHT22_temp;
		$CPU_temp     = empty($CPU_temp) ? 'null' : $CPU_temp;

   		$bmp180Temp[]  = "[$datetime, $BMP180_temp]";
   		$dht22Temp[]   = "[$datetime, $DHT22_temp]";
   		$cpuTemp[]     = "[$datetime, $CPU_temp]";
	}
}

$conn->close();
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
		<META HTTP-EQUIV="PRAGMA" CONTENT="NO-CACHE">
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
	</head>

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
                selected : 1
            },

            title : {
                text : 'Temperatura de la RPi'
            }, 

	    /*subtitle: {
    		text: 'My custom subtitle'
	    },*/

	    navigator : {
		enabled : false
	    },

	    yAxis: [{
                title: {
                    text: 'Temp (ºC)',
		    align: 'high',
		    offset: 10,
		    rotation: 0
                },
                tickWidth: 1,
                tickLength: 8,
                tickPosition: 'outside',
                lineWidth: 2,
		offset : 10,
		opposite: false,
		max: 100,
		min: 0 
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
                name : 'Temperatura de la CPU (ºC)',
                data : [<?php echo join($cpuTemp, ',') ?>],
		yAxis: 0,
		lineWidth:4 
            }, {
                type : 'spline',
                name : 'Temperatura de la caja (ºC)',
                data : [<?php echo join($bmp180Temp, ',') ?>],
                yAxis: 0,
                lineWidth:4 
            }, {
                name: 'Temperatura en el exterior (ºC)',
		type : 'spline',
                data: [<?php echo join($dht22Temp, ',') ?>],
                yAxis: 0,
		lineWidth:4
		//dashStyle: 'dash'
            }]
        });
});
</script>
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
							<div id="myChart" style="height: 500px; "</div>
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
