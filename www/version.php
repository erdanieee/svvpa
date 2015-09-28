<?php

$db = new SQLite3('my_database') or die('Unable to open database');
$query = <<<EOD
  CREATE TABLE IF NOT EXISTS users (
    username STRING PRIMARY KEY,
    password STRING)
EOD;
$db->exec($query) or die('Create db failed');
$user = sanitize($_POST['username']);
$pass = sanitize($_POST['password']);
$query = <<<EOD
  INSERT INTO users VALUES ( '$user', '$pass' )
EOD;
$db->exec($query) or die("Unable to add user $user");
$result = $db->query('SELECT * FROM users') or die('Query failed');
while ($row = $result->fetchArray())
{
  echo "User: {$row['username']}\nPasswd: {$row['password']}\n";
}

?>

