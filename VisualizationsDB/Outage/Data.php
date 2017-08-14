<?php
ini_set('display_errors', 'On');
error_reporting(E_ALL | E_STRICT);
$connection = new MongoClient("mongodb://172.25.11.94");
$db = $connection->InternetDashboard;
$collection = $db->outages;
$date = $_GET["date"]; // Get date from GET request
$query = array("Date" => $date);
$document = $collection->findOne($query);
echo json_encode($document);
?>