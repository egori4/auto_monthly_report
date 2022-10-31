import requests
import json
import os

raw_data_path = "./script_files/AbuseIPDB/Raw Data/"



aipdb_dict = {}
aipdb_dict['Src IP details'] = []

def AbuseIPDBCallEvents(ipAddress):
	
	url = 'https://api.abuseipdb.com/api/v2/check'

	querystring = {
		'ipAddress': ipAddress,
		'maxAgeInDays': '90'
	}

	headers = {
		'Accept': 'application/json',
		'Key': '1331ffc49bbd5c9f4ebdbea55e0e8c3f98e91fa8a43cb6c675c3f5ba324fbb3f790db5849fe84131'
	}

	response = requests.request(method='GET', url=url, headers=headers, params=querystring)

	# Formatted output
	decodedResponse = json.loads(response.text)
	# print(json.dumps(decodedResponse, sort_keys=True, indent=4))

	aipdb_dict['Src IP details'].append(decodedResponse)

	with open(raw_data_path + 'AbuseIPDBEvts.json', 'w') as outfile:
		json.dump(aipdb_dict,outfile)

def AbuseIPDBCallBw(ipAddress):
	
	url = 'https://api.abuseipdb.com/api/v2/check'

	querystring = {
		'ipAddress': ipAddress,
		'maxAgeInDays': '90'
	}

	headers = {
		'Accept': 'application/json',
		'Key': '1331ffc49bbd5c9f4ebdbea55e0e8c3f98e91fa8a43cb6c675c3f5ba324fbb3f790db5849fe84131'
	}

	response = requests.request(method='GET', url=url, headers=headers, params=querystring)

	# Formatted output
	decodedResponse = json.loads(response.text)
	# print(json.dumps(decodedResponse, sort_keys=True, indent=4))

	aipdb_dict['Src IP details'].append(decodedResponse)

	with open(raw_data_path + 'AbuseIPDBBw.json', 'w') as outfile:
		json.dump(aipdb_dict,outfile)


def AbuseIPDBCallPkt(ipAddress):
	
	url = 'https://api.abuseipdb.com/api/v2/check'

	querystring = {
		'ipAddress': ipAddress,
		'maxAgeInDays': '90'
	}

	headers = {
		'Accept': 'application/json',
		'Key': '1331ffc49bbd5c9f4ebdbea55e0e8c3f98e91fa8a43cb6c675c3f5ba324fbb3f790db5849fe84131'
	}

	response = requests.request(method='GET', url=url, headers=headers, params=querystring)

	# Formatted output
	decodedResponse = json.loads(response.text)
	# print(json.dumps(decodedResponse, sort_keys=True, indent=4))

	aipdb_dict['Src IP details'].append(decodedResponse)

	with open(raw_data_path + 'AbuseIPDBPkts.json', 'w') as outfile:
		json.dump(aipdb_dict,outfile)