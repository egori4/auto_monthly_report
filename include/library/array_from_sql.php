<?php
// Get an array of data from an object's SQL query
function array_from_sql($sql, $names=false) {
	global $globals;

	$rowData = array();

	$db      = $globals->dbHandle;

	// Execute the SQL query
	if($globals->debug) {
		print('SQL : ' . replace_vars($sql) . NL);
		$t0 = microtime(true);
	}
	try {
		$db->enableExceptions(true);
		$results = $db->query(replace_vars($sql));
	} catch(Exception $e) {
		die('SQL Error: ' . $e->getMessage() . NL);
	}
	if($globals->debug)
		print(' <time: ' . microtime(true)-$t0 . '>)' . NL);
	$cols = $results->numColumns();
	if($names) {
		// Set the array as the column names
		$rowData[] = array();
		for($i = 0; $i < $cols; ++$i) {
			$rowData[0][$i] = $results->columnName($i);
		}
	}
	// Load the array with data
	while($row = $results->fetchArray(SQLITE3_NUM)) {
		$rowData[] = $row;
	}
	// Release memory
	$results->finalize();

	if($globals->debug > 1)
		describe($rowData,'rowData');

	return ($rowData);
}
