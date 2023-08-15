<?php
// Splits a string onto multiple tokens
function tokenize($line) {
$regex = <<<HERE
/  "  ( (?:[^"\\\\]++|\\\\.)*+ ) \"
 | '  ( (?:[^'\\\\]++|\\\\.)*+ ) \'
 | \( ( [^)]*                  ) \)
 | [\s,]+
/x
HERE;
	$code = new stdclass();
	$tokens = preg_split($regex, $line, -1, PREG_SPLIT_NO_EMPTY | PREG_SPLIT_DELIM_CAPTURE);
	return($tokens);
}
