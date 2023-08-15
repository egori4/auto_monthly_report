# AutoReport by Marcelo Dantas
# version = "5.4"

Set-Location $PSScriptRoot

$day = get-date -format "dd"
$month = get-date -format "MM"
$year = get-date -format "yyyy"

$ErrorActionPreference = "SilentlyContinue"
Stop-Transcript | out-null
$ErrorActionPreference = "Continue"
Start-Transcript -path log_files\Weekly_${year}${month}${day}.log -append

write-host "---------------------------------"
write-host "BROADRIDGE Weekly" -foreground "yellow"
write-host "---------------------------------"

wsl ./script_files/weekly_broadridge.sh

Stop-Transcript
