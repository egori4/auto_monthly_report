
Generate HTML/PDF reports using Google Charts and SQLite/CSV/Text/Python

The script can be run either from Linux, Windows WSL or Container

Prerequisites
------------------
If you plan to run the tool from the Windows, install WSL on your Windows 10 machine (optional):

https://docs.microsoft.com/en-us/windows/wsl/install
https://superuser.com/questions/1271682/is-there-a-way-of-installing-ubuntu-windows-subsystem-for-linux-on-win10-v170
https://docs.microsoft.com/en-us/windows/wsl/install-manual#downloading-distributions

To run AutoReport on Linux or WSL you need to first install php-cli, php-curl and php-sqlite3.
 
To install the required PHP packages on Windows WSL use:

sudo apt install php7.4-cli php7.4-curl php7.4-sqlite3

In addition, python and dependent libraries are required

sudo apt-get update
sudo apt install python3-pip
pip install pandas
pip install openpyxl

To run from WSL or linux, download, extract and put contents of the archive ("tools") uner "app" directory
https://mega.nz/file/lbwE3a4b#v_wu1hGNqzRjRkp5JowjPSGC_Wh6MiwEzCMPCtFiJF0


-------------------

1.1 Before running the script, setting variables is required

1. Rename "run_example.sh" to "run.sh"
2. Modify "run.sh" and set the mandatory "cust_id" variable and other optional variables (email, proxy)
3. Rename "config_files\customers_example.json" to "config_files\customers.json"
4. Modify "config_files\customers.json" and set the mandatory variables
	"id"
	"longName"
	"ip" #This is Vision IP
	"dps" #This is comma separated list of DefensePro IP's for which the data will be collected
	"defensepros" #Key = DefensePro IP, value = DefensePro name
	"user" #This is Vision login username
	"pass" #This is Vision login password
	"exclude" #These are the excluded categories from the data report
	
5. Modify optionals variables 
	"variables" #this is to set the units Mbps/Gbps, Millions/Billions etc.
	"report" #this is source file with instructions which charts/settings will be included in the report

-------------------
2.1 Run from WSL - generate report for the previous month from now and send the summary email

1. Navigate to the ./app directory

2. From the ./app directory, execute ./run.sh

-------------------
3.1 Run from WSL - generate report manually using specific variables


	"Long_customer_name" - can be set to the "Customer_name" or long customer name. for example - short USCC, long US Cellular.

1. Collect and compile the data to sqlite database.

	Set variables 
		"Customer_name"
		"year"
		"lower" - this is the month for which the data will be collected, if set 01.09.2022, the data will be collected starting or ending from this date (depending what is set in the next variable "range")
		"range" - duration. For example if range is set to "+1 month" and "lower" is set to 01.09.2022, the data will be collected starting from 01.09.2022 for the entire month of September.

	Run the command

	./collectAll.php -- -id="Customer_name" -year=2022 -lower="01.09.2022" -range="+1 month" 

2. Parse the data and create report in pdf format

	Set variables
		"Customer_name"
		"longName" - customer full name. Example- "Customer_name" can be USCC, "longName" is "US Cellular".
		"month" - report will be created for the month the variable is set to.
		"year" - report will be created for the year the variable is set to.
		"monthText" - set the variable to the month text. For example, if "month" is set to "9", set "monthText" to "September"
		"monthDays" - set the variable to the number of the days in the month (month is variable "month")
		Optional variables to change units
			-pktDivisor=1000000 -pktUnit="Million Packets" -bwDivisor=8000000 -bwUnit="GigaBytes" -decimals=2 -pktDecimals=2 -bwDecimals=2

	php -f report.php -- -file="json_files/MonthlyReport.json" -id="Customer_name" -longName="Long_customer_name" -month="9" -year="2022" -monthText="September" -monthDays=30 -db="database_files/{id}/database_{id}.sqlite" -doPDF -output="report_files/{id}/report_{id}_{month}_{year}.htm" -pktDivisor=1000000 -pktUnit="Million Packets" -bwDivisor=8000000 -bwUnit="GigaBytes" -decimals=2 -pktDecimals=2 -bwDecimals=2

3. Generate appendix file
		Set variables
			Customer_name
			Month - appendix will be generated for the month the variable is set to
			Year - appendix will be generated for the year the variable is set to

		python3 script_files/data_parser_to_appendix.py "Customer_name" "month" "year"

		Example

		python3 script_files/data_parser_to_appendix.py "Customer_name" 9 2022


4. Print report summary- trend this month, top attacks

		Set variables
			Customer_name
			Month - appendix will be generated for the month the variable is set to
			Year - appendix will be generated for the year the variable is set to
			monthtext - represents the month name.

		python3 script_files/monthly_mgmt_report.py "Customer_name" "month" "monthtext" "year"

		Example

		python3 script_files/monthly_mgmt_report.py Customer_name 9 September 2022


-------------------
4.1 Deploy as a docker container, can be run as a container on APSolute Vision

4.1.1 If vision has access to the internet (online deployment)

	1. Create a container- it will pull the image from the dockerhub

		docker create --name=radware_report --net=host -v /opt/radware/scripts/radware_report/app:/app egori4/radware_report

	2. Create a crontab task (optional)

		Below example will run container every 1st of each month at 3 am.

		echo "00 03 1 * * root docker start radware_report" > /etc/cron.d/radware_report

	3. Upload the monthly report app (copy repository contents under /opt/radware/scripts/radware_report/ )

		https://github.com/egori4/auto_monthly_report

	4. Set the variables (follow the instructions from the section #1.1)


4.1.2 If Vision does not have access to the internet (offline installation)

Instructions how to deploy(offline installation):
 
	1. Login to the Vision server via SSH using root user.
	2. Copy docker installation package “radware_report.tar.gz” to /tmp/ folder on the Vision server.
		
		Option 1 - using SCP with user root 
		
		Option 2 (if Vision has access to the internet) - download the installation package from the filepile directly to the vision:
		
			cd /tmp
			curl -o dp_bdos_monitor.tar.gz https://filepile.radware.com/files/download/xxx -k -L -v --progress-bar
	
	3. Create the scripts folder under /opt/radware/ as this location will not get erased during future upgrades.
	
			mkdir /opt/radware/scripts/
			mkdir /opt/radware/scripts/radware_report
			
				
	4. Extract the files into /opt/radware/scripts/radware_report directory.
	
			tar -zxvf dp_bdos_monitor.tar.gz -C /opt/radware/scripts/radware_report
			tar
	5. Navigate to the script directory
		
			cd /opt/radware/scripts/radware_report
	
	6. Modify config.py to the desired values (config.py file include explanations for every configurable variable)
		
			vi app/
		
			Note: 
						· When running on the Vision as a docker container, VISION_IP variable can be set to the localhost (127.0.0.1) instead of the external IP.
					
		
	7. Modify the ./install.sh file if scheduled task needs to be configured/modified
		
			vi install.sh
				
				Modify to the desired cron job frequency
		
		
	8. Run the installation
		
			./install.sh
					
					
	9. Validate the installation
	
			docker ps -a
	
			Expected output - you should see dp_bdos_monitor line with empty status

	10.  Before running the script, setting variables is required
	1. Rename "run_example.sh" to "run.sh"
	2. Modify "run.sh" and set the mandatory "cust_id" variable and other optional variables (email, proxy)
	3. Rename "config_files\customers_example.json" to "config_files\customers.json"
	4. Modify "config_files\customers.json" and set the mandatory variables
		"id"
		"longName"
		"ip" #This is Vision IP
		"dps" #This is comma separated list of DefensePro IP's for which the data will be collected
		"defensepros" #Key = DefensePro IP, value = DefensePro name
		"user" #This is Vision login username
		"pass" #This is Vision login password
		"exclude" #These are the excluded categories from the data report
		
	5. Modify optionals variables 
		"variables" #this is to set the units Mbps/Gbps, Millions/Billions etc.
		"report" #this is source file with instructions which charts/settings will be included in the report

		
	11. To run the script immediately without waiting for cron job (optional, if configured) , use the command: 
			
			docker start radware_report
			
			To confirm docker container started, run docker ps -a again
			
			STATUS column should show Up
			
	
		
	12. To confirm docker container finished running successfully
		
			docker ps -a
			
			STATUS should show “Existed (0)”
			
	
	13. To check container logs/errors/script failure in case STATUS is not (0)
			
			docker logs radware_report
	
	
	Instructions how to uninstall:
	
	. /opt/radware/scripts/radware_report/uninstall.sh



