<?php
// Get a single text from an object's SQL query
function text_from_sql($sql) {
	global $globals;

	$db = $globals->dbHandle;

	// Execute the SQL query
	if($globals->debug) {
		print('SQL : ' . replace_vars($sql) . NL);
		$t0 = microtime(true);
	}
	try {
		$db->enableExceptions(true);
		$result = $db->query(replace_vars($sql));
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

	return ($text);
}
