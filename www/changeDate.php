<?php
$date = htmlspecialchars($_GET["dateField"]);

exec("sudo date -s \"$date $(date +%H:%M:%S)\"");

header( 'Location: /ajustes.php' ) ;
?>
