<?php
// Parses all the command line arguments
function parse_args($usePositional = false) {
	$args = new stdclass();
	$idx  = 0;
	foreach($GLOBALS['argv'] as $key => $arg) {
		// Ignore self filename ($argv[0])
		if(!$key)
			continue;

		// Error if parameter is not started by '-'
		if(substr($arg, 0, 1) != '-') {
			if($usePositional) {
				$args->{'_' . $idx++} = $arg;
				continue;
			} else {
				print(NL . 'Invalid command line parameter #' . $key . ' (' . $arg . ').' . NL);
				usage();
			}
		}

		// Remove leading '-' from parameter
		while(substr($arg, 0, 1) == '-')
			$arg = substr($arg, 1);

		// Find a '=' on the parameter string
		$eqPos = strpos($arg, '=');
		if($eqPos === false) { // If it has no '=' then it is a global true
			$args->{$arg} = true;
		} else { // Otherwise set it as an argument variable
			$name  = substr($arg, 0, $eqPos);
			$value = substr($arg, $eqPos + 1);
			if(is_numeric($value))
				$value += 0;
			$args->{$name} = $value;
		}
	}

	// Shows help information if requested
	if(isset($args->help) or isset($args->h)) {
		usage();
		die();
	}


	return ($args);
}
