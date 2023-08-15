#!/usr/bin/php
<?php
// Data Compiler - v5.4 - by Marcelo Dantas

////////////////////////////////////////////////////////////////////////////////
// Include files
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
define('NAME', 'compile');
define('VERSION', '5.4');
define('APP', $argv[0]);
define('SPC', str_repeat(' ', 8 + strlen($argv[0])));
define(
	'USAGE',
	'[-h|-help] [-debug[=n]] [-silent] -db=<database file>' . NL .
		SPC . ' -data=<source file> -module=x ...' . NL .
		TAB . '-h|-help    - Shows this help message.' . NL .
		TAB . '-debug[=n]  - Defines the debug (verbosity) level.' . NL .
		TAB . '-silent     - Supresses program header text. (for scripting)' . NL .
		TAB . '-db=<f>     - Defines the database to write the compiled data.' . NL .
		TAB . '-data=<f>   - Defines the data file to read from.' . NL .
		TAB . '-module=<s> - Defines the data compilation module to be used.' . NL .
		TAB . '...         - Any other argument will be available as a global variable.' . NL
);

/////////////////////////////////////////////////////////////////////
// Set global variables onto "globals" object
// This makes it easy to share the object with functions
$globals->moduleLoaded = false;
$globals->overwrite    = false;
$globals->silent       = false;
$globals->geoUseHostIP = false;
$globals->index        = true;
$globals->action       = 'REPLACE';

list($globals->name, $dummy) = explode('.', basename($argv[0]));
$globals->app = str_replace(DIRECTORY_SEPARATOR, '/', $argv[0]);

// Start computing execution time
timeIn();

/////////////////////////////////////////////////////////////////////
// Collect command line parameters and merge them into $globals

$globals = (object) array_merge((array) $globals, (array) parse_args());

// Program start
if (!$globals->silent) {
	print(NL . 'Compile v' . VERSION . ' - by Marcelo Dantas' . NL);
	print(DIVIDER . NL);
}

/////////////////////////////////////////////////////////////////////
// Pre-verifications

// Check for sqlite3 php extension
if (!extension_loaded('sqlite3'))
	die('sqlite3 php extension not installed on php.ini' . NL);

/////////////////////////////////////////////////////////////////////
// Post verifications

// Check for mandatory parameters
if (!isset($globals->data)) {
	print('Data file parameter not found.' . NL . '-data="<data.json>" must be specified.' . NL . NL . usage());
	exit(1);
}
if (!isset($globals->db)) {
	print('Database file parameter not found.' . NL . '-db="<database.sqlite>" must be specified.' . NL . NL . usage());
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
$globals->moduleFile = 'include/compile_' . $globals->module . '.php';
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

// Clean up database file name
if (substr($globals->db, 0, 2) == './')
	$globals->db = substr($globals->db, 2);

// Show content of the globals
if ($globals->debug > 2) {
	print('Globals : ');
	describe($globals);
}
if ($globals->debug > 3)
	die();

/////////////////////////////////////////////////////////////////////
// Compiles the requested data

print('Compiling ' . $globals->module . ' data ... ' . NL);

$db = create_database($globals);
$result = compile_data($globals, $db);

if (!$globals->silent)
	print('Data compiled onto ' . $globals->db . '.' . NL);

print('Finished in ');
timeOut();
print(NL);
?>