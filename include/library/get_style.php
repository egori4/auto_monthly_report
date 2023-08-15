<?php
// Gets the style definition of an object in html format
function get_style($object) {
	$txt = '';
	foreach($object->style as $key => $value)
		$txt .= $key . ': ' . $value . '; ';
	return (trim($txt));
}
