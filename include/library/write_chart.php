<?php
// Writes a chart to the output file
function write_chart($fh, $chart) {
	global $globals;

	// Collect the chart data
	$rowData = $chart->data;
	$cols    = count($rowData[0]);

	// Chart fields
	$chartID   = $chart->id;
	$chartType = $chart->type;
	if (isset($chart->title))
		$chartTitle = $chart->title;

	// Language related
	if (isset($chart->language)) {
		$language   = $chart->language;
	} else {
		$language   = $globals->language;
	}

	// Load language file if exists
	$locfile = 'language_files/' . $language . '.json';
	if (file_exists($locfile)) {
		$json = file_get_contents($locfile);
		$globals->localize = json_decode($json, true);
	}

	// Decimal symbols
	if(!isset($chart->decimals))
		$chart->decimals = 0;
	if(!is_array($chart->decimals))
		$chartDecimals  = (int)replace_vars($chart->decimals);
	$decimalSymbol  = $globals->decimalSymbol;
	$groupingSymbol = $globals->groupingSymbol;

	// Chart optionals
	$fontSize     = 12;
	$titleSize    = 25;
	$titleColor   = '#123456';
	if (isset($chart->fontSize))
		$fontSize = $chart->fontSize;
	if (isset($chart->titleSize))
		$titleSize = $chart->titleSize;
	if (isset($chart->titleColor))
		$titleSize = $chart->titleColor;
	if (isset($chart->xMin))
		$xMin = +$chart->xMin;
	if (isset($chart->xMax))
		$xMax = +replace_vars($chart->xMax);
	if (isset($chart->alwaysOutside))
		$alwaysOutside = $chart->alwaysOutside ? 'true' : 'false';
	if (isset($chart->showTextEvery))
		$showTextEvery = +$chart->showTextEvery;
	if (isset($chart->backgroundColor))
		$backgroundColor = $chart->backgroundColor;
	if (isset($chart->annotationStyle))
		$annotationStyle = $chart->annotationStyle;
	if (isset($chart->annotationSize))
		$annotationSize = +$chart->annotationSize;
	if (isset($chart->annotationColor))
		$annotationColor = $chart->annotationColor;
	if (isset($chart->legend))
		$legend = $chart->legend;
	if (isset($chart->others))
		$others = +$chart->others;
	$revDNS   = isset($chart->revDNS) ? $chart->revDNS : false;
	$noLabel  = isset($chart->noLabel) ? $chart->noLabel : false;
	$noHeader = isset($chart->noHeader) ? $chart->noHeader : false;
	$total  = isset($chart->total) ? $chart->total : false;
	$average  = isset($chart->average) ? $chart->average : false;

	// Some charts must be "noLabel"
	if ($chartType == 'table')
		$noLabel = true;
	if ($chartType == 'sankey')
		$noLabel = true;
	if ($chartType == 'calendar')
		$noLabel = true;

	// Define the default chart options object
	$options = new stdclass();
	$options->allowHtml = isset($chart->allowHtml) ? $chart->allowHtml : true;
	$options->is3d = isset($chart->is3d) ? $chart->is3d : false;
	$options->isStacked = isset($chart->isStacked) ? $chart->isStacked : false;
	$options->logScale = isset($chart->logScale) ? $chart->logScale : false;
	$slantedText = isset($chart->slantedText) ? $chart->slantedText : false;
	$options->enableInteractivity = $globals->doPDF ? false : true;
	if ($noHeader)
		$options->cssClassNames = '{ headerCell: "noHeader" }';
	if (isset($others))
		$options->sliceVisibilityThreshold = $others;
	if (isset($chartTitle)) {
		$options->title = '"' . localize($chartTitle) . '"';
		$options->titleTextStyle = '{ fontSize: ' . $titleSize . ', color: "' . $titleColor . '" }';
	}
	if (isset($alwaysOutside)) {
		$options->annotations = '{ alwaysOutside: ' . $alwaysOutside . ', textStyle: { auraColor: "#ffffff"';
	} else {
		$options->annotations = '{ alwaysOutside: true, textStyle: { auraColor: "#ffffff"';
	}
	if (isset($annotationSize))
		$options->annotations .= ', fontSize: ' . $annotationSize;
	if (isset($annotationColor))
		$options->annotations .= ', color: "' . $annotationColor . '"';
	$options->annotations .= '}';
	if (isset($annotationStyle))
		$options->annotations .= ', style: "' . $annotationStyle . '"';
	$options->annotations .= '}';
	if (isset($colors))
		$options->colors = '[' . $globals->colors . ']';
	if (isset($backgroundColor)) {
		$options->backgroundColor = '"' . $backgroundColor . '"';
	} else {
		$options->backgroundColor = '"transparent"';
	}
	if (isset($legend)) {
		$options->legend = '{ position: "' . $legend . '", maxLines: 5 }';
	} else {
		$options->legend = '{ position: "bottom", maxLines: 5 }';
	}
	if ($average) {
		$options->series = "{ $average: { type: 'line' }}";
	}

	// Merge additional options
	if (isset($chart->options))
		$options = object_merge($options, $chart->options);

	// Output the chart
	fputs($fh, '	<script type="text/javascript">' . NL);
	switch ($chartType) {
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

	for ($i = 0; $i < $cols; ++$i) {
		if (isset($chart->fields[$i])) {
			// Get field description from the object
			switch ($chart->fields[$i]) {
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
			if (!isset($chart->fields))
				$chart->fields = array();
			// Compute the field description (string, number, annotation)
			if ($i) {
				fputs($fh, '			data.addColumn("number", "' . localize($rowData[0][$i]) . '");' . NL);
				$chart->fields[$i] = 'number';
			} else {
				fputs($fh, '			data.addColumn("string", "' . localize($rowData[0][$i]) . '");' . NL);
				$chart->fields[$i] = 'string';
			}
			if (!$noLabel) {
				if ($i) {
					fputs($fh, '			data.addColumn({type: "number", role: "annotation"});' . NL);
					$chart->fields[$i] = 'annotation';
				}
			}
		}
	}
	fputs($fh, '			data.addRows([' . NL);

	// Output the chart data points
	$viewMax = 0;
	foreach ($rowData as $key => $row) {
		if (!$key) // Skip the label row
			continue;
		if ($key > 1)
			fputs($fh, ',' . NL);
		fputs($fh, '				[ ');
		$colValue = 0;
		foreach ($row as $col => $value) {
			if ($col == 0) {
				if ($revDNS and $value != '0.0.0.0' and $value != 'Multiple' and $value != 'Total' and !isset($globals->noDNS)) {
					$res = gethostbyaddr($value);
					if ($res) {
						if ($res != $value) {
							fputs($fh, '"' . $res . '"');
						} else {
							fputs($fh, '"' . localize($value) . '"');
						}
					} else {
						fputs($fh, '"' . localize($value) . '"');
					}
				} else {
					if ($chart->fields[0] == 'day') {
						fputs($fh, 'new Date(' . $globals->year . ', ' . ($globals->month - 1) . ', ' . $value . ')');
					} else {
						fputs($fh, '"' . localize($value) . '"');
					}
				}
				continue;
			}
			fputs($fh, ', ');
			if (is_numeric($value)) {
				if (isset($chart->divisor)) {
					if (!is_array($chart->divisor)) {
						$chart->divisor = (int)replace_vars($chart->divisor);
						$value = round($value / $chart->divisor, $chartDecimals);
					} else {
						if($chart->divisor[$col]!='') {
							$divisor = (int)replace_vars($chart->divisor[$col]);
							if(!is_array($chart->decimals)) {
								$decimals = $chartDecimals;
							} else {
								$decimals = (int)replace_vars($chart->decimals[$col]);
							}
							$value = round($value / $divisor, $decimals);
						}
					}
				}
				fputs($fh, $value);
				if ($options->isStacked) {
					$colValue += $value;
				} else {
					$colValue = max($colValue, $value);
				}
				if (!$noLabel)
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
	foreach ($options as $key => $value) {
		// If it is boolen adjust
		if (gettype($value) == 'boolean')
			$value = $value ? 'true' : 'false';
		fputs($fh, '			' . $key . ': ' . $value . ',' . NL);
	}

	fputs($fh, '			hAxis: {' . NL);
	if (isset($xMin) or isset($xMax)) {
		fputs($fh, '				viewWindow: {');
		if (isset($xMin))
			fputs($fh, ' min: ' . $xMin);
		if (isset($xMin) and isset($xMax))
			fputs($fh, ',');
		if (isset($xMax))
			fputs($fh, ' max: ' . $xMax);
		fputs($fh, ' },' . NL);
	}
	if (isset($showTextEvery))
		fputs($fh, '				showTextEvery: ' . $showTextEvery . ',' . NL);
	if (isset($slantedText))
		fputs($fh, '				slantedText: ' . ($slantedText ? 'true' : 'false') . ',' . NL);
	fputs($fh, '				textStyle: { fontSize: ' . $fontSize . ' }' . NL);
	fputs($fh, '			},' . NL);
	fputs($fh, '			vAxis: {' . NL);
	if ($chartType == 'column' or $chartType == 'area') {
		if (isset($chart->vMax)) {
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

	// Output optional total and average series
	if ($average or $total) {
		if (!isset($chart->ta_columns))
			$chart->ta_columns = "1";
		$tc = explode(',', $chart->ta_columns);
		$ht = array();

		fputs($fh, '		rows = data.getNumberOfRows();' . NL);
		fputs($fh, '		cols = data.getNumberOfColumns();' . NL);
		foreach ($tc as $key => $id) {
			$ht[$id] = true;
			fputs($fh, '		sum' . $id . ' = 0;' . NL);
			fputs($fh, '		for(i = 0; i < rows; i++) {' . NL);
			fputs($fh, '			sum' . $id . ' += data.getValue(i, ' . $id . ');' . NL);
			fputs($fh, '		}' . NL);
			fputs($fh, '		avg' . $id . ' = Math.round(sum' . $id . '/rows);' . NL);
		}
		if ($chartType == 'table') {
			if ($total) {
				fputs($fh, '		data.addRow(["<b>Chart Total</b>"');
				for ($i = 1; $i < $cols; $i++) {
					if (isset($ht[$i]))
						fputs($fh, ',sum' . $i);
					else
						fputs($fh, ',null');
				}
				fputs($fh, ']);' . NL);
			}
			if ($average) {
				fputs($fh, '		data.addRow(["<b>Chart Average</b>"');
				for ($i = 1; $i < $cols; $i++) {
					if (isset($ht[$i]))
						fputs($fh, ',avg' . $i);
					else
						fputs($fh, ',null');
				}
				fputs($fh, ']);' . NL);
			}
		} else {
			if ($average and $id == 1) {
				fputs($fh, '		data.addColumn("number", "Average");' . NL);
				fputs($fh, '		for(i = 0; i < rows; i++) {' . NL);
				fputs($fh, '			data.setValue(i, cols, avg1);' . NL);
				fputs($fh, '		}' . NL);
				fputs($fh, '		options.series = { 1: { type: "line" }};' . NL);
			}
		}
	}


	// Output number formatter
	if (!isset($chart->ta_columns))
		$chart->ta_columns = "1";
	$tc = explode(',', $chart->ta_columns);
	foreach ($tc as $key => $id) {
		fputs($fh, '		var f'.$id.' = new google.visualization.NumberFormat({' . NL);
			if(!is_array($chart->decimals)) {
				$decimals = $chartDecimals;
			} else {
				$decimals = (int)replace_vars($chart->decimals[$id]);
			}
		fputs($fh, '			fractionDigits: ' . $decimals . ',' . NL);
		fputs($fh, '			decimalSymbol: "' . $decimalSymbol . '",' . NL);
		fputs($fh, '			groupingSymbol: "' . $groupingSymbol . '"' . NL);
		fputs($fh, '		});' . NL);
	}
	foreach($tc as $key => $id) {
		fputs($fh, '		f'.$id.'.format(data, '.$id.');' . NL);
	}

	// Output the chart drawing command
	if ($chartType == 'area')
		fputs($fh, '		var chart = new google.visualization.AreaChart(document.getElementById("' . $chartID . '"));' . NL);
	if ($chartType == 'bar')
		fputs($fh, '		var chart = new google.visualization.BarChart(document.getElementById("' . $chartID . '"));' . NL);
	if ($chartType == 'bubble')
		fputs($fh, '		var chart = new google.visualization.BubbleChart(document.getElementById("' . $chartID . '"));' . NL);
	if ($chartType == 'calendar')
		fputs($fh, '		var chart = new google.visualization.Calendar(document.getElementById("' . $chartID . '"));' . NL);
	if ($chartType == 'column')
		fputs($fh, '		var chart = new google.visualization.ColumnChart(document.getElementById("' . $chartID . '"));' . NL);
	if ($chartType == 'line')
		fputs($fh, '		var chart = new google.visualization.LineChart(document.getElementById("' . $chartID . '"));' . NL);
	if ($chartType == 'pie')
		fputs($fh, '		var chart = new google.visualization.PieChart(document.getElementById("' . $chartID . '"));' . NL);
	if ($chartType == 'sankey')
		fputs($fh, '		var chart = new google.visualization.Sankey(document.getElementById("' . $chartID . '"));' . NL);
	if ($chartType == 'scatter')
		fputs($fh, '		var chart = new google.visualization.ScatterChart(document.getElementById("' . $chartID . '"));' . NL);
	if ($chartType == 'table')
		fputs($fh, '		var chart = new google.visualization.Table(document.getElementById("' . $chartID . '"));' . NL);

	if ($package == 'corechart' and $globals->doPNG) {
		fputs($fh, '		google.visualization.events.addListener(chart, "ready", function () {' . NL);
		fputs($fh, '			' . $chartID . '.innerHTML = "<img src=\'" + chart.getImageURI() + "\'>";' . NL);
		fputs($fh, '			console.log(' . $chartID . '.innerHTML);' . NL);
		fputs($fh, '		});' . NL);
	}

	fputs($fh, '		chart.draw(data, options);' . NL);
	fputs($fh, '	}' . NL);
	fputs($fh, '	</script>' . NL);
}
