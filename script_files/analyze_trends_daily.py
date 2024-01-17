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


##### Extract variables from run.sh ##############
run_file = 'run_daily.sh'
with open (run_file) as f:
	for line in f:
	#find line starting with top_n
		if line.startswith('top_n'):
			#print value after = sign
			top_n = int(line.split('=')[1].replace('\n',''))
			continue

		if line.startswith('bw_units'):
			bw_units = str(line.split('=')[1].replace('\n','').replace('"',''))
			continue

		if line.startswith('pkt_units'):
			pkt_units = str(line.split('=')[1].replace('\n','')).replace('"','')
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
	for row in data:
		converted_row = []
		for value in row:
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

	with open(reports_path + f'trends_{cust_id}_{month}_{year}.html', 'w') as f:
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


def events_per_day_html_table():

	# Group by day_of_month, name, deviceName, ruleName and aggregate sum of packetCount
	events_per_day = data_month.groupby(['startDayOfMonth', 'name', 'deviceName', 'ruleName']).size()

	# Get the top 5 events with the highest sum of packet counts for each day
	events_per_day_top5 = events_per_day.groupby(level=['startDayOfMonth'], group_keys=False).nlargest(5).apply(format_with_commas).to_frame('Security Events Count')
	events_per_day_top5 = events_per_day_top5.to_html()

	for device_ip, device_name in defensepros.items():
		events_per_day_top5=events_per_day_top5.replace(device_ip, device_name)

	return events_per_day_top5

def packets_per_day_html_table():

	# Group by day_of_month, name, deviceName, ruleName and aggregate sum of packetCount
	packets_per_day = data_month.groupby(['startDayOfMonth', 'name', 'deviceName', 'ruleName'])['packetCount'].sum()

	# Get the top 5 events with the highest sum of packet counts for each day
	packets_per_day_top5 = packets_per_day.groupby(level=['startDayOfMonth'], group_keys=False).nlargest(5).apply(format_with_commas).to_frame('Malicious Packets sum')
	packets_per_day_top5 = packets_per_day_top5.to_html()

	for device_ip, device_name in defensepros.items():
		packets_per_day_top5=packets_per_day_top5.replace(device_ip, device_name)

	return packets_per_day_top5


def bandwidth_per_day_html_table():
	# Group by day_of_month, name, deviceName, ruleName and aggregate sum of packetCount
	bandwidth_per_day = data_month.groupby(['startDayOfMonth', 'name', 'deviceName', 'ruleName'])['packetBandwidth'].sum()

	# Get the top 5 events with the highest sum of packet counts for each day
	bandwidth_per_day_top5 = bandwidth_per_day.groupby(level=['startDayOfMonth'], group_keys=False).nlargest(5).apply(format_with_commas).to_frame('Malicious bandwidth sum')
	bandwidth_per_day_top5 = bandwidth_per_day_top5.to_html()

	for device_ip, device_name in defensepros.items():
		bandwidth_per_day_top5=bandwidth_per_day_top5.replace(device_ip, device_name)

	return bandwidth_per_day_top5





def events_per_day_html(epm):
	data_month_epm = data_month[data_month['name'] == epm]
	series_epm = data_month_epm.groupby(['name','deviceName','ruleName']).size().sort_values(ascending=False).apply(format_with_commas).head(10)
	events_per_day_html = series_epm.to_frame('Count')
	events_per_day_html=events_per_day_html.to_html()

	for device_ip, device_name in defensepros.items():
		events_per_day_html=events_per_day_html.replace(device_ip, device_name)

	return events_per_day_html

def packets_per_day_html(ppm):
	data_month_ppm = data_month[data_month['name'] == ppm]
	series_ppm = data_month_ppm.groupby(['name','deviceName','ruleName']).sum()['packetCount'].sort_values(ascending=False).apply(format_with_commas).head(10)
	packets_per_day_html = series_ppm.to_frame('Malicious Packets')
	packets_per_day_html=packets_per_day_html.to_html()

	for device_ip, device_name in defensepros.items():
		packets_per_day_html=packets_per_day_html.replace(device_ip, device_name)

	return packets_per_day_html

def bandwidth_per_day_html(bpm):
	data_month_bpm = data_month[data_month['name'] == bpm]
	series_bpm = data_month_bpm.groupby(['name','deviceName','ruleName']).sum()['packetBandwidth'].sort_values(ascending=False).apply(format_with_commas).head(10)
	df_bandwidth_per_day_html = series_bpm.to_frame('Malicious Bandwidth')
	df_bandwidth_per_day_html=df_bandwidth_per_day_html.to_html()

	for device_ip, device_name in defensepros.items():
		df_bandwidth_per_day_html=df_bandwidth_per_day_html.replace(device_ip, device_name)

	return df_bandwidth_per_day_html



def device_events_per_day_html(device_epm):

	for device_ip, device_name in defensepros.items():
		if device_name == device_epm:

			data_month_epm = data_month[data_month['deviceName'] == device_ip]
			device_series_epm = data_month_epm.groupby(['deviceName','name','ruleName']).size().sort_values(ascending=False).apply(format_with_commas).head(10)
			device_events_per_day_html = device_series_epm.to_frame('Count')
			device_events_per_day_html=device_events_per_day_html.to_html().replace(device_ip, device_name)
			
	return device_events_per_day_html

def device_packets_per_day_html(device_ppm):

	for device_ip, device_name in defensepros.items():
		
		if device_name == device_ppm:
			data_month_ppm = data_month[data_month['deviceName'] == device_ip]
			device_series_ppm = data_month_ppm.groupby(['deviceName','name','ruleName']).sum()['packetCount'].sort_values(ascending=False).apply(format_with_commas).head(10)
			device_packets_per_day_html = device_series_ppm.to_frame('Malicious Packets')
			device_packets_per_day_html=device_packets_per_day_html.to_html().replace(device_ip, device_name)
	return device_packets_per_day_html

def device_bandwidth_per_day_html(device_bpm):
	for device_ip, device_name in defensepros.items():
		if device_name == device_bpm:
			data_month_bpm = data_month[data_month['deviceName'] == device_ip]
			device_series_bpm = data_month_bpm.groupby(['deviceName','name','ruleName']).sum()['packetBandwidth'].sort_values(ascending=False).apply(format_with_commas).head(10)
			device_df_bandwidth_per_day_html = device_series_bpm.to_frame('Malicious Bandwidth')
			device_df_bandwidth_per_day_html= device_df_bandwidth_per_day_html.to_html().replace(device_ip, device_name)


	return device_df_bandwidth_per_day_html


def policy_events_per_day_html(policy_epm):

	data_month_epm = data_month[data_month['ruleName'] == policy_epm]
	series_epm = data_month_epm.groupby(['ruleName','name','deviceName']).size().sort_values(ascending=False).apply(format_with_commas).head(10)
	events_per_day_html = series_epm.to_frame('Count')
	events_per_day_html=events_per_day_html.to_html()

	for device_ip, device_name in defensepros.items():
		events_per_day_html=events_per_day_html.replace(device_ip, device_name)
		
	return events_per_day_html

def policy_packets_per_day_html(policy_ppm):
	data_month_ppm = data_month[data_month['ruleName'] == policy_ppm]
	series_ppm = data_month_ppm.groupby(['ruleName','name','deviceName']).sum()['packetCount'].sort_values(ascending=False).apply(format_with_commas).head(10)
	packets_per_day_html = series_ppm.to_frame('Malicious Packets')
	packets_per_day_html=packets_per_day_html.to_html()
	
	for device_ip, device_name in defensepros.items():
		packets_per_day_html=packets_per_day_html.replace(device_ip, device_name)
	
	return packets_per_day_html

def policy_bandwidth_per_day_html(policy_bpm):
	data_month_bpm = data_month[data_month['ruleName'] == policy_bpm]
	series_bpm = data_month_bpm.groupby(['ruleName','name','deviceName']).sum()['packetBandwidth'].sort_values(ascending=False).apply(format_with_commas).head(10)
	df_bandwidth_per_day_html = series_bpm.to_frame('Malicious Bandwidth')
	df_bandwidth_per_day_html=df_bandwidth_per_day_html.to_html()

	for device_ip, device_name in defensepros.items():
		df_bandwidth_per_day_html=df_bandwidth_per_day_html.replace(device_ip, device_name)
	
	return df_bandwidth_per_day_html


def sip_events_per_day_html(sip_epm):

	data_month_epm = data_month[data_month['sourceAddress'] == sip_epm]
	series_epm = data_month_epm.groupby(['sourceAddress','name','deviceName','ruleName']).size().sort_values(ascending=False).apply(format_with_commas).head(10)
	events_per_day_html = series_epm.to_frame('Count')
	events_per_day_html=events_per_day_html.to_html()

	for device_ip, device_name in defensepros.items():
		events_per_day_html=events_per_day_html.replace(device_ip, device_name)
		
	return events_per_day_html


def sip_packets_per_day_html(sip_ppm):
	data_month_ppm = data_month[data_month['sourceAddress'] == sip_ppm]
	series_ppm = data_month_ppm.groupby(['sourceAddress','name','deviceName','ruleName']).sum()['packetCount'].sort_values(ascending=False).apply(format_with_commas).head(10)
	packets_per_day_html = series_ppm.to_frame('Malicious Packets')
	packets_per_day_html=packets_per_day_html.to_html()
	
	for device_ip, device_name in defensepros.items():
		packets_per_day_html=packets_per_day_html.replace(device_ip, device_name)
	
	return packets_per_day_html

def sip_bandwidth_per_day_html(sip_bpm):
	data_month_bpm = data_month[data_month['sourceAddress'] == sip_bpm]
	series_bpm = data_month_bpm.groupby(['sourceAddress','name','deviceName','ruleName']).sum()['packetBandwidth'].sort_values(ascending=False).apply(format_with_commas).head(10)
	df_bandwidth_per_day_html = series_bpm.to_frame('Malicious Bandwidth')
	df_bandwidth_per_day_html=df_bandwidth_per_day_html.to_html()

	for device_ip, device_name in defensepros.items():
		df_bandwidth_per_day_html=df_bandwidth_per_day_html.replace(device_ip, device_name)
	
	return df_bandwidth_per_day_html





def format_with_commas(value):
	return '{:,}'.format(value)


if __name__ == '__main__':


	# Events per day count
	events_per_day_trends = convert_csv_to_list_of_lists(charts_tables_path + 'events_per_day_last_month.csv')

	# Malicious bandwidth per day
	packets_per_day_trends = convert_csv_to_list_of_lists(charts_tables_path + 'packets_per_day_last_month.csv')

	# Malicious bandwidth per day
	bandwidth_per_day_trends = convert_csv_to_list_of_lists(charts_tables_path + 'bandwidth_per_day_last_month.csv')




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
	con = sqlite3.connect(db_path + 'database_'+cust_id+'_'+str(month)+'.sqlite')
	# data = pd.read_sql_query("SELECT * from attacks", con)
	data_month = pd.read_sql_query(f"SELECT deviceName,month,year,packetBandwidth,name,packetCount,ruleName,category,sourceAddress,destAddress,startTime,endTime,startDate,attackIpsId,actionType,maxAttackPacketRatePps,maxAttackRateBps,destPort,protocol,startDayOfMonth from attacks", con)

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
		events_per_day_html_final+=f'<h4>{value} distribution across devices and policies</h4>'
		events_per_day_html_final+= events_per_day_html(events_per_day_top_list[index])

	for index, value in enumerate(packets_per_day_top_list):
		packets_per_day_html_final+=f'<h4>{value} distribution across devices and policies</h4>'
		packets_per_day_html_final+= packets_per_day_html(packets_per_day_top_list[index])
		
	for index, value in enumerate(bandwidth_per_day_top_list):
		bandwidth_per_day_html_final+=f'<h4>{value} distribution across devices and policies</h4>'
		bandwidth_per_day_html_final+= bandwidth_per_day_html(bandwidth_per_day_top_list[index])



	for index, value in enumerate(device_events_per_day_top_list):
		device_events_per_day_html_final+=f'<h4>Top Attacks and policies for device {value}</h4>'
		device_events_per_day_html_final+= device_events_per_day_html(device_events_per_day_top_list[index])

	for index, value in enumerate(device_packets_per_day_top_list):
		device_packets_per_day_html_final+=f'<h4>Top Attacks and policies for device {value}</h4>'
		device_packets_per_day_html_final+= device_packets_per_day_html(device_packets_per_day_top_list[index])

	for index, value in enumerate(device_bandwidth_per_day_top_list):
		device_bandwidth_per_day_html_final+=f'<h4>Top Attacks and policies for device {value}</h4>'
		device_bandwidth_per_day_html_final+= device_bandwidth_per_day_html(device_packets_per_day_top_list[index])


	for index, value in enumerate(policy_events_per_day_top_list):
		policy_events_per_day_html_final+=f'<h4>Distribution of attacks and devices for policy {value}</h4>'
		policy_events_per_day_html_final+= policy_events_per_day_html(policy_events_per_day_top_list[index])

	for index, value in enumerate(policy_packets_per_day_top_list):
		policy_packets_per_day_html_final+=f'<h4>Distribution of attacks and devices for policy {value}</h4>'
		policy_packets_per_day_html_final+= policy_packets_per_day_html(policy_packets_per_day_top_list[index])
		
	for index, value in enumerate(policy_bandwidth_per_day_top_list):
		policy_bandwidth_per_day_html_final+=f'<h4>Distribution of attacks and devices for policy {value}</h4>'
		policy_bandwidth_per_day_html_final+= policy_bandwidth_per_day_html(policy_bandwidth_per_day_top_list[index])


	for index, value in enumerate(sip_events_per_day_top_list):
		sip_events_per_day_html_final+=f'<h4>Distribution of attacks and devices for Source IP {value}</h4>'
		sip_events_per_day_html_final+= sip_events_per_day_html(sip_events_per_day_top_list[index])

	for index, value in enumerate(sip_packets_per_day_top_list):
		sip_packets_per_day_html_final+=f'<h4>Distribution of attacks and devices for Source IP {value}</h4>'
		sip_packets_per_day_html_final+= sip_packets_per_day_html(sip_packets_per_day_top_list[index])
		
	for index, value in enumerate(sip_bandwidth_per_day_top_list):
		sip_bandwidth_per_day_html_final+=f'<h4>Distribution of attacks and devices for Source IP {value}</h4>'
		sip_bandwidth_per_day_html_final+= sip_bandwidth_per_day_html(sip_bandwidth_per_day_top_list[index])


	#5 Generate html for the last month

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

			

			
			var events_per_day_options = {{
			  title: 'Events per day, last month',
			  vAxis: {{minValue: 0}},
			  hAxis: {{ticks: events_per_day_data.getDistinctValues(0),minTextSpacing:1,showTextEvery:1}},
			  isStacked: false,
			  legend: {{position: 'top', maxLines: 5}},
			  width: '100%'
			}};

			  var packets_per_day_options = {{
			  title: 'Malicious packets per day, last month ({pkt_units})',
			  vAxis: {{minValue: 0}},
			  hAxis: {{ticks: packets_per_day_data.getDistinctValues(0),minTextSpacing:1,showTextEvery:1}},
			  isStacked: false,
			  legend: {{position: 'top', maxLines: 5}},
			  width: '100%'
			}};

			var bandwidth_per_day_options = {{
			  title: 'Malicious bandwidth per day, last month ({bw_units})',
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
			  isStacked: true,
			  legend: {{position: 'top', maxLines: 5}},
			  width: '100%'
			}};


			var attack_packets_per_day_options = {{
			  title: 'Malicious Packets trends ({pkt_units}) - TopN by last day',
			  vAxis: {{minValue: 0}},
			  hAxis: {{ticks: events_per_day_data.getDistinctValues(0),minTextSpacing:1,showTextEvery:1}},
			  isStacked: true,
			  legend: {{position: 'top', maxLines: 5}},
			  width: '100%'
			}};

			var attack_bandwidth_per_day_options = {{
			  title: 'Malicious Bandwidth trends ({bw_units}) - TopN by last day',
			  vAxis: {{minValue: 0}},
			  hAxis: {{ticks: events_per_day_data.getDistinctValues(0),minTextSpacing:1,showTextEvery:1}},
			  isStacked: true,
			  legend: {{position: 'top', maxLines: 5}},
			  width: '100%'
			}};



			var events_per_day_options_alltimehigh = {{
			  title: 'Security Events trends - TopN all time high',
			  vAxis: {{minValue: 0}},
			  hAxis: {{ticks: events_per_day_data.getDistinctValues(0),minTextSpacing:1,showTextEvery:1}},
			  isStacked: true,
			  legend: {{position: 'top', maxLines: 5}},
			  width: '100%'
			}};

			var packets_per_day_options_alltimehigh = {{
			  title: 'Malicious Packets trends ({pkt_units}) - TopN all time high',
			  vAxis: {{minValue: 0}},
			  hAxis: {{ticks: events_per_day_data.getDistinctValues(0),minTextSpacing:1,showTextEvery:1}},
			  isStacked: true,
			  legend: {{position: 'top', maxLines: 5}},
			  width: '100%'
			}};

			var bandwidth_per_day_options_alltimehigh = {{
			  title: 'Malicious Bandwidth trends ({bw_units}) - TopN all time high',
			  vAxis: {{minValue: 0}},
			  isStacked: true,
			  hAxis: {{ticks: events_per_day_data.getDistinctValues(0),minTextSpacing:1,showTextEvery:1}},
			  legend: {{position: 'top', maxLines: 5}},
			  width: '100%'
			}};

			var events_per_day_by_device_options = {{
			  title: 'Events by device trends',
			  vAxis: {{minValue: 0}},
			  hAxis: {{ticks: events_per_day_data.getDistinctValues(0),minTextSpacing:1,showTextEvery:1}},
			  isStacked: true,
			  legend: {{position: 'top', maxLines: 5}},
			  width: '100%'
			}};

			var packets_per_day_by_device_options = {{
			  title: 'Packets by device trends ({pkt_units})',
			  vAxis: {{minValue: 0}},
			  hAxis: {{ticks: events_per_day_data.getDistinctValues(0),minTextSpacing:1,showTextEvery:1}},
			  isStacked: true,
			  legend: {{position: 'top', maxLines: 5}},
			  width: '100%'
			}};

			var bandwidth_per_day_by_device_options = {{
			  title: 'Malicious Bandwidth by device trends ({bw_units})',
			  vAxis: {{minValue: 0}},
			  hAxis: {{ticks: events_per_day_data.getDistinctValues(0),minTextSpacing:1,showTextEvery:1}},
			  isStacked: true,
			  legend: {{position: 'top', maxLines: 5}},
			  width: '100%'
			}};

			var sip_events_per_day_options = {{
			  title: 'Security Events trends by source IP',
			  vAxis: {{minValue: 0}},
			  hAxis: {{ticks: events_per_day_data.getDistinctValues(0),minTextSpacing:1,showTextEvery:1}},
			  isStacked: true,
			  legend: {{position: 'top', maxLines: 5}},
			  width: '100%'
			}};

			var sip_packets_per_day_options = {{
			  title: 'Malicious Packets trends ({pkt_units}) by source IP',
			  vAxis: {{minValue: 0}},
			  hAxis: {{ticks: events_per_day_data.getDistinctValues(0),minTextSpacing:1,showTextEvery:1}},
			  isStacked: true,
			  legend: {{position: 'top', maxLines: 5}},
			  width: '100%'
			}};

			var sip_bandwidth_per_day_options = {{
			  title: 'Malicious Bandwidth trends (Megabytes) by source IP',
			  vAxis: {{minValue: 0}},
			  hAxis: {{ticks: events_per_day_data.getDistinctValues(0),minTextSpacing:1,showTextEvery:1}},
			  isStacked: true,
			  legend: {{position: 'top', maxLines: 5}},
			  width: '100%'
			}};

			var policy_events_per_day_options = {{
			  title: 'Security Events trends by Policy',
			  vAxis: {{minValue: 0}},
			  hAxis: {{ticks: events_per_day_data.getDistinctValues(0),minTextSpacing:1,showTextEvery:1}},
			  isStacked: true,
			  legend: {{position: 'top', maxLines: 5}},
			  width: '100%'
			}};

			var policy_packets_per_day_options = {{
			  title: 'Malicious Packets trends ({pkt_units}) by Policy',
			  vAxis: {{minValue: 0}},
			  hAxis: {{ticks: events_per_day_data.getDistinctValues(0),minTextSpacing:1,showTextEvery:1}},
			  isStacked: true,
			  legend: {{position: 'top', maxLines: 5}},
			  width: '100%'
			}};

			var policy_bandwidth_per_day_options = {{
			  title: 'Malicious Bandwidth trends ({bw_units}) by Policy',
			  vAxis: {{minValue: 0}},
			  hAxis: {{ticks: events_per_day_data.getDistinctValues(0),minTextSpacing:1,showTextEvery:1}},
			  isStacked: true,
			  legend: {{position: 'top', maxLines: 5}},
			  width: '100%'
			}};


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
			

			events_per_day_chart.draw(events_per_day_data, events_per_day_options);
			bandwidth_per_day_chart.draw(bandwidth_per_day_data, bandwidth_per_day_options);
			packets_per_day_chart.draw(packets_per_day_data, packets_per_day_options);

;

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

      .fit-text {{
        font-size: 14px; /* Adjust the font size as needed */
        word-wrap: break-word; /* Allow text to break onto the next line if needed */
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
			<th>Daily trends by Security Events count</th>
			<th>Daily trends by Malicious Packets(cumulative)</th>
			<th>Daily trends by Malicious Bandwidth sum(cumulative)</th>
		  </tr>

		  <tr>
			<td><div id="events_per_day_chart_div_alltimehigh" style="height: 600px;"></td>
			<td><div id="packets_per_day_chart_div_alltimehigh" style="height: 600px;"></td>
			<td><div id="bandwidth_per_day_chart_div_alltimehigh" style="height: 600px;"></td>
		  </tr>
		  
		  <tr>
			<td colspan="3">
			<h4>Security Events table</h4>
			{events_trends_table_alltimehigh}
			</td>
		  </tr>
		  <tr>
			<td colspan="3" class="fit-text">
			<h4>Malicious packets table ({pkt_units})</h4>
			{packets_table_alltimehigh}
			</td>
		  </tr>
		  <tr>
			<td colspan="3" class="fit-text">
			<h4>Malicious bandwidth table ({bw_units})</h4>
			{bw_table_alltimehigh}
			</td>
		  </tr>	  
		  
		  <tr>
		 	<td valign="top">
				{events_per_day_html_final}
			</td>
		 	<td valign="top">
				{packets_per_day_html_final} 
			</td>
		 	<td valign="top">
				{bandwidth_per_day_html_final}
			</td>
		  </tr>




		  <tr>
			<td><div id="events_per_day_by_device_chart_div" style="height: 600px;"></td>
			<td><div id="packets_per_day_by_device_chart_div" style="height: 600px;"></td>
			<td><div id="bandwidth_per_day_by_device_chart_div" style="height: 600px;"></td>
		  </tr>

		  <tr>


		  </tr>
		  <tr>
			<td colspan="3">
			<h4>Security Events by device table</h4>
			{events_by_device_table}
			</td>
		  </tr>
		  

		  <tr>
			<td colspan="3" class="fit-text">
			<h4>Malicious packets by device table ({pkt_units})</h4>
			{packets_by_device_table}
			</td>
		  </tr>
			
		  <tr>
			<td colspan="3" class="fit-text">
			<h4>Malicious Bandwidth by device table ({bw_units})</h4>
			{bw_by_device_table}
			</td>
		  </tr>


		  <tr>
		 	<td valign="top">
				{device_events_per_day_html_final}
			</td>
		 	<td valign="top">
				{device_packets_per_day_html_final}
			</td>
		 	<td valign="top">
				{device_bandwidth_per_day_html_final}			
			</td>
		  </tr>



		  <tr>
			<td><div id="policy_events_per_day_chart_div" style="height: 600px;"></td>
			<td><div id="policy_packets_per_day_chart_div" style="height: 600px;"></td>
			<td><div id="policy_bandwidth_per_day_chart_div" style="height: 600px;"></td>
		  </tr>

		  <tr>
			<td colspan="3">
			<h4>Security Events table by Policy</h4>
			{policy_events_trends_table}
			</td>
		  </tr>
		  <tr>
			<td colspan="3" class="fit-text">
			<h4>Malicious packets table ({pkt_units}) by Policy</h4>
			{policy_packets_table}
			</td>
		  </tr>
		  <tr>
			<td colspan="3" class="fit-text">
			<h4>Malicious bandwidth table (Megabytes) by Policy</h4>
			{policy_bw_table}
			</td>
		  </tr>	  

		  <tr>
		 	<td valign="top">
				{policy_events_per_day_html_final}
			</td>
		 	<td valign="top">
				{policy_packets_per_day_html_final} 
			</td>
		 	<td valign="top">
				{policy_bandwidth_per_day_html_final}
			</td>
		  </tr>



		  <tr>
			<td><div id="sip_events_per_day_chart_div" style="height: 600px;"></td>
			<td><div id="sip_packets_per_day_chart_div" style="height: 600px;"></td>
			<td><div id="sip_bandwidth_per_day_chart_div" style="height: 600px;"></td>
		  </tr>

		  

		  <tr>
			<td colspan="3" class="fit-text">
			<h4>Security Events table by source IP</h4>
			{sip_events_trends_table}
			</td>
		  </tr>
		  <tr>
			<td colspan="3" class="fit-text">
			<h4>Malicious packets table ({pkt_units}) by source IP</h4>
			{sip_packets_table}
			</td>
		  </tr>
		  <tr>
			<td colspan="3" class="fit-text">
			<h4>Malicious bandwidth table (Megabytes) by source IP</h4>
			{sip_bw_table}
			</td>
		  </tr>

		  <tr>
		 	<td valign="top">
				{sip_events_per_day_html_final}
			</td>
		 	<td valign="top">
				{sip_packets_per_day_html_final} 
			</td>
		 	<td valign="top">
				{sip_bandwidth_per_day_html_final}
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
