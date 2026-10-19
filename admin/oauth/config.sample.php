<?php
// Copy this file to config.php ON THE SERVER ONLY (it is gitignored) and fill it in.
// Create the OAuth app at GitHub > Settings > Developer settings > OAuth Apps:
//   Homepage URL:               https://eriesistibleclowns.com
//   Authorization callback URL: https://eriesistibleclowns.com/admin/oauth/callback.php
return [
  'client_id'     => 'YOUR_GITHUB_OAUTH_CLIENT_ID',
  'client_secret' => 'YOUR_GITHUB_OAUTH_CLIENT_SECRET',
  'site_origin'   => 'https://eriesistibleclowns.com',
  'scope'         => 'repo',   // use 'public_repo' if the repo is public
];
