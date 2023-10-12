#!/usr/bin/php
<?php
// Report Generator - v5.4 - by Marcelo Dantas

////////////////////////////////////////////////////////////////////////////////
// Constants (Generic)
require_once('include/defines.php');
require_once('include/globals.php');
require_once('include/functions.php');

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
define('NAME', 'report');
define('VERSION', '5.4');
define('APP', $argv[0]);
define(
	'USAGE',
	'[-h|-help] [-debug[=n]] [-silent] -report=<report.json> ...' . NL .
		TAB . '-h|-help    - Shows this help message.' . NL .
		TAB . '-debug[=n]  - Defines the debug (verbosity) level.' . NL .
		TAB . '-silent     - Supresses program header text. (for scripting)' . NL .
		TAB . '-report=<f> - Defines the json report description file to be used.' . NL .
		TAB . '...         - Any other argument will be available as a global variable.' . NL
);
define('PASSWORD', 'mservices'); // Password for .ZIP files

////////////////////////////////////////////////////////////////////////////////
// Set global variables onto "globals" object
// This makes it easy to share the object with functions

// $globals must be included above
$globals->doPDF   = false;
$globals->doPNG   = false;
$globals->doEmail = false;
$globals->doZip   = false;
$globals->timing  = false;
$globals->path    = str_replace(DIRECTORY_SEPARATOR, '/', dirname(realpath($argv[0])));
$globals->version = VERSION;

////////////////////////////////////////////////////////////////////////////////
// Require eMail system
use PHPMailer\PHPMailer\PHPMailer;
use PHPMailer\PHPMailer\Exception;
use PHPMailer\PHPMailer\SMTP;

require_once('include/PHPMailer.php');
require_once('include/Exception.php');
require_once('include/SMTP.php');

list($globals->name, $dummy) = explode('.', basename($argv[0]));
$globals->app = str_replace(DIRECTORY_SEPARATOR, '/', $argv[0]);

$globals->usageText = '-report="<report.json>" [-parm[=value]...]';

// Set some chart defaults

$defaults		    = new stdclass();
$defaults->language = 'en';
$defaults->topN     = 5;
$defaults->decimals = 2;

// Start computing execution time
timeIn();

/////////////////////////////////////////////////////////////////////
// Collect command line parameters and merge them into $globals

$globals = (object) array_merge((array) $globals, (array) parse_args());

// Program start
if (!isset($globals->silent)) {
	print(NL . 'Report v' . VERSION . ' - by Marcelo Dantas' . NL);
	print(DIVIDER . NL);
}

/////////////////////////////////////////////////////////////////////
// Pre-verifications

// Define operating system
if (file_exists('/usr/bin/php')) {
	if (file_exists('/mnt/c')) {
		$globals->os = 'WSL';
	} else {
		$globals->os = 'Linux';
	}
} else {
	$globals->os = 'Windows';
}

// Define browser
if (file_exists('/usr/bin/chrome'))
	$linux_browser = 'chrome';
if (file_exists('/usr/bin/google-chrome'))
	$linux_browser = 'google-chrome';
if (file_exists('/usr/bin/google-chrome-stable'))
	$linux_browser = 'google-chrome-stable';
if (file_exists('/usr/bin/chromium-browser'))
	$linux_browser = 'chromium-browser';

if ($globals->doPDF and $globals->os=='Linux' and !isset($linux_browser))
	die('No chrome available to generate PDFs' . NL);

// Check for sqlite3 php extension
if (!extension_loaded('sqlite3'))
	die('sqlite3 php extension not installed on php.ini' . NL);

/////////////////////////////////////////////////////////////////////
// Post verifications

// Check for mandatory parameters
if (!isset($globals->report)) {
	print('Report file parameter not found.' . NL . '-report="<report.json>" must be specified.' . NL . NL . usage());
	exit(1);
}

// Check if the report file exists
if (!file_exists($globals->report)) {
	print('Report file ' . $globals->report . ' does not exist.' . NL . NL);
	exit(1);
}

// Check report file syntax
$report = get_json_data($globals->report);

// Month (if exists) must have 2 digits
if (isset($globals->month)) {
	if ($globals->month < 10)
		$globals->month = '0' . $globals->month;
}

/////////////////////////////////////////////////////////////////////
// Show report title

if (isset($report->title))
	print(localize(replace_vars($report->title)) . NL);

/////////////////////////////////////////////////////////////////////
// Merge report global variables

if (isset($report->globals))
	$globals = object_merge($report->globals, $globals);

/////////////////////////////////////////////////////////////////////
// Prepare additional variables

// Top N
if (isset($globals->topN))
	$defaults->topN = $globals->topN;

// Output file
if (!isset($globals->output))
	$globals->output = 'output.htm';
if ($globals->debug)
	print('Generating ' . $globals->output . '...' . NL);

// Page Skip list
if (isset($globals->skip)) {
	$skiplist = array();
	$array = explode(',', $globals->skip);
	foreach ($array as $id)
		$skiplist[$id] = true;
}

// Report title
if (!isset($report->title))
	$report->title = 'Report v' . VERSION;

// Report language formatting
if (isset($report->language)) {
	$globals->language = $report->language;
} else {
	if (!isset($globals->language))
		$globals->language = $defaults->language;
}

if ($globals->language == 'en') {
	$globals->decimalSymbol  = '.';
	$globals->groupingSymbol = ',';
} else {
	$globals->decimalSymbol  = ',';
	$globals->groupingSymbol = '.';
}

// Report uses offline Google Charts
$report->offline = isset($report->offline) ? $report->offline : false;

// Resolve all embedded variables on the $globals
foreach ($globals as $key => $value)
	$globals->{$key} = replace_vars($value);

// Clean up input and output file names
if (substr($globals->report, 0, 2) == './')
	$globals->report = substr($globals->report, 2);
if (substr($globals->output, 0, 2) == './')
	$globals->output = substr($globals->output, 2);

// Generate PDF file name
$globals->pdf = str_replace('.htm', '.pdf', $globals->output);

// Generate CSV file name
$globals->csv = str_replace('.htm', '.txt', $globals->output);

// Generate ZIP file name
$globals->zip = str_replace('.htm', '.zip', $globals->output);

// Calculate relative path between the program and the output file 
$globals->relPath = relative_path(dirname($globals->path . '/' . $globals->output), $globals->path, '/');
if ($globals->relPath == '')
	$globals->relPath = './';

// Show content of the globals
if ($globals->debug > 2) {
	print('Globals : ');
	describe($globals);
}
if ($globals->debug > 3)
	die();

/////////////////////////////////////////////////////////////////////
// Process the report file

print('Generating report ');

if (!isset($globals->noCSV)) {
	$csv = fopen($globals->csv, 'w');
	if ($csv === false)
		die('ERROR: Cannot create CSV file. (' . $globals->csv . ')' . NL);
}

$out = fopen($globals->output, 'w');
if ($out === false)
	die('ERROR: Cannot create output file. (' . $globals->output . ')' . NL);

fputs($out, '<html>' . NL);
fputs($out, '<head>' . NL);
fputs($out, '	<title>' . $report->title . '</title>' . NL);
if (isset($report->stylesheet)) {
	fputs($out, '	<link rel="stylesheet" href="' . $report->stylesheet . '">' . NL);
} else {
	fputs($out, '	<link rel="stylesheet" href="' . $globals->relPath . 'html_files/css/default.css">' . NL);
}
if ($report->offline) {
	fputs($out, '	<script type="text/javascript">var relPath="' . $globals->relPath . '";</script>' . NL);
	fputs($out, '	<script type="text/javascript" src="' . $globals->relPath . 'html_files/charts/loader.js"></script>' . NL);
} else {
	fputs($out, '	<script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>' . NL);
}
fputs($out, '</head>' . NL);
fputs($out, '<body>' . NL);

$pageCt = 0;
foreach ($report->pages as $pageID => $page) {
	if (isset($page->include)) {
		$include = $page->include;
		if (file_exists('json_files/include/pages/' . $include . '.json')) {
			$include = json_decode(file_get_contents('json_files/include/pages/' . $include . '.json'));
			$page = object_merge($include, $page);
		} else {
			print('ERROR: Cannot find page include file. (json_files/include/pages/' . $include . '.json)' . NL);
		}
	}
	if (isset($page->id)) {
		if (isset($skiplist[$page->id])) {
			echo ('s');
			continue;
		}
	} else {
		$page->id = 'page' . ($pageID + 1);
	}
	if (isset($page->skip) and $page->skip == true) {
		echo ('s');
		continue;
	}

	if (isset($page->skipIf) and isset($globals->{$page->skipIf})) {
		if ($globals->{$page->skipIf} == true) {
			echo ('i');
			continue;
		}
	}

	if (isset($page->skipIfNot) and isset($globals->{$page->skipIfNot})) {
		if ($globals->{$page->skipIfNot} == false) {
			echo ('n');
			continue;
		}
	}

	if ($globals->timing) {
		timeIn(0);
		print(NL . $page->id . ' : ');
	} else {
		echo ('.');
	}

	$pageCt++;
	// Store the page ID onto the globals
	$globals->pageID     = $pageID++;
	$globals->pageNumber = $pageCt;

	if ($globals->debug)
		print('  \'--Page ' . $globals->pageNumber . '(' . $page->id . ')' . NL);

	// Define if the page is landscape
	$page->landscape = isset($page->landscape) ? $page->landscape : false;

	// Merge page defaults
	if ($page->landscape) {
		if (isset($report->defaults->page_landscape)) {
			if (isset($report->defaults->page_landscape->include)) {
				$include = $report->defaults->page_landscape->include;
				if (file_exists('json_files/include/pages/' . $include . '.json')) {
					$include = json_decode(file_get_contents('json_files/include/pages/' . $include . '.json'));
					$page = object_merge($include, $page);
				} else {
					print('ERROR: Cannot find page defaults include file. (json_files/include/pages/' . $include . '.json)' . NL);
				}
			} else {
				$page = object_merge($report->defaults->page_landscape, $page);
			}
		}
	} else {
		if (isset($report->defaults->page)) {
			if (isset($report->defaults->page->include)) {
				$include = $report->defaults->page->include;
				if (file_exists('json_files/include/pages/' . $include . '.json')) {
					$include = json_decode(file_get_contents('json_files/include/pages/' . $include . '.json'));
					$page = object_merge($include, $page);
				} else {
					print('ERROR: Cannot find page defaults include file. (json_files/include/pages/' . $include . '.json)' . NL);
				}
			} else {
				$page = object_merge($report->defaults->page, $page);
			}
		}
	}

	// Compute object offset number
	$objOffset = 0;
	if (isset($report->defaults->page->objects))
		$objOffset = count($report->defaults->page->objects);

	// Output the page div
	if ($page->landscape) {
		fputs($out, '<div class="page_landscape"');
	} else {
		fputs($out, '<div class="page"');
	}
	fputs($out, ' id="' . replace_vars($page->id) . '"');
	if (isset($page->title))
		fputs($out, ' title="' . $page->title . '"');
	if (isset($page->style))
		fputs($out, ' style="' . get_style($page) . '"');
	fputs($out, '>' . NL);

	// Table to keep the database handles
	$globals->dbHandles = array();

	// Scan through the page objects
	foreach ($page->objects as $objectID => $object) {
		// check for object include
		if (isset($object->include)) {
			$include = $object->include;
			if (file_exists('json_files/include/objects/' . $include . '.json')) {
				$include = json_decode(file_get_contents('json_files/include/objects/' . $include . '.json'));
				$object = object_merge($include, $object);
			} else {
				print('ERROR: Cannot find object include file. (json_files/include/objects/' . $include . '.json)' . NL);
			}
		}

		// Store the page ID onto the globals
		$globals->objectID     = $objectID++;
		$globals->objectNumber = $objectID;

		// Merge object defaults
		if (isset($report->defaults->object))
			$object = object_merge($report->defaults->object, $object);

		// Merge object globals
		if (isset($object->globals))
			$globals = object_merge($globals, $object->globals);

		$objectID -= $objOffset;

		// No object type defined?
		if (!isset($object->object)) {
			print('Warning: No object type defined on page #' . $pageID . ' object ' . $objectID . '.' . NL);
			continue;
		}

		// Is object centered?
		$centered = isset($object->centered) ? $object->centered : false;

		if ($globals->debug)
			print('     \'--Object ' . $globals->objectNumber . ': ' . $object->object . NL);

		// Check if the object already has an open database
		if (isset($globals->db))														// Overrides if passed as global parm
			$object->db = $globals->db;
		if (isset($object->db)) {														// If object has a database definition
			$object->db = replace_vars($object->db);									//   replace the variables on it
			if (isset($globals->dbHandles[$object->db])) {								// If the database is already open
				$globals->dbHandle = $globals->dbHandles[$object->db];
			} else {																	// If the database is not open yet
				$globals->dbHandle = new SQLite3($object->db, SQLITE3_OPEN_READONLY);	// Open it
				$globals->dbHandles[$object->db] = $globals->dbHandle;					//   and store in the table
			}
		}

		/////////////////////////////////////////////////////////////////////
		// Ignore an appendix object
		if ($object->object == 'appendix')
			continue;

		/////////////////////////////////////////////////////////////////////
		// Output an index object
		if ($object->object == 'index') {
			// An index MUST have an ID
			if (!isset($object->id))
				$object->id = 'index_' . $pageID . '_' . $objectID;

			// Output the text div
			if ($centered)
				fputs($out, '	<center>' . NL);
			fputs($out, '	<div class="text"');
			fputs($out, ' id="' . replace_vars($object->id) . '"');
			if (isset($object->style))
				fputs($out, ' style="' . get_style($object) . '"');
			fputs($out, '>' . NL);
			$object->data   = array();
			$object->data[] = array(
				localize('Page Content'),
				localize('Page Number')
			);
			$pageNo = 0;
			foreach ($report->pages as $indexID => $indexPage) {
				if (isset($indexPage->include)) {
					$include = $indexPage->include;
					if (file_exists('json_files/include/pages/' . $include . '.json')) {
						$include = json_decode(file_get_contents('json_files/include/pages/' . $include . '.json'));
						$indexPage = object_merge($include, $indexPage);
					} else {
						print('ERROR: Cannot find indexing page include file. (json_files/include/pages/' . $include . '.json)' . NL);
					}
				}
				if (isset($indexPage->id)) {
					if (isset($skiplist[$indexPage->id]))
						continue;
				}
				if (isset($indexPage->skip) and $indexPage->skip == true)
					continue;

				if (isset($indexPage->skipIf) and isset($globals->{$indexPage->skipIf})) {
					if ($globals->{$indexPage->skipIf} == true)
						continue;
				}

				if (isset($indexPage->skipIfNot) and isset($globals->{$indexPage->skipIfNot})) {
					if ($globals->{$indexPage->skipIfNot} == false)
						continue;
				}

				$pageNo++;
				if (isset($object->minPage)) {
					if ($pageNo < $object->minPage)
						continue;
				}
				if (isset($object->maxPage)) {
					if ($pageNo > $object->maxPage)
						continue;
				}
				if (!isset($indexPage->id))
					$indexPage->id = 'page' . $pageNo;
				if (!isset($indexPage->title))
					$indexPage->title = localize('Page') . ' ' . $pageNo;
				$object->data[] = array(
					'<a href=#' . $indexPage->id . '>' . $indexPage->title . '</a>',
					$pageNo
				);
			}
			$object->type = 'table';
			// If $object->data is an empty array, do not write the chart
			if (count($object->data) == 0) {
				print("WARNING: Chart $object->id ($page->id) has no data.");
			} else {
				// Write the chart
				write_chart($out, $object); // Function to generate chart from object
			}
			fputs($out, '	</div>' . NL);
			if ($centered)
				fputs($out, '	</center>' . NL);
			continue;
		}

		/////////////////////////////////////////////////////////////////////
		// Output a text object
		if ($object->object == 'text') {
			// Merge text defaults
			if (isset($report->defaults->text))
				$object = object_merge($report->defaults->text, $object);

			// If we have a src, override the text
			if (isset($object->src)) {
				if ($object->src == 'sql') {		// Text src can be SQL query
					if (!isset($object->db)) {
						print('Warning: Text sql database not defined on page #' . $pageID . ' object ' . $objectID . '.' . NL);
						continue;
					}
					if (!file_exists($object->db)) {
						print('Warning: Text database file (' . $object->db . ') not found on page #' . $pageID . ' object ' . $objectID . '.' . NL);
						continue;
					}
					if (!isset($object->sql)) {
						print('Warning: Text sql query not defined on page #' . $pageID . ' object ' . $objectID . '.' . NL);
						continue;
					} else {
						if (gettype($object->sql) == 'array')
							$object->sql = implode('; ', $object->sql);
						if ($globals->debug)
							print('        \'--from sql (');
						$object->text = text_from_sql($object->sql);
						if ($globals->debug)
							print(')' . NL);
					}
				}
				if ($object->src == 'file') {	// Text src can be a file
					$file = replace_vars($object->file);
					if (!file_exists($file)) {
						print('Warning: Text file ' . $file . ' not found on page #' . $pageID . ' object ' . $objectID . '.' . NL);
						continue;
					} else {
						if ($globals->debug)
							print('        \'--from file ' . $file . NL);
						$object->text = file_get_contents($file);
					}
				}
				if ($object->src == 'cmd') {		// Text src can be a command
					$cmd = replace_vars($object->cmd);
					if ($globals->debug)
						print('        \'--from command ' . $cmd . NL);
					exec($cmd, $array);
					$object->text = text_from_array($array);
				}
				if ($object->src == 'code') {		// Text src can be PHP code
					if (gettype($object->code) == 'array')
						$object->code = implode('; ', $object->code);
					$code = replace_vars($object->code);
					if ($globals->debug)
						print('        \'--from code ' . $code . NL);
					$object->text = eval($code);
				}
			}

			// A text object MUST have text
			if (!isset($object->text)) {
				print('Warning: Text content not defined on page #' . $pageID . ' object ' . $objectID . '.' . NL);
				continue;
			}

			// Output the text div
			if ($centered)
				fputs($out, '	<center>' . NL);
			fputs($out, '	<div class="text"');
			if (isset($object->id))
				fputs($out, ' id="' . replace_vars($object->id) . '"');
			if (isset($object->style))
				fputs($out, ' style="' . get_style($object) . '"');
			fputs($out, '>' . NL);
			fputs($out, replace_vars($object->text) . NL);
			fputs($out, '	</div>' . NL);
			if ($centered)
				fputs($out, '	</center>' . NL);
			continue;
		}

		/////////////////////////////////////////////////////////////////////
		// Output an image object
		if ($object->object == 'image') {
			// Merge image defaults
			if (isset($report->defaults->image))
				$object = object_merge($report->defaults->image, $object);

			// An image object MUST have a source
			if (!isset($object->src)) {
				print('Warning: Image source not defined on page #' . $pageID . ' object ' . $objectID . '.' . NL);
				continue;
			}

			if ($globals->debug)
				print('        \'--from ' . $object->src . NL);

			// Output the image div
			if ($centered)
				fputs($out, '	<center>' . NL);
			fputs($out, '	<div class="image"');
			if (isset($object->id))
				fputs($out, ' id="' . replace_vars($object->id) . '"');
			if (isset($object->style))
				fputs($out, ' style="' . get_style($object) . '"');
			fputs($out, '>' . NL);
			fputs($out, '		<img src="' . replace_vars($object->src) . '"');
			if (isset($object->width))
				fputs($out, ' width="' . $object->width . '"');
			if (isset($object->height))
				fputs($out, ' height="' . $object->height . '"');
			fputs($out, '>' . NL);
			fputs($out, '	</div>' . NL);
			if ($centered)
				fputs($out, '	</center>' . NL);
			continue;
		}

		/////////////////////////////////////////////////////////////////////
		// Output a chart object
		if ($object->object == 'chart') {
			// Merge chart defaults
			if (isset($report->defaults->chart))
				$object = object_merge($report->defaults->chart, $object);

			// A chart MUST have an ID
			if (!isset($object->id))
				$object->id = 'chart_' . $pageID . '_' . $objectID;

			// A chart MUST have some type
			if (!isset($object->type)) {
				print('Warning: Chart type not defined on page #' . $pageID . ' object ' . $objectID . '.' . NL);
				continue;
			}

			// A chart must have a data source
			if (!isset($object->src)) {
				print('Warning: Chart source not defined on page #' . $pageID . ' object ' . $objectID . '.' . NL);
				continue;
			}

			// Set some per-chart globals
			if (isset($object->topN)) {
				$globals->topN = $object->topN;
			} else {
				$globals->topN = $defaults->topN;
			}
			if (isset($object->decimals)) {
				$globals->decimals = $object->decimals;
			} else {
				$globals->decimals = $defaults->decimals;
			}

			// Evaluates the chart
			if ($object->src == 'last') { 	// Chart src can be the last chart or dummy data
				if (!isset($globals->lastData)) {
					print('Warning: Chart last data not defined on page #' . $pageID . ' object ' . $objectID . '.' . NL);
					continue;
				}
				if ($globals->debug)
					print('        \'--from last' . NL);
				$object->data = $globals->lastData;
			}
			if ($object->src == 'sql') { 	// Chart src can be SQL query
				if (!isset($object->db)) {
					print('Warning: Chart sql database not defined on page #' . $pageID . ' object ' . $objectID . '.' . NL);
					continue;
				}
				if (!file_exists($object->db)) {
					print('Warning: Chart database file (' . $object->db . ') not found on page #' . $pageID . ' object ' . $objectID . '.' . NL);
					continue;
				}
				if (!isset($object->sql)) {
					print('Warning: Chart sql query not found on page #' . $pageID . ' object ' . $objectID . '.' . NL);
					continue;
				} else {
					if (gettype($object->sql) == 'array')
						$object->sql = implode('; ', $object->sql);
					if ($globals->debug)
						print('        \'--from sql (');
					$object->data = array_from_sql($object->sql, true);
					if ($globals->debug)
						print(')' . NL);
				}
			}
			if ($object->src == 'csv') {		// Chart src can be a CSV file
				$file = replace_vars($object->csv);
				if (!file_exists($file)) {
					print('Warning: Chart CSV file ' . $file . ' not found on page #' . $pageID . ' object ' . $objectID . '.' . NL);
					continue;
				} else {
					if ($globals->debug)
						print('        \'--from file ' . $file . NL);
					$object->data = array_from_csv($object);
				}
			}
			if ($object->src == 'cmd') {		// Chart src can be a command
				$cmd = replace_vars($object->cmd);
				$array = explode(' ', $cmd);
				$file = $array[0];
				if (!file_exists($file)) {
					print('Warning: Chart command ' . $file . ' not found on page #' . $pageID . ' object ' . $objectID . '.' . NL);
					continue;
				} else {
					if ($globals->debug)
						print('        \'--from command ' . $cmd . NL);
					$object->data = array_from_cmd($object);
				}
			}
			if ($object->src == 'code') {		// Chart src can be PHP code
				if (gettype($object->code) == 'array')
					$object->code = implode('; ', $object->code);
				$code = replace_vars($object->code);
				if ($globals->debug)
					print('        \'--from code ' . $code . NL);
				$object->data = eval($code);
			}

			// A chart MUST have data
			if (!isset($object->data)) {
				print('Warning: Chart data not defined on page #' . $pageID . ' object ' . $objectID . '.' . NL);
				unset($globals->lastData);
				continue;
			}

			// Save the data for the next chart
			$globals->lastData = $object->data;

			// Output the chart div
			if ($centered)
				fputs($out, '	<center>' . NL . '	');
			fputs($out, '	<div class="chart"');
			if (isset($object->id))
				fputs($out, ' id="' . replace_vars($object->id) . '"');
			if (isset($object->style))
				fputs($out, ' style="' . get_style($object) . '"');
			fputs($out, '></div>' . NL);
			if ($centered)
				fputs($out, '	</center>' . NL);

			// Save data onto the CSV file
			if (!isset($object->title))
				$object->title = 'no title';
			$array = array($object->id, $object->object, $object->type, $object->title);
			if (!isset($globals->noCSV)) {
				fputcsv($csv, $array);
				foreach ($object->data as $data) {
					foreach ($data as $key => $value)
						$data[$key] = localize(replace_vars($value));
					fputcsv($csv, $data);
				}
				fputs($csv, DIVIDER . NL);
			}
			// If $object->data is an empty array, do not write the chart
			if (count($object->data) == 0) {
				print("WARNING: Chart $object->id ($page->id) has no data.");
			} else {
				// Write the chart
				write_chart($out, $object); // Function to generate chart from object
			}

			continue;
		}

		/////////////////////////////////////////////////////////////////////
		// Set a global variable from object
		if ($object->object == 'variable') {
			// Merge variable defaults
			if (isset($report->defaults->variable))
				$object = object_merge($report->defaults->variable, $object);

			// A variable must have a name
			if (!isset($object->name)) {
				print('Warning: Variable name not defined on page #' . $pageID . ' object ' . $objectID . '.' . NL);
				continue;
			}

			// A variable must have a value source
			if (!isset($object->src)) {
				print('Warning: Variable source not defined on page #' . $pageID . ' object ' . $objectID . '.' . NL);
				continue;
			}

			// Compute and store the variable
			if ($object->src == 'sql') { // Variable value can be the result of a SQL query
				if (!isset($object->db)) {
					print('Warning: Variable sql database not defined on page #' . $pageID . ' object ' . $objectID . '.' . NL);
					continue;
				}
				if (!file_exists($object->db)) {
					print('Warning: Variable database file (' . $object->db . ') not found on page #' . $pageID . ' object ' . $objectID . '.' . NL);
					continue;
				}
				if (!isset($object->sql)) {
					print('Warning: Variable sql query not found on page #' . $pageID . ' object ' . $objectID . '.' . NL);
					continue;
				} else {
					if (gettype($object->sql) == 'array')
						$object->sql = implode('; ', $object->sql);
					if ($globals->debug)
						print('        \'--from sql (');
					$object->value = text_from_sql($object->sql);
					if ($globals->debug)
						print(')' . NL);
				}
			}
			if ($object->src == 'cmd') {	// Variable value can be the result of a cmd
				$cmd = replace_vars($object->cmd);
				if ($globals->debug)
					print('        \'--from command ' . $cmd . NL);
				unset($array);
				exec($cmd, $array);
				$object->value = text_from_array($array);
				if ($globals->debug)
					print('         \'--result ' . $object->value . NL);
			}
			if ($object->src == 'code') {	// Variable value can be the result of a PHP code
				if (gettype($object->code) == 'array')
					$object->code = implode('; ', $object->code);
				$code = replace_vars($object->code);
				if ($globals->debug)
					print('        \'--from code ' . $code . NL);
				$object->value = eval($code);
			}

			// Format the variable if numeric
			if (isset($object->format)) {
				if ($object->format == 'number') {
					$decimals      = (int)replace_vars(isset($object->decimals) ? $object->decimals : $globals->decimals);
					$object->value = number_format($object->value * 1, $decimals, $globals->decimalSymbol, $globals->groupingSymbol);
				}
			}

			$globals->{$object->name} = replace_vars($object->value);
			continue;
		}

		/////////////////////////////////////////////////////////////////////
		// Process a dummy (chart) object
		if ($object->object == 'dummy') {
			// Merge dummy defaults
			if (isset($report->defaults->dummy))
				$object = object_merge($report->defaults->dummy, $object);

			// A dummy must have a data source
			if (!isset($object->src)) {
				print('Warning: Dummy source not defined on page #' . $pageID . ' object ' . $objectID . '.' . NL);
				continue;
			}

			// Evaluates the dummy
			if ($object->src == 'sql') { 	// Dummy src can be SQL query
				if (!isset($object->db)) {
					print('Warning: Dummy sql database not defined on page #' . $pageID . ' object ' . $objectID . '.' . NL);
					continue;
				}
				if (!file_exists($object->db)) {
					print('Warning: Dummy database file (' . $object->db . ') not found on page #' . $pageID . ' object ' . $objectID . '.' . NL);
					continue;
				}
				if (!isset($object->sql)) {
					print('Warning: Dummy sql query not found on page #' . $pageID . ' object ' . $objectID . '.' . NL);
					continue;
				} else {
					if (gettype($object->sql) == 'array')
						$object->sql = implode('; ', $object->sql);
					if ($globals->debug)
						print('        \'--from sql (');
					$object->data = array_from_sql($object->sql, true);
					if ($globals->debug)
						print(')' . NL);
				}
			}
			if ($object->src == 'csv') {		// Dummy src can be a CSV file
				$file = replace_vars($object->csv);
				if (!file_exists($file)) {
					print('Warning: Dummy CSV file ' . $file . ' not found on page #' . $pageID . ' object ' . $objectID . '.' . NL);
					continue;
				} else {
					if ($globals->debug)
						print('        \'--from file ' . $file . NL);
					$object->data = array_from_csv($object);
				}
			}
			if ($object->src == 'cmd') {		// Dummy src can be a command
				$cmd = replace_vars($object->cmd);
				$array = explode(' ', $cmd);
				$file = $array[0];
				if (!file_exists($file)) {
					print('Warning: Dummy command ' . $file . ' not found on page #' . $pageID . ' object ' . $objectID . '.' . NL);
					continue;
				} else {
					if ($globals->debug)
						print('        \'--from command ' . $cmd . NL);
					$object->data = array_from_cmd($object);
				}
			}
			if ($object->src == 'code') {		// Dummy src can be PHP code
				if (gettype($object->code) == 'array')
					$object->code = implode('; ', $object->code);
				$code = replace_vars($object->code);
				if ($globals->debug)
					print('        \'--from code ' . $code . NL);
				$object->data = eval($code);
			}

			// A dummy MUST have data
			if (!isset($object->data)) {
				print('Warning: Dummy data not defined on page #' . $pageID . ' object ' . $objectID . '.' . NL);
				unset($globals->lastData);
				continue;
			}

			// Save the data for the next chart
			$globals->lastData = $object->data;

			continue;
		}

		/////////////////////////////////////////////////////////////////////
		// Wrong type
		print('Warning: Wrong object type "' . $object->object . '" defined on page #' . $pageID . ' object ' . $objectID . '.' . NL);
	}
	fputs($out, '</div>' . NL);
	fflush($out);
	if ($globals->timing)
		timeOut(0);
}

fputs($out, '</body>' . NL);
fputs($out, '</html>' . NL);
fclose($out);
if (!isset($globals->noCSV))
	fclose($csv);

print(' Done.' . NL . 'Report recorded onto ' . $globals->output . '.' . NL);

// Generate a PDF
if ($globals->doPDF) {
	print('Generating PDF ...' . NL);
	$filePath = $globals->path . '/' . $globals->output;
	$pdfPath  = $globals->path . '/' . $globals->pdf;
	if ($globals->os == 'Windows') {
		$pdf = '.\tools\chrome\chrome.exe --headless --incognito --print-to-pdf="' . $pdfPath . '" file://' . $filePath;
		exec($pdf);
	} else {
		if ($globals->os == 'Linux') {
			$pdf = $linux_browser . ' --headless --incognito --no-sandbox --print-to-pdf="' . $pdfPath . '" file://' . $filePath;
		} else {
			$pdf = 'tools/chrome/chrome.exe --headless --incognito --print-to-pdf="' . $pdfPath . '" file://' . $filePath;
			$pdf = str_replace('/mnt/c', 'C:', $pdf);
		}
		exec($pdf . ' 2>/dev/null');
	}
	print('PDF recorded onto ' . $globals->pdf . '.' . NL);
// Keep the html file
//	if (!isset($globals->keepHTM)) {
//		print('Removing HTM ...' . NL);
//		unlink($globals->output);
//	}
}

// ZIP the PDF and CSV files if needed
if ($globals->doZip) {
	// if os is windows, disable doZip
	if ($globals->os == 'Windows') {
		print('ZIP disabled on Windows.' . NL);
		unset($globals->doZip);
	} else {
		$files = '';
		print('Compressing Attachments ...' . NL);
		if ($globals->doPDF)
			$files .= $globals->pdf . ' ';
		if (!isset($globals->noCSV))
			$files .= $globals->csv . ' ';
		if ($files != '') {
			$cmd = 'zip -9j -FS -P ' . PASSWORD . ' ' . $globals->zip . ' ' . $files;
			exec($cmd);
		}
	}
}

// Send the PDF via eMail
if ($globals->doEmail and $globals->doPDF) {
	if (isset($globals->eMail)) {
		print('Sending eMail ...' . NL);
		$mail = new PHPMailer(true);
		// Server
		//$mail->SMTPDebug = SMTP::DEBUG_SERVER;
		$mail->isSMTP();
		$mail->Host = '10.100.1.165';
		$mail->Port = 25;
		$mail->SMTPOptions = array(
			'ssl' => array(
				'verify_peer' => false,
				'verify_peer_name' => false,
				'allow_self_signed' => true
			)
		);
		// Recipients
		$mail->setFrom('managed-services.report@radware.com', 'Managed Services Report');
		$array = explode(';', $globals->eMail);
		foreach ($array as $eMail)
			$mail->addAddress($eMail);
		// Attachments
		if ($globals->doZip) {
			$mail->addAttachment($globals->zip);
		} else {
			$mail->addAttachment($globals->pdf);
			if (!isset($globals->noCSV))
				$mail->addAttachment($globals->csv);
		}
		// Content
		$mail->isHTML(false);
		$mail->Subject = 'Monthly Report ' . $globals->month . ' ' . $globals->year . ' - ' . $globals->longName;
		$mailText = 'Dear TAM,' . NL . NL;
		$mailText .= 'Attached is the latest monthly report for ' . $globals->longName . '.' . NL;
		$mailText .= 'Please verify the report content for accuracy.' . NL;
		if ($globals->doZip)
			$mailText .= 'The password to extract the report zip file is "' . PASSWORD . '".' . NL;
		$mailText .= 'If needed, please reply to this message with any requests for modifications.' . NL . NL;
		$mailText .= 'Sincerely,' . NL;
		$mailText .= 'AutoReport v' . VERSION;
		$mail->Body = $mailText;
		// Send
		try {
			$mail->send();
			print('eMail message has been sent to ' . $globals->eMail . '.' . NL);
		} catch (exception $e) {
			print('eMail message could not be sent. Mailer Error: ' . $mail->ErrorInfo . NL);
		}
	} else {
		print('Destination eMail not defined.' . NL);
	}
}

print('Finished in ');
timeOut();
print(NL);
?>