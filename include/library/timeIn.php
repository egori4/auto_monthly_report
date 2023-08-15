<?php
// Starts counting seconds
$timer = array();
function timeIn($id = 254, $time = null) {
	global $timer;
    if($time === null) {
		$array = explode(' ', microtime());
        $time = $array[1]+$array[0];
	}
	$timer[$id] = $time;
}
