<?php
// Returns the human readable difference between two timestamps
function timeDiff($time1, $time2) {
    if ($time1 == $time2) {
        return "0 seconds";
    }
    $diff = abs($time1 - $time2);
    if ($diff < 1) {
        return "less than 1 second";
    }
    $time = '';
    $time_parts = [
        'hour' => floor($diff / (60 * 60)), 
        'minute' => floor(($diff % (60 * 60)) / 60),
        'second' => $diff % 60
    ];
    $time_parts = array_filter($time_parts, function($value) {
        return $value > 0;
    });
    $time = implode(', ', array_map(function($unit, $value) {
        return "$value " . $unit . ($value > 1 ? 's' : '');
    }, array_keys($time_parts), $time_parts));
    $time = preg_replace('/(.*),(.*)$/', '$1 and$2', $time);
    return $time;
}