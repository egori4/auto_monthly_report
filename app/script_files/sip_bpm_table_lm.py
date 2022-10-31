#!/usr/bin/python3

import pandas as pd
import sqlite3
import sys
from pandas.core import series
import time
import abuseipdb as aidb
import os
import json
import urllib.request

if not os.path.exists('./script_files/AbuseIPDB/Raw Data'):
	os.makedirs('./script_files/AbuseIPDB/Raw Data')

start_time = time.time()

cust_id = sys.argv[1]

def df():
	path = f'./database_files/'+cust_id+'/'
	con = sqlite3.connect(path + f'database_'+cust_id+'.sqlite')		
	month_list = pd.DataFrame(pd.read_sql_query("select month from attacks group by year,month", con))['month'].values.tolist()
	frames =[]

	for month in month_list:
		if month == 1:
			cal_month = 'January'
		if month == 2:
			cal_month = 'February'
		if month == 3:
			cal_month = 'March'
		if month == 4:
			cal_month = 'April'
		if month == 5:
			cal_month = 'May'
		if month == 6:
			cal_month = 'June'
		if month == 7:
			cal_month = 'July'
		if month == 8:
			cal_month = 'August'
		if month == 9:
			cal_month = 'September'
		if month == 10:
			cal_month = 'October'
		if month == 11:
			cal_month = 'November'
		if month == 12:
			cal_month = 'December'
		
		df = pd.DataFrame(pd.read_sql_query("select sourceAddress as 'Source IP',sum(packetBandwidth)/8000 as "+cal_month+" from attacks where month="+str(month)+" group by sourceAddress order by sum(packetBandwidth) desc", con)).set_index('Source IP')
		frames.append(df)

	con.close()
	result = pd.concat(frames,axis=1).fillna(0).sort_values(by=[cal_month], ascending=False)

	if 'Multiple' in result.index:
		result = result.drop(['Multiple'])
	if '0.0.0.0' in result.index:	
		result = result.drop(['0.0.0.0'])
		
	result = result.iloc[:10]

	sip_list = result.index[0:10].tolist()


	if Internet_Conn():
		for ip in sip_list:
			aidb.AbuseIPDBCallBw(ip)

		result['srcip'] = result.index
		result['GEO'] = result['srcip'].apply(AbuseIPDBGEO)
		result['Abuse Confidence'] = result['srcip'].apply(AbuseIPDBScore)
		result['ISP'] = result['srcip'].apply(AbuseIPDBISP)

		result = result.drop(['srcip'], axis=1)

		cols = result.columns.tolist()
		cols = cols[-1:] + cols[:-1]
		cols = cols[-1:] + cols[:-1]
		cols = cols[-1:] + cols[:-1]
		result = result[cols]

	print(result.head(10).to_csv())
	return result.head(10).to_csv()

def AbuseIPDBGEO(ip):
	with open('./script_files/AbuseIPDB/Raw Data/AbuseIPDBBw.json') as abuseipdb_file:
		abuseipdb_dic = json.load(abuseipdb_file)

	for data_dic in abuseipdb_dic['Src IP details']:
		for data,data_val in data_dic.items():
			# print(ip)
			if ip == data_val['ipAddress']:
				return data_val['countryCode']
				

def Internet_Conn(host='https://api.abuseipdb.com'):
    try:
        urllib.request.urlopen(host) #Python 3.x
        return True
    except:
        return False

def AbuseIPDBScore(ip):
	with open('./script_files/AbuseIPDB/Raw Data/AbuseIPDBBw.json') as abuseipdb_file:
		abuseipdb_dic = json.load(abuseipdb_file)

	for data_dic in abuseipdb_dic['Src IP details']:
		for data,data_val in data_dic.items():
			if ip == data_val['ipAddress']:
				return data_val['abuseConfidenceScore']

def AbuseIPDBISP(ip):
	with open('./script_files/AbuseIPDB/Raw Data/AbuseIPDBBw.json') as abuseipdb_file:
		abuseipdb_dic = json.load(abuseipdb_file)

	for data_dic in abuseipdb_dic['Src IP details']:
		for data,data_val in data_dic.items():
			if ip == data_val['ipAddress']:
				return data_val['isp']

df()

print("--- %s seconds ---" % (time.time() - start_time))
