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

		# To manipulate the desired date, replace day = 1 with the desired day or month with desired month , e.g self.today_date = datetime.today().replace(month=2) )
		self.today_date = datetime.today()#.replace(month=2)
		print(f'Today date is {self.today_date}')

		self.today_day_number = self.today_date.day

		self.previous_day_number = (self.today_date - timedelta(days=1)).day

		# print(f'Today is {self.today_day_number} and yesterday was {self.previous_day_number}')

		self.today_month_number = self.today_date.month
		self.today_year = self.today_date.year

		self.start_time_lower, self.end_time_upper = self.generate_report_times(self.today_date)

		
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


	def generate_report_times(self,today_date):
		# Get current time
		
	
		if daily:
			# Daily Report Time Variables
			# Yesterday's start time: 00:00:00
			yesterday_start = (today_date - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
			start_time_lower = int(yesterday_start.timestamp())*1000

			# Yesterday's end time: 23:59:59
			yesterday_end = (today_date - timedelta(days=1)).replace(hour=23, minute=59, second=59, microsecond=0)
			end_time_upper = int(yesterday_end.timestamp())*1000

		if monthly:
			# Monthly Report Time Variables
			# First day of the previous month at 00:00:00
			first_day_of_prev_month = (today_date.replace(day=1) - timedelta(days=1)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
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
					'trafficValue': row['row']['trafficValue'],
					'discards': row['row']['discards'],
					'challengeIng': row['row']['challengeIng'],
					'excluded': row['row']['excluded']

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
						fieldnames = ['Date', 'trafficValue','discards','challengeIng','excluded']
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
						fieldnames = ['Date', 'trafficValue','discards','challengeIng','excluded']
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
					fieldnames = ['Date', 'trafficValue','discards','challengeIng','excluded']
				elif type_cps:
					fieldnames = ['Date', 'connectionPerSecond']
				elif type_cec:
					fieldnames = ['Date', 'connectionsPerSecond']
				writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
				writer.writeheader()
				writer.writerows(data)
				print (f'Created {filename}')

	def ams_stats_dashboards_call(self, units="bps", uri = "/mgmt/vrm/monitoring/traffic/periodic/report", report_type="AMS Dasboard"):

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
		response = self._post(api_url, json.dumps(data))
		if response.status_code == 200:
			print(
				f"Pulled {report_type} data. Time range: "
				f"{time.strftime('%d-%b-%Y %H:%M:%S', time.localtime(v.start_time_lower/1000))} - "
				f"{time.strftime('%d-%b-%Y %H:%M:%S', time.localtime(v.end_time_upper/1000))}"
			)
			
			try:
				response_json = response.json()

				# If Null in rows, filter out these rows

				filtered_response_json = {
					"metaData": response_json["metaData"],
					"data": [
						row for row in response_json["data"] 
						if not any(value is None for value in row["row"].values())
					],
					"dataMap": response_json["dataMap"]
				}

				with open(raw_data_path + f"traffic_{units}_raw.json", "w", encoding="utf-8") as json_file:
					json.dump(filtered_response_json, json_file, indent=4)  # Save JSON with indentation
				print(f"Response body saved as pretty JSON in traffic_{units}_raw.json")
				return filtered_response_json

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

		print(
		f"Pulling forensics data. Time range: "
		f"{time.strftime('%d-%b-%Y %H:%M:%S', time.localtime(v.start_time_lower/1000))} - "
		f"{time.strftime('%d-%b-%Y %H:%M:%S', time.localtime(v.end_time_upper/1000))}"
			)
		
		api_url = f'https://{self.ip}/mgmt/monitor/reporter/reports-ext/ATTACK'


		post_payload = self.create_forensics_post_payload()
		current_page = 0
		total_hits = 0
		all_data = []
		metaData = None  # To store metaData from the first response
	

		while True:
			post_payload["pagination"]["page"] = current_page
			response = self._post(api_url, json.dumps(post_payload))


			if response.status_code == 200:

				try:
					response_json = response.json()
					if "data" in response_json:
						all_data.extend(response_json["data"])  # Append the current page's data
						if not metaData:
							metaData = response_json.get("metaData", {})  # Get metaData only once
						total_hits += len(response_json["data"])

						# Stop if the current page has fewer results than the page size
						if len(response_json["data"]) < post_payload["pagination"]["size"]:
							break  # No more data to fetch
						
						current_page += 1  # Move to the next page


					else:
						print(f"No data in the response")
						break

				except json.JSONDecodeError:
					print("Response is not in JSON format, skipping JSON file save.")

			
			else:
				error_message = (
					f"Error pulling forensics data. Time range: "
					f"{time.strftime('%d-%b-%Y %H:%M:%S', time.localtime(v.start_time_lower/1000))} - "
					f"{time.strftime('%d-%b-%Y %H:%M:%S', time.localtime(v.end_time_upper/1000))}"
				)
				print(error_message)
				raise Exception(error_message)

		final_response = {
			"data": all_data,
			"metaData": metaData or {"totalHits": total_hits}
		}
	
		with open(raw_data_path + "forensics_raw.json", "w", encoding="utf-8") as json_file:
			json.dump(final_response, json_file, indent=4)  # Save JSON with indentation
		print("Response body saved as pretty JSON in forensics_raw.json")
		return final_response
	
	def compile_to_sqldb(self):
		

		
		if daily:

			if self.today_day_number == 1 and self.today_month_number != 1: # This is a case for not Jan 1st
				db_file = db_files_path + f'database_{cust_id}_{self.today_month_number -1:02}_{self.today_year}.sqlite'
				print(db_file)


			elif self.today_day_number == 1 and self.today_month_number == 1: # This is a case for  Jan 1st
				db_file = db_files_path + f'database_{cust_id}_{12}_{self.today_year -1:02}.sqlite'
				print(db_file)

			else:
				db_file = db_files_path + f'database_{cust_id}_{self.today_month_number:02}_{self.today_year}.sqlite'
				print(db_file)
			
			
					
			# Connect to SQLite database (it will be created if it doesn't exist)
			conn = sqlite3.connect(db_file)
			cursor = conn.cursor()
			# Create table
			cursor.execute('''
				CREATE TABLE IF NOT EXISTS attacks (
					deviceName TEXT NOT NULL,
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
					attackIpsId TEXT NOT NULL,
					status TEXT NOT NULL,
					duration INTEGER NOT NULL,
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
					radwareId TEXT NOT NULL,
					direction TEXT NOT NULL,
					geoLocation TEXT NOT NULL,
					activationId TEXT NOT NULL,
					packetType TEXT NOT NULL,
					physicalPort TEXT NOT NULL,
					lastPeriodPacketRate INTEGER NOT NULL,
				  	originalStartDate DATE NOT NULL)
				''')
			
			if self.today_day_number == 1 and self.today_month_number == 1: # This is a case for  Jan 1st
				# Clear the table content for the previous day
				cursor.execute('DELETE FROM attacks where month = ? and startDayOfMonth = ?', (12, 31))
			
			elif self.today_day_number == 1 and self.today_month_number != 1: # This is a case for 1st of the month, but not January month
				# Clear the table content for the previous day
				cursor.execute('DELETE FROM attacks where month = ? and startDayOfMonth = ?', (self.today_month_number -1, self.previous_day_number ))
			else:
				# Clear the table content for the previous day
				cursor.execute('DELETE FROM attacks where month = ? and startDayOfMonth = ?', (self.today_month_number, self.previous_day_number))


			# Insert data into the table
			for entry in forensics_raw['data']:

				start_date = datetime.fromtimestamp(int(entry["row"]["startTime"])/ 1000)
				orig_start_date = start_date
				end_date = datetime.fromtimestamp(int(entry["row"]["endTime"])/ 1000)
				
				if self.today_day_number == 2:
					if start_date.day == (self.today_date - timedelta(days=2)).day: # This is a case when the attack started in the day before yesterday day and continued to yesterday
						print(f'Attack started in the day before yesterday ({start_date}) day and continued to yesterday')
						
						if self.today_month_number !=1 : # This is a case for 2nd of the month, but not January month
							start_date = start_date.replace(day= 1, hour=0, minute=0, second=0)
							# print(f'New start date: {start_date}')
						else: # This is a case for 2nd of January
							start_date = start_date.replace(day= 1, month=1,year=self.today_year, hour=0, minute=0, second=0)
							# print(f'New start date: {start_date}')
					



				cursor.execute('''
				INSERT INTO attacks (deviceName, startDate, endDate, name, actionType, ruleName, sourceAddress, destAddress, sourcePort, destPort, protocol, threatGroup, category, attackIpsId, status, duration, risk, startTime, endTime, month, year, startDayOfMonth, endDayOfMonth, vlanTag, packetCount, packetBandwidth, averageAttackPacketRatePps, averageAttackRateBps, maxAttackRateBps, maxAttackPacketRatePps, lastPeriodBandwidth, poId, radwareId, direction, geoLocation, activationId, packetType, physicalPort, lastPeriodPacketRate, originalStartDate)
				VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
				''', (
					entry["row"]["deviceIp"], 
					start_date.strftime('%Y-%m-%d %H:%M:%S'), 
					end_date.strftime('%Y-%m-%d %H:%M:%S'), 
					entry["row"]["name"], 
					entry["row"]["actionType"], 
					entry["row"]["ruleName"], 
					entry["row"]["sourceAddress"], 
					entry["row"]["destAddress"], 
					entry["row"]["sourcePort"], 
					entry["row"]["destPort"], 
					entry["row"]["protocol"], 
					entry["row"]["threatGroup"], 
					entry["row"]["category"], 
					entry["row"]["attackIpsId"], 
					entry["row"]["status"], 
					entry["row"]["duration"], 
					entry["row"]["risk"], 
					entry["row"]["startTime"], 
					entry["row"]["endTime"], 
					end_date.month,
					end_date.year,
					start_date.day, 
					end_date.day, 
					entry["row"]["vlanTag"], 
					entry["row"]["packetCount"], 
					entry["row"]["packetBandwidth"], 
					entry["row"]["averageAttackPacketRatePps"], 
					entry["row"]["averageAttackRateBps"], 
					entry["row"]["maxAttackRateBps"], 
					entry["row"]["maxAttackPacketRatePps"], 
					entry["row"]["lastPeriodBandwidth"], 
					entry["row"]["poId"], 
					entry["row"]["radwareId"], 
					entry["row"]["direction"], 
					json.loads(entry["row"]["enrichmentContainer"]).get("geoLocation", {}).get("countryCode", None), 
					entry["row"]["activationId"], 
					entry["row"]["packetType"], 
					entry["row"]["physicalPort"], 
					entry["row"]["lastPeriodPacketRate"],
					orig_start_date.strftime('%Y-%m-%d %H:%M:%S')
					))
			# Commit changes and close the connection
			conn.commit()
			conn.close()

		if monthly:
			if self.today_month_number != 1: # This is a case for not Jan month
				db_file = db_files_path + f'database_{cust_id}_{self.today_month_number -1:02}_{self.today_year}.sqlite'
				print(db_file)


			else: # This is a case for  Jan month
				db_file = db_files_path + f'database_{cust_id}_{12}_{self.today_year -1}.sqlite'
				print(db_file)

					
			# Connect to SQLite database (it will be created if it doesn't exist)
			conn = sqlite3.connect(db_file)
			cursor = conn.cursor()
			# Create table
			cursor.execute('''
				CREATE TABLE IF NOT EXISTS attacks (
					deviceName TEXT NOT NULL,
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
					attackIpsId TEXT NOT NULL,
					status TEXT NOT NULL,
					duration INTEGER NOT NULL,
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
					radwareId TEXT NOT NULL,
					direction TEXT NOT NULL,
					geoLocation TEXT NOT NULL,
					activationId TEXT NOT NULL,
					packetType TEXT NOT NULL,
					physicalPort TEXT NOT NULL,
					lastPeriodPacketRate INTEGER NOT NULL,
				  	originalStartDate DATE NOT NULL)
				''')
			
			print(self.today_month_number)

			if self.today_month_number != 1: # This is a case for not January month
				# Clear the table content for the previous month
				cursor.execute(f'DELETE FROM attacks where month = {self.today_month_number -1}')


			else: # This is a case for  Jan 1st
				# Clear the table content for the previous month (December)
				cursor.execute('DELETE FROM attacks where month = 12')

			# Insert data into the table
			for entry in forensics_raw['data']:

				start_date = datetime.fromtimestamp(int(entry["row"]["startTime"])/ 1000)
				orig_start_date = start_date
				end_date = datetime.fromtimestamp(int(entry["row"]["endTime"])/ 1000)
				
								# Calculate the month and year 2 months ago
				if self.today_month_number > 2:
					two_months_ago_month = self.today_month_number - 2
				else:
					two_months_ago_month = self.today_month_number + 10  # Wrap around (12 months in a year)
				
				if start_date.month == two_months_ago_month: # This is a case when the attack started in the last day of the month before last month and continued to the first day of the last month
					print(f'Attack started in the last day of the month before last month and continued to the first day of the last month ({start_date})')
					
					if self.today_month_number !=1 : # This is a case for 2nd of the month, but not January month
						start_date = start_date.replace(day= 1, month=self.today_month_number-1, hour=0, minute=0, second=0)
						# print(f'New start date: {start_date}')
					else: # This is a case for 2nd of January
						start_date = start_date.replace(day= 1, month=12, hour=0, minute=0, second=0)
						# print(f'New start date: {start_date}')

				cursor.execute('''
				INSERT INTO attacks (deviceName, startDate, endDate, name, actionType, ruleName, sourceAddress, destAddress, sourcePort, destPort, protocol, threatGroup, category, attackIpsId, status, duration, risk, startTime, endTime, month, year, startDayOfMonth, endDayOfMonth, vlanTag, packetCount, packetBandwidth, averageAttackPacketRatePps, averageAttackRateBps, maxAttackRateBps, maxAttackPacketRatePps, lastPeriodBandwidth, poId, radwareId, direction, geoLocation, activationId, packetType, physicalPort, lastPeriodPacketRate, originalStartDate)
				VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
				''', (
					entry["row"]["deviceIp"], 
					start_date.strftime('%Y-%m-%d %H:%M:%S'), 
					end_date.strftime('%Y-%m-%d %H:%M:%S'), 
					entry["row"]["name"], 
					entry["row"]["actionType"], 
					entry["row"]["ruleName"], 
					entry["row"]["sourceAddress"], 
					entry["row"]["destAddress"], 
					entry["row"]["sourcePort"], 
					entry["row"]["destPort"], 
					entry["row"]["protocol"], 
					entry["row"]["threatGroup"], 
					entry["row"]["category"], 
					entry["row"]["attackIpsId"], 
					entry["row"]["status"], 
					entry["row"]["duration"], 
					entry["row"]["risk"], 
					entry["row"]["startTime"], 
					entry["row"]["endTime"], 
					end_date.month,
					end_date.year,
					start_date.day, 
					end_date.day, 
					entry["row"]["vlanTag"], 
					entry["row"]["packetCount"], 
					entry["row"]["packetBandwidth"], 
					entry["row"]["averageAttackPacketRatePps"], 
					entry["row"]["averageAttackRateBps"], 
					entry["row"]["maxAttackRateBps"], 
					entry["row"]["maxAttackPacketRatePps"], 
					entry["row"]["lastPeriodBandwidth"], 
					entry["row"]["poId"], 
					entry["row"]["radwareId"], 
					entry["row"]["direction"], 
					json.loads(entry["row"]["enrichmentContainer"]).get("geoLocation", {}).get("countryCode", None), 
					entry["row"]["activationId"], 
					entry["row"]["packetType"], 
					entry["row"]["physicalPort"], 
					entry["row"]["lastPeriodPacketRate"],
					orig_start_date.strftime('%Y-%m-%d %H:%M:%S')
					))


			# Commit changes and close the connection
			conn.commit()
			conn.close()




v = Vision(vision_ip, username, password)

# Get AMS Traffic bandwidth BPS and write to csv
traffic_bps_raw = v.ams_stats_dashboards_call(units = "bps", report_type="Traffic Utilization BPS")
v.write_traffic_stats_to_csv(traffic_bps_raw, tmp_files_path + 'traffic.csv')

# Get AMS Traffic bandwidth PPS and write to csv
traffic_pps_raw = v.ams_stats_dashboards_call(units = "pps", report_type="Traffic Utilization PPS")
v.write_traffic_stats_to_csv(traffic_bps_raw, tmp_files_path + 'traffic_pps.csv')

# # Get Forensics data
forensics_raw = v.get_forensics()
v.compile_to_sqldb()

# Get connections per second stats
cps_raw = v.ams_stats_dashboards_call(units = "cps", uri = '/mgmt/vrm/monitoring/traffic/cps', report_type="CPS")

v.write_traffic_stats_to_csv(cps_raw, tmp_files_path + 'traffic_cps.csv')

#Get concurrent established connections stats
cec_raw = v.ams_stats_dashboards_call(units = "cec", uri = '/mgmt/vrm/monitoring/traffic/concurrent-connections', report_type="Concurrent Established Connections")
v.write_traffic_stats_to_csv(cec_raw, tmp_files_path + 'traffic_cec.csv')