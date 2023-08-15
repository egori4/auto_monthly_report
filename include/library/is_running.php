<?php
// Checks if a process name is already running
function is_running($name) {
	exec('ps a', $list, $error);
	if($error)
		tdie('Error: Can not check the running processes.' . NL);
	$running = 0;
	foreach($list as $line) {
		$line  = trim($line);
		$array = preg_split('/\s+/', $line);
		if($array[4] == $name) {
			$running = $array[0];
			break;
		}
	}
	return ($running);
}
