import smtplib
from email.mime.text import MIMEText
from email.mime.base import MIMEBase 
from email.mime.multipart import MIMEMultipart
from email import encoders
from datetime import datetime
import sqlite3
import pandas as pd
import os
import sys
import tarfile

cust_id = sys.argv[1]
#print(f'argv1 {cust_id}')

currentmonth = int(sys.argv[2]) #actual previous month from today
print(f'currentmonth is {currentmonth}')

currentyear = int(sys.argv[3])

smtp_auth = sys.argv[4]
if smtp_auth == "true":
	smtp_auth = True
else:
	smtp_auth = False

#print(smtp_auth)

smtp_server = sys.argv[5] # SMTP server name
#print(smtp_server)

smtp_server_port= sys.argv[6] # SMTP server port
#print(smtp_server_port)

smtp_sender = sys.argv[7] # Email sender address setting
#print(smtp_sender)

smtp_password = sys.argv[8] # Email password (optional)
#print(smtp_password)

smtp_list = sys.argv[10:] # Email address/address list recepient/s(comma separated)

#smtp_list.remove('EA')
print(f'SMTP list is {smtp_list}')

smtp_subject_prefix = sys.argv[9] # Email Subject
print(smtp_subject_prefix)


path_r = './report_files/'
path_d = f'./database_files/{cust_id}/'

prevmonth = int(currentmonth) - 1
print(f'python prevmonth is {prevmonth}')

prevmonth_minus1 = int(prevmonth - 1)
prevyear = int(datetime.now().year) - 1


def email_body():
	#print(path_d + 'database_'+cust_id+'.sqlite')
	con = sqlite3.connect(path_d + 'database_'+cust_id+'.sqlite')

	if currentmonth != 1:
		#print(f'python year {currentyear}, type{type(currentyear)}')
		data = pd.read_sql_query(f"SELECT deviceName,month,year, packetBandwidth,name,packetCount,ruleName,category,sourceAddress,destAddress,startTime,endTime,startDate,attackIpsId,maxAttackPacketRatePps,maxAttackRateBps from attacks", con)
		data_month = data[(data.month == currentmonth) &(data.year == currentyear)] # data for the speicific month  
		#print(data_month)
		data_month_prev = data[(data.month == (currentmonth -1)) & (data.year == currentyear)] # data for the speicific month
	else:
		data = pd.read_sql_query(f"SELECT deviceName,month,year, packetBandwidth,name,packetCount,ruleName,category,sourceAddress,destAddress,startTime,endTime,startDate,attackIpsId,maxAttackPacketRatePps,maxAttackRateBps from attacks where month=12 and year={prevyear}", con)
		data_month = data[(data.month == 12) & (data.year == prevyear)] # data for the speicific month
		data_month_prev = data[(data.month == 11) & (data.year == prevyear)] # data for the speicific month

	con.close()

	#############EA  High Level Management summary#######################

	email_body = f'\r\n\r\nElectronic Arts High Level Management summary:'

	total_mal_bw = '{:.2f}'.format(float(data_month['packetBandwidth'].sum()/8000000000))

	total_mal_bw_iad1 = '{:.2f}'.format(float(data_month[(data_month.deviceName == "10.76.4.241")]['packetBandwidth'].sum()/8000000))
	print(total_mal_bw_iad1)
	email_body = email_body + f"\r\n\r\n\tEA’s on-premise Radware appliances scrubbed {float(total_mal_bw) - float(total_mal_bw_iad1)}TB of attack traffic to protect titles and services. This left {total_mal_bw_iad1}GB of detected attack traffic unmitigated and was absorbed by the infrastructure."

	device = data_month.sort_values(by=['maxAttackRateBps'], ascending=False).iloc[0]['deviceName']
	policy = data_month.sort_values(by=['maxAttackRateBps'], ascending=False).iloc[0]['ruleName']
	attack_cat = data_month.sort_values(by=['maxAttackRateBps'], ascending=False).iloc[0]['category']
	attack_name = data_month.sort_values(by=['maxAttackRateBps'], ascending=False).iloc[0]['name']
	src_ip = data_month.sort_values(by=['maxAttackRateBps'], ascending=False).iloc[0]['sourceAddress']
	dst_ip = data_month.sort_values(by=['maxAttackRateBps'], ascending=False).iloc[0]['destAddress']
	attack_bw = ((data_month.sort_values(by=['maxAttackRateBps'], ascending=False).iloc[0]['packetBandwidth'])/8000000)
	attack_pkt = format((data_month.sort_values(by=['maxAttackRateBps'], ascending=False).iloc[0]['packetCount']), ',d')
	duration = (data_month.sort_values(by=['maxAttackRateBps'], ascending=False).iloc[0]['endTime'])-(data_month.sort_values(by=['maxAttackRateBps'], ascending=False).iloc[0]['startTime'])
	dur = str('{:.1f}'.format(float(duration/60000))) + ' min /' + str(int(duration/1000)) + ' sec'
	attack_start = data_month.sort_values(by=['maxAttackRateBps'], ascending=False).iloc[0]['startDate']
	attack_id = data_month.sort_values(by=['maxAttackRateBps'], ascending=False).iloc[0]['attackIpsId']
	attack_maxpps = data_month.sort_values(by=['maxAttackRateBps'], ascending=False).iloc[0]['maxAttackPacketRatePps']
	attack_maxbps = data_month.sort_values(by=['maxAttackRateBps'], ascending=False).iloc[0]['maxAttackRateBps']

	email_body = email_body + f'\r\n\r\n\tThe most aggressive DDoS attack mitigated by Radware on-premise equipment was a {attack_cat} type {attack_name}. The attack occurred on {attack_start}(UTC) lasting {dur.split()[0].split("/")[0]} min, directed at destination IP {dst_ip} at peak rate of {"{:.2f}".format(float(attack_maxbps/1000000000))} Gbps. The mitigation equipment dropped cumulatively {attack_pkt} packets for a total of {"{:.2f}".format(float(attack_bw))} GB data during this attack.'


	## Events count count this month with previous month ##############################

	email_body = email_body + f'\r\n\r\nMonth to month trends:'
	
	total_events = data_month.name.count()
	total_events_prev = data_month_prev.name.count()

	events_delta = int(total_events) - int(total_events_prev)

	if events_delta > 0:
		email_body = email_body + str(f'\r\n\r\n\tIncrease of {int(abs(events_delta))} events this month compared to the previous month.')
	if events_delta < 0:
		email_body = email_body + str(f'\r\n\r\nDecrease of {int(abs(events_delta))} events this month compared to the previous month.')


	## Maplicious packets count this month with previous month ##############################

	total_mal_pkts = float(data_month['packetCount'].sum()/1000000)
	total_mal_pkts_prev = float(data_month_prev['packetCount'].sum()/1000000)

	pkts_delta = float(total_mal_pkts) - float(total_mal_pkts_prev)

	if pkts_delta > 0:
		email_body = email_body + f'\r\n\r\n\tIncrease of {format(abs(int(pkts_delta)), ",d")} Mil in malicious packets this month compared to the previous month.'
	if pkts_delta < 0:
		email_body = email_body + f'\r\n\r\n\tDecrease of {format(abs(int(pkts_delta)), ",d")} Mil in malicious packets this month compared to the previous month.'


	## Maplicious bandwidth count this month with previous month ##############################

	total_mal_bw = float(data_month['packetBandwidth'].sum()/8000000000)
	total_mal_bw_prev = float(data_month_prev['packetBandwidth'].sum()/8000000000)

	bw_delta = float(total_mal_bw) - float(total_mal_bw_prev)
	if bw_delta > 0:
		email_body = email_body + f'\r\n\r\n\tIncrease of {"{:.2f}".format(abs(bw_delta))} TB in malicious bandwidth this month compared to the previous month.'
	if bw_delta < 0:
		email_body = email_body + f'\r\n\r\n\tDecrease of {"{:.2f}".format(abs(bw_delta))} TB in malicious bandwidth this month compared to the previous month.'



		## Top #1 Attack summary by packet count ####################################

	email_body = email_body + f'\r\n\r\nTop attacks of the month\r\n\r\n'

	device = data_month.sort_values(by=['packetCount'], ascending=False).iloc[0]['deviceName']
	policy = data_month.sort_values(by=['packetCount'], ascending=False).iloc[0]['ruleName']
	attack_cat = data_month.sort_values(by=['packetCount'], ascending=False).iloc[0]['category']
	attack_name = data_month.sort_values(by=['packetCount'], ascending=False).iloc[0]['name']
	src_ip = data_month.sort_values(by=['packetCount'], ascending=False).iloc[0]['sourceAddress']
	dst_ip = data_month.sort_values(by=['packetCount'], ascending=False).iloc[0]['destAddress']
	attack_bw = ((data_month.sort_values(by=['packetCount'], ascending=False).iloc[0]['packetBandwidth'])/8000000)
	attack_pkt = format((data_month.sort_values(by=['packetCount'], ascending=False).iloc[0]['packetCount']), ',d')
	duration = (data_month.sort_values(by=['packetCount'], ascending=False).iloc[0]['endTime'])-(data_month.sort_values(by=['packetCount'], ascending=False).iloc[0]['startTime'])
	dur = str('{:.1f}'.format(float(duration/60000))) + ' min /' + str(int(duration/1000)) + ' sec'
	attack_start = data_month.sort_values(by=['packetCount'], ascending=False).iloc[0]['startDate']
	attack_id = data_month.sort_values(by=['packetCount'], ascending=False).iloc[0]['attackIpsId']
	attack_maxpps = data_month.sort_values(by=['packetCount'], ascending=False).iloc[0]['maxAttackPacketRatePps']
	attack_maxbps = data_month.sort_values(by=['packetCount'], ascending=False).iloc[0]['maxAttackRateBps']


	email_body = email_body + f"#1 attack by packet count:\r\n\r\n"
	email_body = email_body + f"Threat Category: {attack_cat}\r\n"
	email_body = email_body + f"Attack Name: {attack_name}\r\n"
	email_body = email_body + f"Attack source: {src_ip}\r\n"
	email_body = email_body + f"Attack destination: {dst_ip}\r\n"
	email_body = email_body + f"Attack date(UTC): {attack_start}\r\n"
	email_body = email_body + f"Attack total packets: {attack_pkt}\r\n"
	email_body = email_body + f"Attack total data: {'{:.2f}'.format(float(attack_bw))} GB\r\n"
	email_body = email_body + f"Attack rate(PPS): {format(int(attack_maxpps), ',d')}\r\n"
	email_body = email_body + f"Attack rate(Gbps): {'{:.2f}'.format(float(attack_maxbps/1000000000))} Gbps\r\n"
	email_body = email_body + f"Attacked device: {device}\r\n"
	email_body = email_body + f"Attacked policy: {policy}\r\n"
	email_body = email_body + f"Attack duration: {dur}\r\n\r\n"


	## Top #1 Attack summary by bandwidth ####################################

	device = data_month.sort_values(by=['packetBandwidth'], ascending=False).iloc[0]['deviceName']
	policy = data_month.sort_values(by=['packetBandwidth'], ascending=False).iloc[0]['ruleName']
	attack_cat = data_month.sort_values(by=['packetBandwidth'], ascending=False).iloc[0]['category']
	attack_name = data_month.sort_values(by=['packetBandwidth'], ascending=False).iloc[0]['name']
	src_ip = data_month.sort_values(by=['packetBandwidth'], ascending=False).iloc[0]['sourceAddress']
	dst_ip = data_month.sort_values(by=['packetBandwidth'], ascending=False).iloc[0]['destAddress']
	attack_bw = ((data_month.sort_values(by=['packetBandwidth'], ascending=False).iloc[0]['packetBandwidth'])/8000000)
	attack_pkt = format((data_month.sort_values(by=['packetBandwidth'], ascending=False).iloc[0]['packetCount']), ',d')
	duration = (data_month.sort_values(by=['packetBandwidth'], ascending=False).iloc[0]['endTime'])-(data_month.sort_values(by=['packetBandwidth'], ascending=False).iloc[0]['startTime'])
	dur = str('{:.1f}'.format(float(duration/60000))) + ' min /' + str(int(duration/1000)) + ' sec'
	attack_start = data_month.sort_values(by=['packetBandwidth'], ascending=False).iloc[0]['startDate']
	attack_id = data_month.sort_values(by=['packetBandwidth'], ascending=False).iloc[0]['attackIpsId']
	attack_maxpps = data_month.sort_values(by=['packetBandwidth'], ascending=False).iloc[0]['maxAttackPacketRatePps']
	attack_maxbps = data_month.sort_values(by=['packetBandwidth'], ascending=False).iloc[0]['maxAttackRateBps']


	email_body = email_body + f"Top #1 attack by total attack traffic in GB:\r\n\r\n"
	email_body = email_body + f"Threat Category: {attack_cat}\r\n"
	email_body = email_body + f"Attack Name: {attack_name}\r\n"
	email_body = email_body + f"Attack source: {src_ip}\r\n"
	email_body = email_body + f"Attack destination: {dst_ip}\r\n"
	email_body = email_body + f"Attack date(UTC): {attack_start}\r\n"
	email_body = email_body + f"Attack total packets: {attack_pkt}\r\n"
	email_body = email_body + f"Attack total data: {'{:.2f}'.format(float(attack_bw))} GB\r\n"
	email_body = email_body + f"Attack rate(PPS): {format(int(attack_maxpps), ',d')}\r\n"
	email_body = email_body + f"Attack rate(Gbps): {'{:.2f}'.format(float(attack_maxbps/1000000000))} Gbps\r\n"
	email_body = email_body + f"Attacked device: {device}\r\n"
	email_body = email_body + f"Attacked policy: {policy}\r\n"
	email_body = email_body + f"Attack duration: {dur}\r\n\r\n"


	## Top #1 Attack summary by Max Gbps rate ####################################

	device = data_month.sort_values(by=['maxAttackRateBps'], ascending=False).iloc[0]['deviceName']
	policy = data_month.sort_values(by=['maxAttackRateBps'], ascending=False).iloc[0]['ruleName']
	attack_cat = data_month.sort_values(by=['maxAttackRateBps'], ascending=False).iloc[0]['category']
	attack_name = data_month.sort_values(by=['maxAttackRateBps'], ascending=False).iloc[0]['name']
	src_ip = data_month.sort_values(by=['maxAttackRateBps'], ascending=False).iloc[0]['sourceAddress']
	dst_ip = data_month.sort_values(by=['maxAttackRateBps'], ascending=False).iloc[0]['destAddress']
	attack_bw = ((data_month.sort_values(by=['maxAttackRateBps'], ascending=False).iloc[0]['packetBandwidth'])/8000000)
	attack_pkt = format((data_month.sort_values(by=['maxAttackRateBps'], ascending=False).iloc[0]['packetCount']), ',d')
	duration = (data_month.sort_values(by=['maxAttackRateBps'], ascending=False).iloc[0]['endTime'])-(data_month.sort_values(by=['maxAttackRateBps'], ascending=False).iloc[0]['startTime'])
	dur = str('{:.1f}'.format(float(duration/60000))) + ' min /' + str(int(duration/1000)) + ' sec'
	attack_start = data_month.sort_values(by=['maxAttackRateBps'], ascending=False).iloc[0]['startDate']
	attack_id = data_month.sort_values(by=['maxAttackRateBps'], ascending=False).iloc[0]['attackIpsId']
	attack_maxpps = data_month.sort_values(by=['maxAttackRateBps'], ascending=False).iloc[0]['maxAttackPacketRatePps']
	attack_maxbps = data_month.sort_values(by=['maxAttackRateBps'], ascending=False).iloc[0]['maxAttackRateBps']


	email_body = email_body + f"Top #1 attack by max Gbps rate:\r\n\r\n"
	email_body = email_body + f"Threat Category: {attack_cat}\r\n"
	email_body = email_body + f"Attack Name: {attack_name}\r\n"
	email_body = email_body + f"Attack source: {src_ip}\r\n"
	email_body = email_body + f"Attack destination: {dst_ip}\r\n"
	email_body = email_body + f"Attack date(UTC): {attack_start}\r\n"
	email_body = email_body + f"Attack total packets: {attack_pkt}\r\n"
	email_body = email_body + f"Attack total data: {'{:.2f}'.format(float(attack_bw))} GB\r\n"
	email_body = email_body + f"Attack rate(PPS): {format(int(attack_maxpps), ',d')}\r\n"
	email_body = email_body + f"Attack rate(Gbps): {'{:.2f}'.format(float(attack_maxbps/1000000000))} Gbps\r\n"
	email_body = email_body + f"Attacked device: {device}\r\n"
	email_body = email_body + f"Attacked policy: {policy}\r\n"
	email_body = email_body + f"Attack duration: {dur}\r\n\r\n"



	## Top #1 Attack summary by Max PPS rate rate ####################################

	device = data_month.sort_values(by=['maxAttackPacketRatePps'], ascending=False).iloc[0]['deviceName']
	policy = data_month.sort_values(by=['maxAttackPacketRatePps'], ascending=False).iloc[0]['ruleName']
	attack_cat = data_month.sort_values(by=['maxAttackPacketRatePps'], ascending=False).iloc[0]['category']
	attack_name = data_month.sort_values(by=['maxAttackPacketRatePps'], ascending=False).iloc[0]['name']
	src_ip = data_month.sort_values(by=['maxAttackPacketRatePps'], ascending=False).iloc[0]['sourceAddress']
	dst_ip = data_month.sort_values(by=['maxAttackPacketRatePps'], ascending=False).iloc[0]['destAddress']
	attack_bw = (data_month.sort_values(by=['maxAttackPacketRatePps'], ascending=False).iloc[0]['packetBandwidth'])/8000000
	attack_pkt = format((data_month.sort_values(by=['maxAttackPacketRatePps'], ascending=False).iloc[0]['packetCount']), ',d')
	duration = (data_month.sort_values(by=['maxAttackPacketRatePps'], ascending=False).iloc[0]['endTime'])-(data_month.sort_values(by=['maxAttackPacketRatePps'], ascending=False).iloc[0]['startTime'])
	dur = str('{:.1f}'.format(float(duration/60000))) + ' min /' + str(int(duration/1000)) + ' sec'
	attack_start = data_month.sort_values(by=['maxAttackPacketRatePps'], ascending=False).iloc[0]['startDate']
	attack_id = data_month.sort_values(by=['maxAttackPacketRatePps'], ascending=False).iloc[0]['attackIpsId']
	attack_maxpps = data_month.sort_values(by=['maxAttackPacketRatePps'], ascending=False).iloc[0]['maxAttackPacketRatePps']
	attack_maxbps = data_month.sort_values(by=['maxAttackPacketRatePps'], ascending=False).iloc[0]['maxAttackRateBps']


	email_body = email_body + f"Top #1 attack by max PPS rate:\r\n\r\n"
	email_body = email_body + f"Threat Category: {attack_cat}\r\n"
	email_body = email_body + f"Attack Name: {attack_name}\r\n"
	email_body = email_body + f"Attack source: {src_ip}\r\n"
	email_body = email_body + f"Attack destination: {dst_ip}\r\n"
	email_body = email_body + f"Attack date(UTC): {attack_start}\r\n"
	email_body = email_body + f"Attack total packets: {attack_pkt}\r\n"
	email_body = email_body + f"Attack total data: {'{:.2f}'.format(float(attack_bw))} GB\r\n"
	email_body = email_body + f"Attack rate(PPS): {format(int(attack_maxpps), ',d')}\r\n"
	email_body = email_body + f"Attack rate(Gbps): {'{:.2f}'.format(float(attack_maxbps/1000000000))} Gbps\r\n"
	email_body = email_body + f"Attacked device: {device}\r\n"
	email_body = email_body + f"Attacked policy: {policy}\r\n"
	email_body = email_body + f"Attack duration: {dur}\r\n\r\n"


	print(email_body)
	return email_body



def send_report(SMTP_AUTH,SMTP_SERVER,SMTP_SERVER_PORT,SMTP_SENDER,SMTP_PASSWORD,SMTP_LIST,SMTP_SUBJECT_PREFIX):

	msg = MIMEMultipart()
	
	if currentmonth != 1:
		msg["Subject"] = SMTP_SUBJECT_PREFIX + f" Monthly report  - {currentmonth}, {currentyear}"
	else:
		msg["Subject"] = SMTP_SUBJECT_PREFIX + f" Monthly report  - 12, {prevyear}"

	msg["From"] = SMTP_SENDER
	msg["To"] = ', '.join(SMTP_LIST)

	for root, dirs, files in os.walk(path_r):
		if root.split("/")[2] == cust_id:
			for filename in files:
				if int(filename.split("_")[2]) == currentmonth and int(filename.split("_")[3].split(".")[0]) == currentyear:
					if os.stat(os.path.join(root, filename)).st_size > 5000000: #if filesize > 5MB
						print(f'archiving {os.path.join(root, filename)}')
						arcfile = os.path.join(root, filename) + '.tar.gz'
						with tarfile.open(arcfile, "w:gz") as tar:
							tar.add(os.path.join(root, filename), arcname=os.path.basename(os.path.join(root, filename)))


	for root, dirs, files in os.walk(path_r):
		if root.split("/")[2] == cust_id:
			for filename in files:
				if int(filename.split("_")[2]) == currentmonth and int(filename.split("_")[3].split(".")[0]) == currentyear:
					if os.stat(os.path.join(root, filename)).st_size < 5000000:			
						print(f'sending {os.path.join(root, filename)}')
						attachment = open(os.path.join(root, filename), "rb")
						p = MIMEBase('application', 'octet-stream')
						p.set_payload((attachment).read())
						encoders.encode_base64(p)
						p.add_header('Content-Disposition', "attachment; filename= %s" % filename)
						msg.attach(p)
						attachment.close()
						
	body = "This email was automated by the Monthly Report script" + "\r\n" + email_body()
	msg.attach(MIMEText(body, 'plain'))
	mailserver = smtplib.SMTP(host=SMTP_SERVER,port=SMTP_SERVER_PORT)
	mailserver.ehlo()
	if SMTP_AUTH:
		mailserver.starttls()
		mailserver.ehlo()
		mailserver.login(SMTP_SENDER, SMTP_PASSWORD)
	mailserver.sendmail(from_addr=SMTP_SENDER,to_addrs=SMTP_LIST, msg=msg.as_string())
	mailserver.quit()

send_report(smtp_auth,smtp_server,smtp_server_port,smtp_sender,smtp_password,smtp_list,smtp_subject_prefix)
