<?php
// Echoes a string to the output
function lecho($text) {
	global $globals;

	if(isset($globals->log))
		file_put_contents($globals->log, $text , FILE_APPEND | LOCK_EX);

	if(!isset($globals->logOnly))
		print($text);
}
