#!/usr/bin/php
<?php
// Data Collector - v5.4 - by Marcelo Dantas

////////////////////////////////////////////////////////////////////////////////
// Inclide files
require_once('include/defines.php');
require_once('include/globals.php');
require_once($globals->path . '/include/functions.php');
require_once($globals->path . '/include/vision.php');

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
define('NAME', 'collect');
define('VERSION', '5.4');
define('APP', $argv[0]);
define('SPC', str_repeat(' ', 8 + strlen($argv[0])));
define(
	'USAGE',
	'[-h|-help] [-debug[=n]] [-silent] [-data=<data file>]' . NL .
		SPC . '[-module=x] ...' . NL .
		TAB . '-h|-help    - Shows this help message.' . NL .
		TAB . '-debug[=n]  - Defines the debug (verbosity) level.' . NL .
		TAB . '-silent     - Supresses program header text. (for scripting)' . NL .
		TAB . '-data=<f>   - Defines the data file where the output will be saved.' . NL .
		TAB . '-module=<s> - Defines the data collection module to be used.' . NL .
		TAB . '...         - Any other argument will be available as a global variable.' . NL
);

/////////////////////////////////////////////////////////////////////
// Set global variables onto "globals" object
// This makes it easy to share the object with functions
$globals->moduleLoaded = false;
$globals->append       = false;
$globals->silent       = false;
$globals->maxRetry     = 6;
$globals->timeRetry    = 10;
$globals->recLimit     = 10000;

list($globals->name, $dummy) = explode('.', basename($argv[0]));
$globals->app = str_replace(DIRECTORY_SEPARATOR, '/', $argv[0]);

// Start computing execution time
timeIn();

/////////////////////////////////////////////////////////////////////
// Collect command line parameters and merge them into $globals

$globals = (object) array_merge((array) $globals, (array) parse_args());

// Program start
if (!$globals->silent) {
	print(NL . 'Collect v' . VERSION . ' - by Marcelo Dantas' . NL);
	print(DIVIDER . NL);
}

/////////////////////////////////////////////////////////////////////
// Pre-verifications

// Check for curl php extension
if (!extension_loaded('curl'))
	die('curl php extension not installed on php.ini' . NL);

/////////////////////////////////////////////////////////////////////
// Post verifications

// Check for mandatory parameters
if (!isset($globals->data)) {
	print('Data file parameter not found.' . NL . '-data="<data.json>" must be specified.' . NL . NL . usage());
	exit(1);
}
if (!isset($globals->module)) {
	print('Module file parameter not found.' . NL . '-module="<module>" must be specified.' . NL . NL . usage());
	exit(1);
}

/////////////////////////////////////////////////////////////////////
// Prepare additional variables

// Resolve all embedded variables on the $globals
foreach ($globals as $key => $value)
	$globals->{$key} = replace_vars($value);

// Check if the module file exists and loads it
$globals->moduleFile = 'include/collect_' . $globals->module . '.php';
if (!file_exists($globals->moduleFile)) {
	print('Module file ' . $globals->moduleFile . ' does not exist.' . NL . NL);
	exit(1);
}
require($globals->moduleFile);
if (!$globals->moduleLoaded) {
	print('Module file ' . $globals->moduleFile . ' did not load correctly.' . NL . NL);
	exit(1);
}

// Clean up data file name
if (substr($globals->data, 0, 2) == './')
	$globals->data = substr($globals->data, 2);

// Show content of the globals
if ($globals->debug > 2) {
	print('Globals : ');
	describe($globals);
}
if ($globals->debug > 3)
	die();

/////////////////////////////////////////////////////////////////////
// Collects the requested data

print('Collecting ' . $globals->module . ' data from ' . $globals->vision . ' ... ');

$query  = create_query($globals);
$result = collect_data($globals, $query);

if (!$globals->silent)
	print('Data recorded onto ' . $globals->data . '.' . NL);

print('Finished in ');
timeOut();
print(NL);
?>