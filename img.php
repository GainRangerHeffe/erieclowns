<?php
// Turns a photo *page* link (Imgur gallery/album, ImgBB, Google Photos) into the actual picture.
// The events page calls img.php?url=<link>; this looks up the page's share image (og:image)
// once, remembers it, and redirects the browser to the picture. Only the hosts below are allowed.

$PAGE_HOSTS  = ['imgur.com', 'www.imgur.com', 'm.imgur.com', 'ibb.co', 'photos.app.goo.gl', 'photos.google.com'];
$IMAGE_HOSTS = ['i.imgur.com', 'i.ibb.co', 'lh3.googleusercontent.com', 'lh4.googleusercontent.com', 'lh5.googleusercontent.com', 'lh6.googleusercontent.com'];
$CACHE_DIR   = __DIR__ . '/cache';

// A 404 makes the events page hide the photo slot.
function fail() { header('Cache-Control: public, max-age=300'); http_response_code(404); exit; }
function host_ok($url, $hosts) {
  $p = parse_url($url);
  return $p && ($p['scheme'] ?? '') === 'https' && in_array(strtolower($p['host'] ?? ''), $hosts, true);
}

$url = trim((string)($_GET['url'] ?? ''));
if (!host_ok($url, $PAGE_HOSTS)) fail();

$key = $CACHE_DIR . '/' . sha1($url) . '.txt';
$img = is_file($key) && filemtime($key) > time() - 30 * 86400 ? trim((string)file_get_contents($key)) : '';

if ($img === '') {
  $ch = curl_init($url);
  curl_setopt_array($ch, [
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_FOLLOWLOCATION => true,
    CURLOPT_MAXREDIRS => 3,
    CURLOPT_PROTOCOLS => CURLPROTO_HTTPS,
    CURLOPT_REDIR_PROTOCOLS => CURLPROTO_HTTPS,
    CURLOPT_TIMEOUT => 8,
    CURLOPT_USERAGENT => 'Mozilla/5.0 (compatible; facebookexternalhit/1.1)',
  ]);
  $html = (string)curl_exec($ch);
  curl_close($ch);
  if (preg_match('/<meta[^>]+(?:property|name)=["\'](?:og:image|twitter:image)["\'][^>]*content=["\']([^"\']+)/i', $html, $m)
   || preg_match('/<meta[^>]+content=["\']([^"\']+)["\'][^>]*(?:property|name)=["\'](?:og:image|twitter:image)["\']/i', $html, $m)) {
    $img = html_entity_decode($m[1]);
    $img = preg_replace('/\?fb$/', '', $img);
  }
  if ($img === '' || !host_ok($img, $IMAGE_HOSTS)) fail();
  if (is_dir($CACHE_DIR) || @mkdir($CACHE_DIR, 0755)) @file_put_contents($key, $img);
}

header('Cache-Control: public, max-age=86400');
header('Location: ' . $img, true, 302);
