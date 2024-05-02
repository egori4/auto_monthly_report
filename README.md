
Generate HTML/PDF reports using Google Charts and SQLite/CSV/Text/Python

Version control

V7.0 8/24/2023
	- Created new git version
	- Added auto trends_analysis html
	- Fixed recursive directory removal in del_old_files.py

The script can be run either from Linux, WSL for Windows or Container

V7.0.1 8/28/2023
	- Trends analysis html - added 3 new charts - events, packets and bw per device trends

V7.0.2 8/29/2023
	- Trends analysis html
		- added 6 tables for  events, packets and bw trends and  events, packets and bw per device trends
		- added isStacked parameter for the area charts

V7.0.3 8/31/2023	
	- Trends analysis html
		- added 3 charts and 3 tables for top source IP's

V7.0.4 9/5/2023	
	- Trends analysis html
		- added 3 charts and 3 tables for top policies
	- Fixed "Malicious bandwidth by Policy Name trend" units in pdf report
	- Fixed "Traffic in Megabits" units in pdf
	- Fixed "Malicious bandwidth by Device trend" units in pdf report

V7.0.5 9/7/2023
	- Skipped sending report html and report txt files in the email

V7.0.6 9/20/2023
	- analyze_trends.py
		- added calculation of % in trends
	- abuseipdb.py
		- Updated healthcheck to https://api.abuseipdb.com/api/v2/check

v7.0.7 10/11/2023
	- Fixed tables names, phrasing, grammar errors

V7.0.8 10/12/2023
	- Disabled zipping pdf in report.php

V7.0.9 10/24/2023
	- analyze_trends.py - added pkt_units "Thousands"

V7.1 11/7/2023
	- analyze_trends.py - added Title
	- fixed pkt_units to be one variable
	- added three charts - TopN all time high

V7.2 (11/16/2023)
	- Fix Top Source IP by packet count division by packets and making Abuse score 0
	- Added new feature- added additional tables of drilldown the charts further

V7.2.1 (11/17/2023)
	- Moved pkt_units and bw_units variables from analyzed_trends.py to run.sh
	- updated run.sh
		!!! Must update run.sh from run.sh example
 
V7.3 (11/20/2023)
	- New feature- added new chart - Traffic utilization last month
	  !!!!!! Must update run.sh from run.sh example

V7.3.1 (11/21/2023)
	- New features
		- Added new chart and table - Events per day last month
		- Added new chart and table - Malicious bandwidth per day, last month
		- Added new chart and table - Malicious packets per day, last month 

	- Modified Traffic utilization last month - added hour and minute to the scale
	- Added month and year to the Headline

V8.0 (12/4/2023)
	- New feature - creating sqlite db file from forensics
		!!! Requires updating run.sh

	- email_send.py
		- Added EA case

	- analyze_trends.py
		- Added case when previous month data is not available not to calculate it

	- charts_and_tables.py
		- Added case to skip traffic stats if unavailable (if sqlite was created from forensics)
		
	- CollectAll.php - Added creation of directories source_files and database_files if does not exist

V9.0 (12/12/2023)

	- New feature - daily collection and reporting
		Script can collect and append data for every day into the monthly db
		!!! Requires updating run.sh from run_example.sh
	- analyze_trends_daily.py and analyze_trends.py
		Added exporting the data to csv
	- email_send.py
		Enhancment - added case not to archive the file if was already archived (case if the large file was already archived)

V9.1 (12/13/2023)
	- email_send.py
		Fixed case if set to run daily, to send files from the current month, not the previous month

V9.2 (12/29/2023)
	- /script_files/abuseipdb.py
		Disabled InsecureRequestWarning
	- /script_files/analyze_trends.py
		Cosmetics - added tables alignment to the top of the cell
	- /script_files/analyze_trends_daily.py
		fixed path to run file from run.sh to run_daily.sh
	- /script_files/email_send.py
		removed -1 day range section
	- /script_files/email_send_daily.py
		added new file
	- script_files/delete_column_csv.py
		new feature to delete specific data from csv
		
V9.2.1 (1/17/2024)
	- run_daily_example.sh
		fixed bug sending daily email for January
	- script_files/analyze_trends.py and script_files/analyze_trends_daily.py
		fixed top source IP by packets flat chart
	- /script_files/charts_and_tables_daily.py
		fixed calculating "Total" column for events column to include the first collected day column (bug)
	- script_files/delete_column_csv.py
		added removing prevailing topmost attack which skews the stats also from filename == 'events_per_day_chart_alltimehigh.csv'

V9.2.2 (1/25/2024)
	- run_daily_example.sh and run_example.sh
		bugfixes
	- abuseipdb.py
		added printing error in event of communcation error with abuseipdb
	- analyze_trends_daily.py
		realigned charts to the whole page width insted of inside the cells
		Cosmetics - renamed column names
9.2.3 (1/26/2024)
	- analyze_trends_daily.py
		cosmetics - phrasing, naming enhancments

9.3 (1/26/2024) 
	- analyze_trends.py , charts_and_tables.py, analyze_trends_daily.py , charts_and_tables_daily.py , run_daily_example.sh, run_example.sh

		Changed units per customer. Configurable under "./config_files/customers.json"
		
		bwUnit="Gigabytes"
		#Can be configured "Gigabytes", "Terabytes" or "Megabytes

		pktUnit="Millions"
		#Can be configured "Millions", "Billions", "Thousands" or "As is"
		!!! Must update run.sh, run_example.sh, ./config_files/customers.json
9.3.1 (1/29/2024)

	- analyze_trends_daily.py, charts_and_tables_daily.py, ./config_files/customers.json
		Introduced new ./config_files/customers.json variables "bwUnitDaily" and "pktUnitDaily"
	
	!!! Must add and set "bwUnitDaily" and "pktUnitDaily" to ./config_files/customers.json
		"bwUnitDaily" #Can be configured "Gigabytes", "Terabytes" or "Megabytes
		"pktUnitDaily" #Can be configured "Millions", "Billions", "Thousands" or "As is"

9.3.2 (2/12/24)
	- charts_and_tables.py and charts_and_tables_daily.py
		bugfix(enhancment) - if /report_files/<cust_id> does not exist, precreate it so the script won't fail
	- analyze_trends.py for monthly reports
		Cosmetics improvements
			changed 'Count' to "Security Events'
			changed 'deviceName' to 'Device Name'
			changed 'ruleName' to 'Policy Name'
			changed 'name' to 'Attack Name'
			changed sourceAddress to 'Source IP'
			changed 'startDayOfMonth' to 'Day of the Month'
			added units {pkt_units} and units {bw_units}

9.3.3 (2/12/24 commit name "Feb 12 - Added monthly and daily" by Jesus)
	- analyze_trends_daily.py and analyze_trends.py
		modification of the trends_CUSTOMER_MONTH_YEAR.html to trends-daily_CUSTOMER_MONTH_YEAR.html and trends-monthly_CUSTOMER_MONTH_YEAR.html

9.3.4 (2/27/24)
	- analyze_trends_daily.py asnd analyze_trends.py
		Added corner case not to convert strings to numbers for the csv headlines for all csv files
		This is when policy name is a number, do not convert the policy name to be the integer otherwise it breaks the JS

9.3.5 (4/4/24)
	- analyze_trends_daily.py asnd analyze_trends.py
		Added exporting durationRange as 'Duration Range' to csv database
===========================================================================================================================
Instructions how to deploy as a docker container (on Vision example):
 
1. Login to the Vision server via SSH using root user.
2. Copy docker installation package “radware_report.tar.gz” to /tmp/ folder on the Vision server.
	 
	Option 1 - using SCP with user root 
	 
	Option 2 (if Vision has access to the internet) - download the installation package from the filepile directly to the vision:
	 
		cd /tmp
		curl -o radware_report.tar.gz https://filepile.radware.com/files/download/f98-137-a0b -k -L -v --progress-bar
 
3. Create the scripts folder under /opt/radware/storage as this location will not get erased during future upgrades.
 
		mkdir /opt/radware/storage/scripts/
		mkdir /opt/radware/storage/scripts/radware_report
		
			 
4. Extract the files into /opt/radware/storage/scripts/radware_report directory.
 
		tar -zxvf  radware_report.tar.gz -C /opt/radware/storage/scripts/radware_report
		
5. Navigate to the script directory
	 
		cd /opt/radware/storage/scripts/radware_report
 
				
	 
6. Modify the ./install.sh file if scheduled task needs to be configured/modified
	 
		vi install.sh
	        
	        Modify to the desired cron job frequency
	 
	 
7. Run the installation
	 
		./install.sh
                  
                  
8. Validate the installation
 
		docker ps -a
 
		Expected output - you should see radware_report line with empty status


9. Update to the latest version of the code

################### Update to the latest version of the code##################################

	To get the latest code replace"/opt/radware/storage/scripts/radware_report/app" folder by the content from the git below

	Latest app (Marcelo+Egor) https://github.com/egori4/auto_monthly_report
	
	*** Note - if updating from git, 
	
		1. make run.sh  executable
	
			chmod +x run.sh
		
		2. Set variables
			/config_files/config.json
			
		
		3. Rename (remove example)
			text_files/frontpage_en.txt 
			
			Modify contents of the front page as needed
				text_files/frontpage_en.txt 
		
	
			Rename MonthlyReport_example_python.json to  json_files/MonthlyReport.json
			
			
			
		4. Register to abuseipdb and set the api key under scripts/abuseipdb.py (optional if you want to get extra data about malicious IP and malicious score)
			
###########################################################################



10.  Before running the script, setting variables is required
1. Rename "app\run_example.sh" to "run.sh"
2. Modify "app\run.sh" 
3. and set the mandatory "cust_id" variable and other optional variables (email, abuseip proxy)

Note!!! Do not use"_" (underscore) in cust_id name

3. Rename "app\config_files\customers_example.json" to "config_files\customers.json"
4. Modify "app\config_files\customers.json" and set the mandatory variables
    "id"  -this id should match the "cust_id" that was set earlier
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

	 
3. To run the script immediately without waiting for cron job (optional, if configured) , use the command: 
		 
		docker start radware_report
		docker start -i radware_report
		 
		To confirm docker container started, run docker ps -a again
		If you upload from APP GitHub allow permissions to ./run.sh
		
		chmod +x run.sh 
		 
		STATUS column should show Up
		 
 
	 
4. To confirm docker container finished running successfully
	 
		docker ps -a
		 
		STATUS should show “Existed (0)”
		 
 
5. To check container logs/errors/script failure in case STATUS is not (0)
		 
		docker logs radware_report
 


==============================================================================
 
Instructions how to uninstall:
 
		. /opt/radware/storage/scripts/radware_report/uninstall.sh
		
6. Remove the /opt/radware/storage/scripts/radware_report directory and its contents

	 rm -rf /opt/radware/storage/scripts/radware_report
	
	rm -rf /opt/radware/scripts/radware_report
Notes:

For all the previous months trends, instead of geneating for all the previous months, you can copy the existing database to have (if you have it for previous months in other place) and put it under ./database_files/<CUST_ID>.sqlite - next run it will embed the last month into it.


==============================================================================

################### How to update to the latest version of the code ##################################

	To get the latest code replace"/opt/radware/storage/scripts/radware_report/app" folder by the content from the git below

	Latest app (Marcelo+Egor) https://github.com/egori4/auto_monthly_report
	
	*** Note - if updating from git, 
	
		1. make run.sh  executable
	
			chmod +x run.sh
		
		2. Set variables
			/config_files/config.json
			
		
		3. Rename (remove example)
			text_files/frontpage_en.txt 
			
			Modify contents of the front page as needed
				text_files/frontpage_en.txt 
		
	
			Rename MonthlyReport_example_python.json to  json_files/MonthlyReport.json
			
			
			
		4. Register to abuseipdb and set the api key under scripts/abuseipdb.py (optional if you want to get extra data about malicious IP and malicious score)
			
###########################################################################


!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

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



To Run from WSL

1. Navigate to the ./app directory

2. From the ./app directory, execute ./run.sh

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


Instructions how to convert forensics file

1. Put forensics file under /database_files/<customer>/ directory
1. Set the variable in run.sh file

convert_forensics_to_sqlite=true
forensics_file_cust_id="USCC"
forensics_file_name="1_week_2023-11-27_15-53-20.csv"
converted_sqlite_file_name="database_CUSTID_10.sqlite"

Run run.sh

This will take forensics file (example 1_week_2023-11-27_15-53-20.csv) and convert to database_CUSTID_10.sqlite