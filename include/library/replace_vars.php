<?php
// Replaces globals variable names into a text string
function replace_vars($text) {
	global $globals;

	while(strpos($text, '{') !== false) {
		$varStart = strpos($text, '{');
		$varStop  = strpos($text, '}');
		$varName  = substr($text, $varStart + 1, $varStop - $varStart - 1);
		// if varName starts with '^' it needs to have its first character uppercased
		$upper = false;
		if (substr($varName, 0, 1) == '^') {
			$upper = true;
			$varName = substr($varName, 1);
		}
		// if varName starts with '$' evaluate it as a php expression
		if (substr($varName, 0, 1) == '$') {
			eval('$varName = ' . $varName . ';');
			$text = substr($text, 0, $varStart) . $varName . substr($text, $varStop + 1);
		} else 
		if(isset($globals->{$varName})) {
			$text = substr($text, 0, $varStart) . $globals->{$varName} . substr($text, $varStop + 1);
		} else {
			print('Warning: Variable ' . $varName . ' is undefined.' . NL);
			$text = substr($text, 0, $varStart) . '?' . $varName . '?' . substr($text, $varStop + 1);
		}
		if ($upper)
			$text = ucfirst($text);
	}

	return ($text);
}
