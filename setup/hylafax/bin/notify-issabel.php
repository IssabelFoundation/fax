#!/usr/bin/php
<?php
$args = $argv;
$args[0] = '--send';
pcntl_exec('bin/issabel-faxevent', $args, $_ENV);
?>