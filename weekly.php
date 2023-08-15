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
if (file_exists('cancel.exec'))
    die('Execution cancelled by command.' . NL);
if (file_exists('hold.exec')) {
    print('Execution held by command...' . NL);
    while (file_exists('hold.exec'))
        sleep(1);
}

////////////////////////////////////////////////////////////////////////////////
// Constants (App Specific)
define('NAME', 'weekly');
define('VERSION', '5.4');
define('APP', $argv[0]);
define('SPC', str_repeat(' ', 8 + strlen($argv[0])));
define(
    'USAGE',
    '[-h|-help] [-debug[=n]] -id=<customer ID>' . NL .
        SPC . '-date=dd.mm.yyyy [-range=<n>] ...' . NL .
        TAB . '-h|-help   - Shows this help message.' . NL .
        TAB . '-debug[=n] - Defines the debug (verbosity) level.' . NL .
        TAB . '-id=       - Defines the customer ID to be used. (all if undefined)' . NL .
        TAB . '-date=     - Defines the final date for the report.' . NL .
        TAB . '-range=    - Defines the number of days to be included in the report.' . NL .
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

// Check for a set range
if (!isset($globals->range))
    $globals->range = 7;

// Set range text
$globals->rangeText = '-' . $globals->range . ' days';

// Get today's date id needed
if (!isset($globals->date))
    $globals->date = date('d.m.Y');

// Get previous date if needed
if (!isset($globals->prevDate))
    $globals->prevDate = date('d.m.Y', strtotime($globals->rangeText, strtotime($globals->date)));

// get the current year from the date
$globals->year = date('Y', strtotime($globals->date));
// get the current month from the date
$globals->month = date('m', strtotime($globals->date));
// get the current day from the date
$globals->day = date('d', strtotime($globals->date));

// get the previous year from the date
$globals->prevYear = date('Y', strtotime($globals->prevDate));
// get the previous month from the date
$globals->prevMonth = date('m', strtotime($globals->prevDate));
// get the previous day from the date
$globals->prevDay = date('d', strtotime($globals->prevDate));

// Generate month text
$globals->monthText = array('', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')[+$globals->month];
// Generate previous month text
$globals->prevMonthText = array('', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')[+$globals->prevMonth];

// Adjust month type and size
$globals->month = sprintf("%02d", $globals->month);
// Adjust day type and size
$globals->day = sprintf("%02d", $globals->day);
// Adjust previous month type and size
$globals->prevMonth = sprintf("%02d", $globals->prevMonth);
// Adjust previous day type and size
$globals->prevDay = sprintf("%02d", $globals->prevDay);

// convert date to time with miliseconds
$globals->time = strtotime($globals->date) * 1000;
// convert previous date to time with miliseconds
$globals->prevTime = strtotime($globals->prevDate) * 1000;

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
    if (!isset($customer->weekly_report))
        $customer->weekly_report = 'json_files/WeeklyReport.json';

    // For each customer attribute, replace with a global variable if it exists
    foreach ($customer as $key => $value) {
        if (isset($globals->$key))
            $customer->$key = $globals->$key;
    }

    // Create the reports array
    $reports = array();

    // Check if $customer->weekly_report is of type string
    if (is_string($customer->weekly_report)) {
        $reports[] = $customer->weekly_report;
    } else {
        $reports = $customer->weekly_report;
    }

    // Process each report
    foreach ($reports as $key => $report) {
        // Generate report command line
        $cmd = $reportCmd;
        $cmd .= '-report=' . $report . ' ';
        $cmd .= '-id="' . $customer->id . '" -longName="' . $customer->longName . '" ';
        $cmd .= '-date="' . $globals->date . '" -prevDate="' . $globals->prevDate . '" ';
        $cmd .= '-day="' . $globals->day . '" -month="' . $globals->month . '" -year="' . $globals->year . '" ';
        $cmd .= '-prevDay="' . $globals->prevDay . '" -prevMonth="' . $globals->prevMonth . '" -prevYear="' . $globals->prevYear . '" ';
        $cmd .= '-time=' . $globals->time . ' -prevTime=' . $globals->prevTime . ' ';
        $cmd .= '-monthText="' . $globals->monthText . '" -prevMonthText="' . $globals->prevMonthText . '" ';
        $cmd .= '-span=' . ($globals->prevMonth == $globals->month ? '0' : '1') . ' ';
        if (!$key) {
            $cmd .= '-output="report_files/{id}/weekly_{id}_{day}_{month}_{year}.htm" ';
        } else {
            $cmd .= '-output="report_files/{id}/weekly_{id}_{month}_{year}_' . $key . '.htm" ';
        }
        if ($globals->rangeText == '-7 days') {
            $cmd .= '-range="weekly" ';
        } else {
            $cmd .= '-range="' . $globals->range . ' days" ';
        }
        if (!isset($globals->noPDF))
            $cmd .= '-doPDF ';
        if (isset($globals->vision))
            $cmd .= '-vision="' . $globals->vision . '" ';
        if (isset($customer->skip))
            $cmd .= '-skip="' . $customer->skip . '" ';
        if (isset($customer->EAAFdb) and $customer->EAAFdb == true) {
            $cmd .= '-EAAFdb=1 ';
	} else {
		$cmd .= '-EAAFdb=0 ';
	}
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