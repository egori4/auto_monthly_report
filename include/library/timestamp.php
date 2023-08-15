<?php
// Echoes a time stamped string to the output
function timestamp() {
	$t     = microtime(true);
	$micro = sprintf('%06d', ($t - floor($t)) * 1000000);
	$d     = new DateTime(date('Y-m-d H:i:s', $t));
	$pid   = getmypid();
	return ($d->format('ymd-His.' . $micro . '(' . $pid . '): '));
}
