#!/usr/bin/php
<?php
$id = $argv[1];
$month = $argv[2];
$db = $argv[3];

$m2 = $month - 2;
if ($m2 < 1) {
    $m2 = $m2 + 12;
}
if ($m2 < 10) {
    $m2 = '0' . $m2;
}
$m1 = $month - 1;
if ($m1 < 1) {
    $m1 = $m1 + 12;
}
if ($m1 < 10) {
    $m1 = '0' . $m1;
}

$db2 = 'database_previous/' . $id . '/database_' . $id . '_' . $m2 . '.sqlite';
$db1 = 'database_previous/' . $id . '/database_' . $id . '_' . $m1 . '.sqlite';

// if neither of the previous months' databases exist
// list the events for the current month
if (!file_exists($db2) && !file_exists($db1)) {
    $db3 = new SQLite3($db);
    $results = $db3->query('select printf(\'month_%02d\', month) as \'Month\',count(1) as \'Total Events\' from attacks;');
    echo('Month,Total Events' . PHP_EOL);
    while ($row = $results->fetchArray()) {
        echo $row['Month'] . ',' . $row['Total Events'] . PHP_EOL;
    }
    exit;
}

// if db2 doesn't exist
// list the events for the current month and db1
if (!file_exists($db2)) {
    $db3 = new SQLite3($db);
    $db3->exec('attach \'' . $db1 . '\' as d1;');
    $results = $db3->query('select year,printf(\'month_%02d\', month) as \'Month\',count(1) as \'Total Events\' from d1.attacks union select year,printf(\'month_%02d\', month) as \'Month\',count(1) as \'Total Events\' from attacks;');
    echo('Month,Total Events' . PHP_EOL);
    while ($row = $results->fetchArray()) {
        echo $row['Month'] . ',' . $row['Total Events'] . PHP_EOL;
    }
    exit;
}

// list the events for the current month, db1 and db2
$db3 = new SQLite3($db);
$db3->exec('attach \'' . $db2 . '\' as d2;');
$db3->exec('attach \'' . $db1 . '\' as d1;');
$results = $db3->query('select year,printf(\'month_%02d\', month) as \'Month\',count(1) as \'Total Events\' from d2.attacks union select year,printf(\'month_%02d\', month) as \'Month\',count(1) as \'Total Events\' from d1.attacks union select year,printf(\'month_%02d\', month) as \'Month\',count(1) as \'Total Events\' from attacks;');
echo('Month,Total Events' . PHP_EOL);
while ($row = $results->fetchArray()) {
    echo $row['Month'] . ',' . $row['Total Events'] . PHP_EOL;
}

?>