<?php
// Step 2: GitHub sends the editor back here. Trade the code for a token and hand it to the CMS window.
$config = require __DIR__ . '/config.php';
session_start();
$origin = rtrim($config['site_origin'], '/');
$status = 'error';
$payload = ['message' => 'Login failed. Close this window and try again.'];

$expected = $_SESSION['decap_oauth_state'] ?? '';
unset($_SESSION['decap_oauth_state']);
if (!empty($_GET['code']) && $expected !== '' && hash_equals($expected, (string)($_GET['state'] ?? ''))) {
  $ch = curl_init('https://github.com/login/oauth/access_token');
  curl_setopt_array($ch, [
    CURLOPT_POST => true,
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_HTTPHEADER => ['Accept: application/json'],
    CURLOPT_POSTFIELDS => http_build_query([
      'client_id'     => $config['client_id'],
      'client_secret' => $config['client_secret'],
      'code'          => $_GET['code'],
      'redirect_uri'  => $origin . '/admin/oauth/callback.php',
    ]),
  ]);
  $res = json_decode((string)curl_exec($ch), true);
  curl_close($ch);
  if (!empty($res['access_token'])) {
    $status = 'success';
    $payload = ['token' => $res['access_token'], 'provider' => 'github'];
  } elseif (!empty($res['error_description'])) {
    $payload = ['message' => $res['error_description']];
  }
}
$message = 'authorization:github:' . $status . ':' . json_encode($payload);
header('Content-Type: text/html; charset=utf-8');
?>
<!doctype html>
<html><body><p>Finishing login…</p>
<script>
(function () {
  var origin = <?php echo json_encode($origin); ?>;
  var message = <?php echo json_encode($message); ?>;
  function receive(e) {
    if (e.origin !== origin) return;
    window.opener.postMessage(message, origin);
    window.removeEventListener("message", receive);
    setTimeout(function () { window.close(); }, 300);
  }
  window.addEventListener("message", receive, false);
  window.opener.postMessage("authorizing:github", origin);
})();
</script>
</body></html>
