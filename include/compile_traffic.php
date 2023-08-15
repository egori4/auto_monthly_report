<?php

# VERSION = '5.4'

function create_database($globals) {
	// Delete old database (if overwrite requested)
	if ($globals->overwrite) {
		print('Overwriting database ...' . NL);
		if (file_exists($globals->db))
			unlink($globals->db);
	}

	// Open/Create database
	$db = new SQLite3($globals->db);

	// Create the table
	$db->exec(
		'
		CREATE TABLE IF NOT EXISTS traffic (
				vision TEXT,
				timeStamp INTEGER,
				dateTime DATE,
				month INTEGER,
				year INTEGER,
				quarter INTEGER,
				trafficValue INTEGER,
				discards INTEGER,
				excluded INTEGER,
				UNIQUE (vision, timeStamp)
			)
		'
	);

	return ($db);
}

function compile_data($globals, $db) {
	// Set default date to UTC
	date_default_timezone_set('UTC');

	// Store the previous traffic value
	$pValue = 0;

	$handle = fopen($globals->data, 'r');
	if ($handle) {
		$lineCount = 0;
		while (($line = fgets($handle)) !== false) {
			++$lineCount;
			$line = rtrim(trim($line), ',');
			if ($line == '[' or $line == ']' or $line == '')
				continue;
			$data = json_decode($line);
			if (isset($globals->vision))
				$data->metaData->vision = $globals->vision;
			if (isset($data->metaData->totalHits)) {
				$records = $data->metaData->totalHits;
			} else {
				continue;
			}
			$db->exec('BEGIN');
			$statement = $db->prepare('INSERT OR ' . $globals->action . ' INTO traffic (
						vision,
						timeStamp,
						dateTime,
						month,
						year,
						quarter,
						trafficValue,
						discards,
						excluded
					) VALUES (
						:vision,
						:timeStamp,
						:dateTime,
						:month,
						:year,
						:quarter,
						:trafficValue,
						:discards,
						:excluded
					);');
			// Load traffic data
			for ($i = 0; $i < $records; ++$i) {
				$row = $data->data[$i]->row;
				// Remove spikes (or die trying)
				$temp = $row->trafficValue;
				if($pValue > 0) {
					if($row->trafficValue > ($pValue * 20)) {
						$row->trafficValue = $pValue;
						print('WARNING: Spike removed at ' . date("Y-m-d H:i:s", intdiv($row->timeStamp, 1000)) . NL);
					}
				}
				$pValue = $temp;
				//
				$statement->bindValue(':vision', $data->metaData->vision);
				$statement->bindValue(':timeStamp', $row->timeStamp);
				$statement->bindValue(':dateTime', date("Y-m-d H:i:s", intdiv($row->timeStamp, 1000)));
				$statement->bindValue(':month', date('m', intdiv($row->timeStamp, 1000)));
				$statement->bindValue(':year', date('Y', intdiv($row->timeStamp, 1000)));
				$statement->bindValue(':quarter', 'Q' . intdiv(date('m', intdiv($row->timeStamp, 1000)) + 2, 3));
				$statement->bindValue(':trafficValue', $row->trafficValue);
				$statement->bindValue(':discards', $row->discards);
				$statement->bindValue(':excluded', $row->excluded);
				$r = @$statement->execute();
				if ($r === false)
					die('========== CRITICAL ERROR: ' . $db->lastErrorMsg() . NL);
			}
			$r = $db->exec('COMMIT');
			if ($r === false)
				die('========== CRITICAL ERROR: ' . $db->lastErrorMsg() . NL);
		}
		fclose($handle);
		if ($lineCount == 0)
			print('WARNING: No lines have been processed on this compilation.' . NL);
	} else {
		print('ERROR: Cannot open input data file.' . NL);
	}
}

// Signal the module has been loaded
$globals->moduleLoaded = true;
