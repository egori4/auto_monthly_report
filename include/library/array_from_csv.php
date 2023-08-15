<?php
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
