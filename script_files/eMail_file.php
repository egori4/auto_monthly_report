#!/usr/bin/php
<?php
// Send a text file or message as eMail body
///////////////////////////////////////////////////////////////

require_once('include/defines.php');

use PHPMailer\PHPMailer\PHPMailer;
use PHPMailer\PHPMailer\Exception;
use PHPMailer\PHPMailer\SMTP;

require_once('include/PHPMailer.php');
require_once('include/Exception.php');
require_once('include/SMTP.php');

$globals               = new stdclass();
$globals->debug        = false;
require_once('include/functions.php');

if (isset($argv[1])) {
	$file = $argv[1];
} else {
	die('Usage: eMail_file.php <filename> <eMail> <Subject>' . NL);
}

//if (!file_exists($file))
//	die('File does not exist.' . NL);

if (isset($argv[2])) {
	$eMail = $argv[2];
} else {
	die('eMail not set.' . NL);
}

if (isset($argv[3])) {
	$subject = $argv[3];
} else {
	die('Subject not set.' . NL);
}

print("Sending '$file' to $eMail ..." . NL);
$mail = new PHPMailer(true);
// Server
//$mail->SMTPDebug = SMTP::DEBUG_SERVER;
$mail->isSMTP();
$mail->Host = '10.100.1.165';
$mail->Port = 25;
$mail->SMTPOptions = array(
	'ssl' => array(
		'verify_peer' => false,
		'verify_peer_name' => false,
		'allow_self_signed' => true
	)
);
// Recipients
$mail->setFrom('managed-services.report@radware.com', 'Managed Services Report');
$mail->addAddress($eMail);
// Content
$mail->isHTML(false);
$mail->Subject = $subject;
if(file_exists($file)) {
	$mail->Body = file_get_contents($file);
} else {
	$mail->Body = $file;
}
// Send
try {
	$mail->send();
	print('eMail message has been sent to ' . $eMail . '.' . NL);
} catch (exception $e) {
	print('eMail message could not be sent. Mailer Error: ' . $mail->ErrorInfo . NL);
}
