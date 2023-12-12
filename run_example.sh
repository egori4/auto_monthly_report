#!/bin/bash

#-------------------------------------------
# PHP code by Marcelo Dantas
# Bash orchestration, dockerization, python - by Egor Egorov
#-------------------------------------------

###################### Mandatory variables #########################################################
cust_list=(Customer_name)	#space separated list of customer IDs

####################################################################################################

##################### Report Range #################################################################
report_range="-1 month" # set to "-1 month" or "-1 day"

cur_day=$(date +'%d')
#cur_day="25"

cur_month=$(date +'%m') # This sets the month to the current month by default, so the data will be collected and report will be generatd for the previous $report_range. If the data needs to be collected for the different month, set the numberic value. For example if set to 4 (April), the script will collect and generate report for March.
# cur_month=8
cur_year=$(date +%Y)
prev_year=$(expr $cur_year - 1)

if [[ "$cur_month" != 01 ]] || [ "$cur_month" != 1 ]; then
	prev_month=$(expr $cur_month - 1)

else
	prev_month=12
fi




abuseipdb_key="xxxx"
#This variable is needed to fetch the information about top 10 malicious IP addresses from abuseipdb.com.
#Register and obtain your API key from https://www.abuseipdb.com/account/api

delete_old_files_retention=6
#Number of months to keep the old files. For example if set to 6, the script will delete all files older than 6 months.

top_n=7
#Number of top N items to be displayed in the report. For example if set to 10, the script will display top 10 items in the report.


bw_units="Gigabytes"
#Can be configured "Gigabytes", "Terabytes" or "Megabytes"

pkt_units="Millions"
#Can be configured "Millions" or "Billions" or "Thousands"

####################################################################################################

#######################Action variables switch on/off(optional)####################################################
convert_forensics_to_sqlite=true
forensics_file_cust_id="USCC"
forensics_file_name="1_week_2023-11-27_15-53-20.csv"
converted_sqlite_file_name="database_CUSTID_10.sqlite"

del_old_files=true
collect_data=true
gen_python_csv_data=true #generate csv data using python scripts
generate_report=true
generate_appendix=true
analyze_trends=true
email_send=true
####################################################################################################


####################### Email set up parameters for sending email with reports######################
smtp_auth=true
smtp_server="smtp.server.com" # SMTP server name
smtp_server_port=25 # SMTP server port
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





#if directory source_files,database_files,report_files does not exist, create it
if [ ! -d "source_files" ]; then
  mkdir source_files
fi

if [ ! -d "database_files" ]; then
  mkdir database_files
fi

if [ ! -d "report_files" ]; then
  mkdir report_files
fi

#change directory to app
cd app 


################# Convert forensics to sqlite database #########################
if [ $convert_forensics_to_sqlite == "true" ]; then
	echo "Converting Forensics file to sqlite database"
	python3 script_files/forensics_to_sqlite.py $forensics_file_cust_id
fi
################# Collect data from Vision ############################

for cust_id in "${cust_list[@]}"
do

	if [ $collect_data == "true" ]; then
		if [ "$report_range" == "-1 day" ]; then
			php collectAll.php -- -upper=$cur_day.$cur_month.$cur_year -range="$report_range" -id="$cust_id"
		fi

		if [ "$report_range" == "-1 month" ]; then
			php collectAll.php -- -upper=01.$cur_month.$cur_year -range="$report_range" -id="$cust_id"
		fi
	fi
done

################# Set Proxy ##########################################################################

if [ $is_https_proxy == "true" ]; then
	echo "Setting HTTPS Proxy"	

	export https_proxy="$https_proxy"
fi

if [ $is_http_proxy == "true" ]; then
	echo "Setting HTTP Proxy"
	export http_proxy="$http_proxy"
fi	


###Loop through customer list, delete old files, generate appendixes ###################################
for cust_id in "${cust_list[@]}"
do

	####################### Delete old files #################################

	if [[ "$del_old_files" == "true" ]]; then
		echo "Deleting old files"
		python3 script_files/del_old_files.py $cust_id #Delete old files
	fi

	####################### Generate CSV Data #################################

	if [ $gen_python_csv_data == "true" ]; then

		if [ "$report_range" == "-1 day" ]; then

			if [ "$cur_day" == 1 ] || [ "$cur_day" == 01 ]; then
				python3 script_files/charts_and_tables_daily.py $cust_id $prev_month
				echo "Python  csv data generated"

			else
				python3 script_files/charts_and_tables_daily.py $cust_id $cur_month
				echo "Python  csv data generated"
			fi
		fi

		if [ "$report_range" == "-1 month" ]; then

			python3 script_files/charts_and_tables.py $cust_id $prev_month 
			echo "Python  csv data generated"
		fi
	fi

	####################### Generate Report PDF #################################

	if [ $generate_report == "true" ]; then

		if [[ "$cur_month" != 01 ]] || [ "$cur_month" != 1 ]; then
			echo "Generating report for $prev_month $cur_year"
			php reportAll.php -- -month="$prev_month" -year="$cur_year" -id="$cust_id" #Generate and compile report to pdf
		else
			echo "Generating report for $prev_month $prev_year"
			php reportAll.php -- -month="$prev_month" -year="$prev_year" -id="$cust_id" #Generate and compile report to pdf
		fi
	fi


	####################### Generate Appendix #################################

	if [[ "$cur_month" != 01 ]] || [ "$cur_month" != 1 ]; then

		if [ $generate_appendix == "true" ]; then
			echo "Generating appendix for $prev_month $cur_year"
			python3 script_files/data_parser_to_appendix.py $cust_id $prev_month $cur_year #this will generate appendix for the previouis month
		fi

	else
		if [ $generate_appendix == "true" ]; then
			echo "Generating appendix for $prev_month $prev_year"
			python3 script_files/data_parser_to_appendix.py $cust_id $prev_month $prev_year #this will generate appendix for the previouis month
		fi
	fi

	######################### Analyze Trends ######################

	if [[ "$analyze_trends" == "true" ]]; then

		if [ "$report_range" == "-1 day" ]; then

			if [ "$cur_day" == 1 ] || [ "$cur_day" == 01 ]; then		
				echo "Analyzing daily trends for $prev_month $cur_year"
				python3 script_files/analyze_trends_daily.py $cust_id $prev_month $cur_year $bw_units $pkt_units #this will generate appendix for the previouis month
			
			else # if day is not 1
				echo "Analyzing daily trends for $cur_month $cur_year"
				python3 script_files/analyze_trends_daily.py $cust_id $cur_month $cur_year $bw_units $pkt_units #this will generate appendix for the previouis month
			fi
		else # if range is 1 month

			if [[ "$cur_month" != 01 ]] || [ "$cur_month" != 1 ]; then
				echo "Analyzing trends for $prev_month $cur_year"
				python3 script_files/analyze_trends.py $cust_id $prev_month $cur_year $bw_units $pkt_units #this will generate appendix for the previouis month
			else
				echo "Analyzing trends for $prev_month $prev_year"
				python3 script_files/analyze_trends.py $cust_id $prev_month $prev_year $bw_units $pkt_units #this will generate appendix for the previouis month
			fi
		fi
	fi

done


################# Send email ##########################################################################
for cust_id in "${cust_list[@]}"
do
	smtp_subject_prefix="$cust_id" # Email Subject
	if [[ "$cur_month" != 01 ]] || [ "$cur_month" != 1 ]; then
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
