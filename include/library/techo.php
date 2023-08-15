<?php
// Echoes a time stamped string to the output
function techo($text) {
	global $globals;

	$text = timestamp().$text;

	if(isset($globals->log))
		file_put_contents($globals->log, $text , FILE_APPEND | LOCK_EX);

	if(!isset($globals->logOnly))
		print($text);
}
