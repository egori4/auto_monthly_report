#!/usr/bin/php
<?php
// Report Generator - v5.4 - by Marcelo Dantas

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
define('NAME', 'reportAll');
define('VERSION', '5.4');
define('APP', $argv[0]);
define('SPC', str_repeat(' ', 8 + strlen($argv[0])));
define(
	'USAGE',
	'[-h|-help] [-debug[=n]] -id=<customer ID>' . NL .
		SPC . '-month=nn -year=nnnn ...' . NL .
		TAB . '-h|-help   - Shows this help message.' . NL .
		TAB . '-debug[=n] - Defines the debug (verbosity) level.' . NL .
		TAB . '-id=       - Defines the customer ID to be used. (all if undefined)' . NL .
		TAB . '-month=    - Defines the month for the report. Mandatory.' . NL .
		TAB . '-year=     - Defines the year for the report. Mandatory.' . NL .
		TAB . '...        - Any other argument will be available as global a variable.' . NL
);

/////////////////////////////////////////////////////////////////////
// Set global variables onto "globals" object
// This makes it easy to share the object with functions
$globals->config       = 'config_files/customers.json';

list($globals->name, $dummy) = explode('.', basename($argv[0]));
$globals->app = str_replace(DIRECTORY_SEPARATOR, '/', $argv[0]);

// Check presence of config file
if (!file_exists($globals->config))
	die('Config file not found.' . NL);

// Collect command line parameters and merge them into $globals
$globals = (object) array_merge((array) $globals, (array) parse_args());

// Check required variables
if (!isset($globals->month))
	die('-month=mm must be specified.' . NL);
if (!isset($globals->year))
	die('-year=yyyy must be specified.' . NL);

// Generate month text
$globals->monthText = array('', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December')[+$globals->month];

// Adjust month type and size
$globals->month = sprintf("%02d", $globals->month);

// Generate month days
$globals->monthDays = cal_days_in_month(CAL_GREGORIAN, +$globals->month, +$globals->year);

// Define operating system
if (file_exists('/usr/bin/php')) {
	$globals->os = 'Linux';
} else {
	$globals->os = 'Windows';
	if (!isset($globals->id))
		die('This program doenst work correctly under Windows' . NL);
}

// Check for required executables
if ($globals->os == 'Windows') {
	// Check if windows PHP exists
	if (!file_exists($globals->php))
		die('(Windows) PHP not found : ' . $globals->php . NL);
}

// Define base command
if ($globals->os == 'Linux') {
	$reportCmd = 'php -f report.php -- ';
} else {
	$reportCmd = $globals->php . ' -f report.php -- ';
}

// Load customers file
$globals->customers = json_decode(file_get_contents($globals->config));
if ($globals->customers == '')
	die('Syntax error on the customer file.' . NL);

if ($globals->debug > 2)
	describe($globals);
if ($globals->debug > 3)
	exit(1);

// Create report_files folder
if (!file_exists('report_files'))
	mkdir('report_files');

// Scan customers
foreach ($globals->customers as $key => $customer) {
	if (isset($globals->id) and $customer->id != $globals->id)
		continue;
	if (isset($customer->process) and $customer->process === false) {
		if (!isset($globals->id)) {
			print('Customer: ' . $customer->longName . ' (' . $customer->id . ') Not processed!' . NL);
			continue;
		}
	}
	print('Customer: ' . $customer->longName . ' (' . $customer->id . ')' . NL);

	// Create report folder
	$folder = 'report_files/' . $customer->id;
	if (!file_exists($folder))
		mkdir($folder);

	// Set database folder
	$folder = 'database_files/' . $customer->id;

	// Check report file
	if (!isset($customer->report))
		$customer->report = 'json_files/MonthlyReport.json';

	// For each customer attribute, replace with a global variable if it exists
	foreach ($customer as $key => $value) {
		if (isset($globals->$key))
			$customer->$key = $globals->$key;
	}

	// Create the reports array
	$reports = array();

	// Check if $customer->report is of type string
	if (is_string($customer->report)) {
		$reports[] = $customer->report;
	} else {
		$reports = $customer->report;
	}

	// Process each report
	foreach($reports as $key => $report) {
		// Generate report command line
		$cmd = $reportCmd;
		$cmd .= '-report="' . $report . '" ';
		$cmd .= '-id="' . $customer->id . '" -longName="' . $customer->longName . '" ';
		$cmd .= '-month="' . $globals->month . '" -year="' . $globals->year . '" ';
		$cmd .= '-monthText="' . $globals->monthText . '" -monthDays=' . $globals->monthDays . ' ';
		if(!$key) {
			$cmd .= '-output="report_files/{id}/report_{id}_{month}_{year}.htm" ';
		} else {
			$cmd .= '-output="report_files/{id}/report_{id}_{month}_{year}_'.$key.'.htm" ';
		}
		if (isset($globals->noDNS))
			$cmd .= '-noDNS ';
		if (!isset($globals->noPDF))
			$cmd .= '-doPDF ';
		if (isset($globals->vision))
			$cmd .= '-vision="' . $globals->vision . '" ';
		if (isset($customer->skip))
			$cmd .= '-skip="' . $customer->skip . '" ';
		if (isset($customer->EAAFdb) and $customer->EAAFdb == true)
			$cmd .= '-EAAFdb=1 ';
		if (isset($customer->variables)) {
			foreach ($customer->variables as $var => $value) {
				// Override customer variables with command line parameters
				if (isset($globals->{$var}))
					$value = $globals->{$var};
				// Add variable to command line
				if (gettype($value) == 'string') {
					$cmd .= '-' . $var . '="' . $value . '" ';
				} else {
					$cmd .= '-' . $var . '=' . $value . ' ';
				}
			}
		}
		// if debug is set, add it to the command line
		if (isset($globals->debug))
			$cmd .= '-debug=' . $globals->debug . ' ';
      		// if timing is set, add it to the command line
        	if (isset($globals->timing))
            		$cmd .= '-timing ';

		if ($globals->debug > 1) {
			print($cmd . NL);
		} else {
			passthru($cmd . NL, $error);
			if ($error)
				print(' ERROR CODE ' . $error . ' DETECTED' . NL);
		}
	}

	if (!isset($globals->id)) {
		print(DIVIDER . NL . NL);
	} else {
		break;
	}
}
?>