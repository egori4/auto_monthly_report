#!/usr/bin/php -f
<?php
// Daily Data Collector - v5.0.1 - by Marcelo Dantas

/////////////////////////////////////////////////////////////////////
// Constants
define('NL', "\n");
define('TAB', "\t");
define('SQ', "'");

/////////////////////////////////////////////////////////////////////
// Set global variables onto "globals" object
// This makes it easy to share the object with functions

$globals               = new stdclass();
$globals->version      = '5.0.1';
$globals->debug        = false;
$globals->range        = '+1 day';
$globals->config         = 'config_files/customers.json';

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

// Compute collection date
if(!isset($globals->lower)) {
	if(!isset($globals->upper))
		$globals->upper = date('d.m.Y');
	$time = strtotime($globals->upper);
	$globals->lower = date('d.m.Y',strtotime($globals->range, $time));
} else {
	if(!isset($globals->upper)) {
		$time = strtotime($globals->lower);
		$globals->upper = date('d.m.Y',strtotime($globals->range, $time));
	}
}
if(!isset($globals->month))
	$globals->month = date('m', strtotime($globals->lower));
if(!isset($globals->year))
	$globals->year = date('Y', strtotime($globals->lower));

// Define operating system
if(file_exists('/usr/bin/php')) {
	$globals->os = 'Linux';
} else {
	$globals->os = 'Windows';
#	if(!isset($globals->id))
#		die('This program doenst work correctly under Windows' . NL);
}

// Define base command
if($globals->os == 'Linux') {
	$collect = 'php -f collect.php -- ';
	$compile = 'php -f compile.php -- ';
} else {
	$collect = '.\tools\php\php.exe -f collect.php -- ';
	$compile = '.\tools\php\php.exe -f compile.php -- ';
}

// Load customers file
$globals->customers = json_decode(file_get_contents($globals->config));

if($globals->debug > 1)
	print_r($globals);
if($globals->debug > 2)
	exit(1);
	
// Scan customers
foreach($globals->customers as $key => $customer) {
	if(isset($globals->id) and $customer->id != $globals->id)
		continue;
	print('Customer: ' . $customer->longName . ' (' . $customer->id . ')' . NL);

	// Create source folder
	$folder = 'source_files/'.$customer->id;
	if(!file_exists($folder))
		mkdir($folder);

	// Create database folder
	$folder = 'database_files/'.$customer->id;
	if(!file_exists($folder))
		mkdir($folder);

	// Create date folder
	$folder = 'source_files/'.$customer->id.'/'.$globals->month.'_'.$globals->year;
	if(!file_exists($folder))
		mkdir($folder);

	// Collect attacks
	$iter = 0;
	foreach($customer->visions as $key2 => $vision) {
		// Build command
		$cmd = $collect;
		$cmd .= '-data="'.$folder.'/attacks_'.$customer->id.'_'.$globals->lower.'.json" -module="attacks" ';
		$cmd .= '-lower="'.$globals->lower.'" -upper="'.$globals->upper.'" ';
		if(isset($customer->exclude))
			$cmd .= '-exclude="'.$customer->exclude.'" ';
		if(isset($customer->window))
			$cmd .= '-window='.$customer->window.' ';
		$cmd .= '-vision="'.$vision->ip.'" -user="'.$customer->user.'" -pass="'.$customer->pass.'" ';
		$cmd .= '-dps="'.$vision->dps.'" -silent ';

		if($iter)
			$cmd .= '-append ';

		if($globals->debug > 1) {
			print($cmd . NL);
		} else {
			passthru($cmd . NL, $error);
			if($error)
				print(" ERROR CODE $error DETECTED" . NL);
		}
		$iter++;
	}

	// Collect traffic
	$iter = 0;
	foreach($customer->visions as $key2 => $vision) {
		// Build command
		$cmd = $collect;
		$cmd .= '-data="'.$folder.'/traffic_'.$customer->id.'_'.$globals->lower.'.json" -module="traffic" ';
		$cmd .= '-lower="'.$globals->lower.'" -upper="'.$globals->upper.'" ';
		$cmd .= '-vision="'.$vision->ip.'" -user="'.$customer->user.'" -pass="'.$customer->pass.'" ';
		$cmd .= '-dps="'.$vision->dps.'" -silent ';

		if($iter)
			$cmd .= '-append ';

		if($globals->debug > 1) {
			print($cmd . NL);
		} else {
			passthru($cmd . NL, $error);
			if($error)
				print(" ERROR CODE $error DETECTED" . NL);
		}
		$iter++;
	}

	// Compile devices
	$cmd = $compile;
	$cmd .= '-data="'.$globals->config.'" -module="devices" -id="'.$customer->id.'" ';
	$cmd .= '-db="database_files/'.$customer->id.'/database_'.$customer->id.'.sqlite" -silent ';

	if($globals->debug > 1) {
		print($cmd . NL);
	} else {
		passthru($cmd . NL, $error);
		if($error)
			print(" ERROR CODE $error DETECTED" . NL);
	}

	// Compile attacks
	$cmd = $compile;
	$cmd .= '-data="'.$folder.'/attacks_'.$customer->id.'_'.$globals->lower.'.json" -module="attacks" ';
	$cmd .= '-db="database_files/'.$customer->id.'/database_'.$customer->id.'.sqlite" -silent ';
	
	if($globals->debug > 1) {
		print($cmd . NL);
	} else {
		passthru($cmd . NL, $error);
		if($error)
			print(" ERROR CODE $error DETECTED" . NL);
	}

	// Compile traffic
	$cmd = $compile;
	$cmd .= '-data="'.$folder.'/traffic_'.$customer->id.'_'.$globals->lower.'.json" -module="traffic" ';
	$cmd .= '-db="database_files/'.$customer->id.'/database_'.$customer->id.'.sqlite" -silent ';

	if($globals->debug > 1) {
		print($cmd . NL);
	} else {
		passthru($cmd . NL, $error);
		if($error)
			print(" ERROR CODE $error DETECTED" . NL);
	}

	if(!isset($globals->id))
		print("------------------------------------------------------" . NL);
}
?>
