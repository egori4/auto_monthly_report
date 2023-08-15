#!/bin/sh

# VERSION = '5.4'

cd $(dirname "$0")

#./collectAll.php >> daily.log
#mv daily.log `date +"log_files/%Y%m%d.log"`

# if it is the 1st day of the month, then also run reportAll passing the previous month and year as parameters
#if [ `date +"%d"` = "01" ]; then
#    ./reportAll.php -- -month=`date --date="yesterday" +"%m"` -year=`date --date="yesterday" +"%Y"` >> daily.log
#    mv daily.log `date +"log_files/Report_%Y%m%d.log"`
#fi

# run weekly for NYCHHC on Mondays
if [ `date +"%u"` = "1" ]; then
	./weekly.php -- --id=NYCHHC
fi
# run weekly for IHN on Thursdays
if [ `date +"%u"` = "4" ]; then
	./weekly.php -- --id=IHN
fi
# run weekly for WOW on Fridays
if [ `date +"%u"` = "5" ]; then
	./weekly.php -- --id=WOW
fi
