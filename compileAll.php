#!/usr/bin/php
<?php
// Data Compiler - v5.4 - by Marcelo Dantas

////////////////////////////////////////////////////////////////////////////////
// Include files
require_once('include/defines.php');
require_once('include/globals.php');
require_once($globals->path . '/include/functions.php');

////////////////////////////////////////////////////////////////////////////////
// Control execution start
if(file_exists('cancel.exec'))
	die('Execution cancelled by command.' . NL);
if(file_exists('hold.exec')) {
	print('Execution held by command...' . NL);
	while(file_exists('hold.exec'))
		sleep(1);
}

////////////////////////////////////////////////////////////////////////////////
// Constants (App Specific)
define('NAME', 'compileAll');
define('VERSION', '5.4');
define('APP', $argv[0]);
define(
	'USAGE',
	'[-h|-help] [-debug[=n]] [-id=<customer ID>] ...' . NL .
		TAB . '-h|-help   - Shows this help message.' . NL .
		TAB . '-debug[=n] - Defines the debug (verbosity) level.' . NL .
		TAB . '-id=<s>    - Defines the customer ID to use.' . NL .
		TAB . '               if omitted, all customers will be compiled.' . NL .
		TAB . '...        - Any other argument will be available as a global variable.' . NL
);

/////////////////////////////////////////////////////////////////////
// Set global variables onto "globals" object
// This makes it easy to share the object with functions
$globals->range        = '+1 day';
$globals->config       = 'config_files/customers.json';

list($globals->name, $dummy) = explode('.', basename($argv[0]));
$globals->app = str_replace(DIRECTORY_SEPARATOR, '/', $argv[0]);

// Check presence of config file
if (!file_exists($globals->config))
	die('Config file not found.' . NL);

// Collect command line parameters and merge them into $globals
$globals = (object) array_merge((array) $globals, (array) parse_args());

// Compute collection date
if (!isset($globals->lower)) {
	if (!isset($globals->upper))
		$globals->upper = date('d.m.Y');
	$time = strtotime($globals->upper);
	$globals->lower = date('d.m.Y', strtotime('-1 day', $time));
} else {
	if (!isset($globals->upper)) {
		$time = strtotime($globals->lower);
		$globals->upper = date('d.m.Y', strtotime($globals->range, $time));
	}
}
if (!isset($globals->month))
	$globals->month = date('m', strtotime($globals->lower));
if (!isset($globals->year))
	$globals->year = date('Y', strtotime($globals->lower));

// Define operating system
if (file_exists('/usr/bin/php')) {
	$globals->os = 'Linux';
} else {
	$globals->os = 'Windows';
}

// Check for required executables
if ($globals->os == 'Windows') {
	// Check if windows PHP exists
	if (!file_exists($globals->php))
		die('(Windows) PHP not found : ' . $globals->php . NL);
}

// Define base command
if ($globals->os == 'Linux') {
	$compile = 'php -f compile.php -- ';
} else {
	$compile = $globals->php . ' -f compile.php -- ';
}

// Load customers file
$globals->customers = json_decode(file_get_contents($globals->config));

if ($globals->debug > 2)
	describe($globals);
if ($globals->debug > 3)
	exit(1);

// Scan customers
foreach ($globals->customers as $key => $customer) {
	if (isset($globals->id) and $customer->id != $globals->id)
		continue;
	print('Customer: ' . $customer->longName . ' (' . $customer->id . ')' . NL);
	print('Date    : ' . $globals->lower . NL);
	if(isset($customer->EAAFdb) and $customer->EAAFdb == true) {
		print('EAAFdb  : Enabled (new database)' . NL);
	} else {
		print('EAAFdb  : Disabled (old database)' . NL);
	}

	// Compile devices
	$cmd = $compile;
	$cmd .= '-data="' . $globals->config . '" -module="devices" -id="' . $customer->id . '" ';
	$cmd .= '-db="database_files/' . $customer->id . '/database_' . $customer->id . '_' . $globals->month . '.sqlite" -silent ';

	if ($globals->debug > 1) {
		print($cmd . NL);
	} else {
		passthru($cmd . NL, $error);
		if ($error)
			print(' ERROR CODE ' . $error . ' DETECTED' . NL);
	}

	// Create database folder
	$folder = 'database_files/' . $customer->id;
	if (!file_exists($folder))
		mkdir($folder);

	// Set data folder
	$folder = 'source_files/' . $customer->id . '/' . $globals->month . '_' . $globals->year;

	// Compile attacks
	$cmd = $compile;
	$cmd .= '-data="' . $folder . '/attacks_' . $customer->id . '_' . $globals->lower . '.json" -module="attacks" ';
	$cmd .= '-db="database_files/' . $customer->id . '/database_' . $customer->id . '_' . $globals->month . '.sqlite" -silent ';
	if (isset($globals->vision))
		$cmd .= '-vision="' . $globals->vision . '"';
	if(isset($customer->EAAFdb) and $customer->EAAFdb == true)
		$cmd .= ' -EAAFdb=1';

	if ($globals->debug > 1) {
		print($cmd . NL);
	} else {
		passthru($cmd . NL, $error);
		if ($error)
			print(' ERROR CODE ' . $error . ' DETECTED' . NL);
	}

	// Compile traffic
	$cmd = $compile;
	$cmd .= '-data="' . $folder . '/traffic_' . $customer->id . '_' . $globals->lower . '.json" -module="traffic" ';
	$cmd .= '-db="database_files/' . $customer->id . '/database_' . $customer->id . '_' . $globals->month . '.sqlite" -silent ';
	if (isset($globals->vision))
		$cmd .= '-vision="' . $globals->vision . '"';

	if ($globals->debug > 1) {
		print($cmd . NL);
	} else {
		passthru($cmd . NL, $error);
		if ($error)
			print(' ERROR CODE ' . $error . ' DETECTED' . NL);
	}

	if (!isset($globals->id))
		print(DIVIDER . NL);
}
?>