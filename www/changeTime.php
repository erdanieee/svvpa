<?php
$time = htmlspecialchars($_GET["timeField"]);

exec("date +%T -s $time");

header( 'Location: /ajustes.php' ) ;


?>
