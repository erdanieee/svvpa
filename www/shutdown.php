<html>
	<head>
                <meta charset="UTF-8">
                <title>SVVPA</title>
                <meta http-equiv="content-type" content="text/html; charset=utf-8" />
                <link rel="shortcut icon" type="image/x-icon" href="images/favicon.png" />
        </head>

	<body>
		<p>El sistema se ha apagado correctamente.</p>
		<p>Para volver a iniciarlo es necesario quitar y volver a poner la alimentación.</p>

	</body>
</html>

<?php
	exec("/sbin/shutdown -h now");
?>

