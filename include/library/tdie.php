<?php
// Echoes a time stamped string to the output and terminates
function tdie($text, $code=0) {
	techo($text);
	die($code);
}
