
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