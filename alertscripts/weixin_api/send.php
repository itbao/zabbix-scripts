<?php
require "config.php";
require "include/WeiXin.php";

$weiXin = new WeiXin($G_CONFIG['weiXin']);

$testFakeId = "$argv[1]";
$msg = "$argv[3]";
 print_r($weiXin->send($testFakeId, "$msg"));
