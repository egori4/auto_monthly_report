sqlite3 *.sqlite
select month from traffic group by month;

delete from traffic where month=4;
delete from attacks where month=4;

vacuum;
.quit
