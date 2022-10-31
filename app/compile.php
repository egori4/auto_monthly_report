#!/usr/bin/php -f
<?php
// Data Compiler - v5.0.1 - by Marcelo Dantas

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
$globals->moduleLoaded = false;
$globals->overwrite    = false;
$globals->silent       = false;
$globals->geoUseHostIP = false;
$globals->index        = false;
$globals->action       = 'REPLACE';

$globals->path = str_replace(DIRECTORY_SEPARATOR, '/', dirname(realpath($argv[0])));

list($globals->name, $dummy) = explode('.', basename($argv[0]));
$globals->app = str_replace(DIRECTORY_SEPARATOR, '/', $argv[0]);
if(strtoupper(substr(PHP_OS, 0, 3)) === 'WIN') {
	$globals->jq = $globals->path . '/tools/jq.exe';
} else {
	$globals->jq = '/usr/bin/jq';
}

$globals->usageText = '-data="<data.json>" -db="<database.sqlite>" -module="<module>" [-parm[=value]...]';

// Include required libraries
include($globals->path . '/include/functions.php');
include($globals->path . '/include/vision.php');

// Start computing execution time
timeIn();

/////////////////////////////////////////////////////////////////////
// Collect command line parameters and merge them into $globals

$globals = (object) array_merge((array) $globals, (array) parse_args());

// Program start
if(!$globals->silent) {
	print(NL . 'Compile v' . $globals->version . ' - by Marcelo Dantas' . NL);
	print('---------------------------------------' . NL);
}

/////////////////////////////////////////////////////////////////////
// Pre-verifications

// There must be at least the 'data' and 'module' parameters
if($argc < 4) {
	print(usage());
	exit(1);
}

/////////////////////////////////////////////////////////////////////
// Post verifications

// Check for mandatory parameters
if(!isset($globals->data)) {
	print('Data file parameter not found.' . NL . '-data="<data.json>" must be specified.' . NL . NL . usage());
	exit(1);
}
if(!isset($globals->db)) {
	print('Database file parameter not found.' . NL . '-db="<database.sqlite>" must be specified.' . NL . NL . usage());
	exit(1);
}
if(!isset($globals->module)) {
	print('Module file parameter not found.' . NL . '-module="<module>" must be specified.' . NL . NL . usage());
	exit(1);
}

/////////////////////////////////////////////////////////////////////
// Prepare additional variables

// Resolve all embedded variables on the $globals
foreach($globals as $key => $value)
	$globals->{$key} = replace_vars($value);

// Check if the module file exists and loads it
$globals->moduleFile = 'include/compile_' . $globals->module . '.php';
if(!file_exists($globals->moduleFile)) {
	print('Module file ' . $globals->moduleFile . " doesn't exist." . NL . NL);
	exit(1);
}
require($globals->moduleFile);
if(!$globals->moduleLoaded) {
	print("Module file didn't load correctly." . NL . NL);
	exit(1);
}

// Clean up data file name
if(substr($globals->data, 0, 2) == './')
	$globals->data = substr($globals->data, 2);

// Clean up database file name
if(substr($globals->db, 0, 2) == './')
	$globals->db = substr($globals->db, 2);

// Show content of the globals
if($globals->debug > 1) {
	print('Globals : ');
	print_r($globals);
}
if($globals->debug > 2)
	die();

/////////////////////////////////////////////////////////////////////
// Compiles the requested data

print('Compiling ' . $globals->module . ' data ... ' . NL);

$db = create_database($globals);
$result = compile_data($globals, $db);

if(!$globals->silent)
	print('Data compiled onto ' . $globals->db . '.' . NL);

print('Finished in ');
timeOut();
print(NL);
?>