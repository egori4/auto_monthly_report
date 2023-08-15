<?php
// Merges two objects recursively
function object_merge($object1, $object2) {
	// Get the type of the result
	$resultType = gettype($object1);
	if($resultType == 'object') {
		$result = clone $object1; // Make a clone as objects are passed by reference
	} else {
		$result = $object1; // Otherwise just copy
	}
	// Iterate through the values
	foreach($object2 as $key => $value) {
		// Get the type of the value
		$valueType = gettype($value);
		// If it is an object, recurse
		if($valueType == 'object') {
			if(isset($result->{$key})) {
				$result->{$key} = object_merge($result->{$key}, $value);
				continue;
			}
		}
		// If it is an array, recurse
		if(gettype($value) == 'array') {
			if(isset($result->{$key})) {
				$result->{$key} = object_merge($result->{$key}, $value);
				continue;
			}
		}
		// If not, just set over to the result
		if($resultType == 'array' and is_numeric($key)) {
			$result[] = $value; // Numeric keys must be appended
		} else {
			$result->{$key} = $value; // Otherwise can just be set
		}
	}
	return ($result);
}
