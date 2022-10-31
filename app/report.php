#!/usr/bin/php -f
<?php
// Report Generator - v5.0.3 - by Marcelo Dantas

/////////////////////////////////////////////////////////////////////
// Constants
define('NL', "\n");
define('TAB', "\t");

/////////////////////////////////////////////////////////////////////
// Set global variables onto "globals" object
// This makes it easy to share the object with functions

$globals          = new stdclass();
$globals->version = '5.0.3';
$globals->debug   = false;
$globals->doPDF   = false;
$globals->doPNG   = false;
$globals->path    = str_replace(DIRECTORY_SEPARATOR, '/', dirname(realpath($argv[0])));

list($globals->name, $dummy) = explode('.', basename($argv[0]));
$globals->app = str_replace(DIRECTORY_SEPARATOR, '/', $argv[0]);
if(strtoupper(substr(PHP_OS, 0, 3)) === 'WIN') {
	$globals->jq = $globals->path . '/tools/jq.exe';
} else {
	$globals->jq = '/usr/bin/jq';
}

$globals->usageText = '-file="<report.json>" [-parm[=value]...]';

// Set some chart defaults

$defaults		    = new stdclass();
$defaults->language = 'en';
$defaults->topN     = 15;
$defaults->decimals = 2;

// Include required libraries
include($globals->path . '/include/functions.php');

// Start computing execution time
timeIn();

/////////////////////////////////////////////////////////////////////
// Collect command line parameters and merge them into $globals

$globals = (object) array_merge((array) $globals, (array) parse_args());

// Program start
print(NL . 'Report v' . $globals->version . ' - by Marcelo Dantas' . NL);
print('---------------------------------------' . NL);

/////////////////////////////////////////////////////////////////////
// Pre-verifications

// There must be at least the 'file' parameter
if($argc == 1) {
	print(usage());
	exit(1);
}

// Define operating system
if(file_exists('/usr/bin/php')) {
	if(file_exists('/mnt/c')) {
		$globals->os = 'WSL';
	} else {
		$globals->os = 'Linux';
	}
} else {
	$globals->os = 'Windows';
}

// Define browser
if(file_exists('/usr/bin/chrome'))
	$linux_browser = 'chrome';
if(file_exists('/usr/bin/google-chrome'))
	$linux_browser = 'google-chrome';
if(file_exists('/usr/bin/google-chrome-stable'))
	$linux_browser = 'google-chrome-stable';
if(file_exists('/usr/bin/chromium-browser'))
	$linux_browser = 'chromium-browser';

/////////////////////////////////////////////////////////////////////
// Post verifications

// Check for mandatory parameters
if(!isset($globals->file)) {
	print('Report file parameter not found.' . NL . '-file="<report.json>" must be specified.' . NL . NL . usage());
	exit(1);
}

// Check if the report file exists
if(!file_exists($globals->file)) {
	print('Report file ' . $globals->file . " doesn't exist." . NL . NL);
	exit(1);
}

// Check report file syntax
$report = get_json_data($globals->file);
$error  = json_last_error();
if($error !== JSON_ERROR_NONE) {
	echo ('Error while validating the report file.' . NL);
	if(file_exists($globals->jq)) {
		passthru($globals->jq . ' ".[]" ' . $globals->file);
	} else {
		switch($error) {
			case JSON_ERROR_DEPTH:
				$error = 'Maximum depth exceeded!';
				break;
			case JSON_ERROR_STATE_MISMATCH:
				$error = 'Underflow or the modes mismatch!';
				break;
			case JSON_ERROR_CTRL_CHAR:
				$error = 'Unexpected control character found';
				break;
			case JSON_ERROR_SYNTAX:
				$error = 'Malformed JSON';
				break;
			case JSON_ERROR_UTF8:
				$error = 'Malformed UTF-8 characters found!';
				break;
			default:
				$error = 'Unknown error!';
				break;
		}
		echo ($error . NL);
	}
	print("Can't continue." . NL);
	exit(1);
}

/////////////////////////////////////////////////////////////////////
// Show report title

if(isset($report->title))
	print(localize(replace_vars($report->title)) . NL);

/////////////////////////////////////////////////////////////////////
// Merge report global variables

if(isset($report->globals))
	$globals = object_merge($report->globals, $globals);

/////////////////////////////////////////////////////////////////////
// Prepare additional variables

// Top N
if(isset($globals->topN))
	$defaults->topN = $globals->topN;

// Output file
if(!isset($globals->output))
	$globals->output = 'output.htm';
if($globals->debug)
	print('Generating ' . $globals->output . '...' . NL);

// Page Skip list
if(isset($globals->skip)) {
	$skiplist = array();
	$array = explode(',', $globals->skip);
	foreach($array as $id)
		$skiplist[$id] = true;
}

// Report title
if(!isset($report->title))
	$report->title = 'Report v' . $globals->version;

// Report language formatting
if(isset($report->language)) {
	$globals->language = $report->language;
} else {
	if(!isset($globals->language))
		$globals->language = $defaults->language;
}

if($globals->language == 'en') {
	$globals->decimalSymbol  = '.';
	$globals->groupingSymbol = ',';
} else {
	$globals->decimalSymbol  = ',';
	$globals->groupingSymbol = '.';
}

// Report uses offline Google Charts
$report->offline = isset($report->offline) ? $report->offline : false;

// Resolve all embedded variables on the $globals
foreach($globals as $key => $value)
	$globals->{$key} = replace_vars($value);

// Clean up input and output file names
if(substr($globals->file, 0, 2) == './')
	$globals->file = substr($globals->file, 2);
if(substr($globals->output, 0, 2) == './')
	$globals->output = substr($globals->output, 2);

// Generate PDF file name
$globals->pdf = str_replace('.htm', '.pdf', $globals->output);

// Generate CSV file name
$globals->csv = str_replace('.htm', '.txt', $globals->output);

// Calculate relative path between the program and the output file 
$globals->relPath = relative_path(dirname($globals->path . '/' . $globals->output), $globals->path, '/');
if($globals->relPath == '')
	$globals->relPath = './';

// Show content of the globals
if($globals->debug > 1) {
	print('Globals : ');
	print_r($globals);
}
if($globals->debug > 2)
	die();

/////////////////////////////////////////////////////////////////////
// Process the report file

print('Generating report ');

if(!isset($globals->noCSV)) {
	$csv = fopen($globals->csv, 'w');
	if($csv === false)
		die("ERROR: Can't create CSV file. (".$globals->csv.")" . NL);
}

$out = fopen($globals->output, 'w');
if($out === false)
	die("ERROR: Can't create output file. (".$globals->output.")" . NL);

fputs($out, '<html>' . NL);
fputs($out, '<head>' . NL);
fputs($out, '	<title>' . $report->title . '</title>' . NL);
if(isset($report->stylesheet)) {
	fputs($out, '	<link rel="stylesheet" href="' . $report->stylesheet . '">' . NL);
} else {
	fputs($out, '	<link rel="stylesheet" href="' . $globals->relPath . 'html_files/css/default.css">' . NL);
}
if($report->offline) {
	fputs($out, '	<script type="text/javascript">var relPath="' . $globals->relPath . '";</script>' . NL);
	fputs($out, '	<script type="text/javascript" src="' . $globals->relPath . 'html_files/charts/loader.js"></script>' . NL);
} else {
	fputs($out, '	<script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>' . NL);
}
fputs($out, '</head>' . NL);
fputs($out, '<body>' . NL);

$pageCt=0;
foreach($report->pages as $pageID => $page) {
	if(isset($page->id)) {
		if(isset($skiplist[$page->id])) {
			echo('s');
			continue;
		}
	} else {
		$page->id = 'page' . ($pageID + 1);
	}
	if(isset($page->skip) and $page->skip == true) {
		echo('s');
		continue;
	}

	echo('.');
	$pageCt++;
	// Store the page ID onto the globals
	$globals->pageID     = $pageID++;
	$globals->pageNumber = $pageCt;

	if($globals->debug)
		print('  \'--Page ' . $globals->pageNumber . '(' . $page->id . ')' . NL);

	// Merge page defaults
	if(isset($report->defaults->page))
		$page = object_merge($report->defaults->page, $page);

	// Compute object offset number
	$objOffset = 0;
	if(isset($report->defaults->page->objects))
		$objOffset = count($report->defaults->page->objects);

	// Output the page div
	$page->landscape = isset($page->landscape) ? $page->landscape : false;
	if($page->landscape) {
		fputs($out, '<div class="page-landscape"');
	} else {
		fputs($out, '<div class="page"');
	}
	fputs($out, ' id="' . replace_vars($page->id) . '"');
	if(isset($page->title))
		fputs($out, ' title="' . $page->title . '"');
	if(isset($page->style))
		fputs($out, ' style="' . get_style($page) . '"');
	fputs($out, '>' . NL);

	// Scan through the page objects
	foreach($page->objects as $objectID => $object) {
		// Store the page ID onto the globals
		$globals->objectID     = $objectID++;
		$globals->objectNumber = $objectID;

		// Merge object defaults
		if(isset($report->defaults->object))
			$object = object_merge($report->defaults->object, $object);

		$objectID -= $objOffset;

		// No object type defined?
		if(!isset($object->object)) {
			print('Warning: No object type defined on page #' . $pageID . ' object ' . $objectID . '.' . NL);
			continue;
		}

		// Is object centered?
		$centered = isset($object->centered) ? $object->centered : false;

		if($globals->debug)
			print('     \'--Object ' . $globals->objectNumber . ': ' . $object->object . NL);

		/////////////////////////////////////////////////////////////////////
		// Ignore an appendix object
		if($object->object == 'appendix')
			continue;

		/////////////////////////////////////////////////////////////////////
		// Output an index object
		if($object->object == 'index') {
			// An index MUST have an ID
			if(!isset($object->id))
				$object->id = 'index_' . $pageID . '_' . $objectID;

			// Output the text div
			if($centered)
				fputs($out, '	<center>' . NL);
			fputs($out, '	<div class="text"');
			fputs($out, ' id="' . replace_vars($object->id) . '"');
			if(isset($object->style))
				fputs($out, ' style="' . get_style($object) . '"');
			fputs($out, '>' . NL);
			$object->data   = array();
			$object->data[] = array(
				localize('Page Content'),
				localize('Page Number')
			);
			$pageNo=0;
			foreach($report->pages as $indexID => $indexPage) {
				if(isset($indexPage->id)) {
					if(isset($skiplist[$indexPage->id]))
						continue;
				}
				if(isset($indexPage->skip) and $indexPage->skip == true)
					continue;

				$pageNo++;
				if(isset($object->minPage)) {
					if($pageNo < $object->minPage)
						continue;
				}
				if(isset($object->maxPage)) {
					if($pageNo > $object->maxPage)
						continue;
				}
				if(!isset($indexPage->id))
					$indexPage->id = 'page' . $pageNo;
				if(!isset($indexPage->title))
					$indexPage->title = localize('Page') . ' ' . $pageNo;
				$object->data[] = array(
					'<a href=#' . $indexPage->id . '>' . $indexPage->title . '</a>',
					$pageNo
				);
			}
			$object->type = 'table';
			write_chart($out, $object);
			fputs($out, '	</div>' . NL);
			if($centered)
				fputs($out, '	</center>' . NL);
			continue;
		}

		/////////////////////////////////////////////////////////////////////
		// Output a text object
		if($object->object == 'text') {
			// Merge text defaults
			if(isset($report->defaults->text))
				$object = object_merge($report->defaults->text, $object);

			// If we have a src, override the text
			if(isset($object->src)) {
				if($object->src == 'sql') {		// Text src can be SQL query
					if(!isset($object->db)) {
						print('Warning: Text sql database not defined on page #' . $pageID . ' object ' . $objectID . '.' . NL);
						continue;
					}
					$object->db = replace_vars($object->db);
					if(!file_exists($object->db)) {
						print('Warning: Text sql database not found on page #' . $pageID . ' object ' . $objectID . '.' . NL);
						continue;
					}
					if(!isset($object->sql)) {
						print('Warning: Text sql query not defined on page #' . $pageID . ' object ' . $objectID . '.' . NL);
						continue;
					} else {
						if($globals->debug)
							print('        \'--from sql (');
						$object->text = text_from_sql($object);
						if($globals->debug)
							print(')' . NL);
					}
				}
				if($object->src == 'file') {	// Text src can be a file
					$file = replace_vars($object->file);
					if(!file_exists($file)) {
						print('Warning: Text file ' . $file . ' not found on page #' . $pageID . ' object ' . $objectID . '.' . NL);
						continue;
					} else {
						if($globals->debug)
							print('        \'--from file ' . $file . NL);
						$object->text = file_get_contents($file);
					}
				}
				if($object->src == 'cmd') {		// Text src can be a command
					$cmd = replace_vars($object->cmd);
					if($globals->debug)
						print('        \'--from command ' . $cmd . NL);
					exec($cmd, $array);
					$object->text = text_from_array($array);
				}
				if($object->src == 'code') {		// Text src can be PHP code
					$code = replace_vars($object->code);
					if($globals->debug)
						print('        \'--from code ' . $code . NL);
					$object->text = eval($code);
				}
			}

			// A text object MUST have text
			if(!isset($object->text)) {
				print('Warning: Text content not defined on page #' . $pageID . ' object ' . $objectID . '.' . NL);
				continue;
			}

			// Output the text div
			if($centered)
				fputs($out, '	<center>' . NL);
			fputs($out, '	<div class="text"');
			if(isset($object->id))
				fputs($out, ' id="' . replace_vars($object->id) . '"');
			if(isset($object->style))
				fputs($out, ' style="' . get_style($object) . '"');
			fputs($out, '>' . NL);
			fputs($out, replace_vars($object->text) . NL);
			fputs($out, '	</div>' . NL);
			if($centered)
				fputs($out, '	</center>' . NL);
			continue;
		}

		/////////////////////////////////////////////////////////////////////
		// Output an image object
		if($object->object == 'image') {
			// Merge image defaults
			if(isset($report->defaults->image))
				$object = object_merge($report->defaults->image, $object);

			// An image object MUST have a source
			if(!isset($object->src)) {
				print('Warning: Image source not defined on page #' . $pageID . ' object ' . $objectID . '.' . NL);
				continue;
			}

			if($globals->debug)
				print('        \'--from ' . $object->src . NL);

			// Output the image div
			if($centered)
				fputs($out, '	<center>' . NL);
			fputs($out, '	<div class="image"');
			if(isset($object->id))
				fputs($out, ' id="' . replace_vars($object->id) . '"');
			if(isset($object->style))
				fputs($out, ' style="' . get_style($object) . '"');
			fputs($out, '>' . NL);
			fputs($out, '		<img src="' . replace_vars($object->src) . '"');
			if(isset($object->width))
				fputs($out, ' width="' . $object->width . '"');
			if(isset($object->height))
				fputs($out, ' height="' . $object->height . '"');
			fputs($out, '>' . NL);
			fputs($out, '	</div>' . NL);
			if($centered)
				fputs($out, '	</center>' . NL);
			continue;
		}

		/////////////////////////////////////////////////////////////////////
		// Output a chart object
		if($object->object == 'chart') {
			// Merge chart defaults
			if(isset($report->defaults->chart))
				$object = object_merge($report->defaults->chart, $object);

			// A chart MUST have an ID
			if(!isset($object->id))
				$object->id = 'chart_' . $pageID . '_' . $objectID;

			// A chart MUST have some type
			if(!isset($object->type)) {
				print('Warning: Chart type not defined on page #' . $pageID . ' object ' . $objectID . '.' . NL);
				continue;
			}

			// Set some per-chart globals
			if(isset($object->topN)) {
				$globals->topN = $object->topN;
			} else {
				$globals->topN = $defaults->topN;
			}
			if(isset($object->decimals)) {
				$globals->decimals = $object->decimals;
			} else {
				$globals->decimals = $defaults->decimals;
			}

			// If we have a src, override the data
			if(isset($object->src)) {
				if($object->src == 'sql') { 	// Chart src can be SQL query
					if(!isset($object->db)) {
						print('Warning: Chart sql database not defined on page #' . $pageID . ' object ' . $objectID . '.' . NL);
						continue;
					}
					$object->db = replace_vars($object->db);
					if(!file_exists($object->db)) {
						print('Warning: Chart sql database not found on page #' . $pageID . ' object ' . $objectID . '.' . NL);
						continue;
					}
					if(!isset($object->sql)) {
						print('Warning: Chart sql query not found on page #' . $pageID . ' object ' . $objectID . '.' . NL);
						continue;
					} else {
						if($globals->debug)
							print('        \'--from sql (');
						$object->data = array_from_sql($object);
						if($globals->debug)
							print(')' . NL);
					}
				}
				if($object->src == 'last') { 	// Chart src can be the last chart
					if(!isset($globals->lastData)) {
						print('Warning: Chart last data not defined on page #' . $pageID . ' object ' . $objectID . '.' . NL);
						continue;
					}
					if($globals->debug)
						print('        \'--from last' . NL);
					$object->data = $globals->lastData;
				}
				if($object->src == 'csv') {		// Chart src can be a CSV file
					$file = replace_vars($object->csv);
					if(!file_exists($file)) {
						print('Warning: Chart CSV file ' . $file . ' not found on page #' . $pageID . ' object ' . $objectID . '.' . NL);
						continue;
					} else {
						if($globals->debug)
							print('        \'--from file ' . $file . NL);
						$object->data = array_from_csv($object);
					}
				}
				if($object->src == 'cmd') {		// Chart src can be a command
					$cmd = replace_vars($object->cmd);
					$array = explode(' ', $cmd);
					$file = $array[0];
					if(!file_exists($file)) {
						print('Warning: Chart command ' . $file . ' not found on page #' . $pageID . ' object ' . $objectID . '.' . NL);
						continue;
					} else {
						if($globals->debug)
							print('        \'--from command ' . $cmd . NL);
						$object->data = array_from_cmd($object);
					}
				}
				if($object->src == 'code') {		// Chart src can be PHP code
					$code = replace_vars($object->code);
					if($globals->debug)
						print('        \'--from code ' . $code . NL);
					$object->data = eval($code);
				}
			}

			// A chart MUST have data
			if(!isset($object->data)) {
				print('Warning: Chart data not defined on page #' . $pageID . ' object ' . $objectID . '.' . NL);
				continue;
			}

			// Save the data for the next chart
			$globals->lastData = $object->data;

			// Output the chart div
			if($centered)
				fputs($out, '	<center>' . NL . '	');
			fputs($out, '	<div class="chart"');
			if(isset($object->id))
				fputs($out, ' id="' . replace_vars($object->id) . '"');
			if(isset($object->style))
				fputs($out, ' style="' . get_style($object) . '"');
			fputs($out, '></div>' . NL);
			if($centered)
				fputs($out, '	</center>' . NL);

			// Save data onto the CSV file
			if(!isset($object->title))
				$object->title = 'no title';
			$array = array($object->id,$object->object,$object->type,$object->title);
			if(!isset($globals->noCSV)) {
				fputcsv($csv, $array);
				foreach($object->data as $data) {
					foreach($data as $key=>$value)
						$data[$key] = localize(replace_vars($value));
					fputcsv($csv, $data);
				}
				fputs($csv, '---------------------------------------' . NL);
			}
			write_chart($out, $object); // Function to generate chart from object

			continue;
		}

		/////////////////////////////////////////////////////////////////////
		// Set a global variable from object
		if($object->object == 'variable') {
			// Merge variable defaults
			if(isset($report->defaults->variable))
				$object = object_merge($report->defaults->variable, $object);

			// A variable must have a name
			if(!isset($object->name)) {
				print('Warning: Variable name not defined on page #' . $pageID . ' object ' . $objectID . '.' . NL);
				continue;
			}

			// A variable must have a value source
			if(!isset($object->src)) {
				print('Warning: Variable source not defined on page #' . $pageID . ' object ' . $objectID . '.' . NL);
				continue;
			}

			// Compute and store the variable
			if($object->src == 'sql') { // Variable value can be the result of a SQL query
				if(!isset($object->db)) {
					print('Warning: Variable sql database not defined on page #' . $pageID . ' object ' . $objectID . '.' . NL);
					continue;
				}
				$object->db = replace_vars($object->db);
				if(!file_exists($object->db)) {
					print('Warning: Variable sql database not found on page #' . $pageID . ' object ' . $objectID . '.' . NL);
					continue;
				}
				if(!isset($object->sql)) {
					print('Warning: Variable sql query not found on page #' . $pageID . ' object ' . $objectID . '.' . NL);
					continue;
				} else {
					if($globals->debug)
						print('        \'--from sql (');
					$object->value = text_from_sql($object);
					if($globals->debug)
						print(')' . NL);
				}
			}
			if($object->src == 'cmd') {	// Variable value can be the result of a cmd
				$cmd = replace_vars($object->cmd);
				if($globals->debug)
					print('        \'--from command ' . $cmd . NL);
				exec($cmd, $array);
				$object->value = text_from_array($array);
			}
			if($object->src == 'code') {	// Variable value can be the result of a PHP code
				$code = replace_vars($object->code);
				if($globals->debug)
					print('        \'--from code ' . $code . NL);
				$object->value = eval($code);
			}

			// Format the variable if numeric
			if(isset($object->format)) {
				if($object->format == 'number') {
					$decimals      = (int)replace_vars(isset($object->decimals) ? $object->decimals : $globals->decimals);
					$object->value = number_format($object->value, $decimals, $globals->decimalSymbol, $globals->groupingSymbol);
				}
			}

			$globals->{$object->name} = replace_vars($object->value);
			continue;
		}

		/////////////////////////////////////////////////////////////////////
		// Wrong type
		print('Warning: Wrong object type "' . $object->object . '" defined on page #' . $pageID . ' object ' . $objectID . '.' . NL);
	}
	fputs($out, '</div>' . NL);
}

fputs($out, '</body>' . NL);
fputs($out, '</html>' . NL);
fclose($out);
if(!isset($globals->noCSV))
	fclose($csv);

print(' Done.' . NL . 'Report recorded onto ' . $globals->output . '.' . NL);

if($globals->doPDF) {
	print('Generating PDF ...' . NL);
	$filePath = $globals->path . '/' . $globals->output;
	$pdfPath  = $globals->path . '/' . $globals->pdf;
	if($globals->os == 'Windows') {
		$pdf = '.\tools\chrome\chrome.exe --headless --incognito --print-to-pdf="' . $pdfPath . '" file://' . $filePath;
		exec($pdf);
	} else {
		if($globals->os == 'Linux') {
			$pdf = $linux_browser.' --headless --incognito --no-sandbox --print-to-pdf="' . $pdfPath . '" file://' . $filePath;
		} else {
			$pdf = 'tools/chrome/chrome.exe --headless --incognito --print-to-pdf="' . $pdfPath . '" file://' . $filePath;
			$pdf = str_replace('/mnt/c', 'C:', $pdf);
		}
		exec($pdf.' 2>/dev/null');
	}
	print('PDF recorded onto ' . $globals->pdf . '.' . NL);
	if(!isset($globals->keepHTM)) {
		print('Removing HTM ...' . NL);
		unlink($globals->output);
	}
}

print('Finished in ');
timeOut();
print(NL);
?>
