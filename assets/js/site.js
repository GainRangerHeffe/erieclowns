// Where request forms go. FormSubmit emails each request to this address.
// The very first submission sends an activation email to that inbox; click it once.
var FORM_ENDPOINT = "https://formsubmit.co/ajax/TheClownRusty@gmail.com";
// Events come from a Google Sheet published as CSV (File > Share > Publish to web > Events tab > CSV).
// Paste that link here. While it's empty the site falls back to content/events.json.
var EVENTS_SHEET_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRgKP5oG7tjSArSD2RUzweXsIo4uVhGvkC0Jy-I7UxC972Fb0LtnTfDBvaAagwfWEk5OXZdvuwXZCE3/pub?output=csv";
var EVENTS_URL = "content/events.json";

(function () {
  // Mobile menu
  var btn = document.querySelector(".menu-btn");
  var nav = document.getElementById("main-nav");
  if (btn && nav) {
    btn.addEventListener("click", function () {
      var open = nav.classList.toggle("open");
      btn.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  var yr = document.getElementById("yr");
  if (yr) yr.textContent = new Date().getFullYear();

  initForm();
  initEvents();
})();

function initForm() {
  var form = document.getElementById("request-form");
  if (!form) return;
  var result = document.getElementById("f-result");
  var labels = {
    community: "Clowns for a community event",
    private: "Private party referral",
    hall: "Kury Hall rental",
    college: "Clown College",
    join: "Join the alley",
    other: "General question"
  };

  function current() { return form.querySelector('input[name="type"]:checked').value; }
  function sync() {
    var t = current();
    form.querySelectorAll("[data-for]").forEach(function (el) {
      el.hidden = el.getAttribute("data-for").split(" ").indexOf(t) === -1;
    });
  }
  var want = new URLSearchParams(location.search).get("type") || location.hash.replace("#", "");
  var radio = want && document.getElementById("t-" + want);
  if (radio) radio.checked = true;
  form.addEventListener("change", function (e) { if (e.target.name === "type") sync(); });
  sync();

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    var name = form.elements.name, email = form.elements.email;
    result.className = "result err";
    if (!name.value.trim()) { result.textContent = "Please add your name."; name.focus(); return; }
    if (!email.value.trim() || !email.checkValidity()) { result.textContent = "Please add an email address we can reply to."; email.focus(); return; }
    if (form.elements._honey.value) return;

    var t = current();
    var data = { _subject: "Website request: " + labels[t], _template: "table", _captcha: "false", request: labels[t] };
    form.querySelectorAll("input, select, textarea").forEach(function (el) {
      if (el.name === "type" || el.name === "_honey" || !el.name || !el.value) return;
      var box = el.closest("[data-for]");
      if (box && box.hidden) return;
      data[el.name] = el.value;
    });

    var send = document.getElementById("f-submit");
    send.disabled = true;
    result.className = "result";
    result.textContent = "Sending…";
    fetch(FORM_ENDPOINT, {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify(data)
    })
      .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
      .then(function () {
        form.reset(); sync();
        result.className = "result ok";
        result.textContent = "Thanks! Your request is in, and a clown will get back to you soon.";
      })
      .catch(function () {
        result.className = "result err";
        result.textContent = "That didn't go through. Please email TheClownRusty@gmail.com or message us on Facebook.";
      })
      .then(function () { send.disabled = false; });
  });
}

function initEvents() {
  var list = document.getElementById("events-list");
  if (!list) return;
  var limit = parseInt(list.getAttribute("data-limit") || "0", 10);
  var pastBox = document.getElementById("events-past");

  var load = EVENTS_SHEET_CSV
    ? fetch(EVENTS_SHEET_CSV, { cache: "no-store" })
        .then(function (r) { if (!r.ok) throw new Error(r.status); return r.text(); })
        .then(sheetToEvents)
    : fetch(EVENTS_URL, { cache: "no-store" })
        .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
        .then(function (data) { return (data && data.events) || []; });
  load.then(render).catch(function (err) { console.warn("Events could not be loaded:", err); render([]); });

  // Sheet columns (header row, any order, case-insensitive):
  // Title, Date, Start time, End time, Type, Location, Address, Description, Image URL, Link
  function sheetToEvents(text) {
    var rows = parseCSV(text).filter(function (r) { return r.some(function (c) { return c.trim(); }); });
    if (!rows.length) return [];
    var head = rows.shift().map(function (h) { return h.trim().toLowerCase(); });
    function col(row, names) {
      for (var i = 0; i < names.length; i++) {
        var k = head.indexOf(names[i]);
        if (k > -1 && row[k] != null && row[k].trim()) return row[k].trim();
      }
      return "";
    }
    return rows.map(function (r) {
      var day = toISODate(col(r, ["date", "event date"]));
      if (!day) return null;
      var st = toTime(col(r, ["start time", "start", "time"]));
      var et = toTime(col(r, ["end time", "end"]));
      return {
        title: col(r, ["title", "event", "name"]),
        type: col(r, ["type", "category"]),
        start: day + (st ? "T" + st : ""),
        end: et ? day + "T" + et : "",
        location: col(r, ["location", "place", "where"]),
        address: col(r, ["address"]),
        description: col(r, ["description", "details"]),
        image: col(r, ["image url", "image", "photo"]),
        link: col(r, ["link", "more info", "url"])
      };
    }).filter(Boolean);
  }
  function toISODate(s) {
    var m = s.match(/^(\d{4})-(\d{1,2})-(\d{1,2})/);
    if (m) return m[1] + "-" + pad(m[2]) + "-" + pad(m[3]);
    m = s.match(/^(\d{1,2})\/(\d{1,2})\/(\d{2,4})/);
    if (m) return (m[3].length === 2 ? "20" + m[3] : m[3]) + "-" + pad(m[1]) + "-" + pad(m[2]);
    var d = new Date(s);
    return isNaN(d) ? "" : d.getFullYear() + "-" + pad(d.getMonth() + 1) + "-" + pad(d.getDate());
  }
  function toTime(s) {
    var m = s.match(/^(\d{1,2})(?::(\d{2}))?(?::\d{2})?\s*([ap])?\.?m?\.?$/i);
    if (!m) return "";
    var h = +m[1], ap = (m[3] || "").toLowerCase();
    if (ap === "p" && h < 12) h += 12;
    if (ap === "a" && h === 12) h = 0;
    return pad(h) + ":" + (m[2] || "00");
  }
  function pad(n) { return String(n).length < 2 ? "0" + n : String(n); }
  function parseCSV(text) {
    var rows = [], row = [], cell = "", q = false;
    for (var i = 0; i < text.length; i++) {
      var c = text[i];
      if (q) {
        if (c === '"' && text[i + 1] === '"') { cell += '"'; i++; }
        else if (c === '"') q = false;
        else cell += c;
      } else if (c === '"') q = true;
      else if (c === ",") { row.push(cell); cell = ""; }
      else if (c === "\n" || c === "\r") {
        if (c === "\r" && text[i + 1] === "\n") i++;
        row.push(cell); rows.push(row); row = []; cell = "";
      } else cell += c;
    }
    if (cell || row.length) { row.push(cell); rows.push(row); }
    return rows;
  }

  function render(events) {
    var now = new Date();
    var startOfToday = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    events = events.filter(function (e) { return e && e.title && e.start; })
      .map(function (e) { e._start = parseLocal(e.start); e._end = e.end ? parseLocal(e.end) : null; return e; })
      .sort(function (a, b) { return a._start - b._start; });
    var upcoming = events.filter(function (e) { return (e._end || e._start) >= startOfToday; });
    var past = events.filter(function (e) { return (e._end || e._start) < startOfToday; }).reverse();

    var shown = limit ? upcoming.slice(0, limit) : upcoming;
    list.innerHTML = "";
    if (!shown.length) {
      list.innerHTML = '<div class="empty"><h3>No upcoming events posted yet</h3>' +
        '<p>New parades, festivals and Clown College dates show up here as soon as they are scheduled. ' +
        'Follow us on <a href="https://www.facebook.com/ERIEsistibleClowns" target="_blank" rel="noopener">Facebook</a> for the latest.</p></div>';
    } else {
      shown.forEach(function (e) { list.appendChild(card(e, false)); });
    }
    if (pastBox) {
      var pl = pastBox.querySelector(".events");
      if (past.length && pl) {
        past.slice(0, 12).forEach(function (e) { pl.appendChild(card(e, true)); });
        pastBox.hidden = false;
      }
    }
    addStructuredData(upcoming);
  }

  function card(e, isPast) {
    var el = document.createElement("article");
    var img = imageUrl(e.image);
    el.className = "event" + (isPast ? " past" : "");
    var d = e._start;
    var month = d.toLocaleDateString("en-US", { month: "short" });
    var when = d.toLocaleDateString("en-US", { weekday: "long", month: "long", day: "numeric", year: "numeric" });
    if (!/T00:00/.test(e.start) && e.start.indexOf("T") > -1) when += " · " + time(d) + (e._end ? " to " + time(e._end) : "");
    el.innerHTML =
      '<div class="date" aria-hidden="true"><span>' + month + "</span><b>" + d.getDate() + "</b></div>" +
      "<div>" +
      (e.type ? '<span class="tag">' + esc(e.type) + "</span>" : "") +
      "<h3>" + esc(e.title) + "</h3>" +
      '<p class="meta">' + esc(when) + (e.location ? " · " + esc(e.location) : "") + "</p>" +
      (e.description ? '<p class="desc">' + esc(e.description).replace(/\n/g, "<br>") + "</p>" : "") +
      (e.link && !isPast ? '<p class="desc"><a href="' + attr(e.link) + '" target="_blank" rel="noopener">More details</a></p>' : "") +
      "</div>" +
      (img ? '<a class="event-img" href="' + attr(img) + '" target="_blank" rel="noopener"><img src="' + attr(img) +
        '" alt="' + attr(e.title) + '" loading="lazy" referrerpolicy="no-referrer"></a>' : "");
    if (img) {
      el.classList.add("has-img");
      var pic = el.querySelector(".event-img img");
      var drop = function () { el.classList.remove("has-img"); if (pic.parentNode) pic.parentNode.remove(); };
      pic.addEventListener("error", drop);
      // Imgur answers a bad link with its 161x81 "image no longer available" picture instead of an error.
      pic.addEventListener("load", function () { if (pic.naturalWidth === 161 && pic.naturalHeight === 81) drop(); });
    }
    return el;
  }

  function addStructuredData(upcoming) {
    if (!upcoming.length) return;
    var items = upcoming.slice(0, 20).map(function (e) {
      return {
        "@context": "https://schema.org", "@type": "Event", name: e.title, startDate: e.start,
        endDate: e.end || undefined, description: e.description || undefined,
        eventStatus: "https://schema.org/EventScheduled",
        eventAttendanceMode: "https://schema.org/OfflineEventAttendanceMode",
        location: { "@type": "Place", name: e.location || "Erie, PA", address: e.address || e.location || "Erie, PA" },
        organizer: { "@type": "Organization", name: "ERIEsistible Clowns", url: location.origin + "/" }
      };
    });
    var s = document.createElement("script");
    s.type = "application/ld+json";
    s.textContent = JSON.stringify(items);
    document.head.appendChild(s);
  }


  // Turn common "share" links into direct image links.
  function imageUrl(u) {
    u = String(u || "").trim();
    if (!u) return "";
    var m;
    if ((m = u.match(/drive\.google\.com\/(?:file\/d\/|open\?id=|uc\?(?:export=\w+&)?id=)([\w-]+)/))) return "https://lh3.googleusercontent.com/d/" + m[1];
    // Photo pages (Imgur posts, ImgBB, Google Photos) are looked up by img.php on the server,
    // which finds the actual picture behind the page.
    if (/^https:\/\/((www\.|m\.)?imgur\.com|ibb\.co|photos\.app\.goo\.gl|photos\.google\.com)\//.test(u)) return "img.php?url=" + encodeURIComponent(u);
    if (/dropbox\.com\//.test(u)) return u.replace(/([?&])dl=0/, "$1raw=1").replace(/^(?!.*[?&]raw=1)(.*)$/, function (x) { return x + (x.indexOf("?") > -1 ? "&" : "?") + "raw=1"; });
    return u.replace(/^\//, "");
  }
  function parseLocal(s) {
    var m = String(s).match(/^(\d{4})-(\d{2})-(\d{2})(?:[T ](\d{2}):(\d{2}))?/);
    if (!m) return new Date(s);
    return new Date(+m[1], +m[2] - 1, +m[3], +(m[4] || 0), +(m[5] || 0));
  }
  function time(d) { return d.toLocaleTimeString("en-US", { hour: "numeric", minute: "2-digit" }); }
  function esc(s) { return String(s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); }
  function attr(s) { return /^(https?:|\/|[\w.-])/i.test(s) && !/^javascript:/i.test(s) ? esc(s) : "#"; }
}
