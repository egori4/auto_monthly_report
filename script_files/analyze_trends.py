

import csv
import sys
import pandas as pd

cust_id = sys.argv[1]
month = sys.argv[2]
year = sys.argv[3]


# Paths
charts_tables_path = f"./tmp_files/{cust_id}/"
reports_path = f"./report_files/{cust_id}/"

#Units
bw_units = "Gigabytes" #Can be configured "Gigabytes", "Terabytes" or "Megabytes"
pkt_units = "Millions" #Can be configured "Millions" or "Billions"

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

	# Calculate and print the trends
	for name, count_previous, count_last in zip(attack_names, attack_counts_previous, attack_counts_last):
		if int(count_last) < int(count_previous):
			trend = "Decrease"
		else:
			trend = "Increase"
		
		difference = abs(int(count_last) - int(count_previous))

		#check if difference is float


		if isinstance(difference, float):
			difference = round(difference, 2)

		change = f"by {difference} {units} - from {count_previous} to {count_last} {units} "

		analysis += f'<li><strong>{name}:</strong><ul><li> {trend} {change}</li></ul>'

	analysis += '</ul>'

	return analysis


def trends_move_total(data, units="events"):
	
	prev_total = data[-2][1]
	last_total = data[-1][1]

	trend = "increased" if last_total > prev_total else "decreased"
	difference = abs(last_total - prev_total)
	
	if isinstance(difference, float):
		difference = round(difference, 2)

	result = f"This month the total number of {units} {trend} by {difference} {units} - from {prev_total} to {last_total} {units}"
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
	if bw_units or pkt_units:
		formatted_df = df.applymap(lambda x: format_numeric_value(x, bw_units, pkt_units))
	
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



if __name__ == '__main__':
	
	# Total events, packets and bandwidth trends
	events_total_bar_chart = convert_csv_to_list_of_lists(charts_tables_path + 'epm_total_bar.csv')
	events_total_bar_move_text = trends_move_total(events_total_bar_chart, 'events') 

	packets_total_bar = convert_csv_to_list_of_lists(charts_tables_path + 'ppm_total_bar.csv')
	packets_total_bar = convert_packets_units(packets_total_bar, pkt_units)
	pakets_total_bar_move = trends_move_total(packets_total_bar, ' packets(' + pkt_units + ')') 

	bw_total_bar = convert_csv_to_list_of_lists(charts_tables_path + 'bpm_total_bar.csv')
	bw_total_bar = convert_bw_units(bw_total_bar, bw_units)
	bw_total_bar_move = trends_move_total(bw_total_bar, bw_units) 

	# Events, packets and bandwidth trends by Attack Name
	events_trends = convert_csv_to_list_of_lists(charts_tables_path + 'epm_chart_lm.csv')
	events_trends_move = trends_move(events_trends, 'events')
	events_trends_table = csv_to_html_table(charts_tables_path + 'epm_table_lm.csv')

	packets_trends_chart = convert_csv_to_list_of_lists(charts_tables_path + 'ppm_chart_lm.csv')
	packets_trends_chart = convert_packets_units(packets_trends_chart, pkt_units)
	packets_trends_move_text = trends_move(packets_trends_chart, ' packets(' + pkt_units + ')')
	packets_table = csv_to_html_table(charts_tables_path + 'ppm_table_lm.csv',bw_units=None, pkt_units='Millions')



	bw_trends = convert_csv_to_list_of_lists(charts_tables_path + 'bpm_chart_lm.csv')
	bw_trends = convert_bw_units(bw_trends, bw_units)
	bw_trends_move = trends_move(bw_trends, bw_units)
	bw_table = csv_to_html_table(charts_tables_path + 'bpm_table_lm.csv',bw_units)

	# Events, packets and bandwidth trends by Attack Nam

	events_by_device_trends_chart_data = convert_csv_to_list_of_lists(charts_tables_path + 'device_epm_chart_lm.csv')
	events_by_device_trends_move_text = trends_move(events_by_device_trends_chart_data, 'events')
	events_by_device_table = csv_to_html_table(charts_tables_path + 'device_epm_table_lm.csv')

	packets_by_device_trends_chart_data = convert_csv_to_list_of_lists(charts_tables_path + 'device_ppm_chart_lm.csv')
	packets_by_device_trends_chart_data = convert_packets_units(packets_by_device_trends_chart_data, pkt_units)
	packets_by_device_trends_move_text = trends_move(packets_by_device_trends_chart_data, ' packets(' + pkt_units + ')')
	packets_by_device_table = csv_to_html_table(charts_tables_path + 'device_ppm_table_lm.csv',bw_units=None, pkt_units='Millions')


	bw_by_device_trends_chart_data = convert_csv_to_list_of_lists(charts_tables_path + 'device_bpm_chart_lm.csv')
	bw_by_device_trends_chart_data = convert_bw_units(bw_by_device_trends_chart_data, bw_units)
	bw_by_device_trends_move_text = trends_move(bw_by_device_trends_chart_data, bw_units)
	bw_by_device_table = csv_to_html_table(charts_tables_path + 'device_bpm_table_lm.csv',bw_units)



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
		  
			var epm_total_data = google.visualization.arrayToDataTable({events_total_bar_chart});
			var ppm_total_data = google.visualization.arrayToDataTable({packets_total_bar});
			var bpm_total_data = google.visualization.arrayToDataTable({bw_total_bar});

			var epm_data = google.visualization.arrayToDataTable({events_trends});
			var ppm_data = google.visualization.arrayToDataTable({packets_trends_chart});
			var bpm_data = google.visualization.arrayToDataTable({bw_trends});

			var epm_by_device_data = google.visualization.arrayToDataTable({events_by_device_trends_chart_data});
			var ppm_by_device_data = google.visualization.arrayToDataTable({packets_by_device_trends_chart_data});
			var bpm_by_device_data = google.visualization.arrayToDataTable({bw_by_device_trends_chart_data});

			var epm_total_options = {{
			  title: 'Total Events trends',
			  bar: {{groupWidth: "95%"}},
			  legend: {{position: 'none'}},
			  width: '100%'
			}};

			var ppm_total_options = {{
			  title: 'Total Malicious Packets count trends ({pkt_units})',
			  bar: {{groupWidth: "95%"}},
			  legend: {{position: 'none'}},
			  width: '100%'
			}};

			var bpm_total_options = {{
			  title: 'Total Malicious bandwidth sum trends ({bw_units})',
			  bar: {{groupWidth: "95%"}},
			  legend: {{position: 'none'}},
			  width: '100%'
			}};

			var epm_options = {{
			  title: 'Security Events trends',
			  vAxis: {{minValue: 0}},
			  isStacked: true,
			  legend: {{position: 'top', maxLines: 5}},
			  width: '100%'
			}};

			var ppm_options = {{
			  title: 'Malicious Packets trends ({pkt_units})',
			  vAxis: {{minValue: 0}},
			  isStacked: true,
			  legend: {{position: 'top', maxLines: 5}},
			  width: '100%'
			}};

			var bpm_options = {{
			  title: 'Malicious Bandwidth trends ({bw_units})',
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
			  title: 'Packets by device trends ({pkt_units})',
			  vAxis: {{minValue: 0}},
			  isStacked: true,
			  legend: {{position: 'top', maxLines: 5}},
			  width: '100%'
			}};

			var bpm_by_device_options = {{
			  title: 'Malicious Bandwidth by device trends ({bw_units})',
			  vAxis: {{minValue: 0}},
			  isStacked: true,
			  legend: {{position: 'top', maxLines: 5}},
			  width: '100%'
			}};


			var epm_total_chart = new google.visualization.ColumnChart(document.getElementById('epm_total_chart_div'));
			var ppm_total_chart = new google.visualization.ColumnChart(document.getElementById('ppm_total_chart_div'));
			var bpm_total_chart = new google.visualization.ColumnChart(document.getElementById('bpm_total_chart_div'));

			var epm_chart = new google.visualization.AreaChart(document.getElementById('epm_chart_div'));
			var ppm_chart = new google.visualization.AreaChart(document.getElementById('ppm_chart_div'));
			var bpm_chart = new google.visualization.AreaChart(document.getElementById('bpm_chart_div'));

			var epm_by_device_chart = new google.visualization.AreaChart(document.getElementById('epm_by_device_chart_div'));
			var ppm_by_device_chart = new google.visualization.AreaChart(document.getElementById('ppm_by_device_chart_div'));
			var bpm_by_device_chart = new google.visualization.AreaChart(document.getElementById('bpm_by_device_chart_div'));

			epm_total_chart.draw(epm_total_data, epm_total_options);
			ppm_total_chart.draw(ppm_total_data, ppm_total_options);
			bpm_total_chart.draw(bpm_total_data, bpm_total_options);

			epm_chart.draw(epm_data, epm_options);
			ppm_chart.draw(ppm_data, ppm_options);
			bpm_chart.draw(bpm_data, bpm_options);

			epm_by_device_chart.draw(epm_by_device_data, epm_by_device_options);
			ppm_by_device_chart.draw(ppm_by_device_data, ppm_by_device_options);
			bpm_by_device_chart.draw(bpm_by_device_data, bpm_by_device_options);

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

	  #epm_by_device_chart_div {{
		height: 50vh;
	  }}

	  #ppm_by_device_chart_div {{
		height: 50vh;
	  }}

	  #bpm_by_device_chart_div {{
		height: 50vh;
	  }}


	</style>
	<title>Radware Monthly Reports</title>
	</head>
	<body>
	  <table>
		<thead>
		  <tr>
			<th>Month to month trends by Security Events count</th>
			<th>Month to month trends by Malicious Packets(cumulative)</th>
			<th>Month to month trends by Malicious Bandwidth sum(cumulative)</th>
		  </tr>
		</thead>
		<tbody>
		  <tr>
			<td><div id="epm_total_chart_div"></td>
			<td><div id="ppm_total_chart_div"></td>
			<td><div id="bpm_total_chart_div"></td>
		  </tr>

		  <tr>
			<td><div id="epm_chart_div" style="height: 600px;"></td>
			<td><div id="ppm_chart_div" style="height: 600px;"></td>
			<td><div id="bpm_chart_div" style="height: 600px;"></td>
		  </tr>
		  <tr>
			<td style="text-align: left;">
				<h4>Change in Security Events number by attack name this month compared to the previous month</h4>
				{events_total_bar_move_text}{events_trends_move}</td>
			<td style="text-align: left;">
				<h4>Change in Malicious Packets number by attack name this month compared to the previous month</h4>
				{pakets_total_bar_move}{packets_trends_move_text}</td>

			<td style="text-align: left;">
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
			<h4>Malicious packets table ({pkt_units})</h4>
			{packets_table}
			</td>
		  </tr>
		  <tr>
			<td colspan="3">
			<h4>Malicious bandwidth table ({bw_units})</h4>
			{bw_table}
			</td>
		  </tr>	  
		  

		  <tr>
			<td><div id="epm_by_device_chart_div" style="height: 600px;"></td>
			<td><div id="ppm_by_device_chart_div" style="height: 600px;"></td>
			<td><div id="bpm_by_device_chart_div" style="height: 600px;"></td>
		  </tr>

		  <tr>

			<td style="text-align: left;">
				<h4>Change in Security Events number by device this month compared to the previous month</h4>
				{events_by_device_trends_move_text}
			</td>
			<td style="text-align: left;">
				<h4>Change in Malicious Packets number by device this month compared to the previous month</h4>
				{packets_by_device_trends_move_text}
			</td>
			
			<td style="text-align: left;">
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
			<h4>Malicious packets by device table ({pkt_units})</h4>
			{packets_by_device_table}
			</td>
		  </tr>
			
		  <tr>
			<td colspan="3">
			<h4>Malicious Bandwidth by device table ({bw_units})</h4>
			{bw_by_device_table}
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
