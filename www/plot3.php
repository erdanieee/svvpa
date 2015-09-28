<?php
$servername = "localhost";
$username = "temp";
$password = "readtemperature";
$dbname = "svvpa";

// Create connection
$conn = new mysqli($servername, $username, $password, $dbname);
// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
} 

$sql = "SELECT date, temp FROM temp limit 240";
$result = $conn->query($sql);

$legends=array();
$values=array();
$lastDate ="";
$lastHour ="";
$sum=0;
$count=0;
if ($result->num_rows > 0) {   
    while($row = $result->fetch_assoc()) {
	$dt = new DateTime($row["date"]);
	
	if ($lastHour != $dt->format('gA')){
		$lastHour=$dt->format('gA');
		if ($sum!=0){
			if ($lastDate != $dt->format('d')){
				$lastDate = $dt->format('d');
         			$legends[] = $dt->format('d/m/Y gA');

        		} else {
           			$legends[] = $dt->format('gA');
        		}
			$values[] = floatval($sum)/$count;
		}
		$sum=$row["temp"];
		$count=1;

	} else {
		$sum+=$row["temp"];
		$count+=1;
	}
   }
	if ($lastDate != $dt->format('d')){
        	$lastDate = $dt->format('d');
                $legends[] = $dt->format('d/m/Y gA');
                          
        } else {
        	$legends[] = $dt->format('gA');
        }
        $values[] = floatval($sum)/$count;

} else {
    echo "0 results";
}
$conn->close();
//var_dump($legends);
//var_dump($values);
//var_dump($sum);
//var_dump($count);
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
		<script src="js/Chart.js"></script>
		<script src="js/d3.min.js"></script>
		<script src="js/metricsgraphics.min.js"></script>
		<link rel="stylesheet" href="css/metricsgraphics.css" />
		<link rel="shortcut icon" type="image/x-icon" href="images/favicon.png" />
		<noscript>
			<link rel="stylesheet" href="css/skel.css" />
			<link rel="stylesheet" href="css/style.css" />
			<link rel="stylesheet" href="css/style-xlarge.css" />
		</noscript>
	</head>

<script>
var data = {
    labels: <?php
	echo "[\"".$legends[0]."\"";
	for ($i=1;$i<count($legends);$i++){
		echo ",\"".$legends[$i]."\"";
	}
	echo "]";
	?>

,
    datasets: [
        {
            label: "My First dataset",
            fillColor: "rgba(220,220,220,0.2)",
            strokeColor: "rgba(220,220,220,1)",
            pointColor: "rgba(220,220,220,1)",
            pointStrokeColor: "#fff",
            pointHighlightFill: "#fff",
            pointHighlightStroke: "rgba(220,220,220,1)",
            data: <?php   
   		echo "[".$values[0];
          	for ($i=1;$i<count($values);$i++){
                	echo ",".$values[$i];
          	}
          	echo "]";
          		?> 
        }
    ]
};



$( document ).ready(function() {
//	var min=99, max=0;
	var ctx = $("#myChart").get(0).getContext("2d");
	var myLineChart = new Chart(ctx).Line(data,{
			scaleIntegersOnly: false,
			responsive: true
		}); 
	
	d3.json('/getTempJSON.php', function(data) {
   		var d = new Date();
   		var datos=[];
   		for (var i=0; i<data.length; i++) {
        		d.setTime(data[i]['date']);
        		datos.push({date: MG.clone(d), value: data[i]['value']});
//			if (data[i]['value']>max){
//				max = data[i]['value'];
//			}
//			if (data[i]['value']<min){
//                              min = data[i]['value'];
//                      }
    		}

    		//data = MG.convert.date(data, 'date');
    		MG.data_graphic({        
        		data: datos,
        		width: 800,
//			chart_type: 'point',
			full_width: true,
			interpolate_tension: 1,
//			height: 500,
        		right: 40,
			area: false,
			min_y_from_data: true,
//        		min_y: (min-1),
//			max_y: (max+1),
        		target: singleton,
        		x_accessor: 'date',
        		y_accessor: 'value'
    		});
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
						<li><a href="ajustes.php" class="button special">Ajustes</a></li>
					</ul>
				</nav>
			</header>

		<!-- Main -->
			<section id="main" class="wrapper ">
				<div class="container style1">
					<header class="major">
						<h2>Temperatura de la RPi</h2>
					</header>
						<section>
							<canvas id="myChart" width="400" height="400"></canvas>
						</section>

				</div>
				<div class="container style2">
                                        <header class="major">
                                                <h2>Valores históricos</h2>
                                        </header>
                                                <section>
                                                        <div id='singleton'></div>
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
