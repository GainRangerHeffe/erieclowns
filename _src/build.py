#!/usr/bin/env python3
"""Builds the static pages from the shared header, footer and meta template.

Edit SITE settings or page content here, then run:  python3 _src/build.py
The generated .html files at the repo root are what Hostinger serves.
Events are NOT built here: they come from a Google Sheet (EVENTS_SHEET_CSV in assets/js/site.js).
"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def ver(path):
    """Short content hash so browsers and Hostinger's cache pick up changed CSS/JS right away."""
    return hashlib.md5((ROOT / path).read_bytes()).hexdigest()[:8]

SITE = {
    "url": "https://eriesistibleclowns.com",   # TODO: real domain, no trailing slash
    "name": "ERIEsistible Clowns",
    "phone": "",                                # TODO: e.g. "(814) 555-0123"
    "email": "TheClownRusty@gmail.com",
    "facebook": "https://www.facebook.com/ERIEsistibleClowns",
    "street": "512 Kelso Dr",
    "city": "Erie",
    "region": "PA",
    "zip": "16505",
    "hall_price": "",                           # TODO: e.g. "$250 per event"
    "erie_gives": "https://www.eriegives.org/organization/eriesistible-clowns",
    "donate_url": "",                           # TODO: year-round donation link (Zeffy, PayPal, etc.)
    "ein": "47-1013614",
    "college_price": "$125",
    "college_early": "$100",
}

FB_SVG = ('<svg class="fb-icon" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path fill="currentColor" '
          'd="M24 12.07C24 5.41 18.63 0 12 0S0 5.4 0 12.07C0 18.1 4.39 23.1 10.13 24v-8.44H7.08v-3.49h3.04V9.41c0-3.02 '
          '1.8-4.7 4.54-4.7 1.31 0 2.68.24 2.68.24v2.97h-1.5c-1.5 0-1.96.93-1.96 1.89v2.26h3.32l-.53 3.5h-2.8V24C19.62 '
          '23.1 24 18.1 24 12.07"/></svg>')

NAV = [
    ("book-clowns.html", "Book Clowns"),
    ("kury-hall.html", "Kury Hall"),
    ("clown-college.html", "Clown College"),
    ("events.html", "Events"),
    ("donate.html", "Donate"),
]


def todo(value, label):
    return value if value else f'<span class="todo">[{label}]</span>'


def phone_link():
    p = SITE["phone"]
    if not p:
        return '<span>Call or text <span class="todo">[phone]</span></span>'
    digits = "".join(c for c in p if c.isdigit())
    return f'<a href="tel:+1{digits[-10:]}">Call or text {p}</a>'


def org_jsonld():
    data = {
        "@context": "https://schema.org",
        "@type": "NGO",
        "name": SITE["name"],
        "alternateName": "Erie Clowns",
        "slogan": "Purveyors of Nonsense",
        "foundingDate": "1968",
        "taxID": SITE["ein"],
        "url": SITE["url"] + "/",
        "logo": SITE["url"] + "/assets/img/logo.png",
        "email": SITE["email"],
        "sameAs": [SITE["facebook"]],
        "address": {"@type": "PostalAddress", "streetAddress": SITE["street"], "addressLocality": SITE["city"],
                    "addressRegion": SITE["region"], "postalCode": SITE["zip"], "addressCountry": "US"},
        "areaServed": "Erie, Pennsylvania",
    }
    if SITE["phone"]:
        data["telephone"] = SITE["phone"]
    return data


def page(slug, title, description, og_image, body, active=None, extra_ld=None):
    url = SITE["url"] + "/" + ("" if slug == "index.html" else slug)
    full_title = title if slug == "index.html" else f"{title} | {SITE['name']}"
    ld = [org_jsonld()] + (extra_ld or [])
    nav = "\n".join(
        f'      <a href="{href}"{CURRENT if href == active else ""}>{label}</a>' for href, label in NAV
    )
    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
{BASE if slug == "404.html" else ""}<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{full_title}</title>
<meta name="description" content="{description}">
<link rel="canonical" href="{url}">
<meta name="theme-color" content="#c8231b">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{SITE['name']}">
<meta property="og:locale" content="en_US">
<meta property="og:url" content="{url}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:image" content="{SITE['url']}/assets/img/{og_image}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{SITE['name']} logo with {title}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{description}">
<meta name="twitter:image" content="{SITE['url']}/assets/img/{og_image}">
<link rel="icon" href="favicon.ico" sizes="32x32">
<link rel="icon" type="image/png" sizes="192x192" href="assets/img/icon-192.png">
<link rel="apple-touch-icon" href="assets/img/icon-180.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Luckiest+Guy&family=Nunito:wght@400;600;700;800&display=swap">
<link rel="stylesheet" href="assets/css/site.css?v={ver('assets/css/site.css')}">
<script type="application/ld+json">{json.dumps(ld if len(ld) > 1 else ld[0])}</script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<div class="utility">
  <div class="wrap">
    <span class="loc">Kury Hall · {SITE['street']}, {SITE['city']}, {SITE['region']}</span>
    {phone_link()}
    <a href="{SITE['facebook']}" target="_blank" rel="noopener" aria-label="ERIEsistible Clowns on Facebook">{FB_SVG}<span>Facebook</span></a>
  </div>
</div>
<header class="site">
  <div class="wrap">
    <a class="brand" href="index.html"><img src="assets/img/logo.png" alt="" width="60" height="60"><span>ERIEsistible Clowns</span></a>
    <button class="menu-btn" type="button" aria-expanded="false" aria-controls="main-nav" aria-label="Menu"><span></span><span></span><span></span></button>
    <nav class="main" id="main-nav" aria-label="Main">
{nav}
      <a class="btn btn-red" href="contact.html">Request a date</a>
    </nav>
  </div>
</header>
<main id="main">
{body}
</main>
<footer class="site">
  <div class="wrap">
    <div class="stack" style="gap:8px">
      <h3>ERIEsistible Clowns</h3>
      <p>Purveyors of Nonsense. A nonprofit clown alley making Erie smile since 1968.</p>
    </div>
    <div class="stack" style="gap:6px">
      <strong>Visit</strong>
      <p>Kury Hall<br>{SITE['street']}<br>{SITE['city']}, {SITE['region']} {SITE['zip']}</p>
    </div>
    <div class="stack" style="gap:6px">
      <strong>Explore</strong>
      <ul>{"".join(f'<li><a href="{h}">{l}</a></li>' for h, l in NAV)}</ul>
    </div>
    <div class="stack" style="gap:6px">
      <strong>Reach us</strong>
      <ul>
        <li><a href="contact.html">Request a date</a></li>
        <li><a href="mailto:{SITE['email']}">{SITE['email']}</a></li>
        <li><a href="{SITE['facebook']}" target="_blank" rel="noopener">Facebook</a></li>
      </ul>
    </div>
    <p class="copy">© <span id="yr">2026</span> ERIEsistible Clowns. All rights reserved.</p>
  </div>
</footer>
<script src="assets/js/site.js?v={ver('assets/js/site.js')}" defer></script>
</body>
</html>
"""
    (ROOT / slug).write_text(html)
    return slug


BASE = '<base href="/">\n'
CURRENT = ' aria-current="page"'
TENT = '<div class="tent" aria-hidden="true"></div>'

# ---------------------------------------------------------------- pages

HOME = f"""
<section class="hero">
  <div class="wrap split">
    <div class="stack" style="gap:20px">
      <p class="tagline">“Purveyors of Nonsense”</p>
      <h1>Making Erie smile since 1968</h1>
      <p class="lede">Over 50 volunteer clowns bringing balloon twisting, face painting, juggling, magic, skits and parades to events across the Erie area.</p>
      <div class="btn-row">
        <a class="btn btn-red" href="contact.html?type=community">Request clowns</a>
        <a class="btn" href="events.html">See upcoming events</a>
      </div>
    </div>
    <div class="hero-logo"><img src="assets/img/logo.png" alt="ERIEsistible Clowns logo: a smiling clown with a green hat and polka-dot bow tie" width="200" height="200"></div>
  </div>
</section>
{TENT}
<section class="band paper">
  <div class="wrap stack" style="gap:28px">
    <div class="stack"><p class="eyebrow">How can we help?</p><h2>Pick your path</h2></div>
    <div class="paths">
      <a class="path" href="book-clowns.html" style="--c:var(--red)"><strong>Book clowns</strong><span>Parades, festivals, schools, churches and community events. Birthday party referrals too.</span><b>Rates and booking →</b></a>
      <a class="path" href="kury-hall.html" style="--c:var(--blue)"><strong>Rent Kury Hall</strong><span>Room for 250 with a kitchen. Birthdays, baptisms, showers and stag and drags.</span><b>Check a date →</b></a>
      <a class="path" href="clown-college.html" style="--c:var(--green)"><strong>Clown College</strong><span>Eight Thursday nights of clowning around. Ages 8 and up.</span><b>Get on the list →</b></a>
      <a class="path" href="donate.html" style="--c:var(--orange)"><strong>Donate</strong><span>Help us keep the laughter going with a gift through Erie Gives.</span><b>Give today →</b></a>
    </div>
  </div>
</section>
<section class="band blue">
  <div class="wrap facts" aria-label="Quick facts">
    <div class="fact"><strong>1968</strong><span>Founded by Joe and Jill Kury</span></div>
    <div class="fact"><strong>50+</strong><span>Member clowns</span></div>
    <div class="fact"><strong>1 to 100</strong><span>The ages we make laugh</span></div>
    <div class="fact"><strong>250</strong><span>Guests fit in Kury Hall</span></div>
  </div>
</section>
<section class="band">
  <div class="wrap stack" style="gap:24px">
    <div class="split top">
      <div class="stack"><p class="eyebrow">Coming up</p><h2>Where to find the clowns</h2></div>
      <p class="lede">Catch us at parades, festivals and community events around Erie.</p>
    </div>
    <div class="events" id="events-list" data-limit="3"><p class="note">Loading events…</p></div>
    <p><a class="btn" href="events.html">All events</a></p>
  </div>
</section>
{TENT}
<section class="band paper">
  <div class="wrap split">
    <div class="stack">
      <p class="eyebrow">About us</p>
      <h2>A clown alley with its own hall</h2>
      <p class="lede">Joe and Jill Kury started the Erie Clowns in 1968, and members finished building our 5,000 sq ft home, Kury Hall, in 1972. Today the ERIEsistible Clowns are a nonprofit of more than 50 members who perform, march in parades, visit hospitals, and still get together for picnics and Christmas parties.</p>
      <p class="lede">Our mission is simple: make people from 1 to 100 smile and laugh.</p>
      <div class="btn-row"><a class="btn btn-gold" href="contact.html?type=join">Join the alley</a></div>
    </div>
    <img class="pic" src="assets/img/about-clowns.jpg" alt="Six ERIEsistible Clowns in full costume twisting balloons" width="1400" height="1050" loading="lazy">
  </div>
</section>
"""

BOOK = f"""
<section class="hero">
  <div class="wrap split">
    <div class="stack" style="gap:18px">
      <p class="eyebrow">Book clowns</p>
      <h1>Bring the clowns to your event</h1>
      <p class="lede">We're a volunteer nonprofit, so community and nonprofit events come first. Planning a birthday party? We'll connect you with one of our member clowns for free.</p>
      <div class="btn-row"><a class="btn btn-red" href="contact.html?type=community">Request clowns</a><a class="btn" href="contact.html?type=private">Birthday party referral</a></div>
    </div>
    <img class="pic" src="assets/img/clowns-at-event.jpg" alt="ERIEsistible Clowns twisting balloons and face painting under their tent at an outdoor event" width="1400" height="1050">
  </div>
</section>
{TENT}
<section class="band paper">
  <div class="wrap stack" style="gap:24px">
    <h2>What we bring</h2>
    <div class="services">
      <div class="service" style="--c:var(--red)"><h3>Balloon twisting</h3><p>Dogs, swords, hats and flowers, made on the spot.</p></div>
      <div class="service" style="--c:var(--blue)"><h3>Face painting</h3><p>Quick, colorful designs for kids of all ages.</p></div>
      <div class="service" style="--c:var(--green)"><h3>Juggling and magic</h3><p>Walk-around tricks that stop people in their tracks.</p></div>
      <div class="service" style="--c:var(--orange)"><h3>Skits and parades</h3><p>Full clown units for parades, stages and festivals.</p></div>
    </div>
    <p class="note">Our clowns also make hospital visits and appear at community fundraisers.</p>
  </div>
</section>
<section class="band">
  <div class="wrap split top">
    <div class="stack">
      <p class="eyebrow">Community and nonprofit events</p>
      <h2>Rates and guidelines</h2>
      <p>We get lots of requests from charities and organizations, and we'd love to say yes to everyone. As a volunteer-run Pennsylvania nonprofit, though, we can only take on so many events each year, and the cost of balloons and face paint keeps rising. These guidelines help us keep showing up.</p>
      <div class="rates">
        <div class="rate"><div>Community and nonprofit events<small>One-time donation that covers travel, balloons and face paint</small></div><span class="amt">$100 min.</span></div>
        <div class="rate"><div>Private parties (referral)<small>Booked directly with a member clown; rates and availability vary</small></div><span class="amt">~$150/hr</span></div>
        <div class="rate"><div>For comparison<small>Typical professional rate, per clown</small></div><span class="amt">~$125/hr</span></div>
      </div>
      <ul class="dots">
        <li>Events within 20 miles of downtown Erie</li>
        <li>Summer events need a tent or shaded spot for the clowns</li>
        <li>Tell us the date, time and place, and we'll find clowns who can make it</li>
      </ul>
      <div class="btn-row"><a class="btn btn-red" href="contact.html?type=community">Request clowns</a></div>
    </div>
    <div class="callout">
      <h3>Booking a birthday party?</h3>
      <p>The alley itself doesn't do private parties, but many of our members do. Send us your date and we'll pass it to a clown who's free. The referral is free; you pay the clown directly.</p>
      <p><a class="btn btn-gold" href="contact.html?type=private">Get a clown referral</a></p>
    </div>
  </div>
</section>
"""

HALL = f"""
<section class="hero">
  <div class="wrap split">
    <div class="stack" style="gap:18px">
      <p class="eyebrow">Kury Hall rentals</p>
      <h1>Room for 250, kitchen included</h1>
      <p class="lede">Our 5,000 sq ft hall at {SITE['street']} was built by our own members in 1972. It's big enough for a crowd and affordable enough for a family party.</p>
      <div class="btn-row"><a class="btn btn-red" href="contact.html?type=hall">Check a date</a></div>
    </div>
    <img class="pic" src="assets/img/kury-hall.jpg" alt="Inside Kury Hall: a large room with rows of tables and chairs and clown murals on the walls" width="1000" height="750">
  </div>
</section>
{TENT}
<section class="band paper">
  <div class="wrap split top">
    <div class="stack">
      <h2>Rental details</h2>
      <div class="rates">
        <div class="rate"><div>Hall rental<small>Kitchen included</small></div><span class="amt">{todo(SITE['hall_price'], 'price')}</span></div>
        <div class="rate"><div>Security deposit<small>Refunded after your event</small></div><span class="amt">$100</span></div>
        <div class="rate"><div>Capacity<small>Seated and standing</small></div><span class="amt">250 guests</span></div>
      </div>
    </div>
    <div class="stack">
      <h2>Good for</h2>
      <ul class="dots">
        <li>Birthday parties</li>
        <li>Baptisms and showers</li>
        <li>Stag and drags</li>
        <li>Reunions and small-to-medium celebrations</li>
      </ul>
      <p><a href="https://maps.google.com/?q={SITE['street'].replace(' ', '+')}+{SITE['city']}+{SITE['region']}+{SITE['zip']}" target="_blank" rel="noopener">Get directions to {SITE['street']}, {SITE['city']}, {SITE['region']} {SITE['zip']}</a></p>
      <div class="btn-row"><a class="btn btn-red" href="contact.html?type=hall">Check a date</a></div>
    </div>
  </div>
</section>
"""

COLLEGE = f"""
<section class="hero">
  <div class="wrap split">
    <div class="stack" style="gap:18px">
      <p class="eyebrow">Clown College</p>
      <h1>Eight weeks of clowning around</h1>
      <p class="lede">Learn, laugh and perform. Clown College meets one night a week for eight weeks each fall at Kury Hall. Ages 8 and up; kids join with a parent or guardian.</p>
      <div class="btn-row"><a class="btn btn-red" href="contact.html?type=college">Get on the list</a></div>
    </div>
    <div><img class="flyer flyer-college" src="assets/img/flyer-clown-college.jpg" alt="Clown College flyer: 8 weeks, every Thursday, 6 to 8 PM, $125 or $100 when you register early" width="206" height="206"></div>
  </div>
</section>
{TENT}
<section class="band paper">
  <div class="wrap split top">
    <div class="stack">
      <h2>How it works</h2>
      <div class="rates">
        <div class="rate"><div>Schedule<small>Eight weeks, starting each September</small></div><span class="amt">Thursdays, 6 to 8 PM</span></div>
        <div class="rate"><div>Tuition<small>Covers all eight classes</small></div><span class="amt">{SITE['college_price']}</span></div>
        <div class="rate"><div>Early registration<small>Sign up before the early deadline</small></div><span class="amt">{SITE['college_early']}</span></div>
        <div class="rate"><div>Where<small>{SITE['street']}, {SITE['city']}</small></div><span class="amt">Kury Hall</span></div>
      </div>
      <p class="note">This year's class is already underway. Join the list and we'll let you know when the next class opens, including the early registration deadline.</p>
    </div>
    <div class="stack">
      <h2>What you'll learn</h2>
      <ul class="dots">
        <li>Clown makeup and character</li>
        <li>Looking, walking and acting like a clown</li>
        <li>Skit and routine building</li>
        <li>Props and gags</li>
        <li>Costuming</li>
        <li>Audience interaction and improv</li>
      </ul>
      <p>Classes end with a graduation celebration, and graduates can join the alley for events and parades.</p>
      <div class="btn-row"><a class="btn btn-red" href="contact.html?type=college">Get on the list</a></div>
    </div>
  </div>
</section>
<section class="band">
  <div class="wrap stack" style="gap:20px">
    <h2>Graduation day</h2>
    <img class="pic pic-wide" src="assets/img/clown-college-grads.jpg" alt="Clown College graduates in full costume and makeup holding their certificates on the Kury Hall stage" width="1800" height="975" loading="lazy">
  </div>
</section>
"""

EVENTS = f"""
<section class="hero">
  <div class="wrap split">
    <div class="stack" style="gap:18px">
      <p class="eyebrow">Events</p>
      <h1>Where to find the clowns</h1>
      <p class="lede">Parades, festivals, fundraisers and Clown College nights. Want clowns at your event? <a href="contact.html?type=community">Send us a request</a>.</p>
    </div>
    <img class="pic" src="assets/img/clowns-at-event.jpg" alt="ERIEsistible Clowns twisting balloons and face painting under their tent at an outdoor event" width="1400" height="1050">
  </div>
</section>
{TENT}
<section class="band paper">
  <div class="wrap stack" style="gap:28px">
    <div class="events" id="events-list"><p class="note">Loading events…</p></div>
    <details class="past-list stack" id="events-past" hidden>
      <summary>Past events</summary>
      <div class="events" style="margin-top:16px"></div>
    </details>
  </div>
</section>
"""

DONATE_BTN = (f'<a class="btn btn-red" href="{SITE["donate_url"]}" target="_blank" rel="noopener">Donate now</a>'
              if SITE["donate_url"] else '<a class="btn btn-red" href="contact.html?type=other">Ask about donating</a>')

DONATE = f"""
<section class="hero">
  <div class="wrap split">
    <div class="stack" style="gap:18px">
      <p class="eyebrow">Donate</p>
      <h1>Help us keep the laughter going</h1>
      <p class="lede">Your donation helps the ERIEsistible Clowns bring smiles, laughter and joy to children and families across Erie through hospital visits, parades, special events and more.</p>
      <div class="btn-row">{DONATE_BTN}<a class="btn" href="{SITE['erie_gives']}" target="_blank" rel="noopener">Our Erie Gives page</a></div>
      <p class="note">Erie Gives is the Erie Community Foundation's day of giving and is only open for a short time each year. Every dollar makes a difference.</p>
      <p class="note">ERIEsistible Clowns is a Pennsylvania nonprofit. EIN {SITE['ein']}.</p>
    </div>
    <div><img class="flyer" src="assets/img/flyer-erie-gives.jpg" alt="Flyer: Help us keep the laughter going. We need your support on Erie Gives." width="1024" height="1536" loading="lazy"></div>
  </div>
</section>
{TENT}
<section class="band paper">
  <div class="wrap stack" style="gap:24px">
    <h2>Where your gift goes</h2>
    <div class="services">
      <div class="service" style="--c:var(--red)"><h3>Joy and laughter</h3><p>Balloons, face paint and supplies for every event.</p></div>
      <div class="service" style="--c:var(--blue)"><h3>Hospital visits</h3><p>Clowns visiting kids and families when they need it most.</p></div>
      <div class="service" style="--c:var(--green)"><h3>Community events</h3><p>Parades and festivals across the Erie area.</p></div>
      <div class="service" style="--c:var(--orange)"><h3>Kury Hall</h3><p>Keeping our home open for Clown College and the community.</p></div>
    </div>
  </div>
</section>
"""

TYPES = [("community", "Clowns for an event"), ("private", "Birthday or private party"), ("hall", "Kury Hall rental"),
         ("college", "Clown College"), ("join", "Join the alley"), ("other", "Something else")]

CONTACT = f"""
<section class="hero">
  <div class="wrap split top">
    <div class="stack" style="gap:18px">
      <p class="eyebrow">Request a date</p>
      <h1>Tell us what you're planning</h1>
      <p class="lede">Pick what you need and send it over. A real clown reads every request and gets back to you.</p>
      <div class="contact-list">
        <p><strong>Phone:</strong> {phone_link()}</p>
        <p><strong>Email:</strong> <a href="mailto:{SITE['email']}">{SITE['email']}</a></p>
        <p><strong>Facebook:</strong> <a href="{SITE['facebook']}" target="_blank" rel="noopener">ERIEsistibleClowns</a></p>
        <p><strong>Kury Hall:</strong> <a href="https://maps.google.com/?q={SITE['street'].replace(' ', '+')}+{SITE['city']}+{SITE['region']}+{SITE['zip']}" target="_blank" rel="noopener">{SITE['street']}, {SITE['city']}, {SITE['region']} {SITE['zip']}</a></p>
      </div>
    </div>
    <form class="formcard" id="request-form" novalidate>
      <fieldset>
        <legend>What do you need?</legend>
        <div class="types">
{"".join(f'          <input type="radio" name="type" id="t-{v}" value="{v}"{" checked" if i == 0 else ""}><label for="t-{v}">{l}</label>' + chr(10) for i, (v, l) in enumerate(TYPES))}        </div>
      </fieldset>
      <p class="notice" data-for="private">Private parties are booked directly with one of our member clowns. Send this and we'll pass it to a clown who's free that day.</p>
      <p class="notice" data-for="college">This year's class has started. We'll let you know when the next one opens.</p>
      <div class="grid2">
        <div class="field"><label for="f-name">Your name</label><input id="f-name" name="name" autocomplete="name" required></div>
        <div class="field"><label for="f-phone">Phone</label><input id="f-phone" name="phone" type="tel" autocomplete="tel"></div>
      </div>
      <div class="field"><label for="f-email">Email</label><input id="f-email" name="email" type="email" autocomplete="email" required></div>
      <div class="grid2" data-for="community private hall">
        <div class="field"><label for="f-date">Event date</label><input id="f-date" name="date" type="date"></div>
        <div class="field"><label for="f-time">Start time</label><input id="f-time" name="time" type="time"></div>
      </div>
      <div class="field" data-for="community private"><label for="f-where">Where is it?</label><input id="f-where" name="location" placeholder="Venue and town"></div>
      <div class="grid2" data-for="community private">
        <div class="field"><label for="f-hours">How long?</label><select id="f-hours" name="hours"><option>1 hour</option><option>2 hours</option><option>3 hours</option><option>Half day or parade</option></select></div>
        <div class="field"><label for="f-clowns">Clowns needed</label><select id="f-clowns" name="clowns"><option>1</option><option>2</option><option>3 to 5</option><option>6 or more</option></select></div>
      </div>
      <div class="field" data-for="community"><label for="f-org">Organization</label><input id="f-org" name="organization" placeholder="School, church, nonprofit, festival"></div>
      <div class="grid2" data-for="hall">
        <div class="field"><label for="f-guests">Guests</label><input id="f-guests" name="guests" type="number" min="1" max="250" inputmode="numeric"></div>
        <div class="field"><label for="f-kind">Kind of event</label><input id="f-kind" name="event_kind" placeholder="Birthday, baptism, shower"></div>
      </div>
      <div class="grid2" data-for="college">
        <div class="field"><label for="f-students">Students</label><input id="f-students" name="students" type="number" min="1" inputmode="numeric" value="1"></div>
        <div class="field"><label for="f-ages">Their ages</label><input id="f-ages" name="ages" placeholder="e.g. 10 and 42"></div>
      </div>
      <div class="field"><label for="f-msg">Anything else?</label><textarea id="f-msg" name="message" rows="3"></textarea></div>
      <input class="hp" type="text" name="_honey" tabindex="-1" autocomplete="off" aria-hidden="true">
      <button class="btn btn-red" type="submit" id="f-submit">Send request</button>
      <p class="result" id="f-result" role="status" aria-live="polite"></p>
      <p class="note">We only use your details to answer this request.</p>
    </form>
  </div>
</section>
"""

NOT_FOUND = """
<section class="hero">
  <div class="wrap stack" style="gap:18px">
    <p class="eyebrow">Page not found</p>
    <h1>This page took a pie to the face</h1>
    <p class="lede">The page you're looking for isn't here. Try one of these instead.</p>
    <div class="btn-row"><a class="btn btn-red" href="index.html">Home</a><a class="btn" href="events.html">Events</a><a class="btn" href="contact.html">Request a date</a></div>
  </div>
</section>
"""

HALL_LD = {
    "@context": "https://schema.org", "@type": "EventVenue", "name": "Kury Hall",
    "maximumAttendeeCapacity": 250, "url": SITE["url"] + "/kury-hall.html",
    "address": {"@type": "PostalAddress", "streetAddress": SITE["street"], "addressLocality": SITE["city"],
                "addressRegion": SITE["region"], "postalCode": SITE["zip"], "addressCountry": "US"},
}

PAGES = [
    page("index.html", "ERIEsistible Clowns | Erie, PA Clowns Since 1968",
         "Erie's nonprofit clown alley since 1968. Book clowns for parades and community events, rent Kury Hall, or join Clown College.",
         "og-home.jpg", HOME),
    page("book-clowns.html", "Book Clowns in Erie, PA",
         "Balloon twisting, face painting, juggling, magic and parade clowns for Erie community and nonprofit events. Free birthday party referrals.",
         "og-book.jpg", BOOK, "book-clowns.html"),
    page("kury-hall.html", "Rent Kury Hall",
         "Rent Kury Hall at 512 Kelso Dr, Erie PA. Seats 250 with a kitchen, for birthdays, baptisms, showers and stag and drags.",
         "og-hall.jpg", HALL, "kury-hall.html", [HALL_LD]),
    page("clown-college.html", "Clown College",
         "Eight weeks of clowning around at Kury Hall. Thursdays 6 to 8 PM, ages 8 and up. Makeup, character, skits, props and improv.",
         "og-college.jpg", COLLEGE, "clown-college.html"),
    page("events.html", "Upcoming Events",
         "See where the ERIEsistible Clowns are performing next: parades, festivals, fundraisers and community events around Erie.",
         "og-events.jpg", EVENTS, "events.html"),
    page("donate.html", "Donate",
         "Help the ERIEsistible Clowns keep the laughter going. Support hospital visits, parades and community events through Erie Gives.",
         "og-donate.jpg", DONATE, "donate.html"),
    page("contact.html", "Request a Date",
         "Request clowns for your event, check a Kury Hall date, or get on the Clown College list. Contact the ERIEsistible Clowns.",
         "og-home.jpg", CONTACT),
    page("404.html", "Page Not Found", "This page could not be found.", "og-home.jpg", NOT_FOUND),
]

sitemap = "".join(f"  <url><loc>{SITE['url']}/{'' if p == 'index.html' else p}</loc></url>\n" for p in PAGES if p != "404.html")
(ROOT / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{sitemap}</urlset>\n')
(ROOT / "robots.txt").write_text(f"User-agent: *\nDisallow: /_src/\nSitemap: {SITE['url']}/sitemap.xml\n")
print("Built", ", ".join(PAGES))
