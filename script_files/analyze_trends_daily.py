import pandas as pd
import sqlite3
import csv
import sys
import pandas as pd
import json

cust_id = sys.argv[1]
month = sys.argv[2] #this month
year = sys.argv[3] #this year


######### Exctract variables from /config_files/customers.json
customers_json = json.loads(open("./config_files/customers.json", "r").read())
for cust_config_block in customers_json:
	if cust_config_block['id'].lower() == cust_id.lower():
		defensepros = cust_config_block['defensepros']

		bw_units = cust_config_block['variables']['bwUnitDaily']
		#Can be configured "Gigabytes", "Terabytes" or "Megabytes"
		
		pkt_units = cust_config_block['variables']['pktUnitDaily']
		#Can be configured "Millions" or "Billions" or "Thousands"
		if bw_units.lower() == 'megabytes':	
			bw_units_sum = 'ROUND(SUM(packetBandwidth)/8000.0, 2)'
			bps_unit = 1000000
			bps_units_desc = 'Mbps'

		if bw_units.lower() == 'gigabytes':	
			bw_units_sum = 'ROUND(SUM(packetBandwidth)/8000000.0, 2)'
			bps_unit = 1000000000
			bps_units_desc = 'Gbps'

		if bw_units.lower() == 'terabytes':
			bw_units_sum = 'ROUND(SUM(packetBandwidth)/8000000000.0, 2)'
			bps_unit = 1000000000
			bps_units_desc = 'Gbps'

##### Extract variables from run.sh ##############
run_file = 'run_daily.sh'
with open (run_file) as f:
	for line in f:
	#find line starting with top_n
		if line.startswith('top_n'):
			#print value after = sign
			top_n = int(line.split('=')[1].replace('\n',''))
			continue

		if line.startswith('db_from_forensics'):
			#print value after = sign
			db_from_forensics = (line.split('=')[1].replace('\n','').replace('"','')).lower()
			if db_from_forensics == 'true':
				db_from_forensics = True
			else:
				db_from_forensics = False
			continue


# Paths
charts_tables_path = f"./tmp_files/{cust_id}/"
reports_path = f"./report_files/{cust_id}/"
db_path = f'./database_files/{cust_id}/'


def convert_csv_to_list_of_lists(filename):
	# Open csv file and convert to list of lists function
	data = []
	with open(filename, 'r') as file:
		reader = csv.reader(file)
		for row in reader:
			data.append(row)

	return convert_strings_to_numbers(data)

def convert_strings_to_numbers(data):
  # Check values float, integer or string function
	converted_data = []
	
	for sublist_index, sublist in enumerate(data):
		if sublist_index == 0: # do not convert the strings to numbers for the first headline row (policy names might be numbers corner case)
			converted_data.append(sublist)
		else:
			converted_row = []
			for value in sublist:
				#check if not ipv4 address
				if value.count('.') != 3:
					if value.replace(".", "").isdigit():  # Check if value is numeric
						if value.endswith('.0'):
							value = int(value.replace('.0', ''))
							converted_row.append(value)  # Convert ".0" to integer
						#check if value has decimal points
						elif "." in value:
							converted_row.append(float(value))
						elif value.isdigit():
							converted_row.append(int(value))  # Convert to integer
						else:
							print('The value is not defined as integer or float')
					else:
						converted_row.append(value)
				else:
					converted_row.append(value)
			converted_data.append(converted_row)
	return converted_data

def convert_packets_units(data, pkt_units):
	converted_data = []
	for row in data:
		converted_row = []
		for index, value in enumerate(row):
			# if the value is integer or float
			if index==0:
				value = value
			else:
				if isinstance(value, int) or isinstance(value, float):
					if pkt_units == "Billions":
						value = value/1000000000
					elif pkt_units == "Millions":
						value = value/1000000
					elif pkt_units == "Thousands":
						value = value/1000
					elif pkt_units.lower() == "as is":
						pass
					else:
						print(f'Packets unit variable "pkt_units" is not set.')
				
			#if value float convert to integer
					if isinstance(value, float):
						value = int(value)

			converted_row.append(value)
			
		converted_data.append(converted_row)
	return converted_data


def convert_bw_units(data, bw_units):
	converted_data = []

	for row in data:
		converted_row = []

		for index, value in enumerate(row):
			if index == 0:
				# For the first column, just append the value without conversion
				converted_row.append(value)
			elif not isinstance(value, str) and value != "":
				# Check if the value is not a string and not empty
				value = float(value)

				if bw_units.lower() == "megabytes":
					value = value / 8000
				elif bw_units.lower() == "gigabytes":
					value = value / 8000000
				elif bw_units.lower() == "terabytes":
					value = value / 8000000000

				# Leave only two decimal points
				value = round(value, 2)

				converted_row.append(value)
			else:
				# Append the original value if it's a string or empty
				converted_row.append(value)

		converted_data.append(converted_row)

	return converted_data

def trends_move(data, units="events"):

	analysis = '<ul>'
	# Extract attack names and attack counts for June and July
	attack_names = data[0][1:]
	attack_counts_previous = data[-2][1:]
	attack_counts_last = data[-1][1:]

	if isinstance(attack_counts_previous, list) and all(isinstance(item, str) for item in attack_counts_previous):
		analysis = f"Can not calculate trends - no previous month data"
		return analysis

	else:
		# Calculate and print the trends
		for name, count_previous, count_last in zip(attack_names, attack_counts_previous, attack_counts_last):
			if int(count_last) < int(count_previous):
				trend = "Decrease"
			else:
				trend = "Increase"
			
			difference = abs(int(count_last) - int(count_previous))

			if count_previous == 0:
				difference_percentage = "N/A"
			else:
				difference_percentage = (difference / count_previous) * 100

			#check if difference is float


			if isinstance(difference, float):
				difference = round(difference, 2)

			if difference_percentage == "N/A":
				change = f"by N/A %  - from {count_previous} to {count_last} {units} by a total of {difference} {units} "
			else:
				change = f"by {difference_percentage:.2f}% - from {count_previous} to {count_last} {units} by a total of {difference} {units} "
		
			analysis += f'<li><strong>{name}:</strong><ul><li> {trend} {change}</li></ul>'

		analysis += '</ul>'

		return analysis


def trends_move_total(data, units="events"):
	
	prev_total = data[-2][1]
	last_total = data[-1][1]

	if isinstance(prev_total, str):
		result = f"Can not calculate trends - no previous month data"
		return result
	
	else:
		trend = "increased" if last_total > prev_total else "decreased"
		difference = abs(last_total - prev_total)

		if isinstance(difference, float):
			difference = round(difference, 2)

		if float(prev_total) == 0:
			percentage_difference = "N/A"
			result = f"This month the total number of {units} {trend} by {percentage_difference}%- from {prev_total} to {last_total} {units} by a total of {difference} {units}"

		else:
			percentage_difference = (difference / float(prev_total)) * 100
			formatted_percentage_difference = f'{percentage_difference:.2f}%'
			result = f"This month the total number of {units} {trend} by {formatted_percentage_difference}- from {prev_total} to {last_total} {units} by a total of {difference} {units}"

		return result


def format_bw_units_value(value, bw_units=None):
	# Check if value is a number (integer or float)
	if pd.notna(value) and isinstance(value, (int, float)):
		# Apply formatting based on units
		if bw_units:
			if bw_units.lower() == 'megabytes':
				value /= 8000
			elif bw_units.lower() == 'gigabytes':
				value /= 8000000
			elif bw_units.lower() == 'terabytes':
				value /= 8000000000

			value = '{:,.2f}'.format(value)
			return value

	else:
		return value


def format_pkt_units_value(value, pkt_units=None):
	# Check if value is a number (integer or float)
	if pd.notna(value) and isinstance(value, (int, float)):
		# Apply formatting based on units
		if pkt_units:
			if pkt_units.lower() == 'millions':
				value /= 1000000
			elif pkt_units.lower() == 'billions':
				value /= 1000000000
			elif pkt_units.lower() == 'thousands':
				value /= 1000
			elif pkt_units.lower() == 'as is':
				pass
			else:
				print(f'pkt_units variable is not set - value is {value} , pkt_units is {pkt_units}')

			

			# convert float to intiger
			if isinstance(value, float):
				value = int(value)
			

			value = "{:,}".format(value)
			return value
		
			
	else:
		return value

def convert_to_int(column):
	try:
		return column.astype(int)
	except ValueError:
		return column
	
def csv_to_html_table(filename, bw_units=None, pkt_units=None):
	# Read the CSV file, if the value is integer, leave it as integer, if float, leave it as float
	
	df = pd.read_csv(filename)

	# Apply formatting to numeric columns
	if bw_units and filename!=charts_tables_path + 'sip_packets_per_day_table_alltimehigh.csv':
		formatted_df = df.applymap(lambda x: format_bw_units_value(x, bw_units))


	elif pkt_units and filename!=charts_tables_path + 'sip_packets_per_day_table_alltimehigh.csv':
		formatted_df = df.applymap(lambda x: format_pkt_units_value(x, pkt_units))

	else:
		df = df.apply(convert_to_int, axis=0)
		formatted_df = df

	# Convert the formatted DataFrame to an HTML table
	html_table = formatted_df.to_html(index=False, escape=False)
	
	return html_table


def write_html(html_page,month,year):
	# write html_page to file function

	with open(reports_path + f'trends-daily_{cust_id}_{month}_{year}.html', 'w') as f:
		f.write(html_page)


def extract_values_from_csv(csv_file):
	values = []

	with open(charts_tables_path + csv_file, 'r') as csv_file:
		csv_reader = csv.reader(csv_file)
		
		# Skip the header row
		next(csv_reader)

		# Extract values from the first column
		for row in csv_reader:
			values.append(row[0])

	return values

def bw_units_conversion(value):

	if isinstance(value, (int, float)):
		if bw_units.lower() == 'megabytes':
			return round(value / 8000, 2)
		elif bw_units.lower() == 'gigabytes':
			return round(value / 8000000, 2)
		elif bw_units.lower() == 'terabytes':
			return round(value / 8000000000, 2)

def pkt_units_conversion(value):

	if isinstance(value, (int, float)):
		if pkt_units.lower() == 'millions':
			return round(value / 1000000, 2)
		elif pkt_units.lower() == 'billions':
			return round(value / 1000000000, 2)
		if pkt_units.lower() == 'thousands':
			return round(value / 1000, 2)

	return value


def maxpps_per_day_html_table():

	maxpps_indices = data_month.groupby(['Day of the Month'])['maxAttackPacketRatePps'].idxmax()
	maxpps_rows = data_month.loc[maxpps_indices][['startDate', 'Device Name','Policy Name','Attack Name', 'maxAttackPacketRatePps']].reset_index(drop=True)
	maxpps_rows['maxAttackPacketRatePps'] = maxpps_rows['maxAttackPacketRatePps'].apply(lambda x: f"{x:,}")
	maxpps_rows= maxpps_rows.to_html(index=False)
	return maxpps_rows


def maxbps_per_day_html_table():

	maxbps_indices = data_month.groupby(['Day of the Month'])['maxAttackRateBps'].idxmax()
	maxbps_rows = data_month.loc[maxbps_indices][['startDate', 'Device Name','Policy Name','Attack Name', 'maxAttackRateBps']].reset_index(drop=True)
	maxbps_rows['maxAttackRateBps'] = maxbps_rows['maxAttackRateBps'].apply(lambda x: f"{x / bps_unit:,.2f} {bps_units_desc}")
	maxbps_rows= maxbps_rows.to_html(index=False)
	return maxbps_rows

def events_per_day_html_table():

	# Group by day_of_month, name, Device Name, Policy Name and aggregate sum of packetCount
	events_per_day = data_month.groupby(['Day of the Month', 'Attack Name', 'Device Name', 'Policy Name']).size()

	# Get the top 5 events with the highest sum of packet counts for each day
	events_per_day_top5 = events_per_day.groupby(level=['Day of the Month'], group_keys=False).nlargest(5).apply(format_with_commas).to_frame('Security Events Count')
	events_per_day_top5 = events_per_day_top5.to_html()

	for device_ip, device_name in defensepros.items():
		events_per_day_top5=events_per_day_top5.replace(device_ip, device_name)

	return events_per_day_top5

def packets_per_day_html_table():

	# Group by day_of_month, name, Device Name, Policy Name and aggregate sum of packetCount
	packets_per_day = data_month.groupby(['Day of the Month', 'Attack Name', 'Device Name', 'Policy Name'])['packetCount'].sum()
	packets_per_day = packets_per_day.apply(pkt_units_conversion)

	# Get the top 5 events with the highest sum of packet counts for each day
	packets_per_day_top5 = packets_per_day.groupby(level=['Day of the Month'], group_keys=False).nlargest(5).apply(format_with_commas).to_frame('Malicious Packets sum')
	packets_per_day_top5 = packets_per_day_top5.to_html()

	for device_ip, device_name in defensepros.items():
		packets_per_day_top5=packets_per_day_top5.replace(device_ip, device_name)

	return packets_per_day_top5


def bandwidth_per_day_html_table():
	# Group by day_of_month, name, Device Name, Policy Name and aggregate sum of packetCount
	bandwidth_per_day = data_month.groupby(['Day of the Month', 'Attack Name', 'Device Name', 'Policy Name'])['packetBandwidth'].sum()
	bandwidth_per_day = bandwidth_per_day.apply(bw_units_conversion)

	# Get the top 5 events with the highest sum of packet counts for each day
	bandwidth_per_day_top5 = bandwidth_per_day.groupby(level=['Day of the Month'], group_keys=False).nlargest(5).apply(format_with_commas).to_frame('Malicious bandwidth sum')
	bandwidth_per_day_top5 = bandwidth_per_day_top5.to_html()

	for device_ip, device_name in defensepros.items():
		bandwidth_per_day_top5=bandwidth_per_day_top5.replace(device_ip, device_name)

	return bandwidth_per_day_top5





def events_per_day_html(epm):
	data_month_epm = data_month[data_month['Attack Name'] == epm]
	series_epm = data_month_epm.groupby(['Attack Name','Device Name','Policy Name']).size().sort_values(ascending=False).apply(format_with_commas).head(10)
	events_per_day_html = series_epm.to_frame('Security Events')
	events_per_day_html=events_per_day_html.to_html()

	for device_ip, device_name in defensepros.items():
		events_per_day_html=events_per_day_html.replace(device_ip, device_name)

	return events_per_day_html

def packets_per_day_html(ppm):
	data_month_ppm = data_month[data_month['Attack Name'] == ppm]
	series_ppm = data_month_ppm.groupby(['Attack Name','Device Name','Policy Name']).sum()['packetCount'].sort_values(ascending=False)
	# Convert units
	series_ppm = series_ppm.apply(pkt_units_conversion).apply(format_with_commas).head(10)
	packets_per_day_html = series_ppm.to_frame('Malicious Packets')
	packets_per_day_html=packets_per_day_html.to_html()

	for device_ip, device_name in defensepros.items():
		packets_per_day_html=packets_per_day_html.replace(device_ip, device_name)

	return packets_per_day_html

def bandwidth_per_day_html(bpm):
	data_month_bpm = data_month[data_month['Attack Name'] == bpm]
	series_bpm = data_month_bpm.groupby(['Attack Name','Device Name','Policy Name']).sum()['packetBandwidth'].sort_values(ascending=False)
	# Convert units
	series_bpm = series_bpm.apply(bw_units_conversion).apply(format_with_commas).head(10)

	df_bandwidth_per_day_html = series_bpm.to_frame('Malicious Bandwidth')
	df_bandwidth_per_day_html=df_bandwidth_per_day_html.to_html()

	for device_ip, device_name in defensepros.items():
		df_bandwidth_per_day_html=df_bandwidth_per_day_html.replace(device_ip, device_name)

	return df_bandwidth_per_day_html



def device_events_per_day_html(device_epm):

	for device_ip, device_name in defensepros.items():
		if device_name == device_epm:

			data_month_epm = data_month[data_month['Device Name'] == device_ip]
			device_series_epm = data_month_epm.groupby(['Device Name','Attack Name','Policy Name']).size().sort_values(ascending=False).apply(format_with_commas).head(10)
			device_events_per_day_html = device_series_epm.to_frame('Security Events')
			device_events_per_day_html=device_events_per_day_html.to_html().replace(device_ip, device_name)
			
	return device_events_per_day_html

def device_packets_per_day_html(device_ppm):

	for device_ip, device_name in defensepros.items():
		
		if device_name == device_ppm:
			data_month_ppm = data_month[data_month['Device Name'] == device_ip]
			device_series_ppm = data_month_ppm.groupby(['Device Name','Attack Name','Policy Name']).sum()['packetCount'].sort_values(ascending=False)
			device_series_ppm = device_series_ppm.apply(pkt_units_conversion).apply(format_with_commas).head(10)
			device_packets_per_day_html = device_series_ppm.to_frame('Malicious Packets')
			device_packets_per_day_html=device_packets_per_day_html.to_html().replace(device_ip, device_name)
	return device_packets_per_day_html

def device_bandwidth_per_day_html(device_bpm):
	for device_ip, device_name in defensepros.items():
		if device_name == device_bpm:
			data_month_bpm = data_month[data_month['Device Name'] == device_ip]
			device_series_bpm = data_month_bpm.groupby(['Device Name','Attack Name','Policy Name']).sum()['packetBandwidth'].sort_values(ascending=False)
			device_series_bpm = device_series_bpm.apply(bw_units_conversion).apply(format_with_commas).head(10)
			device_df_bandwidth_per_day_html = device_series_bpm.to_frame('Malicious Bandwidth')
			device_df_bandwidth_per_day_html= device_df_bandwidth_per_day_html.to_html().replace(device_ip, device_name)


	return device_df_bandwidth_per_day_html


def policy_events_per_day_html(policy_epm):

	data_month_epm = data_month[data_month['Policy Name'] == policy_epm]
	series_epm = data_month_epm.groupby(['Policy Name','Attack Name','Device Name']).size().sort_values(ascending=False).apply(format_with_commas).head(10)
	events_per_day_html = series_epm.to_frame('Security Events')
	events_per_day_html=events_per_day_html.to_html()

	for device_ip, device_name in defensepros.items():
		events_per_day_html=events_per_day_html.replace(device_ip, device_name)
		
	return events_per_day_html

def policy_packets_per_day_html(policy_ppm):
	data_month_ppm = data_month[data_month['Policy Name'] == policy_ppm]
	series_ppm = data_month_ppm.groupby(['Policy Name','Attack Name','Device Name']).sum()['packetCount'].sort_values(ascending=False)
	series_ppm = series_ppm.apply(pkt_units_conversion).apply(format_with_commas).head(10)
	packets_per_day_html = series_ppm.to_frame('Malicious Packets')
	packets_per_day_html=packets_per_day_html.to_html()
	
	for device_ip, device_name in defensepros.items():
		packets_per_day_html=packets_per_day_html.replace(device_ip, device_name)
	
	return packets_per_day_html

def policy_bandwidth_per_day_html(policy_bpm):
	data_month_bpm = data_month[data_month['Policy Name'] == policy_bpm]
	series_bpm = data_month_bpm.groupby(['Policy Name','Attack Name','Device Name']).sum()['packetBandwidth'].sort_values(ascending=False)
	series_bpm = series_bpm.apply(bw_units_conversion).apply(format_with_commas).head(10)
	df_bandwidth_per_day_html = series_bpm.to_frame('Malicious Bandwidth')
	df_bandwidth_per_day_html=df_bandwidth_per_day_html.to_html()

	for device_ip, device_name in defensepros.items():
		df_bandwidth_per_day_html=df_bandwidth_per_day_html.replace(device_ip, device_name)
	
	return df_bandwidth_per_day_html


def sip_events_per_day_html(sip_epm):

	data_month_epm = data_month[data_month['Source IP'] == sip_epm]
	series_epm = data_month_epm.groupby(['Source IP','Attack Name','Device Name','Policy Name']).size().sort_values(ascending=False).apply(format_with_commas).head(10)
	events_per_day_html = series_epm.to_frame('Security Events')
	events_per_day_html=events_per_day_html.to_html()

	for device_ip, device_name in defensepros.items():
		events_per_day_html=events_per_day_html.replace(device_ip, device_name)
		
	return events_per_day_html


def sip_packets_per_day_html(sip_ppm):
	data_month_ppm = data_month[data_month['Source IP'] == sip_ppm]
	series_ppm = data_month_ppm.groupby(['Source IP','Attack Name','Device Name','Policy Name']).sum()['packetCount'].sort_values(ascending=False)
	series_ppm = series_ppm.apply(pkt_units_conversion).apply(format_with_commas).head(10)
	packets_per_day_html = series_ppm.to_frame('Malicious Packets')
	packets_per_day_html=packets_per_day_html.to_html()
	
	for device_ip, device_name in defensepros.items():
		packets_per_day_html=packets_per_day_html.replace(device_ip, device_name)
	
	return packets_per_day_html

def sip_bandwidth_per_day_html(sip_bpm):
	data_month_bpm = data_month[data_month['Source IP'] == sip_bpm]
	series_bpm = data_month_bpm.groupby(['Source IP','Attack Name','Device Name','Policy Name']).sum()['packetBandwidth'].sort_values(ascending=False)
	series_bpm = series_bpm.apply(bw_units_conversion).apply(format_with_commas).head(10)
	df_bandwidth_per_day_html = series_bpm.to_frame('Malicious Bandwidth')
	df_bandwidth_per_day_html=df_bandwidth_per_day_html.to_html()

	for device_ip, device_name in defensepros.items():
		df_bandwidth_per_day_html=df_bandwidth_per_day_html.replace(device_ip, device_name)
	
	return df_bandwidth_per_day_html





def format_with_commas(value):
	return '{:,}'.format(value)


if __name__ == '__main__':


	maxpps_per_day_trends = convert_csv_to_list_of_lists(charts_tables_path + 'maxpps_per_day_last_month.csv')

	# Malicious bandwidth per day
	maxbps_per_day_trends = convert_csv_to_list_of_lists(charts_tables_path + 'maxbps_per_day_last_month.csv')


	# Events per day count
	events_per_day_trends = convert_csv_to_list_of_lists(charts_tables_path + 'events_per_day_last_month.csv')

	# Malicious bandwidth per day
	packets_per_day_trends = convert_csv_to_list_of_lists(charts_tables_path + 'packets_per_day_last_month.csv')

	# Malicious bandwidth per day
	bandwidth_per_day_trends = convert_csv_to_list_of_lists(charts_tables_path + 'bandwidth_per_day_last_month.csv')


	# Traffic utilization
	if db_from_forensics:
		traffic_per_device_combined_trends_bps = [['Date,Traffic Utilization(Mbps),Blocked traffic,Excluded traffic']]
		attacks_per_device_combined_trends_bps = [['Date,Traffic Utilization(Mbps),Blocked traffic,Excluded traffic']]

	else:
		traffic_per_device_combined_trends_bps = convert_csv_to_list_of_lists(charts_tables_path + 'traffic_per_device_bps.csv')
		attacks_per_device_combined_trends_bps = convert_csv_to_list_of_lists(charts_tables_path + 'attacks_per_device_bps.csv')


	################################################# Events, packets and bandwidth trends by Attack name sorted by the last month ##########################################################
	# events_trends = convert_csv_to_list_of_lists(charts_tables_path + 'events_per_day_chart_lm.csv')
	# events_trends_move = trends_move(events_trends, 'events')
	# events_trends_table = csv_to_html_table(charts_tables_path + 'events_per_day_table_lm.csv')

	# packets_trends_chart = convert_csv_to_list_of_lists(charts_tables_path + 'packets_per_day_chart_lm.csv')
	# packets_trends_chart = convert_packets_units(packets_trends_chart, pkt_units)

	# if pkt_units is not None:
	# 	packets_trends_move_text = trends_move(packets_trends_chart, ' packets(' + pkt_units + ')')
	# 	packets_table = csv_to_html_table(charts_tables_path + 'packets_per_day_table_lm.csv',bw_units=None, pkt_units=pkt_units)

	# else:
	# 	packets_trends_move_text = trends_move(packets_trends_chart, ' packets')
	# 	packets_table = csv_to_html_table(charts_tables_path + 'packets_per_day_table_lm.csv',bw_units=None, pkt_units=None)


	# bw_trends = convert_csv_to_list_of_lists(charts_tables_path + 'bandwidth_per_day_chart_lm.csv')
	# bw_trends = convert_bw_units(bw_trends, bw_units)
	# bw_trends_move = trends_move(bw_trends, bw_units)
	# bw_table = csv_to_html_table(charts_tables_path + 'bandwidth_per_day_table_lm.csv',bw_units)

	################################################# Analyze deeper top category ##########################################################

	#1 Create a data frame
	con = sqlite3.connect(db_path + 'database_' + cust_id + '_' + str(month) + '_' + str(year) + '.sqlite')
	# data = pd.read_sql_query("SELECT * from attacks", con)
	data_month = pd.read_sql_query(f"SELECT deviceName as 'Device Name',month,year,packetBandwidth,name as 'Attack Name',packetCount,ruleName as 'Policy Name',category,sourceAddress as 'Source IP',destAddress,startTime,endTime,startDate,attackIpsId,actionType,maxAttackPacketRatePps,maxAttackRateBps,destPort,protocol,startDayOfMonth as 'Day of the Month' from attacks", con)

	#export data to csv
	data_month.to_csv(reports_path +'database_'+cust_id+'_'+str(month)+'_'+str(year)+'.csv', encoding='utf-8', index=False)

	con.close()

	#2 Extract Top Attacks list

	events_per_day_top_list=extract_values_from_csv('events_per_day_table_alltimehigh.csv')
	packets_per_day_top_list=extract_values_from_csv('packets_per_day_table_alltimehigh.csv')
	bandwidth_per_day_top_list=extract_values_from_csv('bandwidth_per_day_table_alltimehigh.csv')

	device_events_per_day_top_list=extract_values_from_csv('device_events_per_day_table_alltimehigh.csv') #list of devices
	device_packets_per_day_top_list=extract_values_from_csv('device_packets_per_day_table_alltimehigh.csv') #list of devices
	device_bandwidth_per_day_top_list=extract_values_from_csv('device_bandwidth_per_day_table_alltimehigh.csv') #list of devices

	policy_events_per_day_top_list=extract_values_from_csv('policy_events_per_day_table_alltimehigh.csv')
	policy_packets_per_day_top_list=extract_values_from_csv('policy_packets_per_day_table_alltimehigh.csv')
	policy_bandwidth_per_day_top_list=extract_values_from_csv('policy_bandwidth_per_day_table_alltimehigh.csv')

	sip_events_per_day_top_list=extract_values_from_csv('sip_events_per_day_table_alltimehigh.csv')
	sip_packets_per_day_top_list=extract_values_from_csv('sip_packets_per_day_table_alltimehigh.csv')
	sip_bandwidth_per_day_top_list=extract_values_from_csv('sip_bandwidth_per_day_table_alltimehigh.csv')

	#3 Create empty html table
	events_per_day_html_final = ''
	packets_per_day_html_final = ''
	bandwidth_per_day_html_final = ''

	device_events_per_day_html_final = ''
	device_packets_per_day_html_final = ''
	device_bandwidth_per_day_html_final = ''

	policy_events_per_day_html_final = ''
	policy_packets_per_day_html_final = ''
	policy_bandwidth_per_day_html_final = ''

	sip_events_per_day_html_final = ''
	sip_packets_per_day_html_final = ''
	sip_bandwidth_per_day_html_final = ''

	#4 Iterate through each Device and popluate the html table

	for index, value in enumerate(events_per_day_top_list):
		events_per_day_html_final+=f'<h4>Distribution of topmost Security Events for attack "{value}" across devices and policies</h4>'
		events_per_day_html_final+= events_per_day_html(events_per_day_top_list[index])

	for index, value in enumerate(packets_per_day_top_list):
		packets_per_day_html_final+=f'<h4>Distribution of topmost Malicious packets for attack "{value}" across devices and policies</h4>'
		packets_per_day_html_final+= packets_per_day_html(packets_per_day_top_list[index])
		
	for index, value in enumerate(bandwidth_per_day_top_list):
		bandwidth_per_day_html_final+=f'<h4>Distribution of topmost Malicious Bandwidth for attack "{value}" across devices and policies</h4>'
		bandwidth_per_day_html_final+= bandwidth_per_day_html(bandwidth_per_day_top_list[index])



	for index, value in enumerate(device_events_per_day_top_list):
		device_events_per_day_html_final+=f'<h4>Distribution of topmost Security events for device "{value}" across policies</h4>'
		device_events_per_day_html_final+= device_events_per_day_html(device_events_per_day_top_list[index])

	for index, value in enumerate(device_packets_per_day_top_list):
		device_packets_per_day_html_final+=f'<h4>Distribution of topmost malicious packets for device "{value}" across policies</h4>'
		device_packets_per_day_html_final+= device_packets_per_day_html(device_packets_per_day_top_list[index])

	for index, value in enumerate(device_bandwidth_per_day_top_list):
		device_bandwidth_per_day_html_final+=f'<h4>Distribution of topmost malicious bandwidth for device "{value}" across policies</h4>'
		device_bandwidth_per_day_html_final+= device_bandwidth_per_day_html(device_packets_per_day_top_list[index])


	for index, value in enumerate(policy_events_per_day_top_list):
		policy_events_per_day_html_final+=f'<h4>Distribution of topmost Security events for policy "{value}" across devices</h4>'
		policy_events_per_day_html_final+= policy_events_per_day_html(policy_events_per_day_top_list[index])

	for index, value in enumerate(policy_packets_per_day_top_list):
		policy_packets_per_day_html_final+=f'<h4>Distribution of topmost Malicious packets for policy "{value}" across devices</h4>'
		policy_packets_per_day_html_final+= policy_packets_per_day_html(policy_packets_per_day_top_list[index])
		
	for index, value in enumerate(policy_bandwidth_per_day_top_list):
		policy_bandwidth_per_day_html_final+=f'<h4>Distribution of topmost Malicious bandwidth for policy "{value}" across devices</h4>'
		policy_bandwidth_per_day_html_final+= policy_bandwidth_per_day_html(policy_bandwidth_per_day_top_list[index])


	for index, value in enumerate(sip_events_per_day_top_list):
		sip_events_per_day_html_final+=f'<h4>Distribution of topmost Security events for Source IP {value}</h4>'
		sip_events_per_day_html_final+= sip_events_per_day_html(sip_events_per_day_top_list[index])

	for index, value in enumerate(sip_packets_per_day_top_list):
		sip_packets_per_day_html_final+=f'<h4>Distribution of topmost malicious packets for Source IP {value}</h4>'
		sip_packets_per_day_html_final+= sip_packets_per_day_html(sip_packets_per_day_top_list[index])
		
	for index, value in enumerate(sip_bandwidth_per_day_top_list):
		sip_bandwidth_per_day_html_final+=f'<h4>Distribution of topmost malicious bandwidth for Source IP {value}</h4>'
		sip_bandwidth_per_day_html_final+= sip_bandwidth_per_day_html(sip_bandwidth_per_day_top_list[index])


	#5 Generate html for the last month


	maxpps_per_day_table = maxpps_per_day_html_table()
	maxbps_per_day_table = maxbps_per_day_html_table()


	events_per_day_table = events_per_day_html_table()
	packets_per_day_table = packets_per_day_html_table()
	bandwidth_per_day_table = bandwidth_per_day_html_table()


	################################################# Events, packets and bandwidth trends by Attack name sorted by the overall sum of all months together ##########################################################


	events_trends_alltimehigh = convert_csv_to_list_of_lists(charts_tables_path + 'events_per_day_chart_alltimehigh.csv')
	events_trends_move_alltimehigh = trends_move(events_trends_alltimehigh, 'events')
	events_trends_table_alltimehigh = csv_to_html_table(charts_tables_path + 'events_per_day_table_alltimehigh.csv')
	
	
	packets_trends_chart_alltimehigh = convert_csv_to_list_of_lists(charts_tables_path + 'packets_per_day_chart_alltimehigh.csv')
	packets_trends_chart_alltimehigh = convert_packets_units(packets_trends_chart_alltimehigh, pkt_units)

	if pkt_units is not None:
		packets_trends_move_text_alltimehigh = trends_move(packets_trends_chart_alltimehigh, ' packets(' + pkt_units + ')')
		packets_table_alltimehigh = csv_to_html_table(charts_tables_path + 'packets_per_day_table_alltimehigh.csv',bw_units=None, pkt_units=pkt_units)


	else:
		packets_trends_move_text_alltimehigh = trends_move(packets_trends_chart_alltimehigh, ' packets')
		packets_table_alltimehigh = csv_to_html_table(charts_tables_path + 'packets_per_day_table_alltimehigh.csv',bw_units=None, pkt_units=None)




	bw_trends_alltimehigh = convert_csv_to_list_of_lists(charts_tables_path + 'bandwidth_per_day_chart_alltimehigh.csv')
	bw_trends_alltimehigh = convert_bw_units(bw_trends_alltimehigh, bw_units)
	bw_trends_move_alltimehigh = trends_move(bw_trends_alltimehigh, bw_units)
	bw_table_alltimehigh = csv_to_html_table(charts_tables_path + 'bandwidth_per_day_table_alltimehigh.csv',bw_units)


	################################################# Events, packets and bandwidth trends by Device  ##########################################################

	events_by_device_trends_chart_data = convert_csv_to_list_of_lists(charts_tables_path + 'device_events_per_day_chart_alltimehigh.csv')
	events_by_device_trends_move_text = trends_move(events_by_device_trends_chart_data, 'events')
	events_by_device_table = csv_to_html_table(charts_tables_path + 'device_events_per_day_table_alltimehigh.csv')

	packets_by_device_trends_chart_data = convert_csv_to_list_of_lists(charts_tables_path + 'device_packets_per_day_chart_alltimehigh.csv')
	packets_by_device_trends_chart_data = convert_packets_units(packets_by_device_trends_chart_data, pkt_units)
	packets_by_device_trends_move_text = trends_move(packets_by_device_trends_chart_data, ' packets(' + pkt_units + ')')
	packets_by_device_table = csv_to_html_table(charts_tables_path + 'device_packets_per_day_table_alltimehigh.csv',bw_units=None, pkt_units=pkt_units)

	bw_by_device_trends_chart_data = convert_csv_to_list_of_lists(charts_tables_path + 'device_bandwidth_per_day_chart_alltimehigh.csv')
	bw_by_device_trends_chart_data = convert_bw_units(bw_by_device_trends_chart_data, bw_units)
	bw_by_device_trends_move_text = trends_move(bw_by_device_trends_chart_data, bw_units)
	bw_by_device_table = csv_to_html_table(charts_tables_path + 'device_bandwidth_per_day_table_alltimehigh.csv',bw_units)


	################################################# Events, packets and bandwidth trends by Policy ##########################################################

	policy_events_trends_chart = convert_csv_to_list_of_lists(charts_tables_path + 'policy_events_per_day_chart_alltimehigh.csv')
	policy_events_trends_move_text = trends_move(policy_events_trends_chart, 'events')
	policy_events_trends_table = csv_to_html_table(charts_tables_path + 'policy_events_per_day_table_alltimehigh.csv')


	policy_packets_trends_chart = convert_csv_to_list_of_lists(charts_tables_path + 'policy_packets_per_day_chart_alltimehigh.csv')
	policy_packets_trends_chart = convert_packets_units(policy_packets_trends_chart, pkt_units)
	policy_packets_trends_move_text = trends_move(policy_packets_trends_chart, ' packets(' + pkt_units + ')')
	policy_packets_table = csv_to_html_table(charts_tables_path + 'policy_packets_per_day_table_alltimehigh.csv',bw_units=None, pkt_units=pkt_units)


	policy_bw_trends_chart = convert_csv_to_list_of_lists(charts_tables_path + 'policy_bandwidth_per_day_chart_alltimehigh.csv')
	policy_bw_trends_chart = convert_bw_units(policy_bw_trends_chart, bw_units)
	policy_bw_trends_move_text = trends_move(policy_bw_trends_chart, bw_units)
	policy_bw_table = csv_to_html_table(charts_tables_path + 'policy_bandwidth_per_day_table_alltimehigh.csv',bw_units)


	################################################# Top source IP(bw is Megabytes) ##########################################################		
	sip_events_trends_chart = convert_csv_to_list_of_lists(charts_tables_path + 'sip_events_per_day_chart_alltimehigh.csv')
	sip_events_trends_move_text = trends_move(sip_events_trends_chart, 'events')
	sip_events_trends_table = csv_to_html_table(charts_tables_path + 'sip_events_per_day_table_alltimehigh.csv')

	sip_packets_trends_chart = convert_csv_to_list_of_lists(charts_tables_path + 'sip_packets_per_day_chart_alltimehigh.csv')
	sip_packets_trends_chart = convert_packets_units(sip_packets_trends_chart, pkt_units)

	sip_packets_trends_move_text = trends_move(sip_packets_trends_chart, ' packets')
	sip_packets_table = csv_to_html_table(charts_tables_path + 'sip_packets_per_day_table_alltimehigh.csv',bw_units=None, pkt_units=None)



	sip_bw_trends_chart = convert_csv_to_list_of_lists(charts_tables_path + 'sip_bandwidth_per_day_chart_alltimehigh.csv')
	# sip_bw_trends_chart = convert_bw_units(sip_bw_trends_chart, sip_bw_units)
	# sip_bw_trends_move_text = trends_move(sip_bw_trends_chart, sip_bw_units)
	sip_bw_table = csv_to_html_table(charts_tables_path + 'sip_bandwidth_per_day_table_alltimehigh.csv')



	html_page = f"""
	<!DOCTYPE html>
	<html lang="en">
	<head>
	<meta charset="UTF-8">
	<meta name="viewport" content="width=device-width, initial-scale=1.0">

	  <script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>
		<script type="text/javascript">
		  google.charts.load('current', {{'packages':['corechart']}});
		  google.charts.setOnLoadCallback(drawChart);




		  function drawChart() {{
		  
			
			
			// Convert epoch timestamps to Date objects before passing to Google Charts
			var raw_traffic_per_device_combined_trends_bps_data = {traffic_per_device_combined_trends_bps}.map(row => {{
				return [new Date(row[0]), ...row.slice(1)]; // Convert first column, keep others unchanged
			}});

			// Convert epoch timestamps to Date objects before passing to Google Charts
			var raw_attacks_per_device_combined_trends_bps_data = {attacks_per_device_combined_trends_bps}.map(row => {{
				return [new Date(row[0]), ...row.slice(1)]; // Convert first column, keep others unchanged
			}});

			var traffic_per_device_combined_trends_bps_data = google.visualization.arrayToDataTable(raw_traffic_per_device_combined_trends_bps_data);
	
			var attacks_per_device_combined_trends_bps_data = google.visualization.arrayToDataTable(raw_attacks_per_device_combined_trends_bps_data);

			// Function to generate an array of the same red color for all series for attacks data
			function generateSameRedColor(numColors) {{
				return Array(numColors).fill('rgb(200, 0, 0)'); // All red
			}}

			function generateGradientBlueColors(numColors) {{
				return Array.from({{ length: numColors }}, (_, i) => {{
					let blueIntensity = Math.max(120, 200 - i * 20); // Decrease blue intensity for contrast
					let redComponent = Math.min(50 + i * 5, 80); // Slight increase in red for variety
					let greenComponent = Math.min(100 + i * 5, 130); // Slight increase in green for contrast
					return `rgb(${{redComponent}}, ${{greenComponent}}, ${{blueIntensity}})`;
				}});
			}}

			// Determine the number of series dynamically for attack data for red coloring
			let numSeries = attacks_per_device_combined_trends_bps_data.getNumberOfColumns() - 1; // Exclude timestamp column
			let redColors = generateSameRedColor(numSeries);
			let blueColors = generateGradientBlueColors(numSeries);


			var maxpps_per_day_data = google.visualization.arrayToDataTable({maxpps_per_day_trends});
			var maxbps_per_day_data = google.visualization.arrayToDataTable({maxbps_per_day_trends});

			var events_per_day_data = google.visualization.arrayToDataTable({events_per_day_trends});
			var packets_per_day_data = google.visualization.arrayToDataTable({packets_per_day_trends});
			var bandwidth_per_day_data = google.visualization.arrayToDataTable({bandwidth_per_day_trends});

			var events_per_day_data_alltimehigh = google.visualization.arrayToDataTable({events_trends_alltimehigh});
			var packets_per_day_data_alltimehigh = google.visualization.arrayToDataTable({packets_trends_chart_alltimehigh});
			var bandwidth_per_day_data_alltimehigh = google.visualization.arrayToDataTable({bw_trends_alltimehigh});

			var events_per_day_by_device_data = google.visualization.arrayToDataTable({events_by_device_trends_chart_data});
			var packets_per_day_by_device_data = google.visualization.arrayToDataTable({packets_by_device_trends_chart_data});
			var bandwidth_per_day_by_device_data = google.visualization.arrayToDataTable({bw_by_device_trends_chart_data});

			var sip_events_per_day_data = google.visualization.arrayToDataTable({sip_events_trends_chart});
			var sip_packets_per_day_data = google.visualization.arrayToDataTable({sip_packets_trends_chart});
			var sip_bandwidth_per_day_data = google.visualization.arrayToDataTable({sip_bw_trends_chart});

			var policy_events_per_day_data = google.visualization.arrayToDataTable({policy_events_trends_chart });
			var policy_packets_per_day_data = google.visualization.arrayToDataTable({policy_packets_trends_chart });
			var policy_bandwidth_per_day_data = google.visualization.arrayToDataTable({policy_bw_trends_chart });

			var traffic_per_device_combined_trends_bps_options = {{
				title: 'Traffic utilization per device combined',
				vAxis: {{
					title: 'Traffic Volume (Mbps)',
					minValue: 0
					}},
				hAxis: {{
					title: 'Date and time'
					}},
				isStacked: false,
				colors: blueColors,
				focusTarget: 'category',
				legend: {{position: 'top', maxLines: 5}},
				width: '100%',
				explorer: {{
					actions: ['dragToZoom', 'rightClickToReset'],
					axis: 'horizontal',
					maxZoomIn: 0.01,
					maxZoomOut: 20
					}}
				}};

			var attacks_per_device_combined_trends_bps_options = {{
				title: 'All Attacks per device combined',
				vAxis: {{
					title: 'Attack Volume (Mbps)',
					minValue: 0
					}},
				hAxis: {{
					title: 'Date and time'
					}},
				isStacked: true,
				colors: redColors,
				focusTarget: 'category',
				legend: {{position: 'top', maxLines: 5}},
				width: '100%',
				explorer: {{
					actions: ['dragToZoom', 'rightClickToReset'],
					axis: 'horizontal',
					maxZoomIn: 0.01,
					maxZoomOut: 20
					}}
				}};

			var maxpps_per_day_options = {{
			  title: 'Highest PPS rate attack of the day, last month (packet units as is)',
			  vAxis: {{minValue: 0}},
			  hAxis: {{ticks: maxpps_per_day_data.getDistinctValues(0),minTextSpacing:1,showTextEvery:1}},
			  isStacked: false,
			  legend: {{position: 'top', maxLines: 5}},
			  width: '100%'
			}};

			var maxbps_per_day_options = {{
			  title: 'Highest BPS rate attack of the day, last month (units {bps_units_desc})',
			  vAxis: {{minValue: 0}},
			  hAxis: {{ticks: maxbps_per_day_data.getDistinctValues(0),minTextSpacing:1,showTextEvery:1}},
			  isStacked: false,
			  legend: {{position: 'top', maxLines: 5}},
			  width: '100%'
			}};
			
			var events_per_day_options = {{
			  title: 'Events per day, last month',
			  vAxis: {{minValue: 0}},
			  hAxis: {{ticks: events_per_day_data.getDistinctValues(0),minTextSpacing:1,showTextEvery:1}},
			  isStacked: false,
			  legend: {{position: 'top', maxLines: 5}},
			  width: '100%'
			}};

			  var packets_per_day_options = {{
			  title: 'Malicious packets per day, last month (units {pkt_units})',
			  vAxis: {{minValue: 0}},
			  hAxis: {{ticks: packets_per_day_data.getDistinctValues(0),minTextSpacing:1,showTextEvery:1}},
			  isStacked: false,
			  legend: {{position: 'top', maxLines: 5}},
			  width: '100%'
			}};

			var bandwidth_per_day_options = {{
			  title: 'Malicious bandwidth per day, last month (units {bw_units})',
			  vAxis: {{minValue: 0}},
			  hAxis: {{ticks: bandwidth_per_day_data.getDistinctValues(0),minTextSpacing:1,showTextEvery:1}},
			  isStacked: false,
			  legend: {{position: 'top', maxLines: 5}},
			  width: '100%'
			}};

			var attack_events_per_day_options = {{
			  title: 'Security Events trends - TopN by last day',
			  vAxis: {{minValue: 0}},
			  hAxis: {{ticks: events_per_day_data.getDistinctValues(0),minTextSpacing:1,showTextEvery:1}},
			  isStacked: false,
			  focusTarget: 'category',
			  legend: {{position: 'top', maxLines: 5}},
			  width: '100%'
			}};


			var attack_packets_per_day_options = {{
			  title: 'Malicious Packets trends (units {pkt_units}) - TopN by last day',
			  vAxis: {{minValue: 0}},
			  hAxis: {{ticks: events_per_day_data.getDistinctValues(0),minTextSpacing:1,showTextEvery:1}},
			  isStacked: false,
			  focusTarget: 'category',
			  legend: {{position: 'top', maxLines: 5}},
			  width: '100%'
			}};

			var attack_bandwidth_per_day_options = {{
			  title: 'Malicious Bandwidth trends (units {bw_units}) - TopN by last day',
			  vAxis: {{minValue: 0}},
			  hAxis: {{ticks: events_per_day_data.getDistinctValues(0),minTextSpacing:1,showTextEvery:1}},
			  isStacked: false,
			  focusTarget: 'category',
			  legend: {{position: 'top', maxLines: 5}},
			  width: '100%'
			}};



			var events_per_day_options_alltimehigh = {{
			  title: 'Security Events trends - TopN all time high',
			  vAxis: {{minValue: 0}},
			  hAxis: {{ticks: events_per_day_data.getDistinctValues(0),minTextSpacing:1,showTextEvery:1}},
			  isStacked: false,
			  focusTarget: 'category',
			  legend: {{position: 'top', maxLines: 5}},
			  width: '100%'
			}};

			var packets_per_day_options_alltimehigh = {{
			  title: 'Malicious Packets trends (units {pkt_units}) - TopN all time high',
			  vAxis: {{minValue: 0}},
			  hAxis: {{ticks: events_per_day_data.getDistinctValues(0),minTextSpacing:1,showTextEvery:1}},
			  isStacked: false,
			  focusTarget: 'category',
			  legend: {{position: 'top', maxLines: 5}},
			  width: '100%'
			}};

			var bandwidth_per_day_options_alltimehigh = {{
			  title: 'Malicious Bandwidth trends (units {bw_units}) - TopN all time high',
			  vAxis: {{minValue: 0}},
			  isStacked: false,
			  focusTarget: 'category',
			  legend: {{position: 'top', maxLines: 5}},
			  width: '100%'
			}};

			var events_per_day_by_device_options = {{
			  title: 'Events by device trends',
			  vAxis: {{minValue: 0}},
			  hAxis: {{ticks: events_per_day_data.getDistinctValues(0),minTextSpacing:1,showTextEvery:1}},
			  isStacked: false,
			  focusTarget: 'category',
			  legend: {{position: 'top', maxLines: 5}},
			  width: '100%'
			}};

			var packets_per_day_by_device_options = {{
			  title: 'Packets by device trends (units {pkt_units})',
			  vAxis: {{minValue: 0}},
			  hAxis: {{ticks: events_per_day_data.getDistinctValues(0),minTextSpacing:1,showTextEvery:1}},
			  isStacked: false,
			  focusTarget: 'category',
			  legend: {{position: 'top', maxLines: 5}},
			  width: '100%'
			}};

			var bandwidth_per_day_by_device_options = {{
			  title: 'Malicious Bandwidth by device trends (units {bw_units})',
			  vAxis: {{minValue: 0}},
			  hAxis: {{ticks: events_per_day_data.getDistinctValues(0),minTextSpacing:1,showTextEvery:1}},
			  isStacked: false,
			  focusTarget: 'category',
			  legend: {{position: 'top', maxLines: 5}},
			  width: '100%'
			}};

			var sip_events_per_day_options = {{
			  title: 'Security Events trends by source IP',
			  vAxis: {{minValue: 0}},
			  hAxis: {{ticks: events_per_day_data.getDistinctValues(0),minTextSpacing:1,showTextEvery:1}},
			  isStacked: false,
			  focusTarget: 'category',
			  legend: {{position: 'top', maxLines: 5}},
			  width: '100%'
			}};

			var sip_packets_per_day_options = {{
			  title: 'Malicious Packets trends (units {pkt_units}) by source IP',
			  vAxis: {{minValue: 0}},
			  hAxis: {{ticks: events_per_day_data.getDistinctValues(0),minTextSpacing:1,showTextEvery:1}},
			  isStacked: false,
			  focusTarget: 'category',
			  legend: {{position: 'top', maxLines: 5}},
			  width: '100%'
			}};

			var sip_bandwidth_per_day_options = {{
			  title: 'Malicious Bandwidth trends (Megabytes) by source IP',
			  vAxis: {{minValue: 0}},
			  hAxis: {{ticks: events_per_day_data.getDistinctValues(0),minTextSpacing:1,showTextEvery:1}},
			  isStacked: false,
			  focusTarget: 'category',
			  legend: {{position: 'top', maxLines: 5}},
			  width: '100%'
			}};

			var policy_events_per_day_options = {{
			  title: 'Security Events trends by Policy Name',
			  vAxis: {{minValue: 0}},
			  hAxis: {{ticks: events_per_day_data.getDistinctValues(0),minTextSpacing:1,showTextEvery:1}},
			  isStacked: false,
			  focusTarget: 'category',
			  legend: {{position: 'top', maxLines: 5}},
			  width: '100%'
			}};

			var policy_packets_per_day_options = {{
			  title: 'Malicious Packets trends (units {pkt_units}) by Policy Name',
			  vAxis: {{minValue: 0}},
			  hAxis: {{ticks: events_per_day_data.getDistinctValues(0),minTextSpacing:1,showTextEvery:1}},
			  isStacked: false,
			  focusTarget: 'category',
			  legend: {{position: 'top', maxLines: 5}},
			  width: '100%'
			}};

			var policy_bandwidth_per_day_options = {{
			  title: 'Malicious Bandwidth trends (units {bw_units}) by Policy Name',
			  vAxis: {{minValue: 0}},
			  hAxis: {{ticks: events_per_day_data.getDistinctValues(0),minTextSpacing:1,showTextEvery:1}},
			  isStacked: false,
			  focusTarget: 'category',
			  legend: {{position: 'top', maxLines: 5}},
			  width: '100%'
			}};

			var traffic_per_device_combined_trends_bps_chart = new google.visualization.AreaChart(document.getElementById('traffic_per_device_combined_trends_bps_chart_div'));
			var attacks_per_device_combined_trends_bps_chart = new google.visualization.AreaChart(document.getElementById('attacks_per_device_combined_trends_bps_chart_div'));

			var maxpps_per_day_chart = new google.visualization.AreaChart(document.getElementById('maxpps_per_day_chart_div'));
			var maxbps_per_day_chart = new google.visualization.AreaChart(document.getElementById('maxbps_per_day_chart_div'));

			var events_per_day_chart = new google.visualization.AreaChart(document.getElementById('events_per_day_chart_div'));
			var bandwidth_per_day_chart = new google.visualization.AreaChart(document.getElementById('bandwidth_per_day_chart_div'));
			var packets_per_day_chart = new google.visualization.AreaChart(document.getElementById('packets_per_day_chart_div'));

			var events_per_day_chart_alltimehigh = new google.visualization.AreaChart(document.getElementById('events_per_day_chart_div_alltimehigh'));
			var packets_per_day_chart_alltimehigh = new google.visualization.AreaChart(document.getElementById('packets_per_day_chart_div_alltimehigh'));
			var bandwidth_per_day_chart_alltimehigh = new google.visualization.AreaChart(document.getElementById('bandwidth_per_day_chart_div_alltimehigh'));

			var events_per_day_by_device_chart = new google.visualization.AreaChart(document.getElementById('events_per_day_by_device_chart_div'));
			var packets_per_day_by_device_chart = new google.visualization.AreaChart(document.getElementById('packets_per_day_by_device_chart_div'));
			var bandwidth_per_day_by_device_chart = new google.visualization.AreaChart(document.getElementById('bandwidth_per_day_by_device_chart_div'));

			var sip_events_per_day_chart = new google.visualization.AreaChart(document.getElementById('sip_events_per_day_chart_div'));
			var sip_packets_per_day_chart = new google.visualization.AreaChart(document.getElementById('sip_packets_per_day_chart_div'));
			var sip_bandwidth_per_day_chart = new google.visualization.AreaChart(document.getElementById('sip_bandwidth_per_day_chart_div'));		

			var policy_events_per_day_chart = new google.visualization.AreaChart(document.getElementById('policy_events_per_day_chart_div'));
			var policy_packets_per_day_chart = new google.visualization.AreaChart(document.getElementById('policy_packets_per_day_chart_div'));
			var policy_bandwidth_per_day_chart = new google.visualization.AreaChart(document.getElementById('policy_bandwidth_per_day_chart_div'));

            // Create checkboxes for Traffic utilization per device combined
            createCheckboxes('traffic_per_device_combined_trends_bps_chart_div', raw_traffic_per_device_combined_trends_bps_data, function(selectedCategories) {{
                var filteredData = filterDataByCategories(raw_traffic_per_device_combined_trends_bps_data, selectedCategories);
                var filteredDataTable = google.visualization.arrayToDataTable(filteredData);
                traffic_per_device_combined_trends_bps_chart.draw(filteredDataTable, traffic_per_device_combined_trends_bps_options);
            }});

            // Create checkboxes for Attacks per device combined
            createCheckboxes('attacks_per_device_combined_trends_bps_chart_div', raw_attacks_per_device_combined_trends_bps_data, function(selectedCategories) {{
                var filteredData = filterDataByCategories(raw_attacks_per_device_combined_trends_bps_data, selectedCategories);
                var filteredDataTable = google.visualization.arrayToDataTable(filteredData);
                attacks_per_device_combined_trends_bps_chart.draw(filteredDataTable, attacks_per_device_combined_trends_bps_options);
            }});

			// Create checkboxes for each chart
			createCheckboxes('events_per_day_chart_div_alltimehigh', {events_trends_alltimehigh}, function(selectedCategories) {{
				var filteredData = filterDataByCategories({events_trends_alltimehigh}, selectedCategories);
				var filteredDataTable = google.visualization.arrayToDataTable(filteredData);
				events_per_day_chart_alltimehigh.draw(filteredDataTable, events_per_day_options_alltimehigh);
			}});

			createCheckboxes('packets_per_day_chart_div_alltimehigh', {packets_trends_chart_alltimehigh}, function(selectedCategories) {{
				var filteredData = filterDataByCategories({packets_trends_chart_alltimehigh}, selectedCategories);
				var filteredDataTable = google.visualization.arrayToDataTable(filteredData);
				packets_per_day_chart_alltimehigh.draw(filteredDataTable, packets_per_day_options_alltimehigh);
			}});

			createCheckboxes('bandwidth_per_day_chart_div_alltimehigh', {bw_trends_alltimehigh}, function(selectedCategories) {{
				var filteredData = filterDataByCategories({bw_trends_alltimehigh}, selectedCategories);
				var filteredDataTable = google.visualization.arrayToDataTable(filteredData);
				bandwidth_per_day_chart_alltimehigh.draw(filteredDataTable, bandwidth_per_day_options_alltimehigh);
			}});

			createCheckboxes('events_per_day_by_device_chart_div', {events_by_device_trends_chart_data}, function(selectedCategories) {{
				var filteredData = filterDataByCategories({events_by_device_trends_chart_data}, selectedCategories);
				var filteredDataTable = google.visualization.arrayToDataTable(filteredData);
				events_per_day_by_device_chart.draw(filteredDataTable, events_per_day_by_device_options);
			}});

			createCheckboxes('packets_per_day_by_device_chart_div', {packets_by_device_trends_chart_data}, function(selectedCategories) {{
				var filteredData = filterDataByCategories({packets_by_device_trends_chart_data}, selectedCategories);
				var filteredDataTable = google.visualization.arrayToDataTable(filteredData);
				packets_per_day_by_device_chart.draw(filteredDataTable, packets_per_day_by_device_options);
			}});

			createCheckboxes('bandwidth_per_day_by_device_chart_div', {bw_by_device_trends_chart_data}, function(selectedCategories) {{
				var filteredData = filterDataByCategories({bw_by_device_trends_chart_data}, selectedCategories);
				var filteredDataTable = google.visualization.arrayToDataTable(filteredData);
				bandwidth_per_day_by_device_chart.draw(filteredDataTable, bandwidth_per_day_by_device_options);
			}});

			createCheckboxes('sip_events_per_day_chart_div', {sip_events_trends_chart}, function(selectedCategories) {{
				var filteredData = filterDataByCategories({sip_events_trends_chart}, selectedCategories);
				var filteredDataTable = google.visualization.arrayToDataTable(filteredData);
				sip_events_per_day_chart.draw(filteredDataTable, sip_events_per_day_options);
			}});

			createCheckboxes('sip_packets_per_day_chart_div', {sip_packets_trends_chart}, function(selectedCategories) {{
				var filteredData = filterDataByCategories({sip_packets_trends_chart}, selectedCategories);
				var filteredDataTable = google.visualization.arrayToDataTable(filteredData);
				sip_packets_per_day_chart.draw(filteredDataTable, sip_packets_per_day_options);
			}});

			createCheckboxes('sip_bandwidth_per_day_chart_div', {sip_bw_trends_chart}, function(selectedCategories) {{
				var filteredData = filterDataByCategories({sip_bw_trends_chart}, selectedCategories);
				var filteredDataTable = google.visualization.arrayToDataTable(filteredData);
				sip_bandwidth_per_day_chart.draw(filteredDataTable, sip_bandwidth_per_day_options);
			}});

			createCheckboxes('policy_events_per_day_chart_div', {policy_events_trends_chart}, function(selectedCategories) {{
				var filteredData = filterDataByCategories({policy_events_trends_chart}, selectedCategories);
				var filteredDataTable = google.visualization.arrayToDataTable(filteredData);
				policy_events_per_day_chart.draw(filteredDataTable, policy_events_per_day_options);
			}});

			createCheckboxes('policy_packets_per_day_chart_div', {policy_packets_trends_chart}, function(selectedCategories) {{
				var filteredData = filterDataByCategories({policy_packets_trends_chart}, selectedCategories);
				var filteredDataTable = google.visualization.arrayToDataTable(filteredData);
				policy_packets_per_day_chart.draw(filteredDataTable, policy_packets_per_day_options);
			}});

			createCheckboxes('policy_bandwidth_per_day_chart_div', {policy_bw_trends_chart}, function(selectedCategories) {{
				var filteredData = filterDataByCategories({policy_bw_trends_chart}, selectedCategories);
				var filteredDataTable = google.visualization.arrayToDataTable(filteredData);
				policy_bandwidth_per_day_chart.draw(filteredDataTable, policy_bandwidth_per_day_options);
			}});


			traffic_per_device_combined_trends_bps_chart.draw(traffic_per_device_combined_trends_bps_data, traffic_per_device_combined_trends_bps_options);
			attacks_per_device_combined_trends_bps_chart.draw(attacks_per_device_combined_trends_bps_data, attacks_per_device_combined_trends_bps_options);

			maxpps_per_day_chart.draw(maxpps_per_day_data, maxpps_per_day_options);
			maxbps_per_day_chart.draw(maxbps_per_day_data, maxbps_per_day_options);

			events_per_day_chart.draw(events_per_day_data, events_per_day_options);
			bandwidth_per_day_chart.draw(bandwidth_per_day_data, bandwidth_per_day_options);
			packets_per_day_chart.draw(packets_per_day_data, packets_per_day_options);

			events_per_day_chart_alltimehigh.draw(events_per_day_data_alltimehigh, events_per_day_options_alltimehigh);
			packets_per_day_chart_alltimehigh.draw(packets_per_day_data_alltimehigh, packets_per_day_options_alltimehigh);
			bandwidth_per_day_chart_alltimehigh.draw(bandwidth_per_day_data_alltimehigh, bandwidth_per_day_options_alltimehigh);

			events_per_day_by_device_chart.draw(events_per_day_by_device_data, events_per_day_by_device_options);
			packets_per_day_by_device_chart.draw(packets_per_day_by_device_data, packets_per_day_by_device_options);
			bandwidth_per_day_by_device_chart.draw(bandwidth_per_day_by_device_data, bandwidth_per_day_by_device_options);

			sip_events_per_day_chart.draw(sip_events_per_day_data, sip_events_per_day_options);
			sip_packets_per_day_chart.draw(sip_packets_per_day_data, sip_packets_per_day_options);
			sip_bandwidth_per_day_chart.draw(sip_bandwidth_per_day_data, sip_bandwidth_per_day_options);

			policy_events_per_day_chart.draw(policy_events_per_day_data, policy_events_per_day_options);
			policy_packets_per_day_chart.draw(policy_packets_per_day_data, policy_packets_per_day_options);
			policy_bandwidth_per_day_chart.draw(policy_bandwidth_per_day_data, policy_bandwidth_per_day_options);

			

			// Add radio button toggles for stacked/non-stacked


            addStackedToggle('traffic_per_device_combined_trends_bps_chart_div', traffic_per_device_combined_trends_bps_chart, traffic_per_device_combined_trends_bps_data, traffic_per_device_combined_trends_bps_options);
            addStackedToggle('attacks_per_device_combined_trends_bps_chart_div', attacks_per_device_combined_trends_bps_chart, attacks_per_device_combined_trends_bps_data, attacks_per_device_combined_trends_bps_options);

			addStackedToggle('events_per_day_chart_div_alltimehigh', events_per_day_chart_alltimehigh, events_per_day_data_alltimehigh, events_per_day_options_alltimehigh);
			addStackedToggle('packets_per_day_chart_div_alltimehigh', packets_per_day_chart_alltimehigh, packets_per_day_data_alltimehigh, packets_per_day_options_alltimehigh);
			addStackedToggle('bandwidth_per_day_chart_div_alltimehigh', bandwidth_per_day_chart_alltimehigh, bandwidth_per_day_data_alltimehigh, bandwidth_per_day_options_alltimehigh);

			addStackedToggle('events_per_day_by_device_chart_div', events_per_day_by_device_chart, events_per_day_by_device_data, events_per_day_by_device_options);
			addStackedToggle('packets_per_day_by_device_chart_div', packets_per_day_by_device_chart, packets_per_day_by_device_data, packets_per_day_by_device_options);
			addStackedToggle('bandwidth_per_day_by_device_chart_div', bandwidth_per_day_by_device_chart, bandwidth_per_day_by_device_data, bandwidth_per_day_by_device_options);

			addStackedToggle('sip_events_per_day_chart_div', sip_events_per_day_chart, sip_events_per_day_data, sip_events_per_day_options);
			addStackedToggle('sip_packets_per_day_chart_div', sip_packets_per_day_chart, sip_packets_per_day_data, sip_packets_per_day_options);
			addStackedToggle('sip_bandwidth_per_day_chart_div', sip_bandwidth_per_day_chart, sip_bandwidth_per_day_data, sip_bandwidth_per_day_options);

			addStackedToggle('policy_events_per_day_chart_div', policy_events_per_day_chart, policy_events_per_day_data, policy_events_per_day_options);
			addStackedToggle('policy_packets_per_day_chart_div', policy_packets_per_day_chart, policy_packets_per_day_data, policy_packets_per_day_options);
			addStackedToggle('policy_bandwidth_per_day_chart_div', policy_bandwidth_per_day_chart, policy_bandwidth_per_day_data, policy_bandwidth_per_day_options);

		  }}

			// Function to create checkboxes
			function createCheckboxes(containerId, data, callback) {{
			var container = document.getElementById(containerId);
			var categories = data[0].slice(1);  // Extract categories from the first row

			var checkboxContainer = document.createElement('div');
			checkboxContainer.className = 'checkbox-container';
			
			categories.forEach(function(category, index) {{
				var checkbox = document.createElement('input');
				checkbox.type = 'checkbox';
				checkbox.checked = true;
				checkbox.value = index + 1;  // Offset for data columns

				checkbox.onchange = function() {{
				var selectedCategories = Array.from(checkboxContainer.querySelectorAll('input:checked')).map(input => input.value);
				callback(selectedCategories);
				}};

				var label = document.createElement('label');
				label.appendChild(checkbox);
				label.appendChild(document.createTextNode(category));
				
				checkboxContainer.appendChild(label);
			}});

			container.parentNode.insertBefore(checkboxContainer, container);
			}}

			// Function to filter data based on selected categories
			function filterDataByCategories(data, selectedCategories) {{
			var header = [data[0][0], ...selectedCategories.map(index => data[0][index])];  // Filter header row
			var rows = data.slice(1).map(row => [row[0], ...selectedCategories.map(index => row[index])]);  // Filter data rows
			return [header, ...rows];
			}}

			// Function to add Stacked/Non-Stacked toggle via radio buttons
			function addStackedToggle(containerId, chart, data, options) {{
			var container = document.getElementById(containerId);
			var radioContainer = document.createElement('div');
			radioContainer.className = 'radio-container';
			
			var stackedLabel = document.createElement('label');
			var stackedRadio = document.createElement('input');
			stackedRadio.type = 'radio';
			stackedRadio.name = 'stackedToggle_' + containerId;
			stackedRadio.value = 'stacked';
			
			stackedRadio.onchange = function() {{
				options.isStacked = true;
				chart.draw(data, options);
			}};
			stackedLabel.appendChild(stackedRadio);
			stackedLabel.appendChild(document.createTextNode('Stacked'));

			var nonStackedLabel = document.createElement('label');
			var nonStackedRadio = document.createElement('input');
			nonStackedRadio.type = 'radio';
			nonStackedRadio.name = 'stackedToggle_' + containerId;
			nonStackedRadio.value = 'non-stacked';

			 // Set radio button checked state based on the initial options.isStacked value
			 if (options.isStacked) {{
			     stackedRadio.checked = true;
			     nonStackedRadio.checked = false;
			 }} else {{
			     stackedRadio.checked = false;
			     nonStackedRadio.checked = true;
			 }}

			nonStackedRadio.onchange = function() {{
				options.isStacked = false;
				chart.draw(data, options);
			}};
			nonStackedLabel.appendChild(nonStackedRadio);
			nonStackedLabel.appendChild(document.createTextNode('Non-Stacked'));

			radioContainer.appendChild(stackedLabel);
			radioContainer.appendChild(nonStackedLabel);
			
			// container.parentNode.insertBefore(radioContainer, container);
			container.parentNode.insertBefore(radioContainer, container.nextSibling);
			}}


		// Toggle table visibility on button click
		function toggleTable(tableId, button) {{
			const collapsibleTable = document.getElementById(tableId);

			if (collapsibleTable.style.display === 'none' || collapsibleTable.style.display === '') {{
				collapsibleTable.style.display = 'block';
				button.textContent = 'Hide Details';
				button.classList.add('active');
			}} else {{
				collapsibleTable.style.display = 'none';
				button.textContent = button.getAttribute('data-original-text'); // Restore original text
				button.classList.remove('active');
			}}
		}}

		</script>

	<style>
	  body, html {{
		margin: 0;
		display: flex;
		justify-content: center;
		align-items: center;
		background-color: #f0f0f0;
		font-family: Arial, sans-serif;
		font-size: 14px;
	  }}
	  
	  table {{
		width: 100%;
		border-collapse: collapse;
		table-layout: fixed;
	  }}

	  
	  th, td {{
		width: 33%;
		text-align: center;
		border: 1px solid black;
		padding: 10px;
	  }}

	  .checkbox-container, .radio-container {{
      margin-bottom: 10px;
      }}

	  .radio-container {{
		margin-top: 20px; /* Adds space after the chart */
	  }}
	  
      .fit-text {{
        font-size: 14px; /* Adjust the font size as needed */
        word-wrap: break-word; /* Allow text to break onto the next line if needed */
      }}
  
	  #traffic_per_device_combined_trends_bps_chart_div {{
		height: 20vh;
	  }}

	  #attacks_per_device_combined_trends_bps_chart_div {{
		height: 20vh;
	  }}  
	    
	  #maxpps_per_day_chart_div {{
		height: 20vh;
	  }}

	  #maxbps_per_day_chart_div {{
		height: 20vh;
	  }}



	  #events_per_day_chart_div {{
		height: 20vh;
	  }}

	  #bandwidth_per_day_chart_div {{
		height: 20vh;
	  }}

	  #packets_per_day_chart_div {{
		height: 20vh;
	  }}


	  #attack_packets_per_day_chart_div {{
		height: 50vh;
	  }}

	  #attack_bandwidth_per_day_chart_div {{
		height: 50vh;
	  }}


	  #attack_events_per_day_chart_div_alltimehigh {{
		height: 50vh;
	  }}

	  #packets_per_day_chart_div_alltimehigh {{
		height: 50vh;
	  }}

	  #bandwidth_per_day_chart_div_alltimehigh {{
		height: 50vh;
	  }}
	  

	  #events_per_day_by_device_chart_div {{
		height: 50vh;
	  }}

	  #packets_per_day_by_device_chart_div {{
		height: 50vh;
	  }}

	  #bandwidth_per_day_by_device_chart_div {{
		height: 50vh;
	  }}

	  #sip_events_per_day_chart_div {{
		height: 50vh;
	  }}

	  #sip_packets_per_day_chart_div {{
		height: 50vh;
	  }}

	  #sip_bandwidth_per_day_chart_div {{
		height: 50vh;
	  }}

	  #policy_events_per_day_chart_div {{
		height: 50vh;
	  }}

	  #policy_packets_per_day_chart_div {{
		height: 50vh;
	  }}

	  #policy_bandwidth_per_day_chart_div {{
		height: 50vh;
	  }}


        /* Center the toggle button */
        .button-container {{
            display: flex;
            justify-content: center;
            margin: 20px 0;
        }}



        /* Styling for the toggle button */
        .toggle-btn {{
            cursor: pointer;
            background-color: #6c757d; /* Gray color */
            color: white;
            padding: 12px 24px;
            border: none;
            outline: none;
            font-size: 18px;
            border-radius: 5px;
            transition: background-color 0.3s, transform 0.2s;
        }}


        /* Style for the button when active */
        .toggle-btn.active {{
            background-color: #5a6268; /* Darker gray */
        }}


        /* Hover effect */
        .toggle-btn:hover {{
            background-color: #868e96; /* Lighter gray for hover */
            transform: scale(1.05);
        }}

        /* Initial state to hide the collapsible content */
        .collapsible-content {{
            display: none;
            margin-top: 15px;
        }}

		

        /* Styling for the table */
        .dataframe {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}

        .dataframe th, .dataframe td {{
            padding: 8px;
            text-align: center;
            border: 1px solid #ddd;
        }}

        .dataframe thead th {{
            background-color: #f2f2f2;
        }}



	</style>
	<title>Radware Daily Report</title>
	</head>
	<body>



	  <table>
		<thead>

		  <tr>
			<td colspan="3">
			<h1>Radware Daily report {month},{year} - {cust_id}</h1>
			</td>
		  </tr>

          <tr>
            <td colspan="3" style="border-bottom: 0;">
            <h4>Traffic utilization per device combined</h4>
            <div id="traffic_per_device_combined_trends_bps_chart_div" style="height: 400px;">
            </td>
          </tr> 

          <tr>
            <td colspan="3" style="border-bottom: 0;">
            <h4>All Attacks per device combined</h4>
            <div id="attacks_per_device_combined_trends_bps_chart_div" style="height: 400px;">
            </td>
          </tr> 

		  <tr>
		  	<td colspan="3" style="border-bottom: 0;">
			<div id="maxpps_per_day_chart_div">
			</td>
		  </tr>



		  <tr>

		  	<td colspan="3" valign="top" style="border-top: 0;" class="fit-text">
			  
				<!-- Button container for centering -->
				<div class="button-container">
					<button class="toggle-btn" data-original-text="Show Details" onclick="toggleTable('maxppsPerDayTable', this)">Show Details</button>
				</div>
			
		  		<div id="maxppsPerDayTable" class="collapsible-content">
		  			{maxpps_per_day_table}
		  		</div>
		  	</td>
		  </tr>


		  <tr>
		  	<td colspan="3" style="border-bottom: 0;">
			<div id="maxbps_per_day_chart_div">
			</td>
		  </tr>

		  <tr>

			<td colspan="3" valign="top" style="border-top: 0;" class="fit-text">
				<!-- Button container for centering -->
				<div class="button-container">
					<button class="toggle-btn" data-original-text="Show Details" onclick="toggleTable('maxbpsPerDayTable', this)">Show Details</button>
				</div>
		  		<div id="maxbpsPerDayTable" class="collapsible-content">
				{maxbps_per_day_table}
				</div>
			</td>
		  </tr>

		  <tr>
		  	<td colspan="3" style="border-bottom: 0;">
			<div id="events_per_day_chart_div">
			</td>
		  </tr>

		  

		  <tr>

			<td colspan="3" valign="top" style="border-top: 0;" class="fit-text">
				<!-- Button container for centering -->
				<div class="button-container">
					<button class="toggle-btn" data-original-text="Show Details" onclick="toggleTable('eventsPerDayTable', this)">Show Details</button>
				</div>
		  		<div id="eventsPerDayTable" class="collapsible-content">
				  
				{events_per_day_table}
				</div>
			</td>
		  </tr>		  



		  <tr>
		  	<td colspan="3" style="border-bottom: 0;">
				<div id="packets_per_day_chart_div">
			</td>
		  </tr>

		  

		  <tr>

			<td colspan="3" valign="top" style="border-top: 0;" class="fit-text">
				<!-- Button container for centering -->
				<div class="button-container">
					<button class="toggle-btn" data-original-text="Show Details" onclick="toggleTable('packetsPerDayTable', this)">Show Details</button>
				</div>
		  		<div id="packetsPerDayTable" class="collapsible-content">
				  
				{packets_per_day_table}
				</div>
			</td>
		  </tr>		




		  <tr>
		  	<td colspan="3" style="border-bottom: 0;">
				<div id="bandwidth_per_day_chart_div">
			</td>
		  </tr>

		  

		  <tr>

			<td colspan="3" valign="top" style="border-top: 0;" class="fit-text">
				<!-- Button container for centering -->
				<div class="button-container">
					<button class="toggle-btn" data-original-text="Show Details" onclick="toggleTable('bwPerDayTable', this)">Show Details</button>
				</div>
		  		<div id="bwPerDayTable" class="collapsible-content">
				  
				{bandwidth_per_day_table}
				</div>
			</td>
		  </tr>		



	

		  <tr>
		  	<td colspan="3" style="border-bottom: 0;">
			<h4>Daily trends by Security Events count</h4>
			<div id="events_per_day_chart_div_alltimehigh" style="height: 400px;">
			</td>
		  </tr>	


		  
		  <tr>

			<td colspan="3" valign="top" style="border-top: 0;" class="fit-text">
				<!-- Button container for centering -->
				<div class="button-container">
					<button class="toggle-btn" data-original-text="Attack Events count per Day" onclick="toggleTable('AttackEventsPerDayTable', this)">Attack Events count per Day</button>
				</div>
		  		<div id="AttackEventsPerDayTable" class="collapsible-content">
				  
				{events_trends_table_alltimehigh}
				
				</div>


				<!-- Button container for centering -->
				<div class="button-container">
					<button class="toggle-btn" data-original-text="Distribution of topmost attack events across Devices and Policies" onclick="toggleTable('DistributionOfAttacksPerDayTable', this)">Distribution of topmost attack events across Devices and Policies</button>
				</div>
		  		<div id="DistributionOfAttacksPerDayTable" class="collapsible-content">
				  
				
				{events_per_day_html_final}
				</div>


			</td>
	
		  </tr>		




	  
		  <tr>
		  	<td colspan="3" style="border-bottom: 0;">
			<h4>Daily trends by Malicious Packets(cumulative)</h4>
			<div id="packets_per_day_chart_div_alltimehigh" style="height: 400px;">
			</td>
		  </tr>


		  <tr>

			<td colspan="3" valign="top" style="border-top: 0;" class="fit-text">
				<!-- Button container for centering -->
				<div class="button-container">
					<button class="toggle-btn" data-original-text="Malicious packets table" onclick="toggleTable('AttackPacketsPerDayTable', this)">Malicious packets table</button>
				</div>
		  		<div id="AttackPacketsPerDayTable" class="collapsible-content">
				{packets_table_alltimehigh}
				</div>


				<!-- Button container for centering -->
				<div class="button-container">
					<button class="toggle-btn" data-original-text="Distribution of topmost malicious packets across Devices and Policies" onclick="toggleTable('DistributionOfPacketsPerDayTable', this)">Distribution of topmost malicious packets across Devices and Policies</button>
				</div>
		  		<div id="DistributionOfPacketsPerDayTable" class="collapsible-content">
				
				{packets_per_day_html_final} 
				</div>


			</td>
	
		  </tr>		


		  <tr>
		  	<td colspan="3" style="border-bottom: 0;" class="fit-text">
			<h4>Daily trends by Malicious Bandwidth sum(cumulative)</h4>
			<div id="bandwidth_per_day_chart_div_alltimehigh" style="height: 400px;">
			</td>
		  </tr>
  

		   <tr>
		  
			<td colspan="3" valign="top" style="border-top: 0;">
				<!-- Button container for centering -->
				<div class="button-container">
					<button class="toggle-btn" data-original-text="Accumulated Malicious bandwidh per day table" onclick="toggleTable('AttackBWPerDayTable', this)">Accumulated Malicious bandwidh per day table</button>
				</div>
		  		<div id="AttackBWPerDayTable" class="collapsible-content">
				{bw_table_alltimehigh}
				</div>


				<!-- Button container for centering -->
				<div class="button-container">
					<button class="toggle-btn" data-original-text="Distribution of accumulated malicious bandwidth across Devices and Policies" onclick="toggleTable('DistributionOfBWPerDayTable', this)">Distribution of accumulated malicious bandwidth across Devices and Policies</button>
				</div>
		  		<div id="DistributionOfBWPerDayTable" class="collapsible-content">
				
				{bandwidth_per_day_html_final}
				</div>


			</td>
	
		  </tr>		

		  




		  <tr>
		  	<td colspan="3">
			<div id="events_per_day_by_device_chart_div" style="height: 400px;" style="border-bottom: 0;">

			</td>
		  </tr>	



		  <tr>

			<td colspan="3" valign="top" style="border-top: 0;" class="fit-text">
				<!-- Button container for centering -->
				<div class="button-container">
					<button class="toggle-btn" data-original-text="Attack Events by device table" onclick="toggleTable('DeviceAttackEventsPerDayTable', this)">Attack Events by device table</button>
				</div>
		  		<div id="DeviceAttackEventsPerDayTable" class="collapsible-content">
				  
				{events_by_device_table}
				
				</div>


				<!-- Button container for centering -->
				<div class="button-container">
					<button class="toggle-btn" data-original-text="Distribution of topmost attack events" onclick="toggleTable('DistributionOfDeviceAttacksPerDayTable', this)">Distribution of topmost attack events</button>
				</div>
		  		<div id="DistributionOfDeviceAttacksPerDayTable" class="collapsible-content">
				  
				
				{device_events_per_day_html_final}
				</div>


			</td>
	
		  </tr>		



		  
		   
		  <tr>
		  	<td colspan="3" style="border-bottom: 0;">
			<div id="packets_per_day_by_device_chart_div" style="height: 400px;">
			</td>
		  </tr>

		  

		  <tr>

			<td colspan="3" valign="top" style="border-top: 0;" class="fit-text">
				<!-- Button container for centering -->
				<div class="button-container">
					<button class="toggle-btn" data-original-text="Malicious packets by device table" onclick="toggleTable('AttackDevicePacketsPerDayTable', this)">Malicious packets by device table</button>
				</div>
		  		<div id="AttackDevicePacketsPerDayTable" class="collapsible-content">
				{packets_by_device_table}
				</div>


				<!-- Button container for centering -->
				<div class="button-container">
					<button class="toggle-btn" data-original-text="Distribution of topmost malicious packets for device" onclick="toggleTable('DistributionOfDevicePacketsPerDayTable', this)">Distribution of topmost malicious packets for device</button>
				</div>
		  		<div id="DistributionOfDevicePacketsPerDayTable" class="collapsible-content">
				
				{device_packets_per_day_html_final} 
				</div>


			</td>
	
		  </tr>		



		  <tr>
		  	<td colspan="3" style="border-bottom: 0;">
			<div id="bandwidth_per_day_by_device_chart_div" style="height: 400px;">
			</td>
		  </tr>

		   <tr>
		  
			<td colspan="3" valign="top" style="border-top: 0;" class="fit-text">
				<!-- Button container for centering -->
				<div class="button-container">
					<button class="toggle-btn" data-original-text="Malicious Bandwidth by device table" onclick="toggleTable('AttackDeviceBWPerDayTable', this)">Malicious Bandwidth by device table</button>
				</div>
		  		<div id="AttackDeviceBWPerDayTable" class="collapsible-content">
				{bw_by_device_table}
				</div>


				<!-- Button container for centering -->
				<div class="button-container">
					<button class="toggle-btn" data-original-text="Distribution of accumulated malicious bandwidth across Devices and Policies" onclick="toggleTable('DistributionOfDeviceBWPerDayTable', this)">Distribution of accumulated malicious bandwidth across Devices and Policies</button>
				</div>
		  		<div id="DistributionOfDeviceBWPerDayTable" class="collapsible-content">
				
				{device_bandwidth_per_day_html_final}
				</div>


			</td>
	
		  </tr>



		  <tr>
		  	<td colspan="3" style="border-bottom: 0;">
			<div id="policy_events_per_day_chart_div" style="height: 400px;">

			</td>
		  </tr>	




		  <tr>

			<td colspan="3" valign="top" style="border-top: 0;" class="fit-text">
				<!-- Button container for centering -->
				<div class="button-container">
					<button class="toggle-btn" data-original-text="Attack Events by policy table" onclick="toggleTable('PolicyAttackEventsPerDayTable', this)">Attack Events by policy table</button>
				</div>
		  		<div id="PolicyAttackEventsPerDayTable" class="collapsible-content">
				  
				{policy_events_trends_table}
				
				</div>


				<!-- Button container for centering -->
				<div class="button-container">
					<button class="toggle-btn" data-original-text="Distribution of topmost attack events" onclick="toggleTable('DistributionOfPolicyAttacksPerDayTable', this)">Distribution of topmost attack events</button>
				</div>
		  		<div id="DistributionOfPolicyAttacksPerDayTable" class="collapsible-content">
				  
				
				{policy_events_per_day_html_final}
				</div>


			</td>
	
		  </tr>	


		  <tr>
		  	<td colspan="3" style="border-bottom: 0;" class="fit-text">
			<div id="policy_packets_per_day_chart_div" style="height: 400px;">
			</td>
		  </tr>
		  <tr>

			<td colspan="3" valign="top" style="border-top: 0;" class="fit-text">
				<!-- Button container for centering -->
				<div class="button-container">
					<button class="toggle-btn" data-original-text="Malicious packets by device table" onclick="toggleTable('AttackPolicyPacketsPerDayTable', this)">Malicious packets by policy table</button>
				</div>
		  		<div id="AttackPolicyPacketsPerDayTable" class="collapsible-content">
				{policy_packets_table}
				</div>


				<!-- Button container for centering -->
				<div class="button-container">
					<button class="toggle-btn" data-original-text="Distribution of topmost malicious packets for device" onclick="toggleTable('DistributionOfPolicyPacketsPerDayTable', this)">Distribution of topmost malicious packets</button>
				</div>
		  		<div id="DistributionOfPolicyPacketsPerDayTable" class="collapsible-content">
				
				{policy_packets_per_day_html_final} 
				</div>


			</td>
	
		  </tr>		
		  <tr>
		  	<td colspan="3" style="border-bottom: 0;">
			<div id="policy_bandwidth_per_day_chart_div" style="height: 400px;">
			</td>
		  </tr>
		   <tr>
		  
			<td colspan="3" valign="top" style="border-top: 0;" class="fit-text">
				<!-- Button container for centering -->
				<div class="button-container">
					<button class="toggle-btn" data-original-text="Malicious Bandwidth by policy table" onclick="toggleTable('AttackPolicyBWPerDayTable', this)">Malicious Bandwidth by policy table</button>
				</div>
		  		<div id="AttackPolicyBWPerDayTable" class="collapsible-content">
				{policy_bw_table}
				</div>


				<!-- Button container for centering -->
				<div class="button-container">
					<button class="toggle-btn" data-original-text="Distribution of accumulated malicious bandwidth across Devices and Policies" onclick="toggleTable('DistributionOfPolicyBWPerDayTable', this)">Distribution of accumulated malicious bandwidth across Devices and Policies</button>
				</div>
		  		<div id="DistributionOfPolicyBWPerDayTable" class="collapsible-content">
				
				{policy_bandwidth_per_day_html_final}
				</div>


			</td>
	
		  </tr>
		  






		  <tr>
		  	<td colspan="3" style="border-bottom: 0;">
			<div id="sip_events_per_day_chart_div" style="height: 400px;">

			</td>
		  </tr>	
		  <tr>

			<td colspan="3" valign="top" style="border-top: 0;" class="fit-text">
				<!-- Button container for centering -->
				<div class="button-container">
					<button class="toggle-btn" data-original-text="Attack Events per day table by source IP" onclick="toggleTable('SIPAttackEventsPerDayTable', this)">Attack Events per day table by source IP</button>
				</div>
		  		<div id="SIPAttackEventsPerDayTable" class="collapsible-content">
				  
				{sip_events_trends_table}
				
				</div>


				<!-- Button container for centering -->
				<div class="button-container">
					<button class="toggle-btn" data-original-text="Distribution of topmost Security events for Source IP's" onclick="toggleTable('DistributionOfSIPAttacksPerDayTable', this)">Distribution of topmost Security events for Source IP's</button>
				</div>
		  		<div id="DistributionOfSIPAttacksPerDayTable" class="collapsible-content">
				  
				
				{sip_events_per_day_html_final}
				</div>


			</td>
	
		  </tr>	

		  <tr>
		  	<td colspan="3" style="border-bottom: 0;">
			<div id="sip_packets_per_day_chart_div" style="height: 400px;">
			</td>
		  </tr>
		  <tr>

			<td colspan="3" valign="top" style="border-top: 0;" class="fit-text">
				<!-- Button container for centering -->
				<div class="button-container">
					<button class="toggle-btn" data-original-text="Malicious packets per day by Source IP" onclick="toggleTable('AttackSIPPacketsPerDayTable', this)">Malicious packets per day by Source IP</button>
				</div>
		  		<div id="AttackSIPPacketsPerDayTable" class="collapsible-content">
				{sip_packets_table}
				</div>


				<!-- Button container for centering -->
				<div class="button-container">
					<button class="toggle-btn" data-original-text="Distribution of topmost malicious packets for Source IP's" onclick="toggleTable('DistributionOfSIPPacketsPerDayTable', this)">Distribution of topmost malicious packets for Source IP's</button>
				</div>
		  		<div id="DistributionOfSIPPacketsPerDayTable" class="collapsible-content">
				
				{sip_packets_per_day_html_final} 
				</div>


			</td>
	
		  </tr>	
		  <tr>
		  	<td colspan="3" style="border-bottom: 0;">
			<div id="sip_bandwidth_per_day_chart_div" style="height: 400px;">
			</td>
		  </tr>
		   <tr>
		  
			<td colspan="3" valign="top" style="border-top: 0;" class="fit-text">
				<!-- Button container for centering -->
				<div class="button-container">
					<button class="toggle-btn" data-original-text="Malicious Bandwidth by Source IP" onclick="toggleTable('AttackSIPBWPerDayTable', this)">Malicious Bandwidth by Source IP</button>
				</div>
		  		<div id="AttackSIPBWPerDayTable" class="collapsible-content">
				{sip_bw_table}
				</div>


				<!-- Button container for centering -->
				<div class="button-container">
					<button class="toggle-btn" data-original-text="Distribution of topmost malicious bandwidth for Source IP's" onclick="toggleTable('DistributionOfSIPBWPerDayTable', this)">Distribution of topmost malicious bandwidth for Source IP's</button>
				</div>
		  		<div id="DistributionOfSIPBWPerDayTable" class="collapsible-content">
				
				{sip_bandwidth_per_day_html_final}
				</div>


			</td>
	
		  </tr>
		  



		</tbody>

	  </table>

		  <p></p>

	</body>

	</html>
	"""

	# write html_page to file
	write_html(html_page,month,year)

# Path: trends_analyzer.py
