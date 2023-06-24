<?php
$time = $_POST['time'];
$place = $_POST['place'];
$spec = $_POST['spec'];
$azot = $_POST['azot'];
$azdo = $_POST['azdo'];
$alt = $_POST['alt'];
$filename = __DIR__ . '/file.txt';

echo $time;
echo "<br>";
echo $place;
echo "<br>";
echo $spec;
echo $azot;
echo "<br>";
echo $azdo;
echo "<br>";
echo $alt;

file_put_contents($filename, PHP_EOL .$time.' '.$place.' '.$azot.' '.$azdo.' '.$alt.' '.$spec , FILE_APPEND);
?>