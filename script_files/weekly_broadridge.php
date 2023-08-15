#!/usr/bin/php
<?php
// Weekly report of events for Broadridge
///////////////////////////////////////////////////////////////

require_once('include/defines.php');

$globals               = new stdclass();
$globals->debug        = false;
require_once('include/functions.php');

print('Weekly events - Broadridge' . NL);

// Source date is either 1st arg or today
if (isset($argv[1])) {
	$eTime = strtotime($argv[1]);
} else {
	$eTime = strtotime(date('Y-m-d'));
}

// Compute end date
$eDay = date('d', $eTime);
$eMonth = date('m', $eTime);
$eYear = date('Y', $eTime);
$eDate = date('Y-m-d', $eTime);

// Compute start date
$sTime = strtotime('-7 days', $eTime);
$sDay = date('d', $sTime);
$sMonth = date('m', $sTime);
$sYear = date('Y', $sTime);
$sDate = date('Y-m-d', $sTime);

print("Range: $sDate to $eDate" . NL . NL);

// Correct sDate for overlapping month
if ($sMonth != $eMonth)
	$sDate = $eYear . '-' . $eMonth . '-01';

// Set name of current database
$cDB = 'database_files/BROADRIDGE/database_BROADRIDGE_' . $eMonth . '.sqlite';
if (file_exists($cDB)) {
	print("Reading from $cDB" . NL);
} else {
	die('Current database not found.');
}
$globals->dbHandle = new SQLite3($cDB);
$sql = "select '$sDate' as sDate,'$eDate' as eDate,count(1) as 'Event Count',sum(packetCount)/1000000.0 as 'Million Packets',sum(packetBandwidth)/8000000.0 as 'Gigabytes' from attacks where date(endDate)>=date(sDate) and date(endDate)<=date(eDate)";
$result = array_from_sql($sql, true);
foreach ($result as $line) {
	foreach ($line as $str)
		print(str_pad($str, 16));
	print(NL);
}
print(NL);

// Continue if another query is needed
if ($sMonth == $eMonth)
	die();

// Correct eDate for overlapping month
$eDate = $sYear . '-' . $sMonth . '-' . date('d', strtotime('-1 day', strtotime($sDate)));

// Recover sdate
$sDate = date('Y-m-d', $sTime);

// Set name of current database
$pDB = 'database_files/BROADRIDGE/database_BROADRIDGE_' . $sMonth . '.sqlite';
if (file_exists($pDB)) {
	print("Reading from $pDB" . NL);
} else {
	$pDB = '/mnt/d/database_files/BROADRIDGE/database_BROADRIDGE_' . $sMonth . '.sqlite';
	if (file_exists($pDB)) {
		print("Reading from $pDB" . NL);
	} else {
		die('Current database not found.');
	}
}
$globals->dbHandle = new SQLite3($pDB);
$sql = "select '$sDate' as sDate,'$eDate' as eDate,count(1) as 'Event Count',sum(packetCount)/1000000.0 as 'Million Packets',sum(packetBandwidth)/8000000.0 as 'Gigabytes' from attacks where date(endDate)>=date(sDate) and date(endDate)<=date(eDate)";
$result = array_from_sql($sql, true);
foreach ($result as $line) {
	foreach ($line as $str)
		print(str_pad($str, 16));
	print(NL);
}
print(NL);

?>