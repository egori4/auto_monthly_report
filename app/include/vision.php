<?php

# VERSION = '5.0.1'

// Functions to access Vision via REST API - Marcelo Dantas
// Use vision_login function below to obtain the JSESSIONID
// Then pass the JSESSIONID together with any further REST requests

$__jsessionid="";	// JSESSIONID to use for authenticated access

function encode($string)	// Some URL encoding for sending
{
	$entities = array('%21', '%2A', '%27', '%28', '%29', '%3B', '%3A', '%40', '%26', '%3D', '%2B', '%24', '%2C', '%2F', '%3F', '%25', '%23', '%5B', '%5D');
	$replacements = array('!', '*', "'", "(", ")", ";", ":", "@", "&", "=", "+", "$", ",", "/", "?", "%", "#", "[", "]");
	return(str_replace($entities, $replacements, rawurlencode($string)));
}

function rest($method, $service, $data="{}", $decode=true, $outFile=null)	// Executes a REST API call
{
	global $__jsessionid, $__useproxy, $__proxy;

	$service=encode($service);

	$header=array(
		"Accept: application/json",
		"Content-Type: application/json",
	);
	if($__jsessionid!="")
	{
		$header[]="Cookie: JSESSIONID=$__jsessionid";
		$header[]="JSESSIONID: $__jsessionid";
	}

	$handle = curl_init();
	curl_setopt($handle, CURLOPT_URL, $service);
	curl_setopt($handle, CURLOPT_HTTPHEADER, $header);
	curl_setopt($handle, CURLOPT_FOLLOWLOCATION, 1);
	if($outFile == null) {
		curl_setopt($handle, CURLOPT_RETURNTRANSFER, true);
	} else {
		curl_setopt($handle, CURLOPT_FILE, $outFile);
	}
	curl_setopt($handle, CURLOPT_SSL_VERIFYHOST, false);
	curl_setopt($handle, CURLOPT_SSL_VERIFYPEER, false);
	curl_setopt($handle, CURLOPT_TIMEOUT, 300);
	
	// Uses a proxy if needed
	if($__useproxy)
	{
		curl_setopt($handle, CURLOPT_PROXY, $__proxy);
	}
 
	switch($method) {
		case 'GET':
			break;
		case 'POST':
			curl_setopt($handle, CURLOPT_POST, true);
			curl_setopt($handle, CURLOPT_POSTFIELDS, $data);
			break;
		case 'PUT': 
			curl_setopt($handle, CURLOPT_CUSTOMREQUEST, 'PUT');
			curl_setopt($handle, CURLOPT_POSTFIELDS, $data);
			break;
		case 'DELETE':
			curl_setopt($handle, CURLOPT_CUSTOMREQUEST, 'DELETE');
			break;
	}
 
	$result = curl_exec($handle);

	if($result===FALSE)
	{
		echo("Error when executing REST call.\n");
		$code = curl_getinfo($handle, CURLINFO_HTTP_CODE);
		die("HTTP code: $code");
	}

	if($decode)
		$result = json_decode($result);

	return($result);
}

function stringscan($data)
{
	$pos = 0;
	$result = array();
	while ( ($line_end_pos = strpos($data, "\n", $pos)) !== false ) 
	{
		$line = substr($data, $pos, $line_end_pos - $pos);
		if(substr($line, 0, 15)=="rsIDSFilterName")
		{
			$name=explode("\"", $line)[2];
			$result[]=$name;
		}
		$pos = $line_end_pos + 2;
	}
	return($result);
}

function vision_login($vision, $username, $password)	// Logs in to Vision and sets the global JSESSIONID
{
	global $__jsessionid;

	$result="ok";
	$service="https://$vision/mgmt/system/user/login";
	$data=json_encode(array(
		"username"=>$username,
		"password"=>$password
		));
	$resp=rest("POST", $service, $data);
	if($resp->status=="ok")
	{
		$__jsessionid=$resp->jsessionid;
	} else {
		$result=$resp->message;
	}
	return($result);
}

function vision_organization($vision)	// Gets organization information from the Vision server
{
	$service="https://$vision/mgmt/system/config/tree/Organization";
	$resp=rest("GET", $service);
	return($resp);
}

function vision_getdevice($vision, $defensepro)	// Gets information about a device on Vision
{
	$service="https://$vision/mgmt/system/config/tree/device/byip/$defensepro";
	$resp=rest("GET", $service);
	return($resp);
}

function vision_lock($vision, $defensepro) // Attempts to lock a device on Vision
{
	$service="https://$vision/mgmt/system/config/tree/device/byip/$defensepro/lock";
	$resp=rest("POST", $service);
	return($resp);
}

function vision_unlock($vision, $defensepro) // Attempts to unlock a device on Vision
{
	$service="https://$vision/mgmt/system/config/tree/device/byip/$defensepro/unlock";
	$resp=rest("POST", $service);
	return($resp);
}

function vision_policies($vision, $defensepro)	// Gets all policies from a DefensePro
{
	$service="https://$vision/mgmt/device/byip/$defensepro/config/rsIDSNewRulesTable";
	$resp=rest("GET", $service);
	return($resp);
}

function vision_user_signatures($vision, $defensepro)	// Gets all policies from a DefensePro
{
	$service="https://$vision/mgmt/device/byip/$defensepro/config/rsIDSAsAttackTable?filter=rsIDSAsAttackSourceType:3&filtertype=exact&filterRange=3000&count=3000&props=rsIDSAsAttackSourceType,rsIDSAsAttackId,rsIDSAsAttackName";
	$resp=rest("GET", $service);
	return($resp);
}

function vision_update($vision, $defensepro)	// Updates policies
{
	global $__update_wait;
	$service="https://$vision/mgmt/device/byip/$defensepro/config/updatepolicies?";
	$resp=rest("POST", $service);

	sleep($__update_wait);

	return($resp);
}

// Functions to deploy DP configuration via Vision

function deploy_attribute($vision, $defensepro, $policyname)	// Deploy a new attribute
{
	global $__prefix;

	$name=$__prefix.$policyname;

	$service="https://$vision/mgmt/device/byip/$defensepro/config/rsIDSSignaturesAttributesTable/Threat Type/$name";
	$data=json_encode(array(
		"rsIDSSignaturesAttributeType"=>"Threat Type",
		"rsIDSSignaturesAttributeName"=>$name
		));
	$resp=rest("POST", $service, $data);
}

function delete_attribute($vision, $defensepro, $policyname)	// Delete an attribute
{
	global $__prefix;

	$name=$__prefix.$policyname;

	$service="https://$vision/mgmt/device/byip/$defensepro/config/rsIDSSignaturesAttributesTable/Threat Type/$name";
	$resp=rest("DELETE", $service);
}

function deploy_profile($vision, $defensepro, $policyname)	// Deploy a new profile
{
	global $__prefix;

	$name=$__prefix.$policyname;

	$service="https://$vision/mgmt/device/byip/$defensepro/config/rsIDSSignaturesProfilesTable/$name/Rule 1/Threat Type/$name";
	$data=json_encode(array(
		"rsIDSSignaturesProfileName"=>$name,
		"rsIDSSignaturesProfileRuleName"=>"Rule 1",
		"rsIDSSignaturesProfileRuleAttributeType"=>"Threat Type",
		"rsIDSSignaturesProfileRuleAttributeName"=>$name
		));
	$resp=rest("POST", $service, $data);

	// Identify the attributes currently present on the policy
	$service="https://$vision/mgmt/device/byip/$defensepro/config/rsIDSNewRulesTable/$policyname";
	$resp=rest("GET", $service)->rsIDSNewRulesTable[0];

	$previous=trim($resp->rsIDSNewRulesProfileAppsec);
	if($previous=="" or $previous==$name)
	{
		// do nothing
	} else {
		// merge the previous attributes onto the new one
		$service="https://$vision/mgmt/device/byip/$defensepro/config/rsIDSSignaturesProfilesTable/$previous";
		$resp=rest("GET", $service)->rsIDSSignaturesProfilesTable;
		foreach($resp as $attribute)
		{
			$type=$attribute->rsIDSSignaturesProfileRuleAttributeType;
			$value=$attribute->rsIDSSignaturesProfileRuleAttributeName;
			$service="https://$vision/mgmt/device/byip/$defensepro/config/rsIDSSignaturesProfilesTable/$name/Rule 1/$type/$value";
			$data=json_encode(array(
				"rsIDSSignaturesProfileName"=>$name,
				"rsIDSSignaturesProfileRuleName"=>"Rule 1",
				"rsIDSSignaturesProfileRuleAttributeType"=>$type,
				"rsIDSSignaturesProfileRuleAttributeName"=>$value
				));
			rest("POST", $service, $data);
		}
	}
}

function delete_profile($vision, $defensepro, $policyname)	// Remove a custom profile
{
	global $__prefix;

	$name=$__prefix.$policyname;

	$service="https://$vision/mgmt/device/byip/$defensepro/config/rsIDSSignaturesProfilesTable/$name";
	$resp=rest("GET", $service)->rsIDSSignaturesProfilesTable;
	foreach($resp as $attribute)
	{
		$type=$attribute->rsIDSSignaturesProfileRuleAttributeType;
		$value=$attribute->rsIDSSignaturesProfileRuleAttributeName;
		$service="https://$vision/mgmt/device/byip/$defensepro/config/rsIDSSignaturesProfilesTable/$name/Rule 1/$type/$value";
		rest("DELETE", $service);
	}
}

function change_policy($vision, $defensepro, $policyname, $profile)	// Changes the current profile on a policy
{
	$service="https://$vision/mgmt/device/byip/$defensepro/config/rsIDSNewRulesTable/$policyname";
	$data=json_encode(array(
		"rsIDSNewRulesName"=>$policyname,
		"rsIDSNewRulesProfileAppsecThree"=>$profile
		));
	rest("PUT", $service, $data);
}

function deploy_filter($vision, $defensepro, $signature, $buffer)	// Deploy a filter set (basic/advanced)
{

	$array=StoA($buffer);

	eval("$".$array[2].";");
	eval("$".$array[3].";");
  eval("$".$array[4].";");
	eval("$".strtr($array[5], "-", "_").";");

	$name=str_replace("{signature}", $signature, $name);
	$filter=str_replace("{signature}", $signature, $filter);

	// Deploy a basic filter
  if(isset($proto))
  {
    switch($proto)
    {
      case "tcp":
        $proto_id = 2;
        break;
      case "udp":
        $proto_id = 3;
        break;
      case "icmp":
        $proto_id = 4;
        break;
      default:
        $proto_id = 1;
    }
  } else {
    $proto_id = 1;
  }

	$service="https://$vision/mgmt/device/byip/$defensepro/config/rsIDSFilterEntryTable/$name";
	$part1=array(
		"rsIDSFilterName"=>$name,
		"rsIDSFilterProtocol"=>$proto_id, // ip
  );
	
	if(isset($checksum))
	{
		$part2=array(
			"rsIDSFilterOMPCOffset"=>"10",
			"rsIDSFilterOMPCMask"=>"ffff0000",
			"rsIDSFilterOMPCPattern"=>tohex4($checksum)."0000",
			"rsIDSFilterOMPCCondition"=>"2", // Equal
			"rsIDSFilterOMPCLength"=>"2",
			"rsIDSFilterOMPCOffsetBase"=>"2" // IP Header
			);
	}
	if(isset($id_number))
	{
		$part2=array(
			"rsIDSFilterOMPCOffset"=>"4",
			"rsIDSFilterOMPCMask"=>"ffff0000",
			"rsIDSFilterOMPCPattern"=>tohex4($id_number)."0000",
			"rsIDSFilterOMPCCondition"=>"2", // Equal
			"rsIDSFilterOMPCLength"=>"2",
			"rsIDSFilterOMPCOffsetBase"=>"2" // IP Header
			);
	}
	if(isset($message_type))
	{
		$part2=array(
			"rsIDSFilterOMPCOffset"=>"0",
			"rsIDSFilterOMPCMask"=>"ff000000",
			"rsIDSFilterOMPCPattern"=>tohex2($message_type)."000000",
			"rsIDSFilterOMPCCondition"=>"2", // Equal
			"rsIDSFilterOMPCLength"=>"1",
			"rsIDSFilterOMPCOffsetBase"=>"6" // L4 Header
			);
	}
	if(isset($fragment))
	{
		$part2=array(
			"rsIDSFilterOMPCOffset"=>"6",
			"rsIDSFilterOMPCMask"=>"20000000",
			"rsIDSFilterOMPCPattern"=>"20000000",
			"rsIDSFilterOMPCCondition"=>"2", // Equal
			"rsIDSFilterOMPCLength"=>"1",
			"rsIDSFilterOMPCOffsetBase"=>"2" // IP Header
			);
	}
	if(isset($fragment_offset))
	{
		$part2=array(
			"rsIDSFilterOMPCOffset"=>"6",
			"rsIDSFilterOMPCMask"=>"1fff0000",
			"rsIDSFilterOMPCPattern"=>tohex4($fragment_offset)."0000",
			"rsIDSFilterOMPCCondition"=>"2", // Equal
			"rsIDSFilterOMPCLength"=>"2",
			"rsIDSFilterOMPCOffsetBase"=>"2" // IP Header
			);
	}
	if(isset($tos))
	{
		$part2=array(
			"rsIDSFilterOMPCOffset"=>"1",
			"rsIDSFilterOMPCMask"=>"ff000000",
			"rsIDSFilterOMPCPattern"=>tohex2($tos)."000000",
			"rsIDSFilterOMPCCondition"=>"2", // Equal
			"rsIDSFilterOMPCLength"=>"1",
			"rsIDSFilterOMPCOffsetBase"=>"2" // IP Header
			);
	}
	if(isset($ttl))
	{
		$part2=array(
			"rsIDSFilterOMPCOffset"=>"8",
			"rsIDSFilterOMPCMask"=>"ff000000",
			"rsIDSFilterOMPCPattern"=>tohex2($ttl)."000000",
			"rsIDSFilterOMPCCondition"=>"2", // Equal
			"rsIDSFilterOMPCLength"=>"1",
			"rsIDSFilterOMPCOffsetBase"=>"2" // IP Header
			);
	}
	if(isset($source_ip))
	{
		$part2=array(
			"rsIDSFilterOMPCOffset"=>"12",
			"rsIDSFilterOMPCMask"=>"ffffffff",
			"rsIDSFilterOMPCPattern"=>tohex8($source_ip),
			"rsIDSFilterOMPCCondition"=>"2", // Equal
			"rsIDSFilterOMPCLength"=>"4",
			"rsIDSFilterOMPCOffsetBase"=>"2" // IP Header
			);
	}
	if(isset($destination_ip))
	{
		$part2=array(
			"rsIDSFilterOMPCOffset"=>"16",
			"rsIDSFilterOMPCMask"=>"ffffffff",
			"rsIDSFilterOMPCPattern"=>tohex8($destination_ip),
			"rsIDSFilterOMPCCondition"=>"2", // Equal
			"rsIDSFilterOMPCLength"=>"4",
			"rsIDSFilterOMPCOffsetBase"=>"2" // IP Header
			);
	}
	if(isset($source_port))
	{
		$part2=array(
			"rsIDSFilterOMPCOffset"=>"0",
			"rsIDSFilterOMPCMask"=>"ffff0000",
			"rsIDSFilterOMPCPattern"=>tohex4($source_port)."0000",
			"rsIDSFilterOMPCCondition"=>"2", // Equal
			"rsIDSFilterOMPCLength"=>"2",
			"rsIDSFilterOMPCOffsetBase"=>"6" // L4 Header
			);
	}
	if(isset($destination_port))
	{
		$part2=array(
			"rsIDSFilterOMPCOffset"=>"0",
			"rsIDSFilterOMPCMask"=>"0000ffff",
			"rsIDSFilterOMPCPattern"=>"0000".tohex4($destination_port),
			"rsIDSFilterOMPCCondition"=>"2", // Equal
			"rsIDSFilterOMPCLength"=>"2",
			"rsIDSFilterOMPCOffsetBase"=>"6" // L4 Header
			);
	}
	if(isset($sequence_number))
	{
		$part2=array(
			"rsIDSFilterOMPCOffset"=>"4",
			"rsIDSFilterOMPCMask"=>"ffffffff",
			"rsIDSFilterOMPCPattern"=>tohex8($sequence_number),
			"rsIDSFilterOMPCCondition"=>"2", // Equal
			"rsIDSFilterOMPCLength"=>"4",
			"rsIDSFilterOMPCOffsetBase"=>"6" // L4 Header
			);
	}
	if(isset($packet_size))
	{
		$part2=array(
			"rsIDSFilterPacketSizeType"=>"1",
			"rsIDSFilterPacketSizeRange"=>$packet_size-14,

			);
	}

	if(!isset($part2))
		die("Undefined filter type.\n");

	$data=json_encode(array_merge($part1, $part2));
	$resp=rest("POST", $service, $data);

	// Deploy an advanced filter
	$service="https://$vision/mgmt/device/byip/$defensepro/config/rsIDSAdvancedFilterTable/$filter/$name";
	$data=json_encode(array(
		"rsIDSAdvancedFilterEntryName"=>$filter,
		"rsIDSAdvancedFilterEntryBasicName"=>$name,
		"rsIDSAdvancedFilterEntryType"=>"3"
		));
	$resp=rest("POST", $service, $data);
}

function delete_advanced_filters($vision, $defensepro, $signature)
{
	global $__prefix, $__fprefix;

	$service="https://$vision/mgmt/device/byip/$defensepro/config/rsIDSAdvancedFilterTable";
	$resp=rest("GET", $service)->rsIDSAdvancedFilterTable;

	$name="$__fprefix$__prefix$signature-";
	$size=strlen($name);
	foreach($resp as $entry)
	{
		if(substr($entry->rsIDSAdvancedFilterEntryName, 0, $size)==$name)
		{
			$filter=$entry->rsIDSAdvancedFilterEntryName;
			$basic=$entry->rsIDSAdvancedFilterEntryBasicName;
			$service="https://$vision/mgmt/device/byip/$defensepro/config/rsIDSAdvancedFilterTable/$filter/$basic";
			$resp=rest("DELETE", $service);
		}
	}
}

function delete_basic_filters($vision, $defensepro, $signature)
{
	global $__prefix;

	$service="https://$vision/mgmt/device/byip/$defensepro/config/rsIDSFilterEntryTable";
	$resp=stringscan(rest("GET", $service, "{}", false));
	

	$name="$__prefix$signature-";
	$size=strlen($name);
	foreach($resp as $filter)
	{
		if(substr($filter, 0, $size)==$name)
		{
			$service="https://$vision/mgmt/device/byip/$defensepro/config/rsIDSFilterEntryTable/$filter";
			$resp=rest("DELETE", $service);
		}
	}
}

function deploy_attack($vision, $defensepro, $signature, $policy, $buffer)	// Deploy an attack signature
{
	$array=StoA($buffer);

	eval("$".$array[2].";");
	eval("$".$array[3].";");
	eval("$".$array[4].";");

	$name=str_replace("{signature}", $signature, $name);
	$filter=str_replace("{signature}", $signature, $filter);
	$attribute=str_replace("{policy}", $policy, $attribute);

	// Get the next available attack ID
	$service="https://$vision/mgmt/device/byip/$defensepro/config?prop=rsIDSASAttackNextID";
	$resp=rest("GET", $service);
	$id=$resp->rsIDSASAttackNextID;

	// Deploy the attack signature
	$service="https://$vision/mgmt/device/byip/$defensepro/config/rsIDSAsAttackTable/$id";
	$data=json_encode(array(
		"rsIDSAsAttackName"=>$name,
		"rsIDSAsAttackId"=>$id,
		"rsIDSAsAttackServiceName"=>$filter,
		"rsIDSAsAttackTrackingType"=>"20",
		"rsIDSAsAttackThreshold"=>"0",
		"rsIDSAsAttackDropThreshold"=>"0",
		"rsIDSAsAttackTermThreshold"=>"0",
		));
	$resp=rest("POST", $service, $data);

	// Associate the attack to the profile using the attribute
	$service="https://$vision/mgmt/device/byip/$defensepro/config/rsIDSSignaturesAttackAttributesTable/$id/Threat Type/$attribute";
	$data=json_encode(array(
		"rsIDSSignaturesAttackAttributeType"=>"Threat Type",
		"rsIDSSignaturesAttackAttributeName"=>$attribute,
		"rsIDSSignaturesAttackAttributeAttackId"=>$id
		));
	$resp=rest("POST", $service, $data);

	// Remove unecessary associations, so only Threat Type remains
	$service="https://$vision/mgmt/device/byip/$defensepro/config/rsIDSSignaturesAttackAttributesTable/$id/Risk/Low";
	$resp=rest("DELETE", $service);
	$service="https://$vision/mgmt/device/byip/$defensepro/config/rsIDSSignaturesAttackAttributesTable/$id/Confidence/Medium";
	$resp=rest("DELETE", $service);
}

function delete_attacks($vision, $defensepro, $signature)
{
	global $__prefix;

	$signatures=vision_user_signatures($vision, $defensepro)->rsIDSAsAttackTable;
	$name="$__prefix$signature-";
	$size=strlen($name);
	foreach($signatures as $attack)
	{
		if(substr($attack->rsIDSAsAttackName, 0, $size)==$name)
		{
			$id=$attack->rsIDSAsAttackId;
			$service="https://$vision/mgmt/device/byip/$defensepro/config/rsIDSAsAttackTable/$id";
			$resp=rest("DELETE", $service);
		}
	}
}

?>