#!/bin/sh
#
# Backs up data from a specific month range onto SQL files
# Usage: backup.sh [upper [lower]]
#
# Get or compute the upper month to transfer (default current)
if [ -z "$1" ]
then
	export month=`date +%-m`
else
	export month=$1
fi
# Compute the lower month to transfer (default current-3)
if [ -z "$2" ]
then
	export m0=`expr $month - 3`
else
	export m0=$2
fi
if [ $m0 -lt 1 ]
then
	export m0=`expr 12 + $m0`
fi
# Gets the ID from current folder name
export id=`basename $PWD`
export orig=database_$id.sqlite
# Checks if there's a database on the current folder
if [ -f $orig ]
then
	echo Backing up months from $m0 to $month ...
else
	echo Database $orig not found
	exit 1
fi
# Create destination backup folder
export drv=/mnt/d
export dest=$drv/backup/$id
mkdir -p $drv/backup/$id
# Create destination backup files (overwrite)
sqlite3 $orig ".output $dest/dump.sql" ".dump"
