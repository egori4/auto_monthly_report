<?php
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
