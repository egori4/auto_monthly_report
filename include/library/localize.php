<?php
// Apply language localization to text
function localize($text) {
	global $globals;
	$array = explode(' ', $text);
	foreach($array as $key => $value) {
		$array[$key] = isset($globals->localize[$value])?$globals->localize[$value]:$value;
	}
	$text = implode(' ', $array);
	return($text);
}
