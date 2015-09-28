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
		<script src="js/jquery.min.js"></script>
		<script src="js/d3.min.js"></script>
		<script src="js/metricsgraphics.min.js"></script>
		<link rel="stylesheet" href="css/metricsgraphics.css" />
	</head>

<script>





$( document ).ready(function() {
d3.json('/getTempJSON.php', function(data) {
   var d = new Date();
   var datos=[];
   for (var i=0; i<data.length; i++) {
	d.setTime(data[i]['date']);
        datos.push({date: MG.clone(d), value: data[i]['value']});
    }

    //data = MG.convert.date(data, 'date');
    MG.data_graphic({
        title: "Line Chart",
        description: "uments list.",
        data: datos,
        width: 600,
        height: 200,
        right: 40,
	min_y: 39,
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
				<h1><a href="index.html">El Cárabo</a></h1>
				<nav id="nav">
					<ul>
						<li><a href="index.php">Inicio</a></li>
						<li><a href="imagenes.php">Capturas</a></li>
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




<div class='col-lg-7 text-center' id='singleton'></div>

							<canvas id="myChart" width="400" height="400"></canvas>






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
