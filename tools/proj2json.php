#!/usr/bin/php
<?php
// open the project text file from argv[1]
$projFile = fopen($argv[1], "r");
// print error message if file cannot be opened and exit
if (!$projFile) {
    echo "Error opening file: " . $argv[1] . "\n";
    exit(1);
}
// create the json output file from argv[2]
$jsonFile = fopen($argv[2], "w");
// print error message if file cannot be created and exit
if (!$jsonFile) {
    echo "Error creating file: " . $argv[2] . "\n";
    exit(1);
}

// Set the default values to the json object
$proj = array(
    "offline" => false,
    "language" => "en",
    "title" => "Project Title",
    "pages" => array()
);

// initialize the chart counter
$count = 0;
// read the project text file line by line
while (!feof($projFile)) {
    // read a line from the file
    $line = trim(fgets($projFile));
    // skip lines which don't start with a '<sql'
    if (substr($line, 0, 5) != "<sql ") {
        continue;
    }
    // extract the name of the project from the line as xml
    $xml = simplexml_load_string($line);
    // print error message if xml cannot be parsed and exit
    if (!$xml) {
        echo "Error parsing xml: " . $line . "\n";
        exit(1);
    }
    // extract the project name from the xml
    $name = $xml->attributes()->name[0];
    // set chart defaults
    $type = "column";
    $legend = "bottom";
    $slantedText = true;
    $top = 0;
    $left = 0;
    $width = 1100;
    $height = 680;
    $db = "{db}";

    // id name contains ':' then split the name into name and type
    if (strpos($name, ":") !== false) {
        $name = explode(":", $name);
        $type = $name[1];
        $name = $name[0];
    }
    // extract the sql query from the xml
    $xml = (array)$xml;
    $sql = $xml[0];
    // normalize the query name
    $name = (array)$name;
    $name = $name[0];
    // print name and sql to the console
    print "$name\n";
    // add the name and sql to the json object pages array
    $object = (object)array(
            "object" => "chart",
            "style" => new stdClass(),
            "title" => $name,
            "type" => $type,
            "legend" => $legend,
            "slantedText" => $slantedText,
            "db" => $db,
            "src" => "sql",
            "sql" => $sql
    );
    $object->style->top = $top;
    $object->style->left = $left;
    $object->style->width = $width;
    $object->style->height = $height;
    $proj["pages"][] = array(
        "title" => "Chart" . ++$count,
        "objects" => array(
            $object
          )
    );
}
// save the $json object to the json file
fwrite($jsonFile, json_encode($proj, JSON_PRETTY_PRINT));
// close the project text file
fclose($projFile);
// close the json output file
fclose($jsonFile);
?>
