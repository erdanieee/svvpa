<?php
$time = htmlspecialchars($_GET["timeField"]);

exec("sudo date +%T -s $time");

header( 'Location: /ajustes.php' ) ;
?>
