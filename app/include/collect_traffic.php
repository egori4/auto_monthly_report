<?php

# VERSION = '5.0.1'

// Modify usage text
$globals->usageText = '-data="<data.json>" -module="<module>" [-append]' . NL .
 TAB . '-lower="dd.mm.yyyy" -upper="dd.mm.yyyy" (Date range to collect - last day is excluded)' . NL .
 TAB . '-vision="<Vision IP>" -user="<Vision Username>" -pass="<Vision Password>"' . NL .
 TAB . '[-dps="dpIP[,dpIP...]"] (DP IPs to collect data from - default all)' . NL . NL;

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

// Query creation function
function create_query($globals) {
	// Establish a query
	$query = new stdclass();

	$query->aggregation           = new stdclass();
	$query->aggregation->criteria = array();

	// Add date range to the criteria
	$filter                         = new stdclass();
	$filter->type                   = 'timeFilter';
	$filter->field                  = 'timeStamp';
	$filter->lower                  = '{lower}';
	$filter->upper                  = '{upper}';
	$filter->includeLower           = true;
	$filter->includeUpper           = true;
	$query->aggregation->criteria[] = $filter;

	// Add protocol to the criteria
	$filter                         = new stdclass();
	$filter->type                   = 'termFilter';
	$filter->field                  = 'monitoringProtocol';
	$filter->value                  = 'all';
	$query->aggregation->criteria[] = $filter;

	// Add unit to the criteria
	$filter                         = new stdclass();
	$filter->type                   = 'termFilter';
	$filter->field                  = 'unit';
	$filter->value                  = 'bps';
	$query->aggregation->criteria[] = $filter;

	// Add direction to the criteria
	$filter                         = new stdclass();
	$filter->type                   = 'termFilter';
	$filter->field                  = 'direction';
	$filter->value                  = 'Inbound';
	$query->aggregation->criteria[] = $filter;

	// Add devices to the criteria
	$array           = explode(',', $globals->dps);
	$filter          = new stdclass();
	$filter->type    = 'orFilter';
	$filter->filters = array();
	foreach($array as $key => $value) {
		$filter2           = new stdclass();
		$filter2->type     = 'termFilter';
		$filter2->field    = 'deviceIp';
		$filter2->value    = $value;
		$filter->filters[] = $filter2;
	}
	$query->aggregation->criteria[] = $filter;

	$query->aggregation->type                  = 'dateHistogram';
	$query->aggregation->aggField              = 'timeStamp';
	$query->aggregation->aggName               = 'timeStamp';
	$query->aggregation->aggregation           = new stdclass();
	$query->aggregation->aggregation->type     = 'calculation';
	$query->aggregation->aggregation->aggField = null;
	$query->aggregation->aggregation->aggName  = null;
	$query->aggregation->aggregation->metrices = array();

	$filter                                      = new stdclass();
	$filter->type                                = 'sumMetric';
	$filter->aggName                             = 'trafficValue';
	$filter->aggField                            = 'trafficValue';
	$query->aggregation->aggregation->metrices[] = $filter;

	$filter                                      = new stdclass();
	$filter->type                                = 'sumMetric';
	$filter->aggName                             = 'excluded';
	$filter->aggField                            = 'excluded';
	$query->aggregation->aggregation->metrices[] = $filter;

	$filter                                      = new stdclass();
	$filter->type                                = 'sumMetric';
	$filter->aggName                             = 'discards';
	$filter->aggField                            = 'discards';
	$query->aggregation->aggregation->metrices[] = $filter;

	$query->aggregation->timeInterval               = new stdclass();
	$query->aggregation->timeInterval->dateFraction = 'HOUR';
	$query->aggregation->timeInterval->amount       = 1;

	$query->order            = array();
	$filter                  = new stdclass();
	$filter->type            = 'Order';
	$filter->order           = 'ASC';
	$filter->aggregationName = null;
	$filter->field           = 'timeStamp';
	$filter->sortingType     = 'LONG';
	$query->order[]          = $filter;

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
	$uri      = 'DP_TRAFFIC_UTILIZATION_RAW_REPORTS';

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
			$d2 = $upper-1;

			$query->aggregation->criteria[0]->lower = +($d1 . '000');
			$query->aggregation->criteria[0]->upper = +($d2 . '000');

			// Execute REST API call
			$json = json_encode($query);
			if($globals->debug)
				print(json_encode($query, JSON_PRETTY_PRINT) . NL);

			$res = rest('POST', "https://$visionIP/$uriBase/$uri", $json);
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
			break;
		}

		// Move on
		$retries = $globals->maxRetry;
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
			}
		} else {
			echo('#');
		}
		fputs($fh, json_encode($res));
		fputs($fh, "\n");
		$recs++;
		fclose($fh);
		print(" Done!\n");
		print("$calls calls executed. ");
		print("$events events collected. ");
		if($exceed) {
			print("WARNING: $exceed calls exceeded $recLimit records.\n");
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