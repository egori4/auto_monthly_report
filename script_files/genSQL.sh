#!/bin/sh
export id=$1
export month=$2
export sql=$3
export sqlO=$4
# set span to 0 if $5 is not set
export span=${5:-0}

export m2=`expr $month - 2`
if [ $m2 -lt 1 ]; then
	export m2=`expr $m2 + 12`
fi
if [ $m2 -lt 10 ]; then
	export m2=0$m2
fi
export m1=`expr $month - 1`
if [ $m1 -lt 1 ]; then
	export m1=`expr $m1 + 12`
fi
if [ $m1 -lt 10 ]; then
	export m1=0$m1
fi

export tmp=/tmp/tmp_$$.sqlite
export db1=/mnt/d/database_files/$id/database_${id}_${m1}.sqlite
export db=database_files/$id/database_${id}_${month}.sqlite

# delete the temporary database
rm -f $tmp

# execute the sql query for the current month database
sqlite3 $db << END
.headers on
.mode csv
attach '$tmp' as tmp;
create table tmp.data as $sql;
END

# execute the sql query for the previous month database if it exists and the span is 1
if [ $span -eq 1 ]; then
	if [ -f $db1 ]; then
		sqlite3 $db1 << END
.headers on
.mode csv
attach '$tmp' as tmp;
insert into tmp.data $sql;
END
	fi
fi

# execute the output sql query for the temporary database
sqlite3 $tmp ".headers on" ".mode csv" "$sqlO" ".quit"

# delete the temporary database
rm -f $tmp
