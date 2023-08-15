# AutoReport by Marcelo Dantas
# version = "5.4"

Set-Location $PSScriptRoot

$day = get-date -format "dd"
$month = get-date -format "MM"
$year = get-date -format "yyyy"

wsl ./script_files/eMail_file.php "Data Collection Started" marcelod@radware.com "Data Collection Started"

$ErrorActionPreference = "SilentlyContinue"
Stop-Transcript | out-null
$ErrorActionPreference = "Continue"
Start-Transcript -path log_files\AutoReport_${year}${month}${day}.log -append

write-host "---------------------------------"
write-host "Running full collection" -foreground "yellow"
write-host "---------------------------------"

wsl ./CollectAll.php

Stop-Transcript

wsl ./script_files/eMail_file.php ./log_files/AutoReport_${year}${month}${day}.log marcelod@radware.com "Daily data collection log"
wsl ./script_files/eMail_file.php ./log_files/AutoReport_${year}${month}${day}.log mauricet@radware.com "Daily data collection log"
wsl ./script_files/eMail_file.php ./log_files/AutoReport_${year}${month}${day}.log andreasb@radware.com "Daily data collection log"

wsl ./daily.sh
