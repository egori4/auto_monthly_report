<?php
// Describe contents of a variable recursively
function describe($var, $name = '', $index = 0) {
	$lead = str_repeat('  ', $index);
	$type = get_debug_type($var);
	print($lead.'('.$type.')');
	if($name != '')
		print($name);
	switch($type) {
		case 'int':
		case 'float':
			print('=' . $var . NL);
			break;
		case 'string':
			print('="' . addslashes($var) . '"' . NL);
			break;
		case 'stdClass':
		case 'array':
			print(NL . $lead . '{' . NL);
			foreach($var as $key => $value) {
				describe($value, $key, $index + 1);
			}
			print($lead . '}' . NL);
			break;
		case 'bool':
			print($var ? '=true' : '=false');
		default:
			print(NL);
			break;
	}
}
