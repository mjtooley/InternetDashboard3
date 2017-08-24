<?php
$connection = new MongoClient("mongodb://localhost:27017");
$db = $connection->InternetDashboard;
$collection = $db->performance;
$date = $_GET["date"]; // Get date from GET request
//$query = array("Date" => $date);
//$document = $collection->findOne($query);
$s=array('Date' => -1);
$document = $collection->find()->sort($s)->limit(1); // Find the latest entry
echo json_encode($document);
?>