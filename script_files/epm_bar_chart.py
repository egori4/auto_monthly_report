#!/usr/bin/python3

import pandas as pd
import sqlite3
import sys
from pandas.core import series
import time

start_time = time.time()


def df(cust_id,cur_month,cur_year):
	path = f'./database_files/'+cust_id+'/'
	con = sqlite3.connect(path + f'database_'+cust_id+'.sqlite')

	df = pd.DataFrame(pd.read_sql_query(f"select month as 'Month',count(1) as 'Number of Events' from attacks where year={int(cur_year)-1} or month<={cur_month} group by month order by year", con))#.set_index('Month')
	


	


	con.close()

	# change Month value in df to month name
	df['Month'] = df['Month'].apply(lambda x: 'January' if x == 1 else x)
	df['Month'] = df['Month'].apply(lambda x: 'February' if x == 2 else x)
	df['Month'] = df['Month'].apply(lambda x: 'March' if x == 3 else x)
	df['Month'] = df['Month'].apply(lambda x: 'April' if x == 4 else x)
	df['Month'] = df['Month'].apply(lambda x: 'May' if x == 5 else x)
	df['Month'] = df['Month'].apply(lambda x: 'June' if x == 6 else x)
	df['Month'] = df['Month'].apply(lambda x: 'July' if x == 7 else x)
	df['Month'] = df['Month'].apply(lambda x: 'August' if x == 8 else x)
	df['Month'] = df['Month'].apply(lambda x: 'September' if x == 9 else x)
	df['Month'] = df['Month'].apply(lambda x: 'October' if x == 10 else x)
	df['Month'] = df['Month'].apply(lambda x: 'November' if x == 11 else x)
	df['Month'] = df['Month'].apply(lambda x: 'December' if x == 12 else x)

	result = [df.columns.tolist()] + df.values.tolist()
	# print(result)
	return result



print("--- %s seconds ---" % (time.time() - start_time))