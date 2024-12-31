from requests import Session
import requests
import json
import os
import time
import sys
from datetime import datetime, timedelta
import calendar
import csv
import sqlite3

daily = False
monthly = False

cust_id = sys.argv[1]

try:
	if sys.argv[2].lower() =="monthly":
		monthly = True
	elif sys.argv[2].lower() =="daily":
		daily = True
except:
	print('Error: Second argument is not set. Second argument must be either "daily" (data collection for the previous day) or "monthly" (data collection for the previous month). Example:\r\n\r\n collector.py CUSTOMER_NAME monthly')
	sys.exit()

raw_data_path = f"./raw_data_files/{cust_id}/"
tmp_files_path = f"./tmp_files/{cust_id}/"
db_files_path = f"./database_files/{cust_id}/"

# Check if the directory exists, and create it if it doesn't
if not os.path.exists(raw_data_path):
    os.makedirs(raw_data_path)

if not os.path.exists(tmp_files_path):
    os.makedirs(tmp_files_path)

if not os.path.exists(db_files_path):
	os.makedirs(db_files_path)
	
################################# Extract variables from customers.json #########################################

try:
	customers_json_dic = json.loads(open("./config_files/customers.json", "r").read())
	selected_entry = next((entry for entry in customers_json_dic if entry.get("id") == cust_id), None)
	
	if selected_entry:
		username = customers_json_dic[0]['user']
		password = customers_json_dic[0]['pass']
		vision_ip = customers_json_dic[0]['visions'][0]['ip']
		excluded_attacks = customers_json_dic[0]['exclude']
		dps = customers_json_dic[0]['visions'][0]['dps']

		# Print the extracted values
		# print("User:", username)
		# print("Password:", password)
		# print("Visions IP:", vision_ip)

	else:
		print(f"No data found for ID: {cust_id}")

except json.JSONDecodeError as e:
	print("Error parsing JSON:", e)
except (KeyError, IndexError) as e:
	print("Error extracting data:", e)


customers_json = json.loads(open("./config_files/customers.json", "r").read())
for cust_config_block in customers_json:
	if cust_config_block['id'].lower() == cust_id.lower():
		defensepros = cust_config_block['defensepros']

		bw_units = cust_config_block['variables']['bwUnitDaily']
		#Can be configured "Gigabytes", "Terabytes" or "Megabytes"



class Vision:

	def __init__(self, vision_ip, username, password):
		self.ip = vision_ip
		self.login_data = {"username": username, "password": password}
		self.base_url = "https://" + vision_ip
		self.sess = Session()
		
		self.sess.headers.update({"Content-Type": "application/json"})
		self.login()
		print('Connecting to Vision')


		self.today_day_number = datetime.today().day
		self.today_month_number = datetime.today().month

		# self.today_day_number = 31
		self.start_time_lower, self.end_time_upper = self.generate_report_times(self.today_day_number)

		
		print('Collecting DefensePro device list')		
		self.device_list = self.get_device_list()

	def login(self):

		login_url = self.base_url + '/mgmt/system/user/login'
		try:
			r = self.sess.post(url=login_url, json=self.login_data, verify=False)
			r.raise_for_status()
			response = r.json()
		except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError,requests.exceptions.SSLError,requests.exceptions.Timeout,requests.exceptions.ConnectTimeout,requests.exceptions.ReadTimeout) as err:
			raise SystemExit(err)

		if response['status'] == 'ok':
			self.sess.headers.update({"JSESSIONID": response['jsessionid']})
			# print("Auth Cookie is:  " + response['jsessionid'])
		else:
			exit(1)


	def _post(self, URL, requestData = ""):
		try:
			r = self.sess.post(url=URL, verify=False, data=requestData)
		except any as err:
			raise err
		
		try:
			r.raise_for_status()
		except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError, requests.exceptions.SSLError,
			requests.exceptions.Timeout, requests.exceptions.ConnectTimeout,
			requests.exceptions.ReadTimeout) as err:
			raise err

		return r


	def generate_report_times(self,today_day_number):
		# Get current time
		now = datetime.now().replace(day=today_day_number)
	
		if daily:
			# Daily Report Time Variables
			# Yesterday's start time: 00:00:00
			yesterday_start = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
			start_time_lower = int(yesterday_start.timestamp())*1000

			# Yesterday's end time: 23:59:59
			yesterday_end = (now - timedelta(days=1)).replace(hour=23, minute=59, second=59, microsecond=0)
			end_time_upper = int(yesterday_end.timestamp())*1000

		if monthly:
			# Monthly Report Time Variables
			# First day of the previous month at 00:00:00
			first_day_of_prev_month = (now.replace(day=1) - timedelta(days=1)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
			start_time_lower = int(first_day_of_prev_month.timestamp())*1000

			# Last day of the previous month at 23:59:59
			last_day_of_prev_month = first_day_of_prev_month.replace(
				day=calendar.monthrange(first_day_of_prev_month.year, first_day_of_prev_month.month)[1],
				hour=23, minute=59, second=59, microsecond=0
			)
			end_time_upper = int(last_day_of_prev_month.timestamp())*1000

		# Return all variables
		return start_time_lower, end_time_upper
			
	def get_device_list(self):
		# Returns list of DP with mgmt IP, type, Name
		devices_url = self.base_url + '/mgmt/system/config/itemlist/alldevices'
		r = self.sess.get(url=devices_url, verify=False)
		json_txt = r.json()

		dev_list = {item['managementIp']: {'Type': item['type'], 'Name': item['name'],
			'Version': item['deviceVersion'], 'ormId': item['ormId']} for item in json_txt if item['type'] == "DefensePro"}
		
		with open(raw_data_path + 'full_dev_list.json', 'w') as full_dev_list_file:
			json.dump(dev_list,full_dev_list_file)

		return dev_list

################Traffic stats Bps######################
	def write_traffic_stats_to_csv(self,traffic_raw_response, filename):
		"""
		Parses the given response and writes the data to a CSV file, ensuring no overlapping timestamps.
		"""
		data = []

		type_traffic_utilization = False
		type_cps = False
		type_cec = False

		first_row = traffic_raw_response["data"][0]["row"]

		if "excluded" in first_row:
			type_traffic_utilization = True

		if "connectionPerSecond" in first_row:
			type_cps = True

		if "connectionsPerSecond" in first_row:
			type_cec = True

		# Extract new data from the JSON response
		for row in traffic_raw_response['data']:
			timestamp = int(row['row']['timeStamp'])
			if type_traffic_utilization:
				data.append({
					'Date': timestamp,
					'excluded': row['row']['excluded'],
					'discards': row['row']['discards'],
					'trafficValue': row['row']['trafficValue'],
					'challengeIng': row['row']['challengeIng']
				})
			elif type_cps:
				data.append({
					'Date': timestamp,
					'connectionPerSecond': row['row']['connectionPerSecond']
				})
			elif type_cec:
				data.append({
					'Date': timestamp,
					'connectionsPerSecond': row['row']['connectionsPerSecond']
				})

		# Read existing data from the CSV file
		if os.path.isfile(filename):
			with open(filename, 'r') as csvfile:
				reader = csv.DictReader(csvfile)
				existing_data = [row for row in reader]
		else:
			existing_data = []

		# Filter out rows from existing data that overlap with new data (based on year, month, day)
		existing_dates = {
			datetime.fromtimestamp(int(row['Date']) / 1000).date(): row
			for row in existing_data
		}
		new_dates = {
			datetime.fromtimestamp(item['Date'] / 1000).date(): item
			for item in data
		}

		for new_date in new_dates:
			if new_date in existing_dates:
				existing_data = [row for row in existing_data if datetime.fromtimestamp(int(row['Date']) / 1000).date() != new_date]

		# Append new data to existing data
		updated_data = existing_data + data

		################ Write to CSV #######################

		if daily:
			
			if self.today_day_number != 2:
				print('Daily clause day is not 2nd of the month')

				# Write the updated data back to the CSV file
				with open(filename, 'w', newline='') as csvfile:
					if type_traffic_utilization:
						fieldnames = ['Date', 'excluded', 'discards', 'trafficValue', 'challengeIng']
					elif type_cps:
						fieldnames = ['Date', 'connectionPerSecond']
					elif type_cec:
						fieldnames = ['Date', 'connectionsPerSecond']
						
					writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
					writer.writeheader()
					writer.writerows(updated_data)



			else:
				print('Daily clause day is 2nd of the month')
				# This will overwrite the data in the file
				with open(filename, 'w', newline='') as csvfile:
					if type_traffic_utilization:
						fieldnames = ['Date', 'excluded', 'discards', 'trafficValue', 'challengeIng']
					elif type_cps:
						fieldnames = ['Date', 'connectionPerSecond']
					elif type_cec:
						fieldnames = ['Date', 'connectionsPerSecond']

					writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

					writer.writeheader()
					writer.writerows(data)
					print (f'Created {filename}')

		else: # if monthly
			print('Monthly condition')
			# This will overwrite the data
			with open(filename, 'w', newline='') as csvfile:
				if type_traffic_utilization:
					fieldnames = ['Date', 'excluded', 'discards', 'trafficValue', 'challengeIng']
				elif type_cps:
					fieldnames = ['Date', 'connectionPerSecond']
				elif type_cec:
					fieldnames = ['Date', 'connectionsPerSecond']
				writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
				writer.writeheader()
				writer.writerows(data)
				print (f'Created {filename}')

	def ams_stats_dashboards_call(self, units="bps", uri = "/mgmt/vrm/monitoring/traffic/periodic/report"):

		api_url = f'https://{self.ip}' + uri
		data = {
			"direction": "Inbound",
			"timeInterval": {
				"from": v.start_time_lower,
				"to": v.end_time_upper
			},

		}
		if units and units != "cps" and units != "cec":
			data.update({"unit": units})
		print(data)
		response = self._post(api_url, json.dumps(data))
		if response.status_code == 200:
			print(
				f"Pulled traffic utilization. Time range: "
				f"{time.strftime('%d-%b-%Y %H:%M:%S', time.localtime(v.start_time_lower/1000))} - "
				f"{time.strftime('%d-%b-%Y %H:%M:%S', time.localtime(v.end_time_upper/1000))}"
			)
			
			try:
				response_json = response.json()
				with open(raw_data_path + f"traffic_{units}_raw.json", "w", encoding="utf-8") as json_file:
					json.dump(response_json, json_file, indent=4)  # Save JSON with indentation
				print(f"Response body saved as pretty JSON in traffic_{units}_raw.json")
				return response_json

			except json.JSONDecodeError:
				print("Response is not in JSON format, skipping JSON file save.")

			return response.json()
		
		else:
			error_message = (
				f"Error pulling attack rate data. Time range: "
				f"{time.strftime('%d-%b-%Y %H:%M:%S', time.localtime(v.start_time_lower/1000))} - "
				f"{time.strftime('%d-%b-%Y %H:%M:%S', time.localtime(v.end_time_upper/1000))}"
			)
			print(error_message)
			raise Exception(error_message)

	def get_cps(self):

		api_url = f'https://{self.ip}/mgmt/vrm/monitoring/traffic/cps'
		data = {
			"direction": "Inbound",
			"timeInterval": {
				"from": v.start_time_lower,
				"to": v.end_time_upper
			},

		}
		
		response = self._post(api_url, json.dumps(data))
		if response.status_code == 200:
			print(
				f"Pulled CPS stats. Time range: "
				f"{time.strftime('%d-%b-%Y %H:%M:%S', time.localtime(v.start_time_lower/1000))} - "
				f"{time.strftime('%d-%b-%Y %H:%M:%S', time.localtime(v.end_time_upper/1000))}"
			)
			
			try:
				response_json = response.json()
				with open(raw_data_path + "traffic_cps_raw.json", "w", encoding="utf-8") as json_file:
					json.dump(response_json, json_file, indent=4)  # Save JSON with indentation
				print("Response body saved as pretty JSON in traffic_bps_raw.json")

				# self.write_traffic_stats_bps_to_csv(response_json, tmp_files_path + f'cps.csv')

			except json.JSONDecodeError:
				print("Response is not in JSON format, skipping JSON file save.")

			return response.json()
		
		else:
			error_message = (
				f"Error pulling CPS stats data. Time range: "
				f"{time.strftime('%d-%b-%Y %H:%M:%S', time.localtime(v.start_time_lower/1000))} - "
				f"{time.strftime('%d-%b-%Y %H:%M:%S', time.localtime(v.end_time_upper/1000))}"
			)
			print(error_message)
			raise Exception(error_message)
		

	def create_forensics_post_payload(self):

		query = {
			"criteria": [],
			"pagination": {
				"page": 0,
				"size": 10000,
				"topHits": 10000
			}
		}


		# Create an "and" filter
		and_filters = {
			"type": "andFilter",
			"filters": []
		}

		# Date range filter
		time_filter = {
			"type": "timeFilter",
			"field": "endTime",
			"lower": f"{v.start_time_lower}",
			"upper": f"{v.end_time_upper}",
			"includeLower": True,
			"includeUpper": True
		}
		and_filters['filters'].append(time_filter)

		query['criteria'].append(and_filters)

		if excluded_attacks:
			exclude_array = excluded_attacks.split(',')
			for text in exclude_array:
				field, value = text.split(':')
				and_filters['filters'].append({
					"type": "termFilter",
					"field": field,
					"value": value,
					"inverseFilter": True
				})

		# Create an "or" filter for DefensePro IPs
		or_filters = {
			"type": "orFilter",
			"filters": []
		}

		if dps:
			dps_list = dps.split(',')
			for dp in dps_list:
				or_filters['filters'].append({
					"type": "termFilter",
					"field": "deviceIp",
					"value": dp
				})
		else:
			or_filters['filters'].append({
				"type": "termFilter",
				"field": "deviceIp",
				"value": "0.0.0.0",
				"inverseFilter": True
			})

		# Add "or" filters to query criteria
		query['criteria'].append(or_filters)
		return query

	def get_forensics(self):

		api_url = f'https://{self.ip}/mgmt/monitor/reporter/reports-ext/ATTACK'


		post_payload = self.create_forensics_post_payload()

		response = self._post(api_url, json.dumps(post_payload))
		if response.status_code == 200:
			print(
				f"Pulled forensics data. Time range: "
				f"{time.strftime('%d-%b-%Y %H:%M:%S', time.localtime(v.start_time_lower/1000))} - "
				f"{time.strftime('%d-%b-%Y %H:%M:%S', time.localtime(v.end_time_upper/1000))}"
			)
			
			try:
				response_json = response.json()
				with open(raw_data_path + "forensics_raw.json", "w", encoding="utf-8") as json_file:
					json.dump(response_json, json_file, indent=4)  # Save JSON with indentation
				print("Response body saved as pretty JSON in forensics_raw.json")



			except json.JSONDecodeError:
				print("Response is not in JSON format, skipping JSON file save.")

			return response.json()
		
		else:
			error_message = (
				f"Error pulling forensics data. Time range: "
				f"{time.strftime('%d-%b-%Y %H:%M:%S', time.localtime(v.start_time_lower/1000))} - "
				f"{time.strftime('%d-%b-%Y %H:%M:%S', time.localtime(v.end_time_upper/1000))}"
			)
			print(error_message)
			raise Exception(error_message)

	def compile_to_sqldb(self):

		db_file = db_files_path + f'database_{cust_id}_{self.today_month_number}.sqlite'

		print(db_file)
		
		if daily:
			if self.today_day_number != 2:
					# Connect to SQLite database (it will be created if it doesn't exist)
					conn = sqlite3.connect(db_file)
					cursor = conn.cursor()
					# Create table
					cursor.execute('''
						CREATE TABLE IF NOT EXISTS attacks (
							deviceIp TEXT NOT NULL,
							startDate DATE NOT NULL,
							endDate DATE NOT NULL,
							name TEXT NOT NULL,
							actionType TEXT NOT NULL,
							ruleName TEXT NOT NULL,
							sourceAddress TEXT NOT NULL,
							destAddress TEXT NOT NULL,
							sourcePort TEXT NOT NULL,
							destPort TEXT NOT NULL,
							protocol TEXT NOT NULL,
							threatGroup TEXT NOT NULL,
							category TEXT NOT NULL,
							attackIpsId TEXT NOT NULL
							actionType TEXT NOT NULL,
							status TEXT NOT NULL,
							risk TEXT NOT NULL,
							startTime INTEGER NOT NULL,
							endTime INTEGER NOT NULL,
							month INTEGER NOT NULL,
							year INTEGER NOT NULL,
							startDayOfMonth INTEGER NOT NULL,
							endDayOfMonth INTEGER NOT NULL,
							vlanTag TEXT NOT NULL,
							packetCount INTEGER NOT NULL,
							packetBandwidth INTEGER NOT NULL,
							averageAttackPacketRatePps INTEGER NOT NULL,
							averageAttackRateBps INTEGER NOT NULL,
							maxAttackRateBps INTEGER NOT NULL,
							maxAttackPacketRatePps INTEGER NOT NULL,
							lastPeriodBandwidth INTEGER NOT NULL,
							poId TEXT NOT NULL,
							duration INTEGER NOT NULL,
							radwareId TEXT NOT NULL,
							direction TEXT NOT NULL,
							geoLocation TEXT NOT NULL,
							activationId TEXT NOT NULL,
							packetType TEXT NOT NULL,
							physicalPort TEXT NOT NULL,
							lastPeriodPacketRate INTEGER NOT NULL,
							tierId TEXT NOT NULL,
						
					
						)
						''')
					
					# Clear the table content if the file already exists
					cursor.execute('DELETE FROM attacks')

					# Insert data into the table
					for entry in forensics_raw['data']:
						cursor.execute('''
						INSERT INTO attacks (name, attackIpsId)
						VALUES (?, ?)
						''', (entry["row"]["name"], entry["row"]["attackIpsId"]))

					#json.loads(entry["row"]["enrichmentContainer"]).get("geoLocation", {}).get("countryCode", None)

					# Commit changes and close the connection
					conn.commit()
					conn.close()

#   "deviceIp":"10.106.32.43",
#    "sourcePort":"53",
#    "vlanTag":"N/A",
#    "packetCount":"0",
#    "destMsisdn":"N/A",
#    "averageAttackPacketRatePps":"0",
#    "lastPeriodBandwidth":"0",
#    "poId":"N_A",
#    "duration":"15001",
#    "protocol":"UDP",
#    "destPort":"80",
#    "threatGroup":"DDoSGroup",
#    "destAddress":"184.151.230.247",
#    "ruleName":"HOC_New",
#    "radwareId":"1361",
#    "startTime":"1735595410317",
#    "trapVersion":"V8",
#    "direction":"In",
#    "averageAttackRateBps":"0",
#    "activationId":"N_A",
#    "maxAttackRateBps":"0",
#    "packetType":"Regular",
#    "mplsRd":"N/A",
#    "attackIpsId":"39-1734718136",
#    "sourceAddress":"80.237.21.61",
#    "srcMsisdn":"N/A",
#    "enrichmentContainer":"{\"destinationGeoLocation\":{\"countryCode\":\"CA\"},\"geoLocation\":{\"countryCode\":\"RU\"}}",
#    "physicalPort":"1",
#    "actionType":"Drop",
#    "lastPeriodPacketRate":"0",
#    "maxAttackPacketRatePps":"0",
#    "tierId":"N_A",
#    "packetBandwidth":"0",
#    "name":"DOSS-UDP-flood-80-Req",
#    "risk":"Medium",
#    "endTime":"1735595425318",
#    "category":"DOSShield",
#    "status":"Terminated"


	# If daily
		
		# if not 2nd
			# if file does not exists create new file append data
			# if file exists
				# read the file, check if entries for previous day exist, if yes, delete them and then paste new data
	# if 2nd, create new file

v = Vision(vision_ip, username, password)

# # Get AMS Traffic bandwidth BPS and write to csv
# traffic_bps_raw = v.ams_stats_dashboards_call(units = "bps")
# v.write_traffic_stats_to_csv(traffic_bps_raw, tmp_files_path + 'traffic_bps.csv')

# # Get AMS Traffic bandwidth PPS and write to csv
# traffic_pps_raw = v.ams_stats_dashboards_call(units = "pps")
# v.write_traffic_stats_to_csv(traffic_bps_raw, tmp_files_path + 'traffic_pps.csv')

# # Get Forensics data
forensics_raw = v.get_forensics()
v.compile_to_sqldb()

# # Get connections per second stats
# cps_raw = v.ams_stats_dashboards_call(units = "cps", uri = '/mgmt/vrm/monitoring/traffic/cps')

# v.write_traffic_stats_to_csv(cps_raw, tmp_files_path + 'traffic_cps.csv')

# #Get concurrent established connections stats
# cec_raw = v.ams_stats_dashboards_call(units = "cec", uri = '/mgmt/vrm/monitoring/traffic/concurrent-connections')
# v.write_traffic_stats_to_csv(cec_raw, tmp_files_path + 'traffic_cec.csv')



### To do ####

# 2. compile to sqldb
# 1. export to csv

# 3. test full cycle running python only