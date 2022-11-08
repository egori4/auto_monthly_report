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
is_http_proxy=false
is_https_proxy=false

is_proxy_for_email=false

http_proxy="proxyserver.com:3128"
https_proxy="proxyserver.com:3128"
####################################################################################################

#######################Action variables switch on/off(optional)####################################################
collect_data=true
generate_report=true
db_del_old_data=true #Delete old data from SQL DB
del_old_files=true
generate_appendix=true
email_send=true
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
if [ $collect_data == "true" ]; then
	php collectAll.php -- -upper=01.$cur_month.$cur_year -range='-1 month'
fi
######################################################################################################



################# Set Proxy ##########################################################################

if [ $is_https_proxy == "true" ]; then
	echo "Setting HTTPS Proxy"
	export https_proxy="$https_proxy"
fi

if [ $is_http_proxy == "true" ]; then
	echo "Setting HTTP Proxy"
	export http_proxy="$http_proxy"
fi	

########################################################################################################



################# Generate report for all customers ####################################################
# if generate_report is true
if [ $generate_report == "true" ]; then
	echo "Generating report"
	php reportAll.php -- -month="$prev_month" -year="$cur_year" #Generate and compile report to pdf
fi
########################################################################################################



###Loop through customer list, delete old files, generate appendixes ###################################
for cust_id in "${cust_list[@]}"
do
	smtp_subject_prefix="$cust_id" # Email Subject
	if [[ "$del_old_files" == "true" ]]; then
		echo "Deleting old files"
		python3 script_files/del_old_files.py $cust_id #Delete old files
	fi

	if [[ "$cur_month" != 1 ]]; then
		if [ $db_del_old_data == "true" ]; then
			echo "Deleting old data from DB"
			python3 script_files/del_old_months.py $cust_id $prev_month $cur_year #this will delete collected data older than last 6 months
		fi

		if [ $generate_appendix == "true" ]; then
			echo "Generating appendix"
			python3 script_files/data_parser_to_appendix.py $cust_id $prev_month $cur_year #this will generate appendix for the previouis month
		fi

	else
		if [ $db_del_old_data == "true" ]; then
			echo "Deleting old data from DB"
			python3 script_files/del_old_months.py $cust_id $prev_month $prev_year #this will delete collected data older than last 6 months
		fi
		if [ $generate_appendix == "true" ]; then
			echo "Generating appendix"
			python3 script_files/data_parser_to_appendix.py $cust_id $prev_month $prev_year #this will generate appendix for the previouis month
		fi
	fi
done
########################################################################################################

################# Send email ##########################################################################
for cust_id in "${cust_list[@]}"
do
	if [[ "$cur_month" != 1 ]]; then
		# Case for current month except January
		if [ $is_proxy_for_email == "true" ]; then
			# if variable is_proxy_for_email is set to true, then proxy will be set for email sending
			if [ $email_send == "true" ]; then
				echo "Sending email using proxy"
				python3 script_files/email_send.py $cust_id $prev_month $cur_year $smtp_auth $smtp_server $smtp_server_port $smtp_sender $smtp_password $smtp_subject_prefix ${smtp_list[@]}
			fi
		else

			unset https_proxy
			unset http_proxy
			if [ $email_send == "true" ]; then
				echo "Sending email without proxy"
				python3 script_files/email_send.py $cust_id $prev_month $cur_year $smtp_auth $smtp_server $smtp_server_port $smtp_sender $smtp_password $smtp_subject_prefix ${smtp_list[@]}
			fi
		fi

	else
		# Case for current month January

		if [ $is_proxy_for_email == "true" ]; then
			# if variable is_proxy_for_email is set to true, then proxy will be set for email sending
			if [ $email_send == "true" ]; then
				echo "Sending email using proxy"
				python3 script_files/email_send.py $cust_id $prev_month $prev_year $smtp_auth $smtp_server $smtp_server_port $smtp_sender $smtp_password $smtp_subject_prefix ${smtp_list[@]}
			fi
		else
			unset https_proxy
			unset http_proxy
			if [ $email_send == "true" ]; then
				echo "Sending email without proxy"
				python3 script_files/email_send.py $cust_id $prev_month $prev_year $smtp_auth $smtp_server $smtp_server_port $smtp_sender $smtp_password $smtp_subject_prefix ${smtp_list[@]}
			fi
		fi	
	fi
done

#######################################################################################################