<?php

# VERSION = '5.0.1'

// Modify usage text
$globals->usageText = '-data="<data.json>" -module="<module>" [-append]' . NL .
 TAB . '-lower="dd.mm.yyyy" -upper="dd.mm.yyyy" (Date range to collect - last day is excluded)' . NL .
 TAB . '-include="field:value[,field:value...]" (Fields to include in the query - overrides -exclude)' . NL .
 TAB . '-exclude="field:value[,field:value...]" (Fields to exclude from the query)' . NL .
 TAB . '-vision="<Vision IP>" -user="<Vision Username>" -pass="<Vision Password>"' . NL .
 TAB . '[-dps="dpIP[,dpIP...]"] (DP IPs to collect data from - default all)' . NL .
 TAB . '[-window=nnnn] (Time window in seconds for each query request - default 3600)' . NL . NL;

// Check for missing parameters
if(!isset($globals->vision)) {
	print('Vision IP parameter not found.' . NL . NL . usage());
	exit(1);
}
if(!isset($globals->user)) {
	print('Vision username parameter not found.' . NL . NL . usage());
	exit(1);
}
if(!isset($globals->pass)) {
	print('Vision password parameter not found.' . NL . NL . usage());
	exit(1);
}
if(!isset($globals->lower)) {
	print('Lower date parameter not found.' . NL . NL . usage());
	exit(1);
}
if(!isset($globals->upper)) {
	print('Upper date parameter not found.' . NL . NL . usage());
	exit(1);
}

// Date ranges converted to Unix Epoch format (UTC)
date_default_timezone_set('UTC');
$globals->lower = strtotime($globals->lower);
$globals->upper = strtotime($globals->upper);

// Set default parameters
if(!isset($globals->window))
	$globals->window = 3600; // 1 Hour

// Query creation function
function create_query($globals) {
	// Establish a query
	$query = new stdclass();

	// Establish a criteria
	$query->criteria = array();

	// Establish an "and" filter array
	$andFilters            = new stdclass();
	$andFilters->type      = 'andFilter';
	$andFilters->filters   = array();
	// Establish a date range and add to the andFilters
	$filter                = new stdclass();
	$filter->type          = 'timeFilter';
	$filter->field         = 'endTime';
	$filter->lower         = '{lower}';
	$filter->upper         = '{upper}';
	$filter->includeLower  = true;
	$filter->includeUpper  = true;
	$andFilters->filters[] = $filter;

	// Add include or exclude data to the andFilters
	if(isset($globals->include)) { // Include has precedence over exclude
		$array = explode(',', $globals->include);
		if(count($array) == 1) {
			list($field, $value) = explode(':', $globals->include);
			$filter                = new stdclass();
			$filter->type          = 'termFilter';
			$filter->field         = $field;
			$filter->value         = $value;
			$andFilters->filters[] = $filter;
		} else {
			$filter          = new stdclass();
			$filter->type    = 'orFilter';
			$filter->filters = array();
			foreach($array as $key => $text) {
				list($field, $value) = explode(':', $text);
				$filter2           = new stdclass();
				$filter2->type     = 'termFilter';
				$filter2->field    = $field;
				$filter2->value    = $value;
				$filter->filters[] = $filter2;
			}
			$andFilters->filters[] = $filter;
		}
	} else {
		if(isset($globals->exclude)) { // Exclude is a list
			$array = explode(',', $globals->exclude);
			foreach($array as $key => $text) {
				list($field, $value) = explode(':', $text);
				$filter                = new stdclass();
				$filter->type          = 'termFilter';
				$filter->field         = $field;
				$filter->value         = $value;
				$filter->inverseFilter = true;
				$andFilters->filters[] = $filter;
			}
		}
	}

	// Establish an "or" filter array
	$orFilters          = new stdclass();
	$orFilters->type    = 'orFilter';
	$orFilters->filters = array();

	// Add the DefensePro IPs to the orFilters
	if(isset($globals->dps)) {
		$array = explode(',', $globals->dps);
		foreach($array as $key => $value) {
			$filter               = new stdclass();
			$filter->type         = 'termFilter';
			$filter->field        = 'deviceIp';
			$filter->value        = $value;
			$orFilters->filters[] = $filter;
		}
	} else { // If no DefensePro selected, pull from all
		$filter                = new stdclass();
		$filter->type          = 'termFilter';
		$filter->field         = 'deviceIp';
		$filter->value         = '0.0.0.0';
		$filter->inverseFilter = true;
		$orFilters->filters[]  = $filter;
	}

	// Add the filter arrays to the query criteria
	$query->criteria[] = $andFilters;
	$query->criteria[] = $orFilters;

	// Establish pagination info
	$pagination          = new stdclass();
	$pagination->page    = 0;
	$pagination->size    = 10000;
	$pagination->topHits = 10000;

	// Add the pagination to the query criteria
	$query->pagination = $pagination;

	if($globals->debug)
		print(json_encode($query, JSON_PRETTY_PRINT) . NL);

	return ($query);
}

// Data collection function
function collect_data($globals, $query) {
	// Log in to Vision and obtain the JSESSIONID
	$res = vision_login($globals->vision, $globals->user, $globals->pass);
	if($res != 'ok')
		die('Vision credentials are incorrect. Access denied.' . NL . NL);

	$lower    = $globals->lower;
	$upper    = $globals->upper;
	$visionIP = $globals->vision;
	$outFile  = $globals->data;
	$uriBase  = 'mgmt/monitor/reporter/reports-ext';
	$uri      = 'ATTACK';

	// Create Output file
	if($globals->append) {
		$fh = fopen($outFile, 'a');
	} else {
		$fh = fopen($outFile, 'w');
	}

	// Execute the query
	if($fh) {
		$recs    = 0;
		$calls   = 0;
		$events  = 0;
		$exceed  = 0;
		$lost    = 0;
		$retries = $globals->maxRetry;
		while($lower < $upper) {
			$d1 = $lower;
			$d2 = $lower + $globals->window;

			$query->criteria[0]->filters[0]->lower = +($d1 . '000');
			$query->criteria[0]->filters[0]->upper = +($d2 . '000');

			// Execute REST API call
			$json = json_encode($query);
			$res  = rest('POST', "https://$visionIP/$uriBase/$uri", $json);
			if(!isset($res->data)) {
				if($globals->debug)
					print_r($res);
				$retries--;
				if($retries) {
					echo ('r');
					sleep($globals->timeRetry);
					continue;
				}
				echo ("\nERROR: Exceeded number of retries.");
				break;
			}

			// Move on
			$retries = $globals->maxRetry;
			$lower += $globals->window;
			$calls++;
			if(isset($res->metaData)) {
				if($res->metaData->totalHits) {
					$res->metaData->vision = $globals->vision;
					if($res->metaData->totalHits > $globals->recLimit) {
						$exceed++;
						$lost += ($res->metaData->totalHits - $globals->recLimit);
						echo('!');
					} else {
						echo('-');
					}
					$events += $res->metaData->totalHits;
				} else {
					echo('.');
					continue;
				}
			} else {
				echo('#');
				continue;
			}
			fputs($fh, json_encode($res));
			fputs($fh, "\n");
			$recs++;
		}
		fclose($fh);
		print(" Done!\n");
		print("$calls calls executed. ");
		print("$events events collected. ");
		if($exceed) {
			print("WARNING: $exceed calls exceeded " . $globals->recLimit . " records.\n");
			print("WARNING: $lost records lost.\n");
		}
		print("$recs records saved.\n");
		if($recs == 0)
			die('WARNING: No data has been collected.' . NL);
	} else {
		die('ERROR: Cannot create output file.' . NL);
	}

	return ($recs);
}

// Signal the module has been loaded
$globals->moduleLoaded = true;
?>