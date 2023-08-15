#!/bin/sh
./script_files/weekly_broadridge.php $1 | tee /tmp/output.txt
./script_files/eMail_file.php /tmp/output.txt maurice.traynor@radware.com 'BROADRIDGE Weekly'
