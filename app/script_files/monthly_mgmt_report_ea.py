#pip install openpyxl
#python3 script_files/monthly_mgmt_report.py ea 2 February 2022  ---> from WSL
#-------------------
import sys
import pandas as pd
import sqlite3
pd.set_option('display.max_rows', 20)
from datetime import date, datetime
from openpyxl import Workbook
from openpyxl import load_workbook
import time

start_time = time.time()


########Vars##############
cust_id = sys.argv[1]
month = int(sys.argv[2])
mon_name = str(sys.argv[3])
year = int(sys.argv[4])
path_d = f'./database_files/{cust_id}/'
path_r = f'./report_files/{cust_id}/'
##########################


con = sqlite3.connect(path_d + 'database_'+cust_id+'.sqlite')
#data = pd.read_csv("C:\\DATA\\Scripts\\Pull data from Vision by Marcelo\\AutoReport_v3.9\\report_files\\USCC\\USCC 10 2021 attacks.csv", parse_dates=['startDate','endDate'], dtype={"name": "string","attackIpsId":"string","actionType":"string","risk":"string"})
data = pd.read_sql_query("SELECT * from attacks", con)
con.close()

data_month = data[(data.month == month) & (data.year == year)] # data for the speicific month


total_mal_bw = '{:.2f}'.format(float(data_month['packetBandwidth'].sum()/8000000000))

total_mal_bw_iad1 = '{:.2f}'.format(float(data_month[(data_month.deviceName == "iad1-defensepro01")]['packetBandwidth'].sum()/8000000000))


print(f"EA’s on-premise Radware appliances scrubbed {float(total_mal_bw) - float(total_mal_bw_iad1)}TB of attack traffic to protect titles and services. This left {total_mal_bw_iad1}TB of detected attack traffic unmitigated and was absorbed by the infrastructure.")

print("--- %s seconds ---" % (time.time() - start_time))
