<html>
	<head>
		<?php require 'meta.php'; ?>
		<link rel="shortcut icon" type="image/x-icon" href="images/favicon.png" />
	</head>

	<body>
		<p>El sistema se ha apagado correctamente.</p>
		<p>Para volver a iniciarlo es necesario desactivar y volver a activar el miniinterruptor que está junto a las baterías.</p>
	</body>
</html>

<?php
exec("sudo /sbin/shutdown -h now");
?>

