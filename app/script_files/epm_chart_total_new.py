#!/usr/bin/python3

import pandas as pd
import sqlite3
import sys
from pandas.core import series
import time

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

		df = pd.DataFrame(pd.read_sql_query("select name as 'Attack Name',count(*) as "+cal_month+" from attacks where month="+str(month)+" group by name order by count(*) desc", con)).set_index('Attack Name')
		frames.append(df)

	con.close()

	result = pd.concat(frames,axis=1).fillna(0)
	print(result.T.iloc[: , :7].to_csv())
	return result.T.iloc[: , :7].to_csv()

df()

print("--- %s seconds ---" % (time.time() - start_time))