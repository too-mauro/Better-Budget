<html><head><title>Service Verification</title></head>
<body>
<?php
//echo("php block start <br>");
$curl = curl_init();
//echo("curl init<br>");
curl_setopt_array($curl, array(
  CURLOPT_URL => "http://localhost/api/v0/test2",
  CURLOPT_RETURNTRANSFER => true,
  CURLOPT_ENCODING => "",
  CURLOPT_MAXREDIRS => 10,
  CURLOPT_TIMEOUT => 0,
  CURLOPT_FOLLOWLOCATION => true,
  CURLOPT_HTTP_VERSION => CURL_HTTP_VERSION_1_1,
  CURLOPT_CUSTOMREQUEST => "GET"
));
//echo("Curl Opts Set<br>");
$response = curl_exec($curl);
//echo("response got<br>");
//echo(var_dump( curl_error($curl) )) ;
curl_close($curl);
//echo("CURL called & closed<br>");
//echo($response);
$json_response = json_decode($response,true);
echo("<table width='50%' border=1><tr><td><b>ID</b></td><td><b>Text</b></td><td><b>Timestamp</b></td></tr>");
foreach($json_response as $item){
	echo("<tr><td>".$item["identity-key"]."</td><td>".$item["text-field"]."</td><td>".$item["insert-dttm"]."</td></tr>");
}
echo("</table>");
?>
</body></html>