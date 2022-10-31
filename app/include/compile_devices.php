<?php

# VERSION = '5.0.1'

function create_database($globals) {
	// Delete old database (if overwrite requested)
	if($globals->overwrite) {
		print('Overwriting database ...' . NL);
		if(file_exists($globals->db))
			unlink($globals->db);
	}
	
	// Open/Create database
	$db = new SQLite3($globals->db);

	// Create the devices table
	$db->exec('CREATE TABLE IF NOT EXISTS devices (
			deviceIp TEXT,
			deviceName TEXT,
			UNIQUE (deviceIp)
		)');

	return($db);
}

function compile_data($globals, $db) {
	$customers = json_decode(file_get_contents($globals->data));
	$globals->devices = array();
	foreach($customers as $key => $value) {
		if($value->id != $globals->id)
			continue;
		$globals->devices = (array)$value->defensepros;
	}
	$db->exec('BEGIN');
	$statement=$db->prepare('INSERT OR ' . $globals->action . ' INTO devices (
				deviceIp,
				deviceName
			) VALUES (
				:deviceIp,
				:deviceName
			);');
	foreach($globals->devices as $key => $value) {
		$statement->bindValue(':deviceIp', $key);
		$statement->bindValue(':deviceName', $value);
		$statement->execute();
	}
	$db->exec('COMMIT');
}

// Signal the module has been loaded
$globals->moduleLoaded = true;
?>