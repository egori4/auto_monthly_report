#!/bin/bash

###################### Mandatory variables #########################################################
cust_list=(Customer_Name)	#space separated list of customer IDs
####################################################################################################



####################### Email set up parameters for sending email with reports######################
smtp_auth=true
smtp_server="smtp.server.com" # SMTP server name
smtp_server_port=587 # SMTP server port
smtp_sender="sender_email@email.com" # Email sender address setting
smtp_password="smtp_password"  #Email password (optional)
smtp_list=(user1@mail.com user2@mail.com) #space separated list of email addresses		
####################################################################################################



#######################Proxy variables##############################################################
proxy=false
proxy_for_email=false
####################################################################################################


cur_month=$(date +'%m')
cur_year=$(date +%Y)
prev_year=$(expr $cur_year - 1)

if [[ "$cur_month" != 1 ]]; then
	prev_month=$(expr $cur_month - 1)

else
	prev_month=12
fi

cd app

################# Data collection. Perioud - pervious month from today's date ########################
php collectAll.php -- -upper=01.$cur_month.$cur_year -range='-1 month'
######################################################################################################



################# Set Proxy ##########################################################################
if [ $proxy == "true" ]; then	#set proxy if needed

		echo "Setting Proxy"

		https_proxy="proxyserver.com:3128"
		export https_proxy="$https_proxy"

		http_proxy="proxyserver.com:3128"
		export http_proxy="$http_proxy"

fi
########################################################################################################



################# Generate report for all customers ####################################################
php reportAll.php -- -month="$prev_month" -year="$cur_year" #Generate and compile report to pdf
########################################################################################################



###Loop through customer list, delete old data, generate appendixes and send an email###################
for cust_id in "${cust_list[@]}"
do
	smtp_subject_prefix="$cust_id" # Email Subject
	#python3 script_files/del_old_files.py $cust_id #Delete old files

	if [[ "$cur_month" != 1 ]]; then
		echo "Current month is not January"

		python3 script_files/del_old_months.py $cust_id $prev_month $cur_year #this will delete collected data older than last 6 months
		python3 script_files/data_parser_to_appendix.py $cust_id $prev_month $cur_year #this will generate appendix for the previouis month
		

		# if variable proxy_for_email is set to true, then proxy will be set for email sending
		
		if [ $proxy_for_email == "true" ]; then
			echo "Sending email using proxy"
			python3 script_files/email_send.py $cust_id $prev_month $cur_year $smtp_auth $smtp_server $smtp_server_port $smtp_sender $smtp_password $smtp_subject_prefix ${smtp_list[@]}
		else
			echo "Sending email without proxy"

			unset https_proxy
			unset http_proxy

			python3 script_files/email_send.py $cust_id $prev_month $cur_year $smtp_auth $smtp_server $smtp_server_port $smtp_sender $smtp_password $smtp_subject_prefix ${smtp_list[@]}
		fi

	else
		echo "Current month is January"

		python3 script_files/del_old_months.py $cust_id $prev_month $prev_year $retention #this will delete collected data older than last 6 months
		python3 script_files/data_parser_to_appendix.py $cust_id $prev_month $prev_year #this will generate appendix for the previouis month
		
		if [ $proxy_for_email == "true" ]; then
			echo "Sending email using proxy"
			python3 script_files/email_send.py $cust_id $prev_month $prev_year $smtp_auth $smtp_server $smtp_server_port $smtp_sender $smtp_password $smtp_subject_prefix ${smtp_list[@]}
		else
			echo "Sending email without proxy"
			unset https_proxy
			unset http_proxy
			python3 script_files/email_send.py $cust_id $prev_month $prev_year $smtp_auth $smtp_server $smtp_server_port $smtp_sender $smtp_password $smtp_subject_prefix ${smtp_list[@]}
		fi
		
	fi
	#######################################################################################################

done
