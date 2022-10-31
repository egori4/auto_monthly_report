Generate HTML/PDF reports using Google Charts and SQLite/CSV/Text/Python

The script can be run either from Linux, Windows WSL or Container

Prerequisites
------------------
If you plan to run the tool from windows, install WSL on your Windows 10 machine (optional):

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

-------------------

Before running the script, setting variables is required

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
Run from WSL - generate report for the previous month from now and send the summary email

1. comment line "cd app" in "run.sh" file
2. navigate to the app directory
3. run ./run.sh

-------------------
Run from WSL - generate report manually using specific variables



-------------------
Deploy as a docker container, possible on APSolute Vision