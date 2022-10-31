..\..\tools\php\php -f ..\..\report.php -- --file="report.json" --monthText=July --monthDays=31 --month=07 --year=2021 --longName="Test Customer"
if($?) {
	..\..\tools\chrome\chrome --headless --incognito --enable-logging --print-to-pdf="C:\home\mockba\Report_v5.0\report_files\TEST\output.pdf" file://C:\home\mockba\Report_v5.0\report_files\TEST\report.htm
} else {
	write-host "Report not generated."
	write-host ""
}