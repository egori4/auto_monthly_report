#!/usr/bin/php
<?php
// Global defines
define('NL', "\n");
define('URL', 'https://www.gstatic.com/');

// Program Start
print('Google Charts downloader v1.1' . NL);
print('      by Marcelo Dantas' . NL);
print('-----------------------------' . NL);

// Process charts/loader.js
if (!file_exists('charts')) {
	print('Creating charts folder.' . NL);
	exec('mkdir charts');
}

print('Finding the current charts version...' . NL);
$current = 0;
if (file_exists('charts/loader.js')) {
	$file = file_get_contents('charts/loader.js');
	$pos = strpos($file, 'current:');
	$current = substr($file, $pos + 9, 2);
	print('Current version is ' . $current . '.' . NL);
}

print('Downloading charts/loader.js...' . NL);
$file = file_get_contents(URL . 'charts/loader.js');

print('Finding the latest charts version...' . NL);
$pos = strpos($file, 'current:');
$version = substr($file, $pos + 9, 2);
print('Latest version is ' . $version . '.' . NL);

if ($version == $current)
	die('Nothing to download.' . NL);

print('Patching charts/loader.js file...' . NL);
$file = str_replace('"' . URL, 'relPath+"/html_files/', $file);
print('Saving charts/loader.js...' . NL);
file_put_contents(str_replace('/', DIRECTORY_SEPARATOR, 'charts/loader.js'), $file);

// Process charts/{version}/loader.js
if (!file_exists('charts/' . $version)) {
	print('Creating charts/' . $version . ' folder.' . NL);
	exec(str_replace('/', DIRECTORY_SEPARATOR, 'mkdir charts/' . $version));
}

print('Downloading charts/' . $version . '/loader.js...' . NL);
$file = file_get_contents(URL . 'charts/' . $version . '/loader.js');

print('Patching charts/' . $version . '/loader.js file...' . NL);
$file = str_replace('"' . URL, 'relPath+"/html_files/', $file);
print('Saving charts' . $version . '/loader.js...' . NL);
file_put_contents(str_replace('/', DIRECTORY_SEPARATOR, 'charts/' . $version . '/loader.js'), $file);

// Create remaining folders
$folders = array();
$folders[] = 'charts/' . $version . '/css';
$folders[] = 'charts/' . $version . '/css/core';
$folders[] = 'charts/' . $version . '/css/table';
$folders[] = 'charts/' . $version . '/css/util';
$folders[] = 'charts/' . $version . '/i18n';
$folders[] = 'charts/' . $version . '/js';
$folders[] = 'charts/' . $version . '/third_party';
$folders[] = 'charts/' . $version . '/third_party/d3';
$folders[] = 'charts/' . $version . '/third_party/d3/v5';
$folders[] = 'charts/' . $version . '/third_party/d3_sankey';
$folders[] = 'charts/' . $version . '/third_party/d3_sankey/v4';
$folders[] = 'charts/' . $version . '/third_party/dygraphs';

foreach ($folders as $key => $folder) {
	print('Creating folder ' . $folder . '...' . NL);
	if (!file_exists($folder))
		exec(str_replace('/', DIRECTORY_SEPARATOR, 'mkdir ' . $folder));
}

$files = array();

// German
$files[] = 'charts/' . $version . '/i18n/jsapi_compiled_i18n_calendar_module__de.js';
$files[] = 'charts/' . $version . '/i18n/jsapi_compiled_i18n_corechart_module__de.js';
$files[] = 'charts/' . $version . '/i18n/jsapi_compiled_i18n_default_module__de.js';
$files[] = 'charts/' . $version . '/i18n/jsapi_compiled_i18n_fw_module__de.js';
$files[] = 'charts/' . $version . '/i18n/jsapi_compiled_i18n_gantt_module__de.js';
$files[] = 'charts/' . $version . '/i18n/jsapi_compiled_i18n_gauge_module__de.js';
$files[] = 'charts/' . $version . '/i18n/jsapi_compiled_i18n_geo_module__de.js';
$files[] = 'charts/' . $version . '/i18n/jsapi_compiled_i18n_geochart_module__de.js';
$files[] = 'charts/' . $version . '/i18n/jsapi_compiled_i18n_graphics_module__de.js';
$files[] = 'charts/' . $version . '/i18n/jsapi_compiled_i18n_sankey_module__de.js';
$files[] = 'charts/' . $version . '/i18n/jsapi_compiled_i18n_scatter_module__de.js';
$files[] = 'charts/' . $version . '/i18n/jsapi_compiled_i18n_table_module__de.js';
$files[] = 'charts/' . $version . '/i18n/jsapi_compiled_i18n_timeline_module__de.js';
$files[] = 'charts/' . $version . '/i18n/jsapi_compiled_i18n_treemap_module__de.js';
$files[] = 'charts/' . $version . '/i18n/jsapi_compiled_i18n_ui_module__de.js';
$files[] = 'charts/' . $version . '/i18n/jsapi_compiled_i18n_vegachart_module__de.js';
$files[] = 'charts/' . $version . '/i18n/jsapi_compiled_i18n_wordtree_module__de.js';
// French
$files[] = 'charts/' . $version . '/i18n/jsapi_compiled_i18n_calendar_module__fr.js';
$files[] = 'charts/' . $version . '/i18n/jsapi_compiled_i18n_corechart_module__fr.js';
$files[] = 'charts/' . $version . '/i18n/jsapi_compiled_i18n_default_module__fr.js';
$files[] = 'charts/' . $version . '/i18n/jsapi_compiled_i18n_fw_module__fr.js';
$files[] = 'charts/' . $version . '/i18n/jsapi_compiled_i18n_gantt_module__fr.js';
$files[] = 'charts/' . $version . '/i18n/jsapi_compiled_i18n_gauge_module__fr.js';
$files[] = 'charts/' . $version . '/i18n/jsapi_compiled_i18n_geo_module__fr.js';
$files[] = 'charts/' . $version . '/i18n/jsapi_compiled_i18n_geochart_module__fr.js';
$files[] = 'charts/' . $version . '/i18n/jsapi_compiled_i18n_graphics_module__fr.js';
$files[] = 'charts/' . $version . '/i18n/jsapi_compiled_i18n_sankey_module__fr.js';
$files[] = 'charts/' . $version . '/i18n/jsapi_compiled_i18n_scatter_module__fr.js';
$files[] = 'charts/' . $version . '/i18n/jsapi_compiled_i18n_table_module__fr.js';
$files[] = 'charts/' . $version . '/i18n/jsapi_compiled_i18n_timeline_module__fr.js';
$files[] = 'charts/' . $version . '/i18n/jsapi_compiled_i18n_treemap_module__fr.js';
$files[] = 'charts/' . $version . '/i18n/jsapi_compiled_i18n_ui_module__fr.js';
$files[] = 'charts/' . $version . '/i18n/jsapi_compiled_i18n_vegachart_module__fr.js';
$files[] = 'charts/' . $version . '/i18n/jsapi_compiled_i18n_wordtree_module__fr.js';
// Spanish
$files[] = 'charts/' . $version . '/i18n/jsapi_compiled_i18n_calendar_module__es.js';
$files[] = 'charts/' . $version . '/i18n/jsapi_compiled_i18n_corechart_module__es.js';
$files[] = 'charts/' . $version . '/i18n/jsapi_compiled_i18n_default_module__es.js';
$files[] = 'charts/' . $version . '/i18n/jsapi_compiled_i18n_fw_module__es.js';
$files[] = 'charts/' . $version . '/i18n/jsapi_compiled_i18n_gantt_module__es.js';
$files[] = 'charts/' . $version . '/i18n/jsapi_compiled_i18n_gauge_module__es.js';
$files[] = 'charts/' . $version . '/i18n/jsapi_compiled_i18n_geo_module__es.js';
$files[] = 'charts/' . $version . '/i18n/jsapi_compiled_i18n_geochart_module__es.js';
$files[] = 'charts/' . $version . '/i18n/jsapi_compiled_i18n_graphics_module__es.js';
$files[] = 'charts/' . $version . '/i18n/jsapi_compiled_i18n_sankey_module__es.js';
$files[] = 'charts/' . $version . '/i18n/jsapi_compiled_i18n_scatter_module__es.js';
$files[] = 'charts/' . $version . '/i18n/jsapi_compiled_i18n_table_module__es.js';
$files[] = 'charts/' . $version . '/i18n/jsapi_compiled_i18n_timeline_module__es.js';
$files[] = 'charts/' . $version . '/i18n/jsapi_compiled_i18n_treemap_module__es.js';
$files[] = 'charts/' . $version . '/i18n/jsapi_compiled_i18n_ui_module__es.js';
$files[] = 'charts/' . $version . '/i18n/jsapi_compiled_i18n_vegachart_module__es.js';
$files[] = 'charts/' . $version . '/i18n/jsapi_compiled_i18n_wordtree_module__es.js';
// Brazilian Portuguese
$files[] = 'charts/' . $version . '/i18n/jsapi_compiled_i18n_calendar_module__pt_br.js';
$files[] = 'charts/' . $version . '/i18n/jsapi_compiled_i18n_corechart_module__pt_br.js';
$files[] = 'charts/' . $version . '/i18n/jsapi_compiled_i18n_default_module__pt_br.js';
$files[] = 'charts/' . $version . '/i18n/jsapi_compiled_i18n_fw_module__pt_br.js';
$files[] = 'charts/' . $version . '/i18n/jsapi_compiled_i18n_gantt_module__pt_br.js';
$files[] = 'charts/' . $version . '/i18n/jsapi_compiled_i18n_gauge_module__pt_br.js';
$files[] = 'charts/' . $version . '/i18n/jsapi_compiled_i18n_geo_module__pt_br.js';
$files[] = 'charts/' . $version . '/i18n/jsapi_compiled_i18n_geochart_module__pt_br.js';
$files[] = 'charts/' . $version . '/i18n/jsapi_compiled_i18n_graphics_module__pt_br.js';
$files[] = 'charts/' . $version . '/i18n/jsapi_compiled_i18n_sankey_module__pt_br.js';
$files[] = 'charts/' . $version . '/i18n/jsapi_compiled_i18n_scatter_module__pt_br.js';
$files[] = 'charts/' . $version . '/i18n/jsapi_compiled_i18n_table_module__pt_br.js';
$files[] = 'charts/' . $version . '/i18n/jsapi_compiled_i18n_timeline_module__pt_br.js';
$files[] = 'charts/' . $version . '/i18n/jsapi_compiled_i18n_treemap_module__pt_br.js';
$files[] = 'charts/' . $version . '/i18n/jsapi_compiled_i18n_ui_module__pt_br.js';
$files[] = 'charts/' . $version . '/i18n/jsapi_compiled_i18n_vegachart_module__pt_br.js';
$files[] = 'charts/' . $version . '/i18n/jsapi_compiled_i18n_wordtree_module__pt_br.js';
// English (default)
$files[] = 'charts/' . $version . '/js/jsapi_compiled_calendar_module.js';
$files[] = 'charts/' . $version . '/js/jsapi_compiled_corechart_module.js';
$files[] = 'charts/' . $version . '/js/jsapi_compiled_default_module.js';
$files[] = 'charts/' . $version . '/js/jsapi_compiled_fw_module.js';
$files[] = 'charts/' . $version . '/js/jsapi_compiled_gantt_module.js';
$files[] = 'charts/' . $version . '/js/jsapi_compiled_gauge_module.js';
$files[] = 'charts/' . $version . '/js/jsapi_compiled_geo_module.js';
$files[] = 'charts/' . $version . '/js/jsapi_compiled_geochart_module.js';
$files[] = 'charts/' . $version . '/js/jsapi_compiled_graphics_module.js';
$files[] = 'charts/' . $version . '/js/jsapi_compiled_sankey_module.js';
$files[] = 'charts/' . $version . '/js/jsapi_compiled_scatter_module.js';
$files[] = 'charts/' . $version . '/js/jsapi_compiled_table_module.js';
$files[] = 'charts/' . $version . '/js/jsapi_compiled_timeline_module.js';
$files[] = 'charts/' . $version . '/js/jsapi_compiled_treemap_module.js';
$files[] = 'charts/' . $version . '/js/jsapi_compiled_ui_module.js';
$files[] = 'charts/' . $version . '/js/jsapi_compiled_vegachart_module.js';
$files[] = 'charts/' . $version . '/js/jsapi_compiled_wordtree_module.js';
// Download remaining files
$files[] = 'charts/' . $version . '/css/core/tooltip.css';
$files[] = 'charts/' . $version . '/css/table/table.css';
$files[] = 'charts/' . $version . '/css/util/format.css';
$files[] = 'charts/' . $version . '/css/util/util.css';
$files[] = 'charts/' . $version . '/third_party/d3_sankey/v4/d3.sankey.js';
$files[] = 'charts/' . $version . '/third_party/d3/v5/d3.js';
$files[] = 'charts/' . $version . '/third_party/dygraphs/dygraph-tickers-combined.js';

foreach ($files as $key => $name) {
	print('Downloading ' . $name . '...' . NL);
	$file = file_get_contents(URL . $name);
	file_put_contents(str_replace('/', DIRECTORY_SEPARATOR, $name), $file);
}

print('Download finished.' . NL);
?>