<?php
// Step 1 of the Decap CMS GitHub login: send the editor to GitHub to approve access.
$config = require __DIR__ . '/config.php';
session_start();
$state = bin2hex(random_bytes(16));
$_SESSION['decap_oauth_state'] = $state;
$redirect = rtrim($config['site_origin'], '/') . '/admin/oauth/callback.php';
header('Location: https://github.com/login/oauth/authorize?' . http_build_query([
  'client_id'    => $config['client_id'],
  'redirect_uri' => $redirect,
  'scope'        => $config['scope'],
  'state'        => $state,
]));
exit;
