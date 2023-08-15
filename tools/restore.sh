#!/bin/sh
#
# Restores a database from SQL backup folder
# Usage: restore.sh <source folder>
#
# Gets the ID from current folder name
export id=`basename $PWD`
export dest=database_$id.sqlite
echo Rebuilding $dest ...
# Checks if there's a database on the current folder
if [ -f $dest ]
then
	echo Database $dest already exists
	exit 1
else
	echo Database $dest is being restored
fi
# Restores data
sqlite3 $dest < $1/dump.sql
