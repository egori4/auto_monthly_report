<?php
// Stops counting seconds and prints
function timeOut($id = 254, $time = null) {
	global $timer;
	if($time === null) {
		$array = explode(' ', microtime());
	    $time = $array[1]+$array[0];
	}
	printf(timeDiff($timer[$id], $time));
}
