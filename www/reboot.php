<?php
exec("sudo /sbin/shutdown -r now");
?>

<html>
	<script>
		var t = 45;
		function updateClock(){
			if (t>0){
				t= t-1;
				document.getElementById("clock").innerHTML = t;
			} else {
				window.location.replace("/");
			}
		}
	</script>

	<body onload="setInterval('updateClock()', 1000)">
		<p>Espera mientras se reinicia el sistema</p>
		<p><span id="clock" name="clock">45</span> segundos</p>
	</body>
</html>
