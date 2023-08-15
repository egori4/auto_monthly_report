<?php
// This file contains all the common global definitions
$globals = new stdclass();
$globals->debug = false;
$globals->path = str_replace(DIRECTORY_SEPARATOR, '/', dirname(realpath($argv[0])));
$globals->php = $globals->path . '/tools/php/php.exe';
