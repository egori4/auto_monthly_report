<?php
// Shows command line usage
function usage($additional = false) {
	global $globals;
	print('Usage: ' . APP . ' ' . USAGE . NL);
	if($additional)
		print($additional);
}
