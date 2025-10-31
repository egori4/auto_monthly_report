"""
Optimized Data Collector - Direct API to SQLite
Performance improvements:
- Eliminates JSON file I/O (writes directly to SQLite)
- Streaming architecture: writes data in batches as received from API
- Constant memory footprint regardless of data volume
- Better code organization
- Comprehensive timing and debug logs
"""

from requests import Session
import requests
import json
import os
import time
import sys
from datetime import datetime, timedelta, timezone
import calendar
import sqlite3
import urllib3
import pandas as pd
from logger import Logger

# ============================================================================
# INITIALIZATION & CONFIGURATION
# ============================================================================

script_start_time = time.time()

daily = False
monthly = False

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Parse command line arguments
cust_id = sys.argv[1]

try:
	if sys.argv[2].lower() == "monthly":
		monthly = True
	elif sys.argv[2].lower() == "daily":
		daily = True
except:
	print('Error: Second argument is not set. Second argument must be either "daily" or "monthly".')
	print('Example: collector_optimized.py CUSTOMER_NAME monthly')
	sys.exit()

cur_month = int(sys.argv[3])
cur_day = int(sys.argv[4])
cur_year = int(sys.argv[5])

# Paths
db_files_path = f"./database_files/{cust_id}/"
run_file = 'run.sh'

# Read log verbosity from run.sh
with open(run_file) as f:
	for line in f:
		if line.startswith('log_verbosity'):
			log_verbosity = line.split('=')[1].replace('\n', '').replace('"', '').lower()
			break

# Initialize logger
log = Logger(log_verbosity)

log.info(f"="*80)
log.info(f"OPTIMIZED COLLECTOR - Starting execution")
log.info(f"Customer ID: {cust_id}")
log.info(f"Mode: {'Monthly' if monthly else 'Daily'}")
log.info(f"Log verbosity: {log.verbosity}")
log.debug(f"Script start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
log.info(f"="*80)

# Create necessary directories
os.makedirs(db_files_path, exist_ok=True)

# ============================================================================
# LOAD CUSTOMER CONFIGURATION
# ============================================================================

log.debug("Loading customer configuration from customers.json")
config_load_start = time.time()

try:
	with open("./config_files/customers.json", "r") as f:
		customers_json_dic = json.load(f)
	
	selected_entry = next((entry for entry in customers_json_dic if entry.get("id") == cust_id), None)
	
	if not selected_entry:
		log.error(f"No configuration found for customer ID: {cust_id}")
		sys.exit(1)
	
	# Extract configuration
	username = selected_entry['user']
	password = selected_entry['pass']
	vision_ip = selected_entry['visions'][0]['ip']
	excluded_attacks = selected_entry['exclude']
	dp_ips_string = selected_entry['visions'][0]['dps']
	dp_ip_to_name_dict = selected_entry['defensepros']
	bw_units = selected_entry['variables']['bwUnitDaily']
	
	policies_list = selected_entry.get('policiesList', [])
	traffic_window_granular = selected_entry.get('variables', {}).get('TrafficWindowGranular', 14400)
	traffic_window_averaged = selected_entry.get('variables', {}).get('TrafficWindowAveraged', 86400)
	forensics_window = selected_entry.get('variables', {}).get('ForensicsWindow', 3600)
	pre_attack_extra_timestamps = selected_entry.get('variables', {}).get('PreAttackTimestampsToKeep', 4)
	post_attack_extra_timestamps = selected_entry.get('variables', {}).get('PostAttackTimestampsToKeep', 20)
	bps_attack_threshold = selected_entry.get('variables', {}).get('BpsAttackThreshold', 10000)
	pps_attack_threshold = selected_entry.get('variables', {}).get('PpsAttackThreshold', 10000)
	
	log.debug(f"Configuration loaded successfully in {time.time() - config_load_start:.2f}s")
	log.debug(f"Vision IP: {vision_ip}")
	log.debug(f"DefensePro devices: {dp_ips_string}")

except FileNotFoundError:
	log.error("customers.json file not found")
	sys.exit(1)
except json.JSONDecodeError as e:
	log.error(f"Error parsing customers.json: {e}")
	sys.exit(1)
except Exception as e:
	log.error(f"Error loading configuration: {e}")
	sys.exit(1)


# ============================================================================
# VISION API CLIENT CLASS
# ============================================================================

class Vision:
	"""Handles all interactions with Vision API and database operations"""
	
	def __init__(self, vision_ip, username, password):
		"""Initialize Vision API client"""
		init_start = time.time()
		log.debug("Initializing Vision API client")
		
		self.ip = vision_ip
		self.login_data = {"username": username, "password": password}
		self.base_url = f"https://{vision_ip}"
		self.sess = Session()
		self.sess.headers.update({"Content-Type": "application/json"})
		
		# Connect to Vision API
		log.info("Connecting to Vision API...")
		self.login()
		log.info("Collecting DefensePro device list")
		self.device_list = self.get_device_list()
		
		# Set up date/time parameters
		self.today_date = datetime.today().replace(month=cur_month, day=cur_day, year=cur_year)
		log.info(f"Report date set to: {self.today_date.strftime('%Y-%m-%d')}")
		
		self.today_day_number = self.today_date.day
		self.previous_day_number = (self.today_date - timedelta(days=1)).day
		self.today_month_number = self.today_date.month
		self.prev_month_number = 12 if self.today_month_number == 1 else self.today_month_number - 1
		self.today_year = self.today_date.year
		self.start_time_lower, self.end_time_upper = self.generate_report_times(self.today_date)
		self.days_in_prev_month = calendar.monthrange(self.today_year, self.prev_month_number)[1]
		
		log.debug(f"Time range: {datetime.fromtimestamp(self.start_time_lower/1000).strftime('%Y-%m-%d %H:%M:%S')} to {datetime.fromtimestamp(self.end_time_upper/1000).strftime('%Y-%m-%d %H:%M:%S')}")
		log.debug(f"Vision client initialized in {time.time() - init_start:.2f}s")
	
	# ------------------------------------------------------------------------
	# API AUTHENTICATION & COMMUNICATION
	# ------------------------------------------------------------------------
	
	def login(self):
		"""Authenticate with Vision API"""
		login_url = self.base_url + '/mgmt/system/user/login'
		try:
			r = self.sess.post(url=login_url, json=self.login_data, verify=False)
			r.raise_for_status()
			response = r.json()
			
			if response['status'] == 'ok':
				self.sess.headers.update({"JSESSIONID": response['jsessionid']})
				log.debug("Authentication successful")
			else:
				log.error("Authentication failed")
				sys.exit(1)
		except Exception as err:
			log.error(f"Login error: {err}")
			raise SystemExit(err)
	
	def _post(self, URL, requestData=""):
		"""POST request with retry logic for session expiration"""
		max_retries = 3
		
		for attempt in range(max_retries):
			try:
				response = self.sess.post(url=URL, verify=False, data=requestData)
				
				if response.status_code == 403:
					log.debug(f"Session expired (attempt {attempt + 1}), refreshing...")
					self.login()
					response = self.sess.post(url=URL, verify=False, data=requestData)
				
				response.raise_for_status()
				return response
			
			except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError,
					requests.exceptions.SSLError, requests.exceptions.Timeout,
					requests.exceptions.ConnectTimeout, requests.exceptions.ReadTimeout) as err:
				log.debug(f"Request failed (attempt {attempt + 1}): {err}")
				if attempt < max_retries - 1:
					time.sleep(2 ** attempt)
				else:
					log.error(f"Max retries reached. Request failed: {err}")
					return None
		
		return None
	
	# ------------------------------------------------------------------------
	# TIME RANGE CALCULATION
	# ------------------------------------------------------------------------
	
	def generate_report_times(self, today_date):
		"""Calculate start and end timestamps for the report period"""
		if daily:
			yesterday_start = (today_date - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
			start_time_lower = int(yesterday_start.timestamp()) * 1000
			yesterday_end = (today_date - timedelta(days=1)).replace(hour=23, minute=59, second=59, microsecond=0)
			end_time_upper = int(yesterday_end.timestamp()) * 1000
		
		if monthly:
			first_day_of_prev_month = (today_date.replace(day=1) - timedelta(days=1)).replace(
				day=1, hour=0, minute=0, second=0, microsecond=0
			)
			start_time_lower = int(first_day_of_prev_month.timestamp()) * 1000
			
			last_day_of_prev_month = first_day_of_prev_month.replace(
				day=calendar.monthrange(first_day_of_prev_month.year, first_day_of_prev_month.month)[1],
				hour=23, minute=59, second=59, microsecond=0
			)
			end_time_upper = int(last_day_of_prev_month.timestamp()) * 1000
		
		return start_time_lower, end_time_upper
	
	def get_device_list(self):
		"""Retrieve list of DefensePro devices from Vision"""
		devices_url = self.base_url + '/mgmt/system/config/itemlist/alldevices'
		r = self.sess.get(url=devices_url, verify=False)
		json_txt = r.json()
		
		dev_list = {
			item['managementIp']: {
				'Type': item['type'],
				'Name': item['name'],
				'Version': item['deviceVersion'],
				'ormId': item['ormId']
			}
			for item in json_txt if item['type'] == "DefensePro"
		}
		
		log.debug(f"Found {len(dev_list)} DefensePro devices")
		return dev_list
	
	# ------------------------------------------------------------------------
	# DATABASE HELPER METHODS
	# ------------------------------------------------------------------------
	
	def get_database_filename(self):
		"""Calculate the appropriate database filename based on date logic"""
		is_jan_1 = self.today_day_number == 1 and self.today_month_number == 1
		is_day_1 = self.today_day_number == 1
		is_jan = self.today_month_number == 1
		
		if daily and is_day_1:
			if is_jan_1:
				return f'{db_files_path}database_{cust_id}_12_{self.today_year - 1}.sqlite'
			else:
				return f'{db_files_path}database_{cust_id}_{self.today_month_number - 1:02}_{self.today_year}.sqlite'
		elif daily:
			return f'{db_files_path}database_{cust_id}_{self.today_month_number:02}_{self.today_year}.sqlite'
		elif monthly:
			if is_jan:
				return f'{db_files_path}database_{cust_id}_12_{self.today_year - 1}.sqlite'
			else:
				return f'{db_files_path}database_{cust_id}_{self.today_month_number - 1:02}_{self.today_year}.sqlite'
		else:
			raise ValueError("Either daily or monthly must be True")
	
	# ------------------------------------------------------------------------
	# FORENSICS DATA COLLECTION & PROCESSING
	# ------------------------------------------------------------------------
	
	def create_forensics_post_payload(self, start_time_lower, end_time_upper):
		"""Create API query payload for forensics data"""
		query = {
			"criteria": [],
			"pagination": {
				"page": 0,
				"size": 10000,
				"topHits": 10000
			}
		}
		
		# Date range filter
		and_filters = {
			"type": "andFilter",
			"filters": [{
				"type": "timeFilter",
				"field": "endTime",
				"lower": f"{start_time_lower}",
				"upper": f"{end_time_upper}",
				"includeLower": True,
				"includeUpper": True
			}]
		}
		
		# Add exclusion filters
		if excluded_attacks:
			for text in excluded_attacks.split(','):
				field, value = text.split(':')
				and_filters['filters'].append({
					"type": "termFilter",
					"field": field,
					"value": value,
					"inverseFilter": True
				})
		
		query['criteria'].append(and_filters)
		
		# DefensePro IP filters
		or_filters = {"type": "orFilter", "filters": []}
		
		if dp_ips_string:
			for dp in dp_ips_string.split(','):
				and_filter = {
					"type": "andFilter",
					"inverseFilter": False,
					"filters": [
						{
							"type": "termFilter",
							"inverseFilter": False,
							"field": "deviceIp",
							"value": dp
						},
						{
							"type": "orFilter",
							"inverseFilter": False,
							"filters": [
								{
									"type": "termFilter",
									"inverseFilter": False,
									"field": "ruleName",
									"value": policy
								}
								for policy in policies_list
							]
						}
					]
				}
				or_filters["filters"].append(and_filter)
		else:
			or_filters['filters'].append({
				"type": "termFilter",
				"field": "deviceIp",
				"value": "0.0.0.0",
				"inverseFilter": True
			})
		
		query['criteria'].append(or_filters)
		return query
	
	def get_forensics_and_write_to_db(self, start_time_lower, end_time_upper, days_in_prev_month):
		"""Collect forensics data from Vision API and write incrementally to DB (STREAMING)"""
		log.info("="*80)
		log.info("COLLECTING & WRITING FORENSICS DATA (STREAMING)")
		log.info(f"Time range: {datetime.fromtimestamp(start_time_lower/1000).strftime('%Y-%m-%d %H:%M:%S')} to {datetime.fromtimestamp(end_time_upper/1000).strftime('%Y-%m-%d %H:%M:%S')}")
		log.info("="*80)
		
		overall_start_time = time.time()
		
		# Progress tracking
		total_calls = days_in_prev_month * 24 if monthly else 24
		bar_length = 50
		completed_calls = 0
		
		# Database setup
		db_file = self.get_database_filename()
		log.debug(f"Database file: {db_file}")
		
		conn = sqlite3.connect(db_file)
		cursor = conn.cursor()
		
		# Create table with indexes (one-time setup)
		log.debug("Creating/verifying database schema")
		cursor.executescript('''
			CREATE TABLE IF NOT EXISTS attacks (
				attackIpsId TEXT PRIMARY KEY,
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
				originalStartDate DATE NOT NULL
			);
			
			CREATE INDEX IF NOT EXISTS idx_month ON attacks (month);
			CREATE INDEX IF NOT EXISTS idx_startDayOfMonth ON attacks (startDayOfMonth);
			CREATE INDEX IF NOT EXISTS idx_deviceName ON attacks (deviceName);
			CREATE INDEX IF NOT EXISTS idx_sourceAddress ON attacks (sourceAddress);
			CREATE INDEX IF NOT EXISTS idx_ruleName ON attacks (ruleName);
			CREATE INDEX IF NOT EXISTS idx_name ON attacks (name);
			CREATE INDEX IF NOT EXISTS idx_start_end_time ON attacks (startTime, endTime);
			CREATE INDEX IF NOT EXISTS idx_month_year ON attacks (month, year);
		''')
		
		# Set performance pragmas
		cursor.executescript('''
			PRAGMA journal_mode=OFF;
			PRAGMA synchronous=OFF;
			PRAGMA temp_store=MEMORY;
			PRAGMA locking_mode=EXCLUSIVE;
		''')
		
		conn.execute("BEGIN")
		
		insert_sql = '''
			INSERT INTO attacks (
				attackIpsId, deviceName, startDate, endDate, name, actionType, ruleName,
				sourceAddress, destAddress, sourcePort, destPort, protocol, threatGroup, category,
				duration, risk, startTime, endTime, month, year, startDayOfMonth, endDayOfMonth,
				vlanTag, packetCount, packetBandwidth, averageAttackPacketRatePps,
				averageAttackRateBps, maxAttackRateBps, maxAttackPacketRatePps,
				lastPeriodBandwidth, poId, radwareId, direction, geoLocation, activationId,
				packetType, physicalPort, lastPeriodPacketRate, originalStartDate
			)
			VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
			ON CONFLICT(attackIpsId) DO NOTHING
		'''
		
		# Batch processing
		batch_size = 5000  # Write to DB every 5000 records
		rows_batch = []
		total_records_processed = 0
		total_records_inserted = 0
		skipped_records = 0
		
		api_url = f'https://{self.ip}/mgmt/monitor/reporter/reports-ext/ATTACK'
		current_start = start_time_lower
		
		log.info("Starting API calls and incremental database writes...")
		
		while current_start < end_time_upper:
			window_end = current_start + (forensics_window * 1000)
			
			post_payload = self.create_forensics_post_payload(current_start, window_end)
			response = self._post(api_url, json.dumps(post_payload))
			
			if response and response.status_code == 200:
				try:
					response_json = response.json()
					if "data" in response_json:
						# Process this batch of data
						for entry in response_json["data"]:
							row = entry.get("row", {})
							# This duration was a a temp workaround for missing duration field
							# if "duration" not in row:
							# 	skipped_records += 1
							# 	continue
							
							try:
								start_ts = int(row["startTime"]) / 1000
								end_ts = int(row["endTime"]) / 1000
								start_date = datetime.fromtimestamp(start_ts)
								end_date = datetime.fromtimestamp(end_ts)
								orig_start_date = start_date
								
								geo = json.loads(row.get("enrichmentContainer", "{}")).get("geoLocation", {})
								geo_code = geo.get("countryCode")
								
								# Adjust start_date for ongoing attacks from previous period
								if daily and self.today_day_number == 2:
									day_before_yesterday = self.today_date - timedelta(days=2)
									if start_date.day == day_before_yesterday.day:
										start_date = start_date.replace(
											day=1, hour=0, minute=0, second=0,
											month=self.today_month_number if self.today_month_number != 1 else 1,
											year=self.today_year
										)
								
								elif monthly:
									two_months_ago = self.today_month_number - 2 if self.today_month_number > 2 else self.today_month_number + 10
									
									if start_date.month == two_months_ago:
										if self.today_month_number != 1:
											start_date = start_date.replace(
												day=1, month=self.today_month_number - 1,
												hour=0, minute=0, second=0
											)
										else:
											start_date = start_date.replace(
												day=1, month=12, hour=0, minute=0, second=0
											)
								
								rows_batch.append((
									row.get("attackIpsId"),
									row.get("deviceIp"),
									start_date.strftime('%Y-%m-%d %H:%M:%S'),
									end_date.strftime('%Y-%m-%d %H:%M:%S'),
									row.get("name"),
									row.get("actionType"),
									row.get("ruleName"),
									row.get("sourceAddress"),
									row.get("destAddress"),
									row.get("sourcePort"),
									row.get("destPort"),
									row.get("protocol"),
									row.get("threatGroup"),
									row.get("category"),
									row.get("duration"),
									row.get("risk"),
									row.get("startTime"),
									row.get("endTime"),
									end_date.month,
									end_date.year,
									start_date.day,
									end_date.day,
									row.get("vlanTag"),
									row.get("packetCount"),
									row.get("packetBandwidth"),
									row.get("averageAttackPacketRatePps"),
									row.get("averageAttackRateBps"),
									row.get("maxAttackRateBps"),
									row.get("maxAttackPacketRatePps"),
									row.get("lastPeriodBandwidth"),
									row.get("poId"),
									row.get("radwareId"),
									row.get("direction"),
									geo_code,
									row.get("activationId"),
									row.get("packetType"),
									row.get("physicalPort"),
									row.get("lastPeriodPacketRate"),
									orig_start_date.strftime('%Y-%m-%d %H:%M:%S')
								))
								
								total_records_processed += 1
								
								# Write batch to database when batch size is reached
								if len(rows_batch) >= batch_size:
									cursor.executemany(insert_sql, rows_batch)
									total_records_inserted += len(rows_batch)
									log.debug(f"Inserted batch: {len(rows_batch)} rows (Total: {total_records_inserted})")
									rows_batch.clear()
							
							except Exception as e:
								log.debug(f"Error processing forensics record: {e}")
								skipped_records += 1
								continue
						
						# Progress bar
						completed_calls += 1
						percent = (completed_calls / total_calls) * 100
						filled_length = int(bar_length * completed_calls // total_calls)
						bar = "=" * filled_length + "-" * (bar_length - filled_length)
						sys.stdout.write(f"\r[{bar}] {percent:.2f}% | Records: {total_records_processed}")
						sys.stdout.flush()
						
						current_start += (forensics_window * 1000)
					else:
						log.debug(f"No data in response for window {current_start}")
						break
				
				except json.JSONDecodeError:
					log.error("Failed to parse JSON response")
					break
			else:
				log.error(f"API call failed for forensics data")
				break
		
		# Insert remaining rows
		if rows_batch:
			cursor.executemany(insert_sql, rows_batch)
			total_records_inserted += len(rows_batch)
			log.debug(f"Inserted final batch: {len(rows_batch)} rows")
		
		conn.commit()
		conn.close()
		
		print()  # New line after progress bar
		
		overall_duration = time.time() - overall_start_time
		log.info(f"Forensics collection & DB write completed in {overall_duration:.2f}s")
		log.info(f"Total records: {total_records_processed}, Inserted: {total_records_inserted}, Skipped: {skipped_records}")
		log.debug(f"Average API call time: {overall_duration/max(completed_calls, 1):.2f}s per call")
		log.debug(f"Insert rate: {total_records_inserted/overall_duration:.0f} records/second")
		
		return {"total_processed": total_records_processed, "total_inserted": total_records_inserted}
	

	
	# ------------------------------------------------------------------------
	# TRAFFIC DATA COLLECTION & PROCESSING
	# ------------------------------------------------------------------------
	
	def ams_stats_dashboards_per_device_window_calls(self, start_time_lower, end_time_upper,
													  traffic_window, units, uri, report_type):
		"""Collect traffic stats from Vision API in time windows"""
		log.info(f"Collecting {report_type} data")
		api_start_time = time.time()
		
		initial_start_time_lower = start_time_lower
		api_url = f'https://{self.ip}' + uri
		
		query = {
			"direction": "Inbound",
			"timeInterval": {
				"from": start_time_lower,
				"to": end_time_upper
			}
		}
		
		if units == "bps" or units == "pps":
			query.update({"unit": units})
		
		combined_response_json = {}
		total_api_calls = 0
		
		if dp_ips_string:
			dps_list = dp_ips_string.split(',')
			
			for dp in dps_list:
				start_time_lower = initial_start_time_lower
				
				query.update({
					"selectedDevices": [{
						"deviceId": dp,
						"networkPolicies": policies_list,
						"ports": []
					}]
				})
				
				while start_time_lower < end_time_upper:
					window_start = start_time_lower
					window_end = start_time_lower + (traffic_window * 1000)
					
					query.update({
						"timeInterval": {
							"from": window_start,
							"to": window_end
						}
					})
					
					response = self._post(api_url, json.dumps(query))
					
					if response and response.status_code == 200:
						try:
							response_json = response.json()
							filtered_data = [
								row for row in response_json["data"]
								if not any(value is None for value in row["row"].values())
							]
							
							if dp not in combined_response_json:
								combined_response_json[dp] = {"data": [], "dataMap": {}}
							
							combined_response_json[dp]["data"].extend(filtered_data)
							
							# Update maxValue
							current_max = float(combined_response_json[dp].get("dataMap", {})
													.get("maxValue", {}).get("trafficValue", 0))
							try:
								new_max = float(response_json["dataMap"]["maxValue"]["trafficValue"])
								if new_max > current_max:
									combined_response_json[dp]["dataMap"]["maxValue"] = response_json["dataMap"]["maxValue"]
							except:
								pass
							
							total_api_calls += 1
							start_time_lower += (traffic_window * 1000)
						
						except json.JSONDecodeError:
							log.error(f"Failed to parse JSON for {dp}")
							break
					else:
						log.error(f"API call failed for {dp} at {window_start}")
						break
				
				start_time_lower = initial_start_time_lower
		
		api_duration = time.time() - api_start_time
		total_data_points = sum(len(dp_data["data"]) for dp_data in combined_response_json.values())
		
		log.info(f"{report_type} collection completed: {total_data_points} data points from {total_api_calls} API calls in {api_duration:.2f}s")
		log.debug(f"Average: {api_duration/max(total_api_calls, 1):.2f}s per API call")
		
		return combined_response_json
	
	def extract_attack_data_only(self, data, attack_threshold, pre_attack_extra_timestamps,
								  post_attack_extra_timestamps):
		"""Identify timestamps where attacks exceeded threshold"""
		log.debug(f"Extracting attack timestamps (threshold: {attack_threshold})")
		extract_start = time.time()
		
		attack_timestamps = set()
		
		for ip, details in data.items():
			timestamps = [int(entry["row"]["timeStamp"]) for entry in details["data"]]
			
			for i, entry in enumerate(details["data"]):
				row = entry["row"]
				if float(row["discards"]) > attack_threshold:
					attack_timestamps.add(timestamps[i])
					attack_timestamps.update(timestamps[max(0, i - pre_attack_extra_timestamps):i])
					attack_timestamps.update(timestamps[i + 1:min(len(timestamps), i + 1 + post_attack_extra_timestamps)])
		
		result = sorted(attack_timestamps)
		log.debug(f"Found {len(result)} attack timestamps in {time.time() - extract_start:.2f}s")
		return result
	
	def merge_attacks_to_aggregate(self, traffic_aggregate, traffic_granular, attack_timestamps):
		"""Merge granular attack data into aggregate data"""
		log.debug("Merging granular attack data into aggregate data")
		merge_start = time.time()
		
		merged_data = traffic_aggregate.copy()
		
		for ip, details in traffic_granular.items():
			if ip not in merged_data:
				merged_data[ip] = {"data": []}
			
			existing_entries = {
				int(entry["row"]["timeStamp"]): entry
				for entry in merged_data[ip]["data"]
			}
			
			for entry in details["data"]:
				timestamp = int(entry["row"]["timeStamp"])
				if timestamp in attack_timestamps:
					existing_entries[timestamp] = entry
			
			merged_data[ip]["data"] = sorted(
				existing_entries.values(),
				key=lambda entry: int(entry["row"]["timeStamp"])
			)
		
		log.debug(f"Merge completed in {time.time() - merge_start:.2f}s")
		return merged_data
	
	def write_traffic_stats_to_db(self, traffic_raw_response, report_type):
		"""Write traffic statistics directly to SQLite database (OPTIMIZED - NO JSON)"""
		log.info(f"Writing {report_type} to database")
		db_write_start = time.time()
		
		# Determine table name
		table_map = {
			"Traffic Volume BPS": "traffic_bps",
			"Traffic Volume PPS": "traffic_pps",
			"Traffic Volume BPS Excluded": "traffic_bps_excluded",
			"Traffic Volume PPS Excluded": "traffic_pps_excluded",
			"Traffic CPS": "traffic_cps",
			"Traffic CEC": "traffic_cec"
		}
		db_table_name = table_map.get(report_type)
		
		# Build DataFrames for each DP
		all_dps_df_list = []
		dp_names_list = []
		
		for dp_ip, dp_ip_traffic_stats in traffic_raw_response.items():
			dp_name = dp_ip_to_name_dict.get(dp_ip, dp_ip)
			dp_names_list.append(dp_name)
			
			rows = []
			for entry in dp_ip_traffic_stats['data']:
				row = entry['row']
				
				if report_type == "Traffic Volume BPS":
					row['trafficValue'] = round(float(row['trafficValue']) / 1000, 2)
					row['discards'] = round(float(row['discards']) / 1000, 2)
					rows.append({
						'Timestamp': row['timeStamp'],
						f'Traffic {dp_name}': float(row['trafficValue']) - float(row['discards']),
						f'Attacks {dp_name}': float(row['discards'])
					})
				
				elif report_type == "Traffic Volume PPS":
					row['trafficValue'] = round(float(row['trafficValue']), 2)
					row['discards'] = round(float(row['discards']), 2)
					rows.append({
						'Timestamp': row['timeStamp'],
						f'Traffic {dp_name}': float(row['trafficValue']) - float(row['discards']),
						f'Attacks {dp_name}': float(row['discards'])
					})
				
				elif report_type == "Traffic Volume BPS Excluded":
					row['excluded'] = round(float(row['excluded']) / 1000, 2)
					rows.append({
						'Timestamp': row['timeStamp'],
						f'{dp_name}': float(row['excluded'])
					})
				
				elif report_type == "Traffic Volume PPS Excluded":
					row['excluded'] = round(float(row['excluded']), 2)
					rows.append({
						'Timestamp': row['timeStamp'],
						f'{dp_name}': float(row['excluded'])
					})
				
				elif report_type == "Traffic CPS":
					row['connectionPerSecond'] = float(row['connectionPerSecond'])
					rows.append({
						'Timestamp': row['timeStamp'],
						f'{dp_name}': float(row['connectionPerSecond'])
					})
				
				elif report_type == "Traffic CEC":
					row['connectionsPerSecond'] = float(row['connectionsPerSecond'])
					rows.append({
						'Timestamp': row['timeStamp'],
						f'{dp_name}': float(row['connectionsPerSecond'])
					})
			
			df_single_dp = pd.DataFrame(rows)
			if not df_single_dp.empty:
				all_dps_df_list.append(df_single_dp)
		
		# Merge all DP DataFrames
		df_final = all_dps_df_list[0]
		for df in all_dps_df_list[1:]:
			df_final = pd.merge(df_final, df, on='Timestamp', how='outer')
		
		df_final = df_final.sort_values(by='Timestamp')
		df_final['DateTime'] = pd.to_datetime(df_final['Timestamp'].astype('int64'), unit='ms').dt.strftime('%Y-%m-%d %H:%M:%S')
		
		# Rearrange columns
		if report_type in ["Traffic Volume BPS", "Traffic Volume PPS"]:
			traffic_cols = [f'Traffic {dp_name}' for dp_name in dp_names_list]
			attack_cols = [f'Attacks {dp_name}' for dp_name in dp_names_list]
			ordered_cols = ['Timestamp', 'DateTime'] + traffic_cols + attack_cols
			df_final = df_final[ordered_cols]
		
		df_final = df_final.dropna().reset_index(drop=True)
		
		# Get database file
		db_file = self.get_database_filename()
		
		# Write to SQLite
		conn = sqlite3.connect(db_file)
		cursor = conn.cursor()
		
		create_cols = ", ".join([f'"{col}" REAL' for col in df_final.columns if col not in ['Timestamp', 'DateTime']])
		cursor.execute(f'''
			CREATE TABLE IF NOT EXISTS {db_table_name} (
				Timestamp TEXT,
				DateTime TEXT,
				{create_cols}
			)
		''')
		
		# Delete overlapping data
		end_time_inclusive = ((self.end_time_upper // 1000) + 1) * 1000
		cursor.execute(f'''
			DELETE FROM {db_table_name}
			WHERE CAST(Timestamp AS INTEGER) >= ? AND CAST(Timestamp AS INTEGER) <= ?
		''', (self.start_time_lower, end_time_inclusive))
		
		# Insert new data
		df_final.to_sql(db_table_name, conn, if_exists='append', index=False)
		
		conn.commit()
		conn.close()
		
		db_duration = time.time() - db_write_start
		log.info(f"{report_type} database write completed: {len(df_final)} rows in {db_duration:.2f}s")
		log.debug(f"Insert rate: {len(df_final)/db_duration:.0f} rows/second")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
	"""Main execution flow"""
	
	log.info("")
	log.info("="*80)
	log.info("PHASE 1: INITIALIZATION")
	log.info("="*80)
	
	# Initialize Vision client
	v = Vision(vision_ip, username, password)
	
	# -------------------------------------------------------------------------
	# FORENSICS DATA COLLECTION & STREAMING DB WRITE
	# -------------------------------------------------------------------------
	
	log.info("")
	log.info("="*80)
	log.info("PHASE 2: FORENSICS DATA (STREAMING TO DB)")
	log.info("="*80)
	
	forensics_start = time.time()
	
	# Collect from API and write incrementally to DB (streaming, no large memory buffer)
	forensics_result = v.get_forensics_and_write_to_db(v.start_time_lower, v.end_time_upper, v.days_in_prev_month)
	
	forensics_total = time.time() - forensics_start
	log.info(f"Forensics processing completed in {forensics_total:.2f}s")
	
	# # -------------------------------------------------------------------------
	# # TRAFFIC DATA COLLECTION (BPS)
	# # -------------------------------------------------------------------------
	
	# log.info("")
	# log.info("="*80)
	# log.info("PHASE 3: TRAFFIC BPS DATA COLLECTION")
	# log.info("="*80)
	
	# traffic_bps_start = time.time()
	
	# # Collect granular BPS data
	# traffic_bps_per_device_granular = v.ams_stats_dashboards_per_device_window_calls(
	# 	v.start_time_lower, v.end_time_upper, traffic_window_granular,
	# 	units="bps", uri="/mgmt/vrm/monitoring/traffic/periodic/report",
	# 	report_type="Traffic Volume BPS Granular"
	# )
	
	# # Extract attack timestamps
	# bps_attack_only_timestamps_list = v.extract_attack_data_only(
	# 	traffic_bps_per_device_granular, bps_attack_threshold,
	# 	pre_attack_extra_timestamps, post_attack_extra_timestamps
	# )
	
	# # Collect aggregate BPS data
	# traffic_bps_per_device_aggregate = v.ams_stats_dashboards_per_device_window_calls(
	# 	v.start_time_lower, v.end_time_upper, traffic_window_averaged,
	# 	units="bps", uri="/mgmt/vrm/monitoring/traffic/periodic/report",
	# 	report_type="Traffic Volume BPS Aggregate"
	# )
	
	# # Merge and write to database
	# traffic_bps_per_device_merged = v.merge_attacks_to_aggregate(
	# 	traffic_bps_per_device_aggregate, traffic_bps_per_device_granular,
	# 	bps_attack_only_timestamps_list
	# )
	# v.write_traffic_stats_to_db(traffic_bps_per_device_merged, report_type="Traffic Volume BPS")
	
	# traffic_bps_total = time.time() - traffic_bps_start
	# log.info(f"Traffic BPS processing completed in {traffic_bps_total:.2f}s")
	
	# # -------------------------------------------------------------------------
	# # TRAFFIC DATA COLLECTION (PPS)
	# # -------------------------------------------------------------------------
	
	# log.info("")
	# log.info("="*80)
	# log.info("PHASE 4: TRAFFIC PPS DATA COLLECTION")
	# log.info("="*80)
	
	# traffic_pps_start = time.time()
	
	# # Collect granular PPS data
	# traffic_pps_per_device_granular = v.ams_stats_dashboards_per_device_window_calls(
	# 	v.start_time_lower, v.end_time_upper, traffic_window_granular,
	# 	units="pps", uri="/mgmt/vrm/monitoring/traffic/periodic/report",
	# 	report_type="Traffic Volume PPS Granular"
	# )
	
	# # Extract attack timestamps
	# pps_attack_only_timestamps_list = v.extract_attack_data_only(
	# 	traffic_pps_per_device_granular, pps_attack_threshold,
	# 	pre_attack_extra_timestamps, post_attack_extra_timestamps
	# )
	
	# # Collect aggregate PPS data
	# traffic_pps_per_device_aggregate = v.ams_stats_dashboards_per_device_window_calls(
	# 	v.start_time_lower, v.end_time_upper, traffic_window_averaged,
	# 	units="pps", uri="/mgmt/vrm/monitoring/traffic/periodic/report",
	# 	report_type="Traffic Volume PPS Aggregate"
	# )
	
	# # Merge and write to database
	# traffic_pps_per_device_merged = v.merge_attacks_to_aggregate(
	# 	traffic_pps_per_device_aggregate, traffic_pps_per_device_granular,
	# 	pps_attack_only_timestamps_list
	# )
	# v.write_traffic_stats_to_db(traffic_pps_per_device_merged, report_type="Traffic Volume PPS")
	
	# traffic_pps_total = time.time() - traffic_pps_start
	# log.info(f"Traffic PPS processing completed in {traffic_pps_total:.2f}s")
	
	# # Merge attack timestamps
	# merged_attack_only_timestamps_list = sorted(
	# 	set(bps_attack_only_timestamps_list) | set(pps_attack_only_timestamps_list)
	# )
	# log.debug(f"Total unique attack timestamps: {len(merged_attack_only_timestamps_list)}")
	
	# # -------------------------------------------------------------------------
	# # EXCLUDED TRAFFIC DATA
	# # -------------------------------------------------------------------------
	
	# log.info("")
	# log.info("="*80)
	# log.info("PHASE 5: EXCLUDED TRAFFIC DATA")
	# log.info("="*80)
	
	# excluded_start = time.time()
	
	# v.write_traffic_stats_to_db(traffic_bps_per_device_aggregate, report_type="Traffic Volume BPS Excluded")
	# v.write_traffic_stats_to_db(traffic_pps_per_device_aggregate, report_type="Traffic Volume PPS Excluded")
	
	# excluded_total = time.time() - excluded_start
	# log.info(f"Excluded traffic processing completed in {excluded_total:.2f}s")
	
	# # -------------------------------------------------------------------------
	# # CPS DATA COLLECTION
	# # -------------------------------------------------------------------------
	
	# log.info("")
	# log.info("="*80)
	# log.info("PHASE 6: CPS DATA COLLECTION")
	# log.info("="*80)
	
	# cps_start = time.time()
	
	# # Collect granular CPS data
	# cps_per_device_granular = v.ams_stats_dashboards_per_device_window_calls(
	# 	v.start_time_lower, v.end_time_upper, traffic_window_granular,
	# 	units=None, uri="/mgmt/vrm/monitoring/traffic/cps",
	# 	report_type="CPS Granular"
	# )
	
	# # Collect aggregate CPS data
	# cps_per_device_aggregate = v.ams_stats_dashboards_per_device_window_calls(
	# 	v.start_time_lower, v.end_time_upper, traffic_window_averaged,
	# 	units=None, uri="/mgmt/vrm/monitoring/traffic/cps",
	# 	report_type="CPS Aggregate"
	# )
	
	# # Merge and write to database
	# cps_per_device_merged = v.merge_attacks_to_aggregate(
	# 	cps_per_device_aggregate, cps_per_device_granular,
	# 	merged_attack_only_timestamps_list
	# )
	# v.write_traffic_stats_to_db(cps_per_device_merged, report_type="Traffic CPS")
	
	# cps_total = time.time() - cps_start
	# log.info(f"CPS processing completed in {cps_total:.2f}s")
	
	# # -------------------------------------------------------------------------
	# # CEC DATA COLLECTION
	# # -------------------------------------------------------------------------
	
	# log.info("")
	# log.info("="*80)
	# log.info("PHASE 7: CONCURRENT CONNECTIONS DATA COLLECTION")
	# log.info("="*80)
	
	# cec_start = time.time()
	
	# # Collect granular CEC data
	# cec_per_device_granular = v.ams_stats_dashboards_per_device_window_calls(
	# 	v.start_time_lower, v.end_time_upper, traffic_window_granular,
	# 	units=None, uri="/mgmt/vrm/monitoring/traffic/concurrent-connections",
	# 	report_type="Concurrent Connections Granular"
	# )
	
	# # Collect aggregate CEC data
	# cec_per_device_aggregate = v.ams_stats_dashboards_per_device_window_calls(
	# 	v.start_time_lower, v.end_time_upper, traffic_window_averaged,
	# 	units=None, uri="/mgmt/vrm/monitoring/traffic/concurrent-connections",
	# 	report_type="Concurrent Connections Aggregate"
	# )
	
	# # Merge and write to database
	# cec_per_device_merged = v.merge_attacks_to_aggregate(
	# 	cec_per_device_aggregate, cec_per_device_granular,
	# 	merged_attack_only_timestamps_list
	# )
	# v.write_traffic_stats_to_db(cec_per_device_merged, report_type="Traffic CEC")
	
	# cec_total = time.time() - cec_start
	# log.info(f"CEC processing completed in {cec_total:.2f}s")
	
	# -------------------------------------------------------------------------
	# FINAL SUMMARY
	# -------------------------------------------------------------------------
	
	total_execution_time = time.time() - script_start_time
	
	log.info("")
	log.info("="*80)
	log.info("EXECUTION SUMMARY")
	log.info("="*80)
	log.info(f"Forensics:         {forensics_total:>8.2f}s")
	# log.info(f"Traffic BPS:       {traffic_bps_total:>8.2f}s")
	# log.info(f"Traffic PPS:       {traffic_pps_total:>8.2f}s")
	# log.info(f"Excluded Traffic:  {excluded_total:>8.2f}s")
	# log.info(f"CPS:               {cps_total:>8.2f}s")
	# log.info(f"CEC:               {cec_total:>8.2f}s")
	log.info(f"{'-'*80}")
	log.info(f"TOTAL TIME:        {total_execution_time:>8.2f}s ({total_execution_time/60:.2f} minutes)")
	log.info("="*80)
	log.info(f"Script completed successfully at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
	log.info("="*80)


if __name__ == "__main__":
	try:
		main()
	except KeyboardInterrupt:
		log.error("\nScript interrupted by user")
		sys.exit(1)
	except Exception as e:
		log.error(f"\nFatal error: {e}")
		import traceback
		log.error(traceback.format_exc())
		sys.exit(1)
