<?php
$date = htmlspecialchars($_GET["dateField"]);

exec("date -s \"$date $(date +%H:%M:%S)\"");

header( 'Location: /ajustes.php' ) ;


?>
