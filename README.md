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

1. Navigate to the ./app directory

2. From the ./app directory, execute ./run.sh

-------------------
Run from WSL - generate report manually using specific variables


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
Deploy as a docker container, can be run as a container on APSolute Vision

