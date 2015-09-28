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

$sql = "SELECT date, temp FROM temp limit 15000";
$result = $conn->query($sql);

$data=array();
if ($result->num_rows > 0) {  
    // output data of each row
    while($row = $result->fetch_assoc()) {
	$a=array();
        $a["date"] = strtotime($row["date"])*1000;
        $a["value"] = floatval($row["temp"]);
	$data[] = $a;
    }
} else { 
    echo "0 results";
}
$conn->close();

echo json_encode ($data);
?>

