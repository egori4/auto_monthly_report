<?php

# VERSION = '5.4'

// Load ipToName translations
$globals->ipToName = array();
if (file_exists('text_files/ipToName.txt')) {
	print('Reading ipToNames table ... ');
	$array = file('text_files/ipToName.txt');
	foreach ($array as $key => $value) {
		if (trim($value) == '')
			continue;
		list($ip, $name) = explode(',', trim($value));
		$globals->ipToName[$ip] = trim($name);
	}
	print(' ok.' . NL);
}

function create_database($globals) {
	// Delete old database (if overwrite requested)
	if ($globals->overwrite) {
		print('Overwriting database ...' . NL);
		if (file_exists($globals->db))
			unlink($globals->db);
	}

	// Open/Create database
	$db = new SQLite3($globals->db);

	// Create the attacks table
	$db->exec(
		'
		CREATE TABLE IF NOT EXISTS attacks (
			vision TEXT,
			name TEXT,
			attackIpsId TEXT,
			actionType TEXT,
			risk TEXT,
			startTime INTEGER,
			endTime INTEGER,
			startDate DATE,
			endDate DATE,
			month INTEGER,
			year INTEGER,
			quarter INTEGER,
			deviceIp TEXT,
			deviceName TEXT,
			sourceAddress TEXT,
			sourcePort TEXT,
			destAddress TEXT,
			destPort TEXT,
			protocol TEXT,
			packetBandwidth INTEGER,
			packetCount INTEGER,
			direction TEXT,
			geoLocation TEXT,
			ruleName TEXT,
			category TEXT,
			threatGroup TEXT,
			startDayOfMonth INTEGER,
			endDayOfMonth INTEGER,
			protocolPort TEXT,
			durationRange TEXT,
			averageAttackPacketRatePps INTEGER,
			maxAttackPacketRatePps INTEGER,
			averageAttackRateBps INTEGER,
			maxAttackRateBps INTEGER,
			UNIQUE (attackIpsId, deviceIp)
		);
		'
	);
	$db->exec(
		'
		CREATE TABLE IF NOT EXISTS ertfeed (
			src TEXT,
			vision TEXT,
			attackIpsId TEXT,
			deviceIp TEXT,
			name TEXT,
			sourceAddress TEXT,
			destAddress TEXT,
			geoLocation TEXT,
			packetBandwidth INTEGER,
			packetCount INTEGER,
			endDayOfMonth INTEGER,
			UNIQUE (attackIpsId, deviceIp)
		);
		'
	);
	if ($globals->index) {
		$db->exec(
			'
			PRAGMA journal_mode=memory;
			CREATE INDEX IF NOT EXISTS PktCount on attacks(packetCount);
			CREATE INDEX IF NOT EXISTS PktBandwidth on attacks(packetBandwidth);
			CREATE INDEX IF NOT EXISTS EndDayOfMonth on attacks(endDayOfMonth);
			CREATE INDEX IF NOT EXISTS DeviceIp on attacks(deviceIp);
			CREATE INDEX IF NOT EXISTS DeviceIpPktCount on attacks(deviceIp,packetCount);
			CREATE INDEX IF NOT EXISTS DeviceIpPktBandwidth on attacks(deviceIp,packetBandwidth);
			CREATE INDEX IF NOT EXISTS GeoLocation on attacks(geoLocation);
			CREATE INDEX IF NOT EXISTS SourceAddressGeoLocation on attacks(sourceAddress,geoLocation);
			CREATE INDEX IF NOT EXISTS DestAddress on attacks(destAddress);
			CREATE INDEX IF NOT EXISTS RuleName on attacks(ruleName);
			CREATE INDEX IF NOT EXISTS RuleNamePacketCount on attacks(ruleName,packetCount);
			CREATE INDEX IF NOT EXISTS RuleNamePacketBandwidth on attacks(ruleName,packetBandwidth);
			CREATE INDEX IF NOT EXISTS Name on attacks(name);
			CREATE INDEX IF NOT EXISTS NamePacketCount on attacks(name,packetCount);
			CREATE INDEX IF NOT EXISTS NamePacketBandwidth on attacks(name,packetBandwidth);
			CREATE INDEX IF NOT EXISTS ProtocolPort on attacks(protocolPort);
			CREATE INDEX IF NOT EXISTS Protocol on attacks(protocol);
			CREATE INDEX IF NOT EXISTS ProtocolPacketCount on attacks(protocol,packetCount);
			CREATE INDEX IF NOT EXISTS ProtocolPacketBandwidth on attacks(protocol,packetBandwidth);
			CREATE INDEX IF NOT EXISTS DurationRange on attacks(durationRange);
			CREATE INDEX IF NOT EXISTS CategoryPacketCount on attacks(category,packetCount);
			CREATE INDEX IF NOT EXISTS CategoryPacketBandwidth on attacks(category,packetBandwidth);
			CREATE INDEX IF NOT EXISTS Month on attacks(month);
			CREATE INDEX IF NOT EXISTS MonthPacketCount on attacks(month,packetCount);
			CREATE INDEX IF NOT EXISTS MonthPacketBandwidth on attacks(month,packetBandwidth);
			CREATE INDEX IF NOT EXISTS EndTime on attacks(endTime);
			'
		);
		$db->exec(
			'
			PRAGMA journal_mode=memory;
			CREATE INDEX IF NOT EXISTS eName on ertfeed(name);
			CREATE INDEX IF NOT EXISTS eGeoLocation on ertfeed(geoLocation);
			CREATE INDEX IF NOT EXISTS eEndDayOfMonth on ertfeed(EndDayOfMonth);
			'
		);
	}

	return ($db);
}

function compile_data($globals, $db) {
	// Set default date to UTC
	date_default_timezone_set('UTC');

	$geoCache = array();

	$handle = fopen($globals->data, 'r');
	if ($handle) {
		$lineCount = 0;
		while (($line = fgets($handle)) !== false) {
			++$lineCount;
			$line = rtrim(trim($line), ',');
			if ($line == '[' or $line == ']' or $line == '')
				continue;
			$data = json_decode($line);
			if (isset($globals->vision))
				$data->metaData->vision = $globals->vision;
			if (isset($data->metaData->totalHits)) {
				$records = $data->metaData->totalHits;
			} else {
				continue;
			}
			$db->exec('PRAGMA journal_mode=memory');
			$db->exec('BEGIN');
			$statement = $db->prepare('INSERT OR ' . $globals->action . ' INTO attacks (
						vision,
						name,
						attackIpsId,
						actionType,
						risk,
						startTime,
						endTime,
						startDate,
						endDate,
						month,
						year,
						quarter,
						deviceIp,
						deviceName,
						sourceAddress,
						sourcePort,
						destAddress,
						destPort,
						protocol,
						packetBandwidth,
						packetCount,
						direction,
						geoLocation,
						ruleName,
						category,
						threatGroup,
						startDayOfMonth,
						endDayOfMonth,
						protocolPort,
						durationRange,
						averageAttackPacketRatePps,
						maxAttackPacketRatePps,
						averageAttackRateBps,
						maxAttackRateBps
					) VALUES (
						:vision,
						:name,
						:attackIpsId,
						:actionType,
						:risk,
						:startTime,
						:endTime,
						:startDate,
						:endDate,
						:month,
						:year,
						:quarter,
						:deviceIp,
						:deviceName,
						:sourceAddress,
						:sourcePort,
						:destAddress,
						:destPort,
						:protocol,
						:packetBandwidth,
						:packetCount,
						:direction,
						:geoLocation,
						:ruleName,
						:category,
						:threatGroup,
						:startDayOfMonth,
						:endDayOfMonth,
						:protocolPort,
						:durationRange,
						:averageAttackPacketRatePps,
						:maxAttackPacketRatePps,
						:averageAttackRateBps,
						:maxAttackRateBps
					);');
			if (isset($globals->EAAFdb) and $globals->EAAFdb == true) {
				$statement_ert = $db->prepare('INSERT OR ' . $globals->action . ' INTO ertfeed (
						src,
						vision,
						attackIpsId,
						deviceIp,
						name,
						sourceAddress,
						destAddress,
						geoLocation,
						packetCount,
						packetBandwidth,
						endDayOfMonth
					) VALUES (
						:src,
						:vision,
						:attackIpsId,
						:deviceIp,
						:name,
						:sourceAddress,
						:destAddress,
						:geoLocation,
						:packetCount,
						:packetBandwidth,
						:endDayOfMonth
					);');
			}
			$nrec = $records;
			if ($records > 10000)
				$nrec = 10000;
			for ($i = 0; $i < $nrec; ++$i) {
				$row = $data->data[$i]->row;

				$row->startDayOfMonth = +gmdate('d', $row->startTime / 1000);
				$row->endDayOfMonth = +gmdate('d', $row->endTime / 1000);
				$row->protocolPort = $row->destPort . ' (' . $row->protocol . ')';
				if ($globals->geoUseHostIP) {
					// Get GEO from the source IP itself
					if (!isset($geoCache[$row->sourceAddress]))
						$geoCache[$row->sourceAddress] = trim(file_get_contents('http://api.hostip.info/country.php?ip=' . $row->sourceAddress));
					$row->geoLocation = $geoCache[$row->sourceAddress];
				} else {
					// Get GEO from the Enrichment Container
					if (isset($row->enrichmentContainer)) {
						$json = json_decode($row->enrichmentContainer);
						$row->geoLocation = $json->geoLocation->countryCode;
					} else {
						$row->geoLocation = '--';
					}
				}
				if ($row->geoLocation == 'XX')
					$row->geoLocation = '--';
				if ($row->geoLocation == 'Multiple')
					$row->geoLocation = '--';

				if (isset($globals->EAAFdb) and $globals->EAAFdb == true) {
					if ($row->category == 'ErtFeed' or $row->category == 'GeoFeed') {
						$statement_ert->bindValue(':src', substr($row->category, 0, 1));
						$statement_ert->bindValue(':vision', $data->metaData->vision);
						$statement_ert->bindValue(':attackIpsId', $row->attackIpsId);
						$statement_ert->bindValue(':deviceIp', $row->deviceIp);
						if ($row->category == 'ErtFeed') {
							if (trim($row->name) == '')
								$row->name = 'ERT Active Attacker: ERT';
							$statement_ert->bindValue(':name', substr($row->name, 21));
						} else {
							$statement_ert->bindValue(':name', 'GEO');
						}
						$statement_ert->bindValue(':sourceAddress', $row->sourceAddress);
						$statement_ert->bindValue(':destAddress', $row->destAddress);
						$statement_ert->bindValue(':geoLocation', $row->geoLocation);
						$statement_ert->bindValue(':packetCount', $row->packetCount);
						$statement_ert->bindValue(':packetBandwidth', $row->packetBandwidth);
						$statement_ert->bindValue(':endDayOfMonth', $row->endDayOfMonth);
						$r = @$statement_ert->execute();
						if ($r === false)
							die('========== CRITICAL ERROR: ' . $db->lastErrorMsg() . NL);
						continue;
					}
				}

				// translate DP IP to DP Name (if possible)
				$row->deviceName = isset($globals->ipToName[$row->deviceIp]) ? $globals->ipToName[$row->deviceIp] : $row->deviceIp;
				// Computing some derived keys
				if (!isset($row->duration))
					$row->duration = $row->endTime - $row->startTime;
				$minutes = intval($row->duration / 1000 / 60);
				if ($minutes < 2) {
					$range = '00 to 01 minutes';
				} else if ($minutes < 6) {
					$range = '01 to 05 minutes';
				} else if ($minutes < 11) {
					$range = '05 to 10 minutes';
				} else if ($minutes < 31) {
					$range = '10 to 30 minutes';
				} else if ($minutes < 61) {
					$range = '30 to 60 minutes';
				} else {
					$range = '60 minutes or more';
				}
				$row->durationRange = $range;
				$statement->bindValue(':vision', $data->metaData->vision);
				$statement->bindValue(':name', $row->name);
				$statement->bindValue(':attackIpsId', $row->attackIpsId);
				$statement->bindValue(':actionType', $row->actionType);
				$statement->bindValue(':risk', $row->risk);
				$statement->bindValue(':startTime', $row->startTime);
				$statement->bindValue(':endTime', $row->endTime);
				$statement->bindValue(':startDate', date('Y-m-d H:i:s', intdiv($row->startTime, 1000)));
				$statement->bindValue(':endDate', date('Y-m-d H:i:s', intdiv($row->endTime, 1000)));
				$statement->bindValue(':month', date('m', intdiv($row->endTime, 1000)));
				$statement->bindValue(':year', date('Y', intdiv($row->endTime, 1000)));
				$statement->bindValue(':quarter', 'Q' . intdiv(date('m', intdiv($row->endTime, 1000)) + 2, 3));
				$statement->bindValue(':deviceIp', $row->deviceIp);
				$statement->bindValue(':deviceName', $row->deviceName);
				$statement->bindValue(':sourceAddress', $row->sourceAddress);
				$statement->bindValue(':sourcePort', $row->sourcePort);
				$statement->bindValue(':destAddress', $row->destAddress);
				$statement->bindValue(':destPort', $row->destPort);
				$statement->bindValue(':protocol', $row->protocol);
				$statement->bindValue(':packetBandwidth', $row->packetBandwidth);
				$statement->bindValue(':packetCount', $row->packetCount);
				$statement->bindValue(':direction', $row->direction);
				$statement->bindValue(':geoLocation', $row->geoLocation);
				$statement->bindValue(':ruleName', $row->ruleName);
				$statement->bindValue(':category', $row->category);
				$statement->bindValue(':threatGroup', $row->threatGroup);
				$statement->bindValue(':startDayOfMonth', $row->startDayOfMonth);
				$statement->bindValue(':endDayOfMonth', $row->endDayOfMonth);
				$statement->bindValue(':protocolPort', $row->protocolPort);
				$statement->bindValue(':durationRange', $row->durationRange);
				$statement->bindValue(':averageAttackPacketRatePps', $row->averageAttackPacketRatePps);
				$statement->bindValue(':maxAttackPacketRatePps', $row->maxAttackPacketRatePps);
				$statement->bindValue(':averageAttackRateBps', $row->averageAttackRateBps);
				$statement->bindValue(':maxAttackRateBps', $row->maxAttackRateBps);
				$r = @$statement->execute();
				if ($r === false)
					die('========== CRITICAL ERROR: ' . $db->lastErrorMsg() . NL);
			}
			$r = $db->exec('COMMIT');
			if ($r === false)
				die('========== CRITICAL ERROR: ' . $db->lastErrorMsg() . NL);
		}
		fclose($handle);
		if ($lineCount == 0)
			print('WARNING: No lines have been processed on this compilation.' . NL);
	} else {
		print('ERROR: Cannot open input data file.' . NL);
	}
}

// Signal the module has been loaded
$globals->moduleLoaded = true;
