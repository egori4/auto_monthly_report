<?php
// Gets json data from a file
function get_json_data($file) {
	global $globals;
	$data  = json_decode(file_get_contents($file));
	$error = json_last_error();
	if($error !== JSON_ERROR_NONE) {
		print('Error: While validating the JSON file.' . NL);
		if(file_exists($globals->jq)) {
			passthru($globals->jq . ' ".[]" ' . $globals->config);
		} else {
			switch($error) {
				case JSON_ERROR_DEPTH:
					$error = 'Maximum depth exceeded!';
					break;
				case JSON_ERROR_STATE_MISMATCH:
					$error = 'Underflow or the modes mismatch!';
					break;
				case JSON_ERROR_CTRL_CHAR:
					$error = 'Unexpected control character found';
					break;
				case JSON_ERROR_SYNTAX:
					$error = 'Malformed JSON';
					break;
				case JSON_ERROR_UTF8:
					$error = 'Malformed UTF-8 characters found!';
					break;
				default:
					$error = 'Unknown error!';
					break;
			}
			print($error . NL);
		}
		exit(1);
	}
	return ($data);
}
