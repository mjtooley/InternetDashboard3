<?php
$connection = new MongoClient("mongodb://172.25.11.86");
$db = $connection->Internet_Dashboard;
$collection = $db->interconnects;
$date = $_GET["date"]; // Get date from GET request
$query = array("Date" => $date);
$document = $collection->findOne($query);
echo json_encode($document);
?>
