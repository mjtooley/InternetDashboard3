<?php
$connection = new MongoClient("mongodb://localhost:27017");
$db = $connection->InternetDashboard;
$collection = $db->interconnects;
$date = $_GET["date"]; // Get date from GET request
$query = array("Date" => $date);
$document = $collection->findOne($query);
echo json_encode($document);
?>
