# AutoReport by Marcelo Dantas
$version = "5.0.1"

cd $PSScriptRoot

$day = get-date -format "dd"
$month = get-date -format "MM"
$year = get-date -format "yyyy"

$ErrorActionPreference="SilentlyContinue"
Stop-Transcript | out-null
$ErrorActionPreference="Continue"
Start-Transcript -path log_files\AutoReport_${year}${month}${day}.log -append

write-host "---------------------------------"
write-host "Running full generation" -foreground "yellow"
write-host "---------------------------------"

wsl ./CollectAll.php -- -range='-1 day'

Stop-Transcript
