<?php
// This file includes a library of functions from the 'library' folder.
// All the functions present on the library folder will be available to the program.

if($globals->debug)
	print('Loading functions.' . NL);
$functions = scandir(__DIR__.'/library');
foreach($functions as $function) {
	if($function=='.' or $function=='..')
		continue;
	if(isset($globals->start) and $function!=$globals->start)
		continue;
	if($globals->debug)
		print('   '.$function.NL);
	require_once __DIR__.'/library/'.$function;
};
if($globals->debug)
	print('All functions loaded.' . NL);
