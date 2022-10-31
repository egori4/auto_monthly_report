#!/usr/bin/php -f
<?php
// Report Generator - v5.0.1 - by Marcelo Dantas

/////////////////////////////////////////////////////////////////////
// Constants
define('NL', "\n");
define('TAB', "\t");

/////////////////////////////////////////////////////////////////////
// Set global variables onto "globals" object
// This makes it easy to share the object with functions

$globals               = new stdclass();
$globals->version      = '5.0.1';
$globals->debug        = false;
$globals->config       = 'config_files/customers.json';

$globals->path = str_replace(DIRECTORY_SEPARATOR, '/', dirname(realpath($argv[0])));

list($globals->name, $dummy) = explode('.', basename($argv[0]));
$globals->app = str_replace(DIRECTORY_SEPARATOR, '/', $argv[0]);
if(strtoupper(substr(PHP_OS, 0, 3)) === 'WIN') {
	$globals->jq = $globals->path . '/tools/jq.exe';
} else {
	$globals->jq = '/usr/bin/jq';
}

// Include required libraries
include($globals->path . '/include/functions.php');

// Check presence of config file
if(!file_exists($globals->config))
	die('Config file not found.' . NL);

// Collect command line parameters and merge them into $globals
$globals = (object) array_merge((array) $globals, (array) parse_args());

// Check required variables
if(!isset($globals->month))
	die('-month=mm must be specified.' . NL);
if(!isset($globals->year))
	die('-year=yyyy must be specified.' . NL);

// Adjust month type and size
$globals->month = sprintf("%02d", $globals->month);

// Generate month text
$globals->monthText = array('', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December')[+$globals->month];

// Generate month days
$globals->monthDays = cal_days_in_month(CAL_GREGORIAN, +$globals->month, +$globals->year);

// Define operating system
if(file_exists('/usr/bin/php')) {
	$globals->os = 'Linux';
} else {
	$globals->os = 'Windows';
	if(!isset($globals->id))
		die('This program doenst work correctly under Windows' . NL);
}

// Define base command
if($globals->os == 'Linux') {
	$report = 'php -f report.php -- ';
} else {
	$report = '.\tools\php\php.exe -f report.php -- ';
}

// Load customers file
$globals->customers = json_decode(file_get_contents($globals->config));
if($globals->customers == '')
	die('Syntax error on the customer file.' . NL);

if($globals->debug > 1)
	print_r($globals);
if($globals->debug > 2)
	exit(1);

// Create report_files folder
if(!file_exists('report_files'))
	mkdir('report_files');
	
// Scan customers
foreach($globals->customers as $key => $customer) {
	if(isset($globals->id) and $customer->id != $globals->id)
		continue;
	if(isset($customer->process) and $customer->process === false) {
		if(!isset($globals->id)) {
			print('Customer: ' . $customer->longName . ' (' . $customer->id . ') Not processed!' . NL);
			continue;
		}
	}
	print('Customer: ' . $customer->longName . ' (' . $customer->id . ')' . NL);

	// Create report folder
	$folder = 'report_files/'.$customer->id;
	if(!file_exists($folder))
		mkdir($folder);

	// Set database folder
	$folder = 'database_files/'.$customer->id;

	// Check report file
	if(!isset($customer->report))
		$customer->report = 'json_files/MonthlyReport.json';

	// Override customer skip page list
	if(isset($globals->skip))
		$customer->skip = $globals->skip;

	// Generate report
	$cmd = $report;
	$cmd .= '-file="'.$customer->report.'" ';
	$cmd .= '-id="'.$customer->id.'" -longName="'.$customer->longName.'" ';
	$cmd .= '-month="'.$globals->month.'" -year="'.$globals->year.'" ';
	$cmd .= '-monthText="'.$globals->monthText.'" -monthDays='.$globals->monthDays.' ';
	$cmd .= '-output="report_files/{id}/report_{id}_{month}_{year}.htm" ';
	if(!isset($globals->noPDF))
		$cmd .= '-doPDF ';
	if(isset($globals->vision))
		$cmd .= '-vision="' . $globals->vision . '" ';
	if(isset($customer->skip))
		$cmd .= '-skip="' . $customer->skip . '" ';		
	if(isset($customer->variables)) {
		foreach($customer->variables as $var => $value) {
			if(gettype($value) == 'string') {
				$cmd .= '-' . $var . '="' . $value . '" ';
			} else {
				$cmd .= '-' . $var . '=' . $value . ' ';
			}
		}
	}
	
	if($globals->debug > 1) {
		print($cmd . NL);
	} else {
		passthru($cmd . NL, $error);
		if($error)
			print(" ERROR CODE $error DETECTED" . NL);
	}

	if(!isset($globals->id))
		print("------------------------------------------------------" . NL . NL);
}
?>
