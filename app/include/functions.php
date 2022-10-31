<?php

# VERSION = '5.0.3'

/////////////////////////////////////////////////////////////////////
// Functions

// Show command line usage
function usage() {
	global $globals;
	print('Usage: ' . $globals->app . ' ' . $globals->usageText . NL . NL);
}

// Parses all the command line arguments
function parse_args($usePositional = false) {
	$args = new stdclass();
	$idx  = 0;
	foreach($GLOBALS['argv'] as $key => $arg) {
		// Ignore self filename ($argv[0])
		if(!$key)
			continue;

		// Error if parameter is not started by '-'
		if(substr($arg, 0, 1) != '-') {
			if($usePositional) {
				$args->{"_" . $idx++} = $arg;
				continue;
			} else {
				print("\n" . 'Invalid command line parameter #' . $key . ' (' . $arg . ').' . "\n");
				usage();
			}
		}

		// Remove leading '-' from parameter
		while(substr($arg, 0, 1) == '-')
			$arg = substr($arg, 1);

		// Find a '=' on the parameter string
		$eqPos = strpos($arg, '=');
		if($eqPos === false) { // If it has no '=' then it is a global true
			$args->{$arg} = true;
		} else { // Otherwise set it as an argument variable
			$name          = substr($arg, 0, $eqPos);
			$value         = substr($arg, $eqPos + 1);
			if(is_numeric($value))
				$value+=0;
			$args->{$name} = $value;
		}
	}
	return ($args);
}

// Calculates relative paths
function relative_path($from, $to, $ps = DIRECTORY_SEPARATOR) {
	$arFrom = explode($ps, rtrim($from, $ps));
	$arTo   = explode($ps, rtrim($to, $ps));
	while(count($arFrom) && count($arTo) && ($arFrom[0] == $arTo[0])) {
		array_shift($arFrom);
		array_shift($arTo);
	}
	return (str_pad('', count($arFrom) * 3, '..' . $ps) . implode($ps, $arTo));
}

// Gets json data from a file
function get_json_data($file) {
	return (json_decode(file_get_contents($file)));
}

// Gets the style definition of an object in html format
function get_style($object) {
	$txt = '';
	foreach($object->style as $key => $value)
		$txt .= $key . ': ' . $value . '; ';
	return (trim($txt));
}

// Starts counting seconds
$timer = array();
function timeIn($id = 254, $time = null) {
    if($time == null)
        $time = time();
	global $timer;
	$timer[$id] = $time;
}

// Stops counting seconds and prints
function timeOut($id = 254, $time = null) {
	global $timer;
	if($time == null)
	    $time = time();
	$dif = $time - $timer[$id];
	$tz = date_default_timezone_get();
	date_default_timezone_set('UTC');
	if($dif > 3599)
		echo(+date('H', $dif).' hours, ');
	if($dif > 59)
		echo(+date('i', $dif).' minutes, ');
	echo(+date('s', $dif).' seconds');
	date_default_timezone_set($tz);
}

// Merges two objects recursively
function object_merge($object1, $object2) {
	// Get the type of the result
	$resultType = gettype($object1);
	if($resultType == 'object') {
		$result = clone $object1; // Make a clone as objects are passed by reference
	} else {
		$result = $object1; // Otherwise just copy
	}
	// Iterate through the values
	foreach($object2 as $key => $value) {
		// Get the type of the value
		$valueType = gettype($value);
		// If it is an object, recurse
		if($valueType == 'object') {
			if(isset($result->{$key})) {
				$result->{$key} = object_merge($result->{$key}, $value);
				continue;
			}
		}
		// If it is an array, recurse
		if(gettype($value) == 'array') {
			if(isset($result->{$key})) {
				$result->{$key} = object_merge($result->{$key}, $value);
				continue;
			}
		}
		// If not, just set over to the result
		if($resultType == 'array' and is_numeric($key)) {
			$result[] = $value; // Numeric keys must be appended
		} else {
			$result->{$key} = $value; // Otherwise can just be set
		}
	}
	return ($result);
}

// Replaces globals variable names into a text string
function replace_vars($text) {
	global $globals;

	while(strpos($text, '{') !== false) {
		$varStart = strpos($text, '{');
		$varStop  = strpos($text, '}');
		$varName  = substr($text, $varStart + 1, $varStop - $varStart - 1);
		if(isset($globals->{$varName})) {
			$text = substr($text, 0, $varStart) . $globals->{$varName} . substr($text, $varStop + 1);
		} else {
			print('Warning: Variable ' . $varName . ' is undefined.' . NL);
			$text = substr($text, 0, $varStart) . '?' . $varName . '?' . substr($text, $varStop + 1);
		}
	}

	return ($text);
}

// Apply language localization to text
function localize($text) {
	global $globals;
	$array = explode(' ', $text);
	foreach($array as $key => $value) {
		$array[$key] = isset($globals->localize[$value])?$globals->localize[$value]:$value;
	}
	$text = implode(' ', $array);
	return($text);
}

// Get a single text from an object's SQL query
function text_from_sql($object) {
	global $globals;

	// Open the database
	$db = new SQLite3($object->db);
	// Execute the SQL query
	if($globals->debug) {
		print('SQL : ' . replace_vars($object->sql) . NL);
		$t0 = microtime(true);
	}
	try {
		$db->enableExceptions(true);
		$result = $db->query(replace_vars($object->sql));
	}
	catch(Exception $e) {
		print('SQL Error: ' . $e->getMessage() . NL);
		exit(1);
	}
	if($globals->debug)
		print(' <time: ' . microtime(true)-$t0 . '>)' . NL);
	// Get the first result row
	$row  = $result->fetchArray(SQLITE3_NUM);
	$text = $row[0];
	// Release memory
	$result->finalize();
	// Close the database
	$db->close();

	if($globals->debug > 1) {
		print('RowData : ');
		print_r($rowData);
	}

	return ($text);
}

// Converts an exec array to a string
function text_from_array($array) {
	return(implode(NL, $array));
}

// Get an array of data from an object's SQL query
function array_from_sql($object) {
	global $globals;

	$rowData = array();
	// Open the database
	$db      = new SQLite3($object->db);
	// Execute the SQL query
	if($globals->debug) {
		print('SQL : ' . replace_vars($object->sql));
		$t0 = microtime(true);
	}
	try {
		$db->enableExceptions(true);
		$results = $db->query(replace_vars($object->sql));
	}
	catch(Exception $e) {
		print('SQL Error: ' . $e->getMessage() . NL);
		exit(1);
	}
	if($globals->debug)
		print(' <time: ' . microtime(true)-$t0 . '>)' . NL);
	$cols      = $results->numColumns();
	// Set the array as the column names
	$rowData[] = array();
	for($i = 0; $i < $cols; ++$i) {
		$rowData[0][$i] = $results->columnName($i);
	}
	// Load the array with data
	while($row = $results->fetchArray(SQLITE3_NUM)) {
		$rowData[] = $row;
	}
	// Release memory
	$results->finalize();
	// Close the database
	$db->close();

	if($globals->debug > 1) {
		print('RowData : ');
		print_r($rowData);
	}

	return ($rowData);
}

// Get an array of data from an object's CSV file
function array_from_csv($object) {
	global $globals;
	$rowData = array();
	// Open the file
	$fh      = fopen(replace_vars($object->csv), 'r');
	// Read as CSV
	while(($data = fgetcsv($fh, 1000, ',')) !== FALSE) {
		if(count($data) == 1)
			continue;
		$rowData[] = $data;
	}
	// Close the file
	fclose($fh);

	if($globals->debug > 1) {
		print('RowData : ');
		print_r($rowData);
	}

	return ($rowData);
}

// Get an array of data from a command generated CSV
function array_from_cmd($object) {
	global $globals;
	$rowData = array();
	// Open the file
	$fh      = popen(replace_vars($object->cmd), 'r');
	// Read as CSV
	while(($data = fgetcsv($fh, 1000, ',')) !== FALSE) {
		if(count($data) == 1)
			continue;
		$rowData[] = $data;
	}
	// Close the file
	pclose($fh);

	if($globals->debug > 1) {
		print('RowData : ');
		print_r($rowData);
	}

	return ($rowData);
}

// Writes a chart to the output file
function write_chart($fh, $chart) {
	global $globals;

	// Collect the chart data
	$rowData = $chart->data;
	$rows    = count($rowData);
	$cols    = count($rowData[0]);

	// Chart fields
	$chartID   = $chart->id;
	$chartType = $chart->type;
	if(isset($chart->title))
		$chartTitle = $chart->title;

	// Language related
	if(isset($chart->language)) {
		$language   = $chart->language;
	} else {
		$language   = $globals->language;
	}

	// Load language file if exists
	$locfile = 'language_files/'.$language.'.json';
	if(file_exists($locfile)) {
		$json = file_get_contents($locfile);
		$globals->localize = json_decode($json, true);
	}

	// Decimal symbols
	$chartDecimals  = (int)replace_vars(isset($chart->decimals) ? $chart->decimals : 0);
	$decimalSymbol  = $globals->decimalSymbol;
	$groupingSymbol = $globals->groupingSymbol;

	// Chart optionals
	$fontSize     = 12;
	$titleSize    = 25;
	$titleColor   = '#123456';
	if(isset($chart->fontSize))
		$fontSize = $chart->fontSize;
	if(isset($chart->titleSize))
		$titleSize = $chart->titleSize;
	if(isset($chart->titleColor))
		$titleSize = $chart->titleColor;
	if(isset($chart->xMin))
		$xMin = +$chart->xMin;
	if(isset($chart->xMax))
		$xMax = +replace_vars($chart->xMax);
	if(isset($chart->alwaysOutside))
		$alwaysOutside = $chart->alwaysOutside ? 'true' : 'false';
	if(isset($chart->showTextEvery))
		$showTextEvery = +$chart->showTextEvery;
	if(isset($chart->backgroundColor))
		$backgroundColor = $chart->backgroundColor;
	if(isset($chart->annotationStyle))
		$annotationStyle = $chart->annotationStyle;
	if(isset($chart->annotationSize))
		$annotationSize = +$chart->annotationSize;
	if(isset($chart->annotationColor))
		$annotationColor = $chart->annotationColor;
	if(isset($chart->legend))
		$legend = $chart->legend;
	if(isset($chart->others))
		$others = +$chart->others;
	$revDNS   = isset($chart->revDNS) ? $chart->revDNS : false;
	$noLabel  = isset($chart->noLabel) ? $chart->noLabel : false;
	$noHeader = isset($chart->noHeader) ? $chart->noHeader : false;
	$total  = isset($chart->total) ? $chart->total : false;
	$average  = isset($chart->average) ? $chart->average : false;

	// Some charts must be "noLabel"
	if($chartType == 'table')
		$noLabel = true;
	if($chartType == 'sankey')
		$noLabel = true;
	if($chartType == 'calendar')
		$noLabel = true;

	// Define the default chart options object
	$options = new stdclass();
	$options->allowHtml = isset($chart->allowHtml) ? $chart->allowHtml : true;
	$options->is3d = isset($chart->is3d) ? $chart->is3d : false;
	$options->isStacked = isset($chart->isStacked) ? $chart->isStacked : false;
	$options->logScale = isset($chart->logScale) ? $chart->logScale : false;
	$slantedText = isset($chart->slantedText) ? $chart->slantedText : false;
	$options->enableInteractivity = $globals->doPDF ? false : true;
	if($noHeader)
		$options->cssClassNames = '{ headerCell: "noHeader" }';
	if(isset($others))
		$options->sliceVisibilityThreshold = $others;
	if(isset($chartTitle)) {
		$options->title = '"' . localize($chartTitle) . '"';
		$options->titleTextStyle = '{ fontSize: ' . $titleSize . ', color: "' . $titleColor . '" }';
	}
	if(isset($alwaysOutside)) {
		$options->annotations = '{ alwaysOutside: ' . $alwaysOutside . ', textStyle: { auraColor: "#ffffff"';
	} else {
		$options->annotations = '{ alwaysOutside: true, textStyle: { auraColor: "#ffffff"';
	}
	if(isset($annotationSize))
		$options->annotations .= ', fontSize: ' . $annotationSize;
	if(isset($annotationColor))
		$options->annotations .= ', color: "' . $annotationColor . '"';
	$options->annotations .= '}';
	if(isset($annotationStyle))
		$options->annotations .= ', style: "' . $annotationStyle . '"';
	$options->annotations .= '}';
	if(isset($colors))
		$options->colors = '[' . $globals->colors . ']';
	if(isset($backgroundColor)) {
		$options->backgroundColor = '"' . $backgroundColor . '"';
	} else {
		$options->backgroundColor = '"transparent"';
	}
	if(isset($legend)) {
		$options->legend = '{ position: "' . $legend . '", maxLines: 5 }';
	} else {
		$options->legend = '{ position: "bottom", maxLines: 5 }';
	}
	if($average) {
		$options->series = "{ $average: { type: 'line' }}";
	}

	// Merge additional options
	if(isset($chart->options))
		$options = object_merge($options, $chart->options);

	// Output the chart
	fputs($fh, '	<script type="text/javascript">' . NL);
	switch($chartType) {
		case 'calendar':
			$package = 'calendar';
			break;
		case 'sankey':
			$package = 'sankey';
			break;
		case 'table':
			$package = 'table';
			break;
		default:
			$package = 'corechart';
			break;
	}
	fputs($fh, ' 	google.charts.load("current", {"packages":["' . $package . '"], language: "' . $language . '"});' . NL);
	fputs($fh, ' 	google.charts.setOnLoadCallback(drawChart);' . NL);
	fputs($fh, ' 	function drawChart() {' . NL);
	fputs($fh, '		var data = new google.visualization.DataTable();' . NL);

	for($i = 0; $i < $cols; ++$i) {
		if(isset($chart->fields[$i])) {
			// Get field description from the object
			switch($chart->fields[$i]) {
				case 'annotation':
					fputs($fh, '			data.addColumn({type: "number", role: "annotation"});' . NL);
					break;
				case 'day':
					fputs($fh, '			data.addColumn("date");' . NL);
					break;
				case 'integer':
				case 'number':
					fputs($fh, '			data.addColumn("number", "' . localize($rowData[0][$i]) . '");' . NL);
					break;
				default:
					fputs($fh, '			data.addColumn("' . $chart->fields[$i] . '", "' . localize($rowData[0][$i]) . '");' . NL);
			}
		} else {
			if(!isset($chart->fields))
				$chart->fields = array();
			// Compute the field description (string, number, annotation)
			if($i) {
				fputs($fh, '			data.addColumn("number", "' . localize($rowData[0][$i]) . '");' . NL);
				$chart->fields[$i] = 'number';
			} else {
				fputs($fh, '			data.addColumn("string", "' . localize($rowData[0][$i]) . '");' . NL);
				$chart->fields[$i] = 'string';
			}
			if(!$noLabel) {
				if($i) {
					fputs($fh, '			data.addColumn({type: "number", role: "annotation"});' . NL);
					$chart->fields[$i] = 'annotation';
				}
			}
		}
	}
	fputs($fh, '			data.addRows([' . NL);

	// Output the chart data points
	$viewMax = 0;
	foreach($rowData as $key => $row) {
		if(!$key) // Skip the label row
			continue;
		if($key > 1)
			fputs($fh, ',' . NL);
		fputs($fh, '				[ ');
		$colValue = 0;
		foreach($row as $col => $value) {
			if($col == 0) {
				if($revDNS and $value != '0.0.0.0' and $value != 'Multiple' and $value != 'Total') {
					$res = gethostbyaddr($value);
					if($res) {
						if($res != $value) {
							fputs($fh, '"' . $res . '"');
						} else {
							fputs($fh, '"' . localize($value) . '"');
						}
					} else {
						fputs($fh, '"' . localize($value) . '"');
					}
				} else {
					if($chart->fields[0] == 'day') {
						fputs($fh, 'new Date(' . $globals->year . ', ' . ($globals->month - 1) . ', ' . $value . ')');
					} else {
						fputs($fh, '"' . localize($value) . '"');
					}
				}
				continue;
			}
			fputs($fh, ', ');
			if(is_numeric($value)) {
				if(isset($chart->divisor)) {
					$chart->divisor = (int)replace_vars($chart->divisor);
					$value = round($value / $chart->divisor, $chartDecimals);
				}
				fputs($fh, $value);
				if($options->isStacked) {
					$colValue += $value;
				} else {
					$colValue = max($colValue, $value);
				}
				if(!$noLabel)
					fputs($fh, ', ' . $value);
			} else {
				$value = addslashes($value);
				fputs($fh, '"' . localize(replace_vars($value)) . '"');
			}
		}
		$viewMax = max($viewMax, $colValue);
		fputs($fh, ' ]');
	}
	fputs($fh, NL . '			]);' . NL);

	// Output the chart options
	fputs($fh, '		var options = {' . NL);

	$options = (array)$options;
	foreach($options as $key => $value) {
		// If it is boolen adjust
		if(gettype($value) == 'boolean')
			$value = $value?'true':'false';
		fputs($fh, '			' . $key . ': ' . $value . ',' . NL);
	}

	fputs($fh, '			hAxis: {' . NL);
	if(isset($xMin) or isset($xMax)) {
		fputs($fh, '				viewWindow: {');
		if(isset($xMin))
			fputs($fh, ' min: ' . $xMin);
		if(isset($xMin) and isset($xMax))
			fputs($fh, ',');
		if(isset($xMax))
			fputs($fh, ' max: ' . $xMax);
		fputs($fh, ' },' . NL);
	}
	if(isset($showTextEvery))
		fputs($fh, '				showTextEvery: ' . $showTextEvery . ',' . NL);
	if(isset($slantedText))
		fputs($fh, '				slantedText: ' . ($slantedText ? 'true' : 'false') . ',' . NL);
	fputs($fh, '				textStyle: { fontSize: ' . $fontSize . ' }' . NL);
	fputs($fh, '			},' . NL);
	fputs($fh, '			vAxis: {' . NL);
	if($chartType == 'column' or $chartType == 'area') {
		if(isset($chart->vMax)) {
			$viewMax = $chart->vMax;
		} else {
			$viewMax *= 1.1;
		}
		$viewMax = ceil($viewMax / 10) * 10;
		fputs($fh, '				viewWindow: { max: ' . $viewMax . ', min: 0 },' . NL);
	} else {
		fputs($fh, '				viewWindow: { min: 0 },' . NL);
	}
	fputs($fh, '				textStyle: { fontSize: ' . $fontSize . ' }' . NL);
	fputs($fh, '			}' . NL);
	fputs($fh, '		};' . NL);

	// Output number formatter
	fputs($fh, '		var formatter = new google.visualization.NumberFormat({' . NL);
	fputs($fh, '			fractionDigits: ' . $chartDecimals . ',' . NL);
	fputs($fh, '			decimalSymbol: "' . $decimalSymbol . '",' . NL);
	fputs($fh, '			groupingSymbol: "' . $groupingSymbol . '"' . NL);
	fputs($fh, '		});' . NL);
	if(!$noLabel) {
		fputs($fh, '		formatter.format(data, 2);' . NL);
	} else {
		foreach($chart->fields as $id => $type) {
			if($type == 'number')
				fputs($fh, '		formatter.format(data, '.$id.');' . NL);
		}
	}

	// Output optional total and average series
	if($average or $total) {

		fputs($fh, '		rows = data.getNumberOfRows();' . NL);
		fputs($fh, '		cols = data.getNumberOfColumns();' . NL);
		fputs($fh, '		sum = 0;' . NL);
		fputs($fh, '		for(i = 0; i < rows; i++) {' . NL);
		fputs($fh, '			sum += data.getValue(i, 1);' . NL);
		fputs($fh, '		}' . NL);
		fputs($fh, '		avg = Math.round(sum/rows);' . NL);
		if($chartType == 'table') {
			if($total)
				fputs($fh, '		data.addRow(["Total", sum]);' . NL);
			if($average)
				fputs($fh, '		data.addRow(["Average", avg]);' . NL);
		} else {
			if($average) {
				fputs($fh, '		data.addColumn("number", "Average");' . NL);
				fputs($fh, '		for(i = 0; i < rows; i++) {' . NL);
				fputs($fh, '			data.setValue(i, cols, avg);' . NL);
				fputs($fh, '		}' . NL);
				fputs($fh, '		options.series = { 1: { type: "line" }};' . NL);
			}
		}

	}

	// Output the chart drawing command
	if($chartType == 'area')
		fputs($fh, '		var chart = new google.visualization.AreaChart(document.getElementById("' . $chartID . '"));' . NL);
	if($chartType == 'bar')
		fputs($fh, '		var chart = new google.visualization.BarChart(document.getElementById("' . $chartID . '"));' . NL);
	if($chartType == 'bubble')
		fputs($fh, '		var chart = new google.visualization.BubbleChart(document.getElementById("' . $chartID . '"));' . NL);
	if($chartType == 'calendar')
		fputs($fh, '		var chart = new google.visualization.Calendar(document.getElementById("' . $chartID . '"));' . NL);
	if($chartType == 'column')
		fputs($fh, '		var chart = new google.visualization.ColumnChart(document.getElementById("' . $chartID . '"));' . NL);
	if($chartType == 'line')
		fputs($fh, '		var chart = new google.visualization.LineChart(document.getElementById("' . $chartID . '"));' . NL);
	if($chartType == 'pie')
		fputs($fh, '		var chart = new google.visualization.PieChart(document.getElementById("' . $chartID . '"));' . NL);
	if($chartType == 'sankey')
		fputs($fh, '		var chart = new google.visualization.Sankey(document.getElementById("' . $chartID . '"));' . NL);
	if($chartType == 'scatter')
		fputs($fh, '		var chart = new google.visualization.ScatterChart(document.getElementById("' . $chartID . '"));' . NL);
	if($chartType == 'table')
		fputs($fh, '		var chart = new google.visualization.Table(document.getElementById("' . $chartID . '"));' . NL);

	if($package == 'corechart' and $globals->doPNG) {
		fputs($fh, '		google.visualization.events.addListener(chart, "ready", function () {' . NL);
		fputs($fh, '			' . $chartID . '.innerHTML = "<img src=\'" + chart.getImageURI() + "\'>";' . NL);
		fputs($fh, '			console.log(' . $chartID . '.innerHTML);' . NL);
		fputs($fh, '		});' . NL);
	}

	fputs($fh, '		chart.draw(data, options);' . NL);
	fputs($fh, '	}' . NL);
	fputs($fh, '	</script>' . NL);
}

?>