import pandas as pd
import sqlite3
import csv
import sys
import pandas as pd
import json

cust_id = sys.argv[1]
month = sys.argv[2]
year = sys.argv[3]


customers_json = json.loads(open("./config_files/customers.json", "r").read())

for cust_config_block in customers_json:
	if cust_config_block['id'].lower() == cust_id.lower():
		defensepros = cust_config_block['defensepros']
		bw_units = cust_config_block['variables']['bwUnit']
		#Can be configured "Gigabytes", "Terabytes" or "Megabytes"
		
		pkt_units = cust_config_block['variables']['pktUnit']
		#Can be configured "Millions" or "Billions" or "Thousands"

		bw_units_daily = cust_config_block['variables']['bwUnitDaily']
		#Can be configured "Gigabytes", "Terabytes" or "Megabytes"
		
		pkt_units_daily = cust_config_block['variables']['pktUnitDaily']
		#Can be configured "Millions" or "Billions" or "Thousands"

		if bw_units_daily.lower() == 'megabytes':	
			bw_units_sum = 'ROUND(SUM(packetBandwidth)/8000.0, 2)'
			bps_unit = 1000000
			bps_units_desc = 'Mbps'

		if bw_units_daily.lower() == 'gigabytes':	
			bw_units_sum = 'ROUND(SUM(packetBandwidth)/8000000.0, 2)'
			bps_unit = 1000000000
			bps_units_desc = 'Gbps'

		if bw_units_daily.lower() == 'terabytes':
			bw_units_sum = 'ROUND(SUM(packetBandwidth)/8000000000.0, 2)'
			bps_unit = 1000000000
			bps_units_desc = 'Gbps'

# Paths
charts_tables_path = f"./tmp_files/{cust_id}/"
reports_path = f"./report_files/{cust_id}/"
db_path = f'./database_files/{cust_id}/'
run_file = 'run.sh'


with open (run_file) as f:
	for line in f:
	#find line starting with top_n
		if line.startswith('db_from_forensics'):
			#print value after = sign
			db_from_forensics = (line.split('=')[1].replace('\n','').replace('"','')).lower()
			if db_from_forensics == 'true':
				db_from_forensics = True
			else:
				db_from_forensics = False
			continue

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
		for value in row:
			# if the value is integer or float
			if isinstance(value, int) or isinstance(value, float):
				if pkt_units == "Billions":
					value = value/1000000000
				elif pkt_units == "Millions":
					value = value/1000000
				elif pkt_units == "Thousands":
					value = value/1000
				else:
					print(f'Invalid packets unit is set under "pkt_units" variable in the script. Please set it to "Millions" or "Billions" ')
				
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
		for value in row:
			# if the value is integer or float
			if isinstance(value, int) or isinstance(value, float):

				if bw_units.lower() == "megabytes":
					value = value/8000
				elif bw_units.lower() == "gigabytes":
					value = value/8000000
				elif bw_units.lower() == "terabytes":
					value = value/8000000000

				if isinstance(value, float):
					#leave only two decimal points
					value = round(value, 2)

				
				else:
					print(f'Invalid bandwidth unit is set under "bw_units" variable in the script. Please set it to "Megabytes", "Gigabytes" or "Terabytes" ')
			
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


def format_numeric_value(value, bw_units=None, pkt_units=None):
	# Check if value is a number (integer or float)
	if pd.notna(value) and isinstance(value, (int, float)):
		# Apply formatting based on units
		if pkt_units:
			if pkt_units.lower() == 'millions':
				value /= 1000000
			elif pkt_units.lower() == 'billions':
				value /= 1000000000
			if pkt_units.lower() == 'thousands':
				value /= 1000

		if bw_units:
			if bw_units.lower() == 'megabytes':
				value /= 8000
			elif bw_units.lower() == 'gigabytes':
				value /= 8000000
			elif bw_units.lower() == 'terabytes':
				value /= 8000000000

		# Format the value with thousands separator
		if pkt_units:
			# remove decimal points if the value is integer
			if isinstance(value, float):
				value = int(value)
				return value

		else:
			return '{:,.2f}'.format(value)
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
	if bw_units or pkt_units and filename!=charts_tables_path + 'sip_ppm_table_lm.csv':
		formatted_df = df.applymap(lambda x: format_numeric_value(x, bw_units, pkt_units))
	
	else:
		df = df.apply(convert_to_int, axis=0)
		formatted_df = df

	# Convert the formatted DataFrame to an HTML table
	html_table = formatted_df.to_html(index=False, escape=False)
	
	return html_table


def write_html(html_page,month,year):
	# write html_page to file function

	with open(reports_path + f'trends-monthly_{cust_id}_{month}_{year}.html', 'w') as f:
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

def events_per_day_html():

	# Group by day_of_month, name, Device Name, ruleName and aggregate sum of packetCount
	events_per_day = data_month.groupby(['Day of the Month', 'Attack Name', 'Device Name', 'Policy Name']).size()

	# Get the top 5 events with the highest sum of packet counts for each day
	events_per_day_top5 = events_per_day.groupby(level=['Day of the Month'], group_keys=False).nlargest(5).apply(format_with_commas).to_frame('Security Events Count')
	events_per_day_top5 = events_per_day_top5.to_html()

	for device_ip, device_name in defensepros.items():
		events_per_day_top5=events_per_day_top5.replace(device_ip, device_name)

	return events_per_day_top5


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


def bandwidth_per_day_html():
	# Group by day_of_month, name, Device Name, ruleName and aggregate sum of packetCount
	bandwidth_per_day = data_month.groupby(['Day of the Month', 'Attack Name', 'Device Name', 'Policy Name'])['packetBandwidth'].sum()

	# Convert units to Megabytes/Gigabytes/Terabytes
	bandwidth_per_day = bandwidth_per_day.apply(bw_units_conversion)

	# Get the top 5 events with the highest sum of packet counts for each day
	bandwidth_per_day_top5 = bandwidth_per_day.groupby(level=['Day of the Month'], group_keys=False).nlargest(5).apply(format_with_commas).to_frame('Malicious bandwidth sum')
	bandwidth_per_day_top5 = bandwidth_per_day_top5.to_html()

	for device_ip, device_name in defensepros.items():
		bandwidth_per_day_top5=bandwidth_per_day_top5.replace(device_ip, device_name)

	return bandwidth_per_day_top5


def packets_per_day_html():

	# Group by day_of_month, name, Device Name, ruleName and aggregate sum of packetCount
	packets_per_day = data_month.groupby(['Day of the Month', 'Attack Name', 'Device Name', 'Policy Name'])['packetCount'].sum()

	# Convert units
	packets_per_day = packets_per_day.apply(pkt_units_conversion)

	# Get the top 5 events with the highest sum of packet counts for each day
	packets_per_day_top5 = packets_per_day.groupby(level=['Day of the Month'], group_keys=False).nlargest(5).apply(format_with_commas).to_frame('Malicious Packets sum')
	packets_per_day_top5 = packets_per_day_top5.to_html()

	for device_ip, device_name in defensepros.items():
		packets_per_day_top5=packets_per_day_top5.replace(device_ip, device_name)

	return packets_per_day_top5


def epm_html(epm):
	data_month_epm = data_month[data_month['Attack Name'] == epm]
	series_epm = data_month_epm.groupby(['Attack Name','Device Name','Policy Name']).size().sort_values(ascending=False).apply(format_with_commas).head(10)
	epm_html = series_epm.to_frame('Security Events')
	epm_html=epm_html.to_html()

	for device_ip, device_name in defensepros.items():
		epm_html=epm_html.replace(device_ip, device_name)

	return epm_html

def ppm_html(ppm):
	data_month_ppm = data_month[data_month['Attack Name'] == ppm]
	series_ppm = data_month_ppm.groupby(['Attack Name','Device Name','Policy Name']).sum()['packetCount'].sort_values(ascending=False)
	# Convert units
	series_ppm = series_ppm.apply(pkt_units_conversion).apply(format_with_commas).head(10)
	ppm_html = series_ppm.to_frame('Malicious Packets')
	ppm_html=ppm_html.to_html()

	for device_ip, device_name in defensepros.items():
		ppm_html=ppm_html.replace(device_ip, device_name)

	return ppm_html

def bpm_html(bpm):
	data_month_bpm = data_month[data_month['Attack Name'] == bpm]
	series_bpm = data_month_bpm.groupby(['Attack Name','Device Name','Policy Name']).sum()['packetBandwidth'].sort_values(ascending=False)
	# Convert units
	series_bpm = series_bpm.apply(bw_units_conversion).apply(format_with_commas).head(10)
	df_bpm_html = series_bpm.to_frame('Malicious Bandwidth')
	df_bpm_html=df_bpm_html.to_html()

	for device_ip, device_name in defensepros.items():
		df_bpm_html=df_bpm_html.replace(device_ip, device_name)

	return df_bpm_html



def device_epm_html(device_epm):

	for device_ip, device_name in defensepros.items():
		if device_name == device_epm:

			data_month_epm = data_month[data_month['Device Name'] == device_ip]
			device_series_epm = data_month_epm.groupby(['Device Name','Attack Name','Policy Name']).size().sort_values(ascending=False).apply(format_with_commas).head(10)
			device_epm_html = device_series_epm.to_frame('Security Events')
			device_epm_html=device_epm_html.to_html().replace(device_ip, device_name)
			return device_epm_html
		else:
			continue

def device_ppm_html(device_ppm):
	for device_ip, device_name in defensepros.items():
		if device_name == device_ppm:
			data_month_ppm = data_month[data_month['Device Name'] == device_ip]
			device_series_ppm = data_month_ppm.groupby(['Device Name','Attack Name','Policy Name']).sum()['packetCount'].sort_values(ascending=False)
			device_series_ppm = device_series_ppm.apply(pkt_units_conversion).apply(format_with_commas).head(10)
			device_ppm_html = device_series_ppm.to_frame('Malicious Packets')
			device_ppm_html=device_ppm_html.to_html().replace(device_ip, device_name)
			return device_ppm_html
		else:
			continue

def device_bpm_html(device_bpm):

	for device_ip, device_name in defensepros.items():
		if device_name == device_bpm:
			data_month_bpm = data_month[data_month['Device Name'] == device_ip]
			device_series_bpm = data_month_bpm.groupby(['Device Name','Attack Name','Policy Name']).sum()['packetBandwidth'].sort_values(ascending=False)
			device_series_bpm = device_series_bpm.apply(bw_units_conversion).apply(format_with_commas).head(10)
			device_df_bpm_html = device_series_bpm.to_frame('Malicious Bandwidth')
			device_df_bpm_html= device_df_bpm_html.to_html().replace(device_ip, device_name)
			return device_df_bpm_html
		else:
			continue


def policy_epm_html(policy_epm):

	data_month_epm = data_month[data_month['Policy Name'] == policy_epm]
	series_epm = data_month_epm.groupby(['Policy Name','Attack Name','Device Name']).size().sort_values(ascending=False).apply(format_with_commas).head(10)
	epm_html = series_epm.to_frame('Security Events')
	epm_html=epm_html.to_html()

	for device_ip, device_name in defensepros.items():
		epm_html=epm_html.replace(device_ip, device_name)
		
	return epm_html

def policy_ppm_html(policy_ppm):
	data_month_ppm = data_month[data_month['Policy Name'] == policy_ppm]
	series_ppm = data_month_ppm.groupby(['Policy Name','Attack Name','Device Name']).sum()['packetCount'].sort_values(ascending=False)
	series_ppm = series_ppm.apply(pkt_units_conversion).apply(format_with_commas).head(10)
	ppm_html = series_ppm.to_frame('Malicious Packets')
	ppm_html=ppm_html.to_html()
	
	for device_ip, device_name in defensepros.items():
		ppm_html=ppm_html.replace(device_ip, device_name)
	
	return ppm_html

def policy_bpm_html(policy_bpm):
	data_month_bpm = data_month[data_month['Policy Name'] == policy_bpm]
	series_bpm = data_month_bpm.groupby(['Policy Name','Attack Name','Device Name']).sum()['packetBandwidth'].sort_values(ascending=False)
	series_bpm = series_bpm.apply(bw_units_conversion).apply(format_with_commas).head(10)
	df_bpm_html = series_bpm.to_frame('Malicious Bandwidth')
	df_bpm_html=df_bpm_html.to_html()

	for device_ip, device_name in defensepros.items():
		df_bpm_html=df_bpm_html.replace(device_ip, device_name)
	
	return df_bpm_html


def sip_epm_html(sip_epm):

	data_month_epm = data_month[data_month['Source IP'] == sip_epm]
	series_epm = data_month_epm.groupby(['Source IP','Attack Name','Device Name','Policy Name']).size().sort_values(ascending=False).apply(format_with_commas).head(10)
	epm_html = series_epm.to_frame('Security Events')
	epm_html=epm_html.to_html()

	for device_ip, device_name in defensepros.items():
		epm_html=epm_html.replace(device_ip, device_name)
		
	return epm_html


def sip_ppm_html(sip_ppm):
	data_month_ppm = data_month[data_month['Source IP'] == sip_ppm]
	series_ppm = data_month_ppm.groupby(['Source IP','Attack Name','Device Name','Policy Name']).sum()['packetCount'].sort_values(ascending=False)
	series_ppm = series_ppm.apply(pkt_units_conversion).apply(format_with_commas).head(10)
	ppm_html = series_ppm.to_frame('Malicious Packets')
	ppm_html=ppm_html.to_html()
	
	for device_ip, device_name in defensepros.items():
		ppm_html=ppm_html.replace(device_ip, device_name)
	
	return ppm_html

def sip_bpm_html(sip_bpm):
	data_month_bpm = data_month[data_month['Source IP'] == sip_bpm]
	series_bpm = data_month_bpm.groupby(['Source IP','Attack Name','Device Name','Policy Name']).sum()['packetBandwidth'].sort_values(ascending=False)
	series_bpm = series_bpm.apply(bw_units_conversion).apply(format_with_commas).head(10)
	df_bpm_html = series_bpm.to_frame('Malicious Bandwidth')
	df_bpm_html=df_bpm_html.to_html()

	for device_ip, device_name in defensepros.items():
		df_bpm_html=df_bpm_html.replace(device_ip, device_name)
	
	return df_bpm_html





def format_with_commas(value):
	return '{:,}'.format(value)

if __name__ == '__main__':

	maxpps_per_day_trends = convert_csv_to_list_of_lists(charts_tables_path + 'maxpps_per_day_last_month.csv')

	# Malicious bandwidth per day
	maxbps_per_day_trends = convert_csv_to_list_of_lists(charts_tables_path + 'maxbps_per_day_last_month.csv')

	# Traffic utilization
	if db_from_forensics:
		traffic_trends = [['Date,Traffic Utilization(Mbps),Blocked traffic,Excluded traffic']]
	else:
		traffic_trends = convert_csv_to_list_of_lists(charts_tables_path + 'traffic.csv')
	
	# Events per day count
	events_per_day_trends = convert_csv_to_list_of_lists(charts_tables_path + 'events_per_day_last_month.csv')
	
	# Malicious bandwidth per day
	bandwidth_per_day_trends = convert_csv_to_list_of_lists(charts_tables_path + 'bandwidth_per_day_last_month.csv')

	# Malicious bandwidth per day
	packets_per_day_trends = convert_csv_to_list_of_lists(charts_tables_path + 'packets_per_day_last_month.csv')


	# Total events, packets and bandwidth trends (blue bars charts)
	events_total_bar_chart = convert_csv_to_list_of_lists(charts_tables_path + 'epm_total_bar.csv')
	events_total_bar_move_text = trends_move_total(events_total_bar_chart, 'events') 

	packets_total_bar = convert_csv_to_list_of_lists(charts_tables_path + 'ppm_total_bar.csv')
	packets_total_bar = convert_packets_units(packets_total_bar, pkt_units)
	pakets_total_bar_move = trends_move_total(packets_total_bar, ' packets(' + pkt_units + ')')

	bw_total_bar = convert_csv_to_list_of_lists(charts_tables_path + 'bpm_total_bar.csv')
	bw_total_bar = convert_bw_units(bw_total_bar, bw_units)
	bw_total_bar_move = trends_move_total(bw_total_bar, bw_units) 

	################################################# Events, packets and bandwidth trends by Attack name sorted by the last month ##########################################################
	events_trends = convert_csv_to_list_of_lists(charts_tables_path + 'epm_chart_lm.csv')
	events_trends_move = trends_move(events_trends, 'events')
	events_trends_table = csv_to_html_table(charts_tables_path + 'epm_table_lm.csv')

	packets_trends_chart = convert_csv_to_list_of_lists(charts_tables_path + 'ppm_chart_lm.csv')
	packets_trends_chart = convert_packets_units(packets_trends_chart, pkt_units)
	packets_trends_move_text = trends_move(packets_trends_chart, ' packets(' + pkt_units + ')')
	packets_table = csv_to_html_table(charts_tables_path + 'ppm_table_lm.csv',bw_units=None, pkt_units=pkt_units)


	bw_trends = convert_csv_to_list_of_lists(charts_tables_path + 'bpm_chart_lm.csv')
	bw_trends = convert_bw_units(bw_trends, bw_units)
	bw_trends_move = trends_move(bw_trends, bw_units)
	bw_table = csv_to_html_table(charts_tables_path + 'bpm_table_lm.csv',bw_units)

	################################################# Analyze deeper top category ##########################################################

	#1 Create a data frame
	con = sqlite3.connect(db_path + 'database_'+cust_id+'_'+str(month)+'.sqlite')
	# data = pd.read_sql_query("SELECT * from attacks", con)
	if db_from_forensics:
		data_month = pd.read_sql_query(f"SELECT deviceName as 'Device Name',month,year,packetBandwidth,name as 'Attack Name',packetCount,ruleName as 'Policy Name',category,sourceAddress as 'Source IP',destAddress,startTime,endTime,startDate,attackIpsId,actionType,maxAttackPacketRatePps,maxAttackRateBps,destPort,protocol,startDayOfMonth as 'Day of the Month' from attacks", con)
	else:
		data_month = pd.read_sql_query(f"SELECT deviceName as 'Device Name',month,year,packetBandwidth,name as 'Attack Name',packetCount,ruleName as 'Policy Name',category,sourceAddress as 'Source IP',destAddress,startTime,endTime,startDate,attackIpsId,actionType,maxAttackPacketRatePps,maxAttackRateBps,destPort,protocol,geoLocation,durationRange,startDayOfMonth as 'Day of the Month',durationRange as 'Duration Range' from attacks", con)

	#export data to csv
	data_month.to_csv(reports_path +'database_'+cust_id+'_'+str(month)+'_'+str(year)+'.csv', encoding='utf-8', index=False)


	con.close()

	#2 Extract Top Attacks list

	epm_top_list=extract_values_from_csv('epm_table_lm.csv')
	ppm_top_list=extract_values_from_csv('ppm_table_lm.csv')
	bpm_top_list=extract_values_from_csv('bpm_table_lm.csv')

	device_epm_top_list=extract_values_from_csv('device_epm_table_lm.csv')
	device_ppm_top_list=extract_values_from_csv('device_ppm_table_lm.csv')
	device_bpm_top_list=extract_values_from_csv('device_bpm_table_lm.csv')

	policy_epm_top_list=extract_values_from_csv('policy_epm_table_lm.csv')
	policy_ppm_top_list=extract_values_from_csv('policy_ppm_table_lm.csv')
	policy_bpm_top_list=extract_values_from_csv('policy_bpm_table_lm.csv')

	sip_epm_top_list=extract_values_from_csv('sip_epm_table_lm.csv')
	sip_ppm_top_list=extract_values_from_csv('sip_ppm_table_lm.csv')
	sip_bpm_top_list=extract_values_from_csv('sip_bpm_table_lm.csv')

	#3 Create empty html table
	epm_html_final = ''
	ppm_html_final = ''
	bpm_html_final = ''

	device_epm_html_final = ''
	device_ppm_html_final = ''
	device_bpm_html_final = ''

	policy_epm_html_final = ''
	policy_ppm_html_final = ''
	policy_bpm_html_final = ''

	sip_epm_html_final = ''
	sip_ppm_html_final = ''
	sip_bpm_html_final = ''

	#4 Iterate through each Device and popluate the html table



	for index, value in enumerate(epm_top_list):
		epm_html_final+=f'<h4>{value} distribution across devices and policies</h4>'
		epm_html_final+= epm_html(epm_top_list[index])

	for index, value in enumerate(ppm_top_list):
		ppm_html_final+=f'<h4>{value} distribution across devices and policies</h4>'
		ppm_html_final+= ppm_html(ppm_top_list[index])
		
	for index, value in enumerate(bpm_top_list):
		bpm_html_final+=f'<h4>{value} distribution across devices and policies</h4>'
		bpm_html_final+= bpm_html(bpm_top_list[index])



	for index, value in enumerate(device_epm_top_list):
		device_epm_html_final+=f'<h4>Top Attacks and policies for device {value}</h4>'
		device_epm_html_final+= device_epm_html(device_epm_top_list[index])

	for index, value in enumerate(device_ppm_top_list):
		device_ppm_html_final+=f'<h4>Top Attacks and policies for device {value}</h4>'
		device_ppm_html_final+= device_ppm_html(device_ppm_top_list[index])

	for index, value in enumerate(device_bpm_top_list):
		device_bpm_html_final+=f'<h4>Top Attacks and policies for device {value}</h4>'
		device_bpm_html_final+= device_bpm_html(device_ppm_top_list[index])


	for index, value in enumerate(policy_epm_top_list):
		policy_epm_html_final+=f'<h4>Distribution of attacks and devices for policy {value}</h4>'
		policy_epm_html_final+= policy_epm_html(policy_epm_top_list[index])

	for index, value in enumerate(policy_ppm_top_list):
		policy_ppm_html_final+=f'<h4>Distribution of attacks and devices for policy {value}</h4>'
		policy_ppm_html_final+= policy_ppm_html(policy_ppm_top_list[index])
		
	for index, value in enumerate(policy_bpm_top_list):
		policy_bpm_html_final+=f'<h4>Distribution of attacks and devices for policy {value}</h4>'
		policy_bpm_html_final+= policy_bpm_html(policy_bpm_top_list[index])


	for index, value in enumerate(sip_epm_top_list):
		sip_epm_html_final+=f'<h4>Distribution of attacks and devices for Source IP {value}</h4>'
		sip_epm_html_final+= sip_epm_html(sip_epm_top_list[index])

	for index, value in enumerate(sip_ppm_top_list):
		sip_ppm_html_final+=f'<h4>Distribution of attacks and devices for Source IP {value}</h4>'
		sip_ppm_html_final+= sip_ppm_html(sip_ppm_top_list[index])
		
	for index, value in enumerate(sip_bpm_top_list):
		sip_bpm_html_final+=f'<h4>Distribution of attacks and devices for Source IP {value}</h4>'
		sip_bpm_html_final+= sip_bpm_html(sip_bpm_top_list[index])


	#5 Generate html for the last month


	maxpps_per_day_table = maxpps_per_day_html_table()
	maxbps_per_day_table = maxbps_per_day_html_table()

	events_per_day_table = events_per_day_html()
	bandwidth_per_day_table = bandwidth_per_day_html()
	packets_per_day_table = packets_per_day_html()
	################################################# Events, packets and bandwidth trends by Attack name sorted by the overall sum of all months together ##########################################################


	events_trends_alltimehigh = convert_csv_to_list_of_lists(charts_tables_path + 'epm_chart_alltimehigh.csv')
	events_trends_move_alltimehigh = trends_move(events_trends_alltimehigh, 'events')
	events_trends_table_alltimehigh = csv_to_html_table(charts_tables_path + 'epm_table_alltimehigh.csv')

	packets_trends_chart_alltimehigh = convert_csv_to_list_of_lists(charts_tables_path + 'ppm_chart_alltimehigh.csv')
	packets_trends_chart_alltimehigh = convert_packets_units(packets_trends_chart_alltimehigh, pkt_units)
	packets_trends_move_text_alltimehigh = trends_move(packets_trends_chart_alltimehigh, ' packets(' + pkt_units + ')')
	packets_table_alltimehigh = csv_to_html_table(charts_tables_path + 'ppm_table_alltimehigh.csv',bw_units=None, pkt_units=pkt_units)


	bw_trends_alltimehigh = convert_csv_to_list_of_lists(charts_tables_path + 'bpm_chart_alltimehigh.csv')
	bw_trends_alltimehigh = convert_bw_units(bw_trends_alltimehigh, bw_units)
	bw_trends_move_alltimehigh = trends_move(bw_trends_alltimehigh, bw_units)
	bw_table_alltimehigh = csv_to_html_table(charts_tables_path + 'bpm_table_alltimehigh.csv',bw_units)


	################################################# Events, packets and bandwidth trends by Device  ##########################################################

	events_by_device_trends_chart_data = convert_csv_to_list_of_lists(charts_tables_path + 'device_epm_chart_lm.csv')
	events_by_device_trends_move_text = trends_move(events_by_device_trends_chart_data, 'events')
	events_by_device_table = csv_to_html_table(charts_tables_path + 'device_epm_table_lm.csv')

	packets_by_device_trends_chart_data = convert_csv_to_list_of_lists(charts_tables_path + 'device_ppm_chart_lm.csv')
	packets_by_device_trends_chart_data = convert_packets_units(packets_by_device_trends_chart_data, pkt_units)
	packets_by_device_trends_move_text = trends_move(packets_by_device_trends_chart_data, ' packets(' + pkt_units + ')')
	packets_by_device_table = csv_to_html_table(charts_tables_path + 'device_ppm_table_lm.csv',bw_units=None, pkt_units=pkt_units)


	bw_by_device_trends_chart_data = convert_csv_to_list_of_lists(charts_tables_path + 'device_bpm_chart_lm.csv')
	bw_by_device_trends_chart_data = convert_bw_units(bw_by_device_trends_chart_data, bw_units)
	bw_by_device_trends_move_text = trends_move(bw_by_device_trends_chart_data, bw_units)
	bw_by_device_table = csv_to_html_table(charts_tables_path + 'device_bpm_table_lm.csv',bw_units)

	################################################# Top source IP(bw is Megabytes) ##########################################################		
	sip_events_trends_chart = convert_csv_to_list_of_lists(charts_tables_path + 'sip_epm_chart_lm.csv')
	sip_events_trends_move_text = trends_move(sip_events_trends_chart, 'events')
	sip_events_trends_table = csv_to_html_table(charts_tables_path + 'sip_epm_table_lm.csv')

	sip_packets_trends_chart = convert_csv_to_list_of_lists(charts_tables_path + 'sip_ppm_chart_lm.csv')
	sip_packets_trends_chart = convert_packets_units(sip_packets_trends_chart, pkt_units)
	sip_packets_trends_move_text = trends_move(sip_packets_trends_chart, ' packets(' + pkt_units + ')')
	sip_packets_table = csv_to_html_table(charts_tables_path + 'sip_ppm_table_lm.csv',bw_units=None, pkt_units=None)


	sip_bw_trends_chart = convert_csv_to_list_of_lists(charts_tables_path + 'sip_bpm_chart_lm.csv')
	# sip_bw_trends_chart = convert_bw_units(sip_bw_trends_chart, sip_bw_units)
	# sip_bw_trends_move_text = trends_move(sip_bw_trends_chart, sip_bw_units)
	sip_bw_table = csv_to_html_table(charts_tables_path + 'sip_bpm_table_lm.csv')

	################################################# Events, packets and bandwidth trends by Policy ##########################################################

	policy_events_trends_chart = convert_csv_to_list_of_lists(charts_tables_path + 'policy_epm_chart_lm.csv')
	policy_events_trends_move_text = trends_move(policy_events_trends_chart, 'events')
	policy_events_trends_table = csv_to_html_table(charts_tables_path + 'policy_epm_table_lm.csv')

	policy_packets_trends_chart = convert_csv_to_list_of_lists(charts_tables_path + 'policy_ppm_chart_lm.csv')
	policy_packets_trends_chart = convert_packets_units(policy_packets_trends_chart, pkt_units)
	policy_packets_trends_move_text = trends_move(policy_packets_trends_chart, ' packets(' + pkt_units + ')')
	policy_packets_table = csv_to_html_table(charts_tables_path + 'policy_ppm_table_lm.csv',bw_units=None, pkt_units=pkt_units)

	policy_bw_trends_chart = convert_csv_to_list_of_lists(charts_tables_path + 'policy_bpm_chart_lm.csv')
	policy_bw_trends_chart = convert_bw_units(policy_bw_trends_chart, bw_units)
	policy_bw_trends_move_text = trends_move(policy_bw_trends_chart, bw_units)
	policy_bw_table = csv_to_html_table(charts_tables_path + 'policy_bpm_table_lm.csv',bw_units)


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
		  
			var traffic_data = google.visualization.arrayToDataTable({traffic_trends});

			var maxpps_per_day_data = google.visualization.arrayToDataTable({maxpps_per_day_trends});
			var maxbps_per_day_data = google.visualization.arrayToDataTable({maxbps_per_day_trends});

			var events_per_day_data = google.visualization.arrayToDataTable({events_per_day_trends});
			var bandwidth_per_day_data = google.visualization.arrayToDataTable({bandwidth_per_day_trends});
			var packets_per_day_data = google.visualization.arrayToDataTable({packets_per_day_trends});
  
			var epm_total_data = google.visualization.arrayToDataTable({events_total_bar_chart});
			var ppm_total_data = google.visualization.arrayToDataTable({packets_total_bar});
			var bpm_total_data = google.visualization.arrayToDataTable({bw_total_bar});

			var epm_data = google.visualization.arrayToDataTable({events_trends});
			var ppm_data = google.visualization.arrayToDataTable({packets_trends_chart});
			var bpm_data = google.visualization.arrayToDataTable({bw_trends});

			var epm_data_alltimehigh = google.visualization.arrayToDataTable({events_trends_alltimehigh});
			var ppm_data_alltimehigh = google.visualization.arrayToDataTable({packets_trends_chart_alltimehigh});
			var bpm_data_alltimehigh = google.visualization.arrayToDataTable({bw_trends_alltimehigh});

			var epm_by_device_data = google.visualization.arrayToDataTable({events_by_device_trends_chart_data});
			var ppm_by_device_data = google.visualization.arrayToDataTable({packets_by_device_trends_chart_data});
			var bpm_by_device_data = google.visualization.arrayToDataTable({bw_by_device_trends_chart_data});

			var sip_epm_data = google.visualization.arrayToDataTable({sip_events_trends_chart});
			var sip_ppm_data = google.visualization.arrayToDataTable({sip_packets_trends_chart});
			var sip_bpm_data = google.visualization.arrayToDataTable({sip_bw_trends_chart});

			var policy_epm_data = google.visualization.arrayToDataTable({policy_events_trends_chart });
			var policy_ppm_data = google.visualization.arrayToDataTable({policy_packets_trends_chart });
			var policy_bpm_data = google.visualization.arrayToDataTable({policy_bw_trends_chart });

			

			
			var traffic_options = {{
			  title: 'Traffic utilization, last month',
			  vAxis: {{minValue: 0}},
			  isStacked: false,
			  legend: {{position: 'top', maxLines: 5}},
			  width: '100%'
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

			var bandwidth_per_day_options = {{
			  title: 'Malicious bandwidth per day, last month (units {bw_units})',
			  vAxis: {{minValue: 0}},
			  hAxis: {{ticks: bandwidth_per_day_data.getDistinctValues(0),minTextSpacing:1,showTextEvery:1}},
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

			var epm_total_options = {{
			  title: 'Total Events trends',
			  bar: {{groupWidth: "95%"}},
			  legend: {{position: 'none'}},
			  width: '100%'
			}};

			var ppm_total_options = {{
			  title: 'Total Malicious Packets count trends (units {pkt_units})',
			  bar: {{groupWidth: "95%"}},
			  legend: {{position: 'none'}},
			  width: '100%'
			}};

			var bpm_total_options = {{
			  title: 'Total Malicious bandwidth sum trends (units {bw_units})',
			  bar: {{groupWidth: "95%"}},
			  legend: {{position: 'none'}},
			  width: '100%'
			}};

			var epm_options = {{
			  title: 'Security Events trends - TopN by last month',
			  vAxis: {{minValue: 0}},
			  isStacked: true,
			  legend: {{position: 'top', maxLines: 5}},
			  width: '100%'
			}};

			var ppm_options = {{
			  title: 'Malicious Packets trends (units {pkt_units}) - TopN by last month',
			  vAxis: {{minValue: 0}},
			  isStacked: true,
			  legend: {{position: 'top', maxLines: 5}},
			  width: '100%'
			}};

			var bpm_options = {{
			  title: 'Malicious Bandwidth trends (units {bw_units}) - TopN by last month',
			  vAxis: {{minValue: 0}},
			  isStacked: true,
			  legend: {{position: 'top', maxLines: 5}},
			  width: '100%'
			}};

			var epm_options_alltimehigh = {{
			  title: 'Security Events trends - TopN all time high',
			  vAxis: {{minValue: 0}},
			  isStacked: true,
			  legend: {{position: 'top', maxLines: 5}},
			  width: '100%'
			}};

			var ppm_options_alltimehigh = {{
			  title: 'Malicious Packets trends (units {pkt_units}) - TopN all time high',
			  vAxis: {{minValue: 0}},
			  isStacked: true,
			  legend: {{position: 'top', maxLines: 5}},
			  width: '100%'
			}};

			var bpm_options_alltimehigh = {{
			  title: 'Malicious Bandwidth trends (units {bw_units}) - TopN all time high',
			  vAxis: {{minValue: 0}},
			  isStacked: true,
			  legend: {{position: 'top', maxLines: 5}},
			  width: '100%'
			}};

			var epm_by_device_options = {{
			  title: 'Events by device trends',
			  vAxis: {{minValue: 0}},
			  isStacked: true,
			  legend: {{position: 'top', maxLines: 5}},
			  width: '100%'
			}};

			var ppm_by_device_options = {{
			  title: 'Packets by device trends (units {pkt_units})',
			  vAxis: {{minValue: 0}},
			  isStacked: true,
			  legend: {{position: 'top', maxLines: 5}},
			  width: '100%'
			}};

			var bpm_by_device_options = {{
			  title: 'Malicious Bandwidth by device trends (units {bw_units})',
			  vAxis: {{minValue: 0}},
			  isStacked: true,
			  legend: {{position: 'top', maxLines: 5}},
			  width: '100%'
			}};

			var sip_epm_options = {{
			  title: 'Security Events trends by source IP',
			  vAxis: {{minValue: 0}},
			  isStacked: true,
			  legend: {{position: 'top', maxLines: 5}},
			  width: '100%'
			}};

			var sip_ppm_options = {{
			  title: 'Malicious Packets trends (units {pkt_units}) by source IP',
			  vAxis: {{minValue: 0}},
			  isStacked: true,
			  legend: {{position: 'top', maxLines: 5}},
			  width: '100%'
			}};

			var sip_bpm_options = {{
			  title: 'Malicious Bandwidth trends (Megabytes) by source IP',
			  vAxis: {{minValue: 0}},
			  isStacked: true,
			  legend: {{position: 'top', maxLines: 5}},
			  width: '100%'
			}};

			var policy_epm_options = {{
			  title: 'Security Events trends by Policy',
			  vAxis: {{minValue: 0}},
			  isStacked: true,
			  legend: {{position: 'top', maxLines: 5}},
			  width: '100%'
			}};

			var policy_ppm_options = {{
			  title: 'Malicious Packets trends (units {pkt_units}) by Policy',
			  vAxis: {{minValue: 0}},
			  isStacked: true,
			  legend: {{position: 'top', maxLines: 5}},
			  width: '100%'
			}};

			var policy_bpm_options = {{
			  title: 'Malicious Bandwidth trends (units {bw_units}) by Policy',
			  vAxis: {{minValue: 0}},
			  isStacked: true,
			  legend: {{position: 'top', maxLines: 5}},
			  width: '100%'
			}};



			var traffic_chart = new google.visualization.AreaChart(document.getElementById('traffic_chart_div'));

			var maxpps_per_day_chart = new google.visualization.AreaChart(document.getElementById('maxpps_per_day_chart_div'));
			var maxbps_per_day_chart = new google.visualization.AreaChart(document.getElementById('maxbps_per_day_chart_div'));

			var events_per_day_chart = new google.visualization.AreaChart(document.getElementById('events_per_day_chart_div'));
			var bandwidth_per_day_chart = new google.visualization.AreaChart(document.getElementById('bandwidth_per_day_chart_div'));
			var packets_per_day_chart = new google.visualization.AreaChart(document.getElementById('packets_per_day_chart_div'));

			var epm_total_chart = new google.visualization.ColumnChart(document.getElementById('epm_total_chart_div'));
			var ppm_total_chart = new google.visualization.ColumnChart(document.getElementById('ppm_total_chart_div'));
			var bpm_total_chart = new google.visualization.ColumnChart(document.getElementById('bpm_total_chart_div'));

			var epm_chart = new google.visualization.AreaChart(document.getElementById('epm_chart_div'));
			var ppm_chart = new google.visualization.AreaChart(document.getElementById('ppm_chart_div'));
			var bpm_chart = new google.visualization.AreaChart(document.getElementById('bpm_chart_div'));

			var epm_chart_alltimehigh = new google.visualization.AreaChart(document.getElementById('epm_chart_div_alltimehigh'));
			var ppm_chart_alltimehigh = new google.visualization.AreaChart(document.getElementById('ppm_chart_div_alltimehigh'));
			var bpm_chart_alltimehigh = new google.visualization.AreaChart(document.getElementById('bpm_chart_div_alltimehigh'));

			var epm_by_device_chart = new google.visualization.AreaChart(document.getElementById('epm_by_device_chart_div'));
			var ppm_by_device_chart = new google.visualization.AreaChart(document.getElementById('ppm_by_device_chart_div'));
			var bpm_by_device_chart = new google.visualization.AreaChart(document.getElementById('bpm_by_device_chart_div'));

			var sip_epm_chart = new google.visualization.AreaChart(document.getElementById('sip_epm_chart_div'));
			var sip_ppm_chart = new google.visualization.AreaChart(document.getElementById('sip_ppm_chart_div'));
			var sip_bpm_chart = new google.visualization.AreaChart(document.getElementById('sip_bpm_chart_div'));		

			var policy_epm_chart = new google.visualization.AreaChart(document.getElementById('policy_epm_chart_div'));
			var policy_ppm_chart = new google.visualization.AreaChart(document.getElementById('policy_ppm_chart_div'));
			var policy_bpm_chart = new google.visualization.AreaChart(document.getElementById('policy_bpm_chart_div'));
			


			traffic_chart.draw(traffic_data, traffic_options);

			maxpps_per_day_chart.draw(maxpps_per_day_data, maxpps_per_day_options);
			maxbps_per_day_chart.draw(maxbps_per_day_data, maxbps_per_day_options);

			events_per_day_chart.draw(events_per_day_data, events_per_day_options);
			bandwidth_per_day_chart.draw(bandwidth_per_day_data, bandwidth_per_day_options);
			packets_per_day_chart.draw(packets_per_day_data, packets_per_day_options);

			epm_total_chart.draw(epm_total_data, epm_total_options);
			ppm_total_chart.draw(ppm_total_data, ppm_total_options);
			bpm_total_chart.draw(bpm_total_data, bpm_total_options);

			epm_chart.draw(epm_data, epm_options);
			ppm_chart.draw(ppm_data, ppm_options);
			bpm_chart.draw(bpm_data, bpm_options);

			epm_chart_alltimehigh.draw(epm_data_alltimehigh, epm_options_alltimehigh);
			ppm_chart_alltimehigh.draw(ppm_data_alltimehigh, ppm_options_alltimehigh);
			bpm_chart_alltimehigh.draw(bpm_data_alltimehigh, bpm_options_alltimehigh);

			epm_by_device_chart.draw(epm_by_device_data, epm_by_device_options);
			ppm_by_device_chart.draw(ppm_by_device_data, ppm_by_device_options);
			bpm_by_device_chart.draw(bpm_by_device_data, bpm_by_device_options);

			sip_epm_chart.draw(sip_epm_data, sip_epm_options);
			sip_ppm_chart.draw(sip_ppm_data, sip_ppm_options);
			sip_bpm_chart.draw(sip_bpm_data, sip_bpm_options);

			policy_epm_chart.draw(policy_epm_data, policy_epm_options);
			policy_ppm_chart.draw(policy_ppm_data, policy_ppm_options);
			policy_bpm_chart.draw(policy_bpm_data, policy_bpm_options);

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

	  
	  #traffic_chart_div {{
		height: 40vh;
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

	  #epm_total_chart_div {{
		height: 50vh;
	  }}

	  #ppm_total_chart_div {{
		height: 50vh;
	  }}

	  #bpm_total_chart_div {{
		height: 50vh;
	  }}

	  #epm_chart_div {{
		height: 50vh;
	  }}

	  #ppm_chart_div {{
		height: 50vh;
	  }}

	  #bpm_chart_div {{
		height: 50vh;
	  }}


	  #epm_chart_div_alltimehigh {{
		height: 50vh;
	  }}

	  #ppm_chart_div_alltimehigh {{
		height: 50vh;
	  }}

	  #bpm_chart_div_alltimehigh {{
		height: 50vh;
	  }}
	  

	  #epm_by_device_chart_div {{
		height: 50vh;
	  }}

	  #ppm_by_device_chart_div {{
		height: 50vh;
	  }}

	  #bpm_by_device_chart_div {{
		height: 50vh;
	  }}

	  #sip_epm_chart_div {{
		height: 50vh;
	  }}

	  #sip_ppm_chart_div {{
		height: 50vh;
	  }}

	  #sip_bpm_chart_div {{
		height: 50vh;
	  }}

	  #policy_epm_chart_div {{
		height: 50vh;
	  }}

	  #policy_ppm_chart_div {{
		height: 50vh;
	  }}

	  #policy_bpm_chart_div {{
		height: 50vh;
	  }}

	</style>
	<title>Radware Monthly Reports</title>
	</head>
	<body>

	  <table>
		<thead>

		  <tr>
			<td colspan="3">
			<h1>Radware Monthly report {month},{year} - {cust_id}</h1>
			</td>
		  </tr>

		  <tr>
		  	<td colspan="3">
			<div id="traffic_chart_div">
			</td>
		  </tr>

		  <tr>
		  	<td colspan="3">
			<div id="maxpps_per_day_chart_div">
			
			</td>
		  </tr>

		  <tr>
			<td colspan="3" valign="top">{maxpps_per_day_table}</td>
		  </tr>

		  <tr>
		  	<td colspan="3">
			<div id="maxbps_per_day_chart_div">
			</td>
		  </tr>

		  <tr>
			<td colspan="3" valign="top">{maxbps_per_day_table}</td>
		  </tr>

		  <tr>
		  	<td colspan="3">
			<div id="events_per_day_chart_div">
			</td>
		  </tr>

		  <tr>
		  	<td colspan="3">
			<div id="packets_per_day_chart_div">
			</td>
		  </tr>

		  <tr>
		  	<td colspan="3">
			<div id="bandwidth_per_day_chart_div">
			</td>
		  </tr>

		  <tr>
			<th>Security Events count by day</th>
			<th>Malicious Packets(cumulative) by day</th>
			<th>Malicious Bandwidth sum(cumulative) by day</th>
		  </tr>
		</thead>
		<tbody>
		  <tr>
			<td valign="top">{events_per_day_table}</td>
			<td valign="top"> {packets_per_day_table}</td>
			<td valign="top">{bandwidth_per_day_table}</td>
		  </tr>

		  <tr>
			<th>Month to month trends by Security Events count</th>
			<th>Month to month trends by Malicious Packets(cumulative)</th>
			<th>Month to month trends by Malicious Bandwidth sum(cumulative)</th>
		  </tr>

		  <tr>
			<td><div id="epm_total_chart_div"></td>
			<td><div id="ppm_total_chart_div"></td>
			<td><div id="bpm_total_chart_div"></td>
		  </tr>


		  <tr>
			<td><div id="epm_chart_div_alltimehigh" style="height: 600px;"></td>
			<td><div id="ppm_chart_div_alltimehigh" style="height: 600px;"></td>
			<td><div id="bpm_chart_div_alltimehigh" style="height: 600px;"></td>
		  </tr>



		  <tr>
			<td><div id="epm_chart_div" style="height: 600px;"></td>
			<td><div id="ppm_chart_div" style="height: 600px;"></td>
			<td><div id="bpm_chart_div" style="height: 600px;"></td>
		  </tr>

		  <tr>
			<td valign="top" style="text-align: left;">
				<h4>Change in Security Events number by attack name this month compared to the previous month</h4>
				{events_total_bar_move_text}{events_trends_move}</td>
			<td valign="top" style="text-align: left;">
				<h4>Change in Malicious Packets number by attack name this month compared to the previous month</h4>
				{pakets_total_bar_move}{packets_trends_move_text}</td>

			<td valign="top" style="text-align: left;">
				<h4>Change in Malicious Traffic sum by attack name this month compared to the previous month</h4>
				{bw_total_bar_move}{bw_trends_move}</td>
		  </tr>

		  
		  <tr>
			<td colspan="3">
			<h4>Security Events table</h4>
			{events_trends_table}
			</td>
		  </tr>
		  <tr>
			<td colspan="3">
			<h4>Malicious packets table (units {pkt_units})</h4>
			{packets_table}
			</td>
		  </tr>
		  <tr>
			<td colspan="3">
			<h4>Malicious bandwidth table (units {bw_units})</h4>
			{bw_table}
			</td>
		  </tr>	  
		  
		  <tr>
		 	<td  valign="top">
				{epm_html_final}
			</td>
		 	<td  valign="top">
				{ppm_html_final} 
			</td>
		 	<td  valign="top">
				{bpm_html_final}
			</td>
		  </tr>




		  <tr>
			<td><div id="epm_by_device_chart_div" style="height: 600px;"></td>
			<td><div id="ppm_by_device_chart_div" style="height: 600px;"></td>
			<td><div id="bpm_by_device_chart_div" style="height: 600px;"></td>
		  </tr>

		  <tr>

			<td valign="top" style="text-align: left;">
				<h4>Change in Security Events number by device this month compared to the previous month</h4>
				{events_by_device_trends_move_text}
			</td>
			<td valign="top" style="text-align: left;">
				<h4>Change in Malicious Packets number by device this month compared to the previous month</h4>
				{packets_by_device_trends_move_text}
			</td>
			
			<td valign="top" style="text-align: left;">
				<h4>Change in Malicious Traffic sum by device this month compared to the previous month</h4>
				{bw_by_device_trends_move_text}
			</td>

		  </tr>
		  <tr>
			<td colspan="3">
			<h4>Security Events by device table</h4>
			{events_by_device_table}
			</td>
		  </tr>
		  

		  <tr>
			<td colspan="3">
			<h4>Malicious packets by device table (units {pkt_units})</h4>
			{packets_by_device_table}
			</td>
		  </tr>
			
		  <tr>
			<td colspan="3">
			<h4>Malicious Bandwidth by device table (units {bw_units})</h4>
			{bw_by_device_table}
			</td>
		  </tr>


		  <tr>
		 	<td valign="top">
				{device_epm_html_final}
			</td>
		 	<td valign="top">
				{device_ppm_html_final}
			</td>
		 	<td valign="top">
				{device_bpm_html_final}			
			</td>
		  </tr>



		  <tr>
			<td><div id="policy_epm_chart_div" style="height: 600px;"></td>
			<td><div id="policy_ppm_chart_div" style="height: 600px;"></td>
			<td><div id="policy_bpm_chart_div" style="height: 600px;"></td>
		  </tr>

		  <tr>
			<td colspan="3">
			<h4>Security Events table by Policy</h4>
			{policy_events_trends_table}
			</td>
		  </tr>
		  <tr>
			<td colspan="3">
			<h4>Malicious packets table (units {pkt_units}) by Policy</h4>
			{policy_packets_table}
			</td>
		  </tr>
		  <tr>
			<td colspan="3">
			<h4>Malicious bandwidth table (Megabytes) by Policy</h4>
			{policy_bw_table}
			</td>
		  </tr>	  

		  <tr>
		 	<td valign="top">
				{policy_epm_html_final}
			</td>
		 	<td valign="top">
				{policy_ppm_html_final} 
			</td>
		 	<td valign="top">
				{policy_bpm_html_final}
			</td>
		  </tr>



		  <tr>
			<td><div id="sip_epm_chart_div" style="height: 600px;"></td>
			<td><div id="sip_ppm_chart_div" style="height: 600px;"></td>
			<td><div id="sip_bpm_chart_div" style="height: 600px;"></td>
		  </tr>

		  

		  <tr>
			<td colspan="3">
			<h4>Security Events table by source IP</h4>
			{sip_events_trends_table}
			</td>
		  </tr>
		  <tr>
			<td colspan="3">
			<h4>Malicious packets table (units {pkt_units}) by source IP</h4>
			{sip_packets_table}
			</td>
		  </tr>
		  <tr>
			<td colspan="3">
			<h4>Malicious bandwidth table (Megabytes) by source IP</h4>
			{sip_bw_table}
			</td>
		  </tr>

		  <tr>
		 	<td valign="top">
				{sip_epm_html_final}
			</td>
		 	<td valign="top">
				{sip_ppm_html_final} 
			</td>
		 	<td valign="top">
				{sip_bpm_html_final}
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
