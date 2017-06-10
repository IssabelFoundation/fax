#!/usr/bin/php
<?php
$cmdLine = "";
for($i=1; $i<$_SERVER['argc']; $i++)
	$cmdLine .= "\"{$_SERVER['argv'][$i]}\" ";

if(file_exists("bin/faxrcvd-avantfax.php"))
	echo `bin/faxrcvd-avantfax.php $cmdLine`;

if(file_exists("bin/faxrcvd-issabel.php"))
	echo `bin/faxrcvd-issabel.php  $cmdLine`;
?>
