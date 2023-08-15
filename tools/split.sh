#!/bin/sh
#
# Backs up data from a specific month range onto SQL files
# Usage: backup.sh [upper [lower]]
#
# Gets the ID from current folder name
export id=`basename $PWD`
export orig=database_${id}_07.sqlite
# Checks if there's a database on the current folder
if [ -f $orig ]
then
	echo Splitting $orig ...
else
	echo Database $orig not found
	exit 1
fi

# Create destination backup folder
export drv=/mnt/d
export dest=$drv/database_files/$id
mkdir -p $drv/database_files/$id

# Remove destination parts
rm -f $dest/database_${id}_05.sqlite
rm -f $dest/database_${id}_06.sqlite
rm -f $dest/database_${id}_7.sqlite

# Save source schema
#sqlite3 $orig ".schema" | grep -v 'CREATE INDEX' > $dest/schema.sql
sqlite3 $orig ".schema" > $dest/schema.sql

# Create the destination databases
sqlite3 $dest/database_${id}_05.sqlite < $dest/schema.sql
sqlite3 $dest/database_${id}_06.sqlite < $dest/schema.sql
sqlite3 $dest/database_${id}_7.sqlite < $dest/schema.sql

# export devices
echo devices month 5.
sqlite3 $orig 'pragma cache_size=-8000' '.mode insert devices' 'select * from devices' | sqlite3 $dest/database_${id}_05.sqlite -cmd 'pragma cache_size=-8000' -cmd 'pragma journal_mode=memory'
echo devices month 6.
sqlite3 $orig 'pragma cache_size=-8000' '.mode insert devices' 'select * from devices' | sqlite3 $dest/database_${id}_06.sqlite -cmd 'pragma cache_size=-8000' -cmd 'pragma journal_mode=memory'
echo devices month 7.
sqlite3 $orig 'pragma cache_size=-8000' '.mode insert devices' 'select * from devices' | sqlite3 $dest/database_${id}_7.sqlite -cmd 'pragma cache_size=-8000' -cmd 'pragma journal_mode=memory'
# export traffic
echo traffic month 5.
sqlite3 $orig 'pragma cache_size=-8000' '.mode insert traffic' 'select * from traffic where month=5' | sqlite3 $dest/database_${id}_05.sqlite -cmd 'pragma cache_size=-8000' -cmd 'pragma journal_mode=memory'
echo traffic month 6.
sqlite3 $orig 'pragma cache_size=-8000' '.mode insert traffic' 'select * from traffic where month=6' | sqlite3 $dest/database_${id}_06.sqlite -cmd 'pragma cache_size=-8000' -cmd 'pragma journal_mode=memory'
echo traffic month 7.
sqlite3 $orig 'pragma cache_size=-8000' '.mode insert traffic' 'select * from traffic where month=7' | sqlite3 $dest/database_${id}_7.sqlite -cmd 'pragma cache_size=-8000' -cmd 'pragma journal_mode=memory'
# export attacks
echo attacks month 5.
sqlite3 $orig 'pragma cache_size=-8000' '.mode insert attacks' 'select * from attacks where month=5' | sqlite3 $dest/database_${id}_05.sqlite -cmd 'pragma synchronous=off' -cmd 'pragma cache_size=-8000' -cmd 'pragma journal_mode=memory'
echo attacks month 6.
sqlite3 $orig 'pragma cache_size=-8000' '.mode insert attacks' 'select * from attacks where month=6' | sqlite3 $dest/database_${id}_06.sqlite -cmd 'pragma synchronous=off' -cmd 'pragma cache_size=-8000' -cmd 'pragma journal_mode=memory'
echo attacks month 7.
sqlite3 $orig 'pragma cache_size=-8000' '.mode insert attacks' 'select * from attacks where month=7' | sqlite3 $dest/database_${id}_7.sqlite -cmd 'pragma synchronous=off' -cmd 'pragma cache_size=-8000' -cmd 'pragma journal_mode=memory'
# index attacks
#echo index month 5.
#sqlite3 $dest/database_${id}_05.sqlite -cmd 'pragma cache_size=-16000' -cmd 'pragma synchronous=off' -cmd 'pragma journal_mode=memory' < /mnt/c/AutoReport/Report_v5.1/tools/indexdb.sql
#echo index month 6.
#sqlite3 $dest/database_${id}_06.sqlite -cmd 'pragma cache_size=-16000' -cmd 'pragma synchronous=off' -cmd 'pragma journal_mode=memory' < /mnt/c/AutoReport/Report_v5.1/tools/indexdb.sql
#echo index month 7.
#sqlite3 $dest/database_${id}_7.sqlite -cmd 'pragma cache_size=-16000' -cmd 'pragma synchronous=off' -cmd 'pragma journal_mode=memory' < /mnt/c/AutoReport/Report_v5.1/tools/indexdb.sql
# cleanup
rm schema.sql
echo done.