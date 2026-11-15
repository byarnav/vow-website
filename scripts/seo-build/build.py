#!/usr/bin/env python3
"""Generate Vow's static content pages (Phase 3 of SEO_AEO_PLAN.md).

Usage: python3 -I build.py ~/Desktop/vow-website
Writes <slug>/index.html for each page. Plain static HTML; re-run after editing content here.
"""
import html, json, sys, os

ROOT = sys.argv[1]
BASE = "https://vow.byarnav.com"
CSS_V = "8"
UPDATED_ISO = "2026-11-05"
UPDATED_HUMAN = "November 5, 2026"
DMG = "https://raw.githubusercontent.com/byarnav/offline-lock-releases/main/Vow.dmg"
ORG = {"@type": "Organization", "@id": BASE + "/#org", "name": "byArnav", "url": "https://byarnav.com"}

GUIDES = [
    ("/block-internet-on-mac/", "Block the internet on a Mac"),
    ("/freedom-alternative/", "Freedom alternative"),
    ("/cold-turkey-alternative/", "Cold Turkey alternative"),
    ("/selfcontrol-alternative/", "SelfControl alternative"),
    ("/changelog/", "Changelog"),
]

def guides_line():
    return "Guides: " + " &middot; ".join(f'<a href="{u}">{t}</a>' for u, t in GUIDES)

def strip_tags(s):
    out, inside = [], False
    for ch in s:
        if ch == "<": inside = True
        elif ch == ">": inside = False
        elif not inside: out.append(ch)
    return " ".join(html.unescape("".join(out)).split())

def fig(src, alt, caption=None):
    cap = f"\n    <figcaption>{caption}</figcaption>" if caption else ""
    return f'''  <figure>
    <img src="/images/{src}" width="1600" height="900" alt="{alt}" loading="lazy" decoding="async">{cap}
  </figure>'''

def table(caption, head, rows):
    US = ' class="us"'
    th = "".join(f'<th scope="col"{US if h == "Vow" else ""}>{h}</th>' for h in head)
    body = ""
    for r in rows:
        cells = f'<th scope="row">{r[0]}</th>' + "".join(
            f'<td{US if head[i + 1] == "Vow" else ""}>{c}</td>' for i, c in enumerate(r[1:]))
        body += f"        <tr>{cells}</tr>\n"
    return f'''  <div class="table-scroll">
    <table>
      <caption>{caption}</caption>
      <thead><tr>{th}</tr></thead>
      <tbody>
{body}      </tbody>
    </table>
  </div>'''

def faq_block(faqs):
    items = ""
    for q, ps in faqs:
        items += "    <details>\n      <summary>" + q + "</summary>\n" + "".join(f"      <p>{p}</p>\n" for p in ps) + "    </details>\n"
    return f'''  <h2 id="faq">Questions</h2>
  <div class="faq">
{items}  </div>'''

CTA = f'''  <div class="article-cta">
    <h2>Try Vow free</h2>
    <p>Vow is a Mac app that turns off your internet and keeps it off until your timer ends, from 5 minutes to 24 hours. Try 3 full sessions free, then pay $9.99 once. Requires macOS 26 or later on Apple Silicon.</p>
    <div class="actions">
      <a class="btn primary" href="/#pricing">Buy Vow &middot; $9.99</a>
      <a class="btn secondary" href="{DMG}">Try 3 sessions free</a>
    </div>
  </div>'''

def page(slug, title, desc, h1, crumb, summary, body, faqs=None, cta=True):
    url = f"{BASE}/{slug}/"
    assert len(html.unescape(title)) <= 60, (slug, len(title))
    assert len(html.unescape(desc)) <= 155, (slug, len(html.unescape(desc)))
    graph = [
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Vow", "item": BASE + "/"},
            {"@type": "ListItem", "position": 2, "name": crumb, "item": url}]},
        {"@type": "Article", "@id": url + "#article", "headline": strip_tags(h1), "description": html.unescape(desc),
         "datePublished": UPDATED_ISO, "dateModified": UPDATED_ISO, "inLanguage": "en",
         "author": ORG, "publisher": ORG, "image": BASE + "/images/og-image.jpg",
         "mainEntityOfPage": url, "about": {"@id": BASE + "/#app"}},
    ]
    if faqs:
        graph.append({"@type": "FAQPage", "@id": url + "#faq", "mainEntity": [
            {"@type": "Question", "name": strip_tags(q),
             "acceptedAnswer": {"@type": "Answer", "text": " ".join(strip_tags(p) for p in ps)}} for q, ps in faqs]})
    ld = json.dumps({"@context": "https://schema.org", "@graph": graph}, indent=2, ensure_ascii=False).replace("</", "<\\/")
    t_attr, d_attr = title, desc
    doc = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{t_attr}</title>
<meta name="description" content="{d_attr}">
<meta name="color-scheme" content="light dark">
<link rel="canonical" href="{url}">
<meta name="theme-color" content="#ffffff" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#000000" media="(prefers-color-scheme: dark)">
<meta property="og:type" content="article">
<meta property="og:site_name" content="Vow">
<meta property="og:url" content="{url}">
<meta property="og:title" content="{t_attr}">
<meta property="og:description" content="{d_attr}">
<meta property="og:image" content="{BASE}/images/og-image.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Vow's main window on a Mac: choose how long to go offline, then press Go Offline.">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/images/favicon-16.png" sizes="16x16" type="image/png">
<link rel="icon" href="/images/favicon-32.png" sizes="32x32" type="image/png">
<link rel="icon" href="/images/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/images/apple-touch-icon.png">
<link rel="stylesheet" href="/style.css?v={CSS_V}">
<script type="application/ld+json">
{ld}
</script>
</head>
<body>
<header class="bar">
  <div class="wrap-wide bar-inner">
    <a href="/" class="mark">Vow</a>
    <nav aria-label="Primary">
      <a href="/#compare">Compare</a>
      <a href="/#pricing">Pricing</a>
      <a href="/#faq">FAQ</a>
      <a href="/#pricing" class="nav-buy">Buy</a>
    </nav>
  </div>
</header>

<main class="wrap">
<article class="article">
  <nav class="crumbs" aria-label="Breadcrumb"><a href="/">Vow</a> <span aria-hidden="true">&rsaquo;</span> <span aria-current="page">{crumb}</span></nav>
  <h1>{h1}</h1>
  <p class="updated">Last updated: <time datetime="{UPDATED_ISO}">{UPDATED_HUMAN}</time></p>
  <p class="summary">{summary}</p>

{body}
{faq_block(faqs) if faqs else ""}
{CTA if cta else ""}
</article>
</main>

<footer class="foot">
  <div class="foot-inner">
    <p>{guides_line()}</p>
    <p>Signed with an Apple Developer ID and notarized by Apple. Requires macOS 26 or later on Apple Silicon.</p>
    <p>No analytics. Checkout is handled by Paddle. <a href="/privacy.html">Privacy Policy</a> &middot; <a href="/terms.html">Terms</a> &middot; 14-day money-back guarantee.</p>
    <p>Copyright &copy; 2026 <a href="https://byarnav.com">byArnav</a>. All rights reserved.<span class="foot-mail"><span class="dot"> &middot; </span><a href="mailto:support@byarnav.com">support@byarnav.com</a></span></p>
  </div>
</footer>
</body>
</html>
'''
    os.makedirs(f"{ROOT}/{slug}", exist_ok=True)
    with open(f"{ROOT}/{slug}/index.html", "w", encoding="utf-8") as f:
        f.write(doc)
    print(f"wrote /{slug}/  title={len(html.unescape(title))}  desc={len(html.unescape(desc))}  faqs={len(faqs or [])}")

# ---------------------------------------------------------------- shared comparison rows (from homepage table, Nov 2026)
VOW = {
 "stops": "<strong>The whole internet</strong>: every browser, app and terminal tool goes quiet at once",
 "how": "<strong>Turns off the Mac's network connections</strong> using built-in macOS tools",
 "ext": "<strong>None.</strong> Works in every browser and never sees what sites you visit",
 "apps": "<strong>All offline automatically.</strong> Apps stay open, so you can read old messages, with zero new pings",
 "net": "<strong>Clean.</strong> Never touches proxies, /etc/hosts or DNS, and restores your exact pre-session state",
 "local": "<strong>Always work</strong> (loopback stays up; local containers work via localhost ports)",
 "lists": "<strong>None</strong>",
 "quit": "<strong>Nothing changes.</strong> A system helper holds the timer across quit and restart",
 "emerg": "<strong>Built-in 15-minute cooldown</strong>: stops impulses, but never traps you in a real emergency",
 "acct": "<strong>No.</strong> 100% local on your Mac",
 "price": "<strong>$9.99 once</strong> (3 free sessions)",
 "runs": "<strong>Mac only</strong> (macOS 26 or later, Apple Silicon)",
}

# ================================================================ 1. Pillar guide
pillar_body = f'''  <h2>The quick answer</h2>
  <ul>
    <li><strong>For a quick break:</strong> turn off Wi-Fi in Control Center. It's instant, and it's one click to undo.</li>
    <li><strong>For a block that holds:</strong> use an app that takes your whole Mac offline on a timer and doesn't let you cancel on impulse. Vow does this for anywhere from 5 minutes to 24 hours, and quitting the app or restarting your Mac won't bring the internet back.</li>
  </ul>

  <h2>Built-in ways to turn off the internet on a Mac</h2>
  <p>macOS has no "go offline until 5 pm" switch, but you can get part of the way with what's already on your Mac.</p>

  <h3>1. Turn off Wi-Fi</h3>
  <p>Click the Wi-Fi icon in the menu bar or Control Center and switch it off, or go to System Settings &rsaquo; Wi-Fi. It's free and instant. The catch: it's one click to turn back on, there's no timer, and it only stops Wi-Fi. An Ethernet cable, a USB network adapter or an iPhone connected by USB can still get you online.</p>

  <h3>2. Use Terminal</h3>
  <p>If you're comfortable with the command line, <code>networksetup -setairportpower en0 off</code> turns Wi-Fi off, and the same command with <code>on</code> turns it back on. Wi-Fi is usually <code>en0</code> on a Mac laptop; run <code>networksetup -listallhardwareports</code> to check yours. It has the same weakness as the Wi-Fi switch: one command undoes it, and nothing turns it back on for you.</p>

  <h3>3. Screen Time</h3>
  <p>Screen Time (System Settings &rsaquo; Screen Time) can limit apps with Downtime and App Limits, and its Apps &amp; Websites settings can restrict websites. It was designed for parents managing a child's Mac. When you set the passcode yourself, you can switch it off in seconds, and it limits apps and sites by list rather than turning off the network.</p>

  <h3>4. Focus modes</h3>
  <p>Focus modes silence notifications, but your internet stays on. They're a good companion to a block, not a block.</p>

  <h3>5. Your router</h3>
  <p>Many routers can pause the internet on a schedule. That's hard to undo from your Mac, but it affects everyone at home, and an iPhone hotspot gets around it immediately.</p>

  <h2>Why most blocks don't hold</h2>
  <p>Block YouTube, and you open Netflix. Block WhatsApp, and you move to Telegram. Close Safari, and you open Chrome. Lists of blocked sites invite you to find the gap, and a block you can undo in one click is only as strong as your willpower in that moment.</p>
  <p>A block that actually holds needs three things:</p>
  <ol>
    <li><strong>It covers every connection:</strong> Wi-Fi, Ethernet, USB adapters and hotspots, for every app and browser.</li>
    <li><strong>It can't be cancelled on impulse,</strong> but it still has a way out for a real emergency.</li>
    <li><strong>It survives you quitting the app or restarting your Mac.</strong></li>
  </ol>

  <h2>How to block the internet on a Mac with Vow</h2>
  <p>Vow is a Mac app built around those three rules. Here's a session from start to finish.</p>

  <h3>Step 1: Choose how long</h3>
  <p>Pick a duration from 5 minutes to 24 hours. There are presets for 15 minutes, 30 minutes, 1 hour and 2 hours, or choose Custom. Vow shows exactly when you'll be back online.</p>
{fig("vow-duration-picker.jpg", "Vow's main window: Go offline for 1 hr, back online at 16:29, with 15 min, 30 min, 1 hr, 2 hr and Custom presets.")}

  <h3>Step 2: Confirm, and go offline</h3>
  <p>Press Go Offline. Vow explains the one rule before it starts: there's no instant cancel. Then it turns off every network connection on your Mac.</p>

  <h3>Step 3: Stay offline</h3>
  <p>A countdown shows the time left. Closing the window doesn't end the session, and neither does quitting Vow or restarting your Mac. A small background helper keeps the timer running silently.</p>
{fig("vow-offline-countdown.jpg", "An active Vow session: Offline, 4:50 left, back online at 15:37. Closing this window does not end the session.")}

  <h3>Step 4: Back online, automatically</h3>
  <p>When the timer ends, your internet comes back on its own, exactly as it was before.</p>

  <h3>If you really need to get online early</h3>
  <p>Life happens. You can request an early unlock, and your Mac stays offline for 15 more minutes first. You can cancel the request during those 15 minutes, which is usually all it takes for the urge to pass.</p>
{fig("vow-how-it-works-steps.jpg", "How Vow works: choose a duration from 5 minutes to 24 hours, no instant cancel, early unlock after 15 more minutes, automatic return.")}

  <h3>Schedule it</h3>
  <p>To go offline at the same time every day, add a schedule, such as Monday to Friday at 18:00 for 1 hour. If your Mac is asleep when a schedule starts and wakes within a minute, the full session runs. If it wakes later, Vow runs the remaining time, as long as at least 15 minutes are left.</p>
{fig("vow-new-weekday-schedule.jpg", "Vow's New Schedule form: repeat Monday to Friday, start 18:00, duration 1 hour, back online at 19:00.")}

  <h2>What still works while you're offline</h2>
  <ul>
    <li><strong>Your files and apps.</strong> Write, design, read, code.</li>
    <li><strong>Messaging apps stay open,</strong> so you can read old messages. Nothing new comes in.</li>
    <li><strong>Local AI models</strong> and tools like Ollama.</li>
    <li><strong>localhost and local dev servers.</strong> The loopback interface stays up, and local containers work through localhost ports.</li>
    <li><strong>Bluetooth.</strong> AirPods, wireless mice and keyboards, and Apple Watch keep working.</li>
  </ul>

  <h2>Which option should you use?</h2>
{table("Ways to turn off the internet on a Mac, compared", ["Method", "Covers every connection", "Timer", "How easy to undo"], [
    ["Wi-Fi switch", "No, Wi-Fi only", "No", "One click"],
    ["Terminal", "No, one interface per command", "No", "One command"],
    ["Screen Time", "No, limits apps and sites by list", "Downtime schedules", "Your own passcode"],
    ["Router schedule", "Everyone on your home network", "Depends on the router", "An iPhone hotspot gets around it"],
    ["Vow", "<strong>Yes</strong>: Wi-Fi, Ethernet, USB adapters, hotspots", "<strong>5 minutes to 24 hours</strong>, plus schedules", "<strong>No instant cancel</strong>; early unlock after 15 minutes"],
])}
  <p>For a short break, the Wi-Fi switch is fine. For focused work, an evening off, or getting through a bad habit, you want something that holds when your willpower doesn't.</p>'''

pillar_faqs = [
    ("Can I turn off the internet on my Mac without turning off Bluetooth?",
     ["Yes. Wi-Fi and Bluetooth are separate, so turning off Wi-Fi leaves Bluetooth on. Vow also leaves Bluetooth alone, so your AirPods, mouse, keyboard and Apple Watch keep working during a session."]),
    ("Does turning off Wi-Fi also block Ethernet or an iPhone hotspot?",
     ["No. Turning off Wi-Fi only stops Wi-Fi. A plugged-in Ethernet cable, a USB network adapter or an iPhone connected by USB can still get you online. Vow turns off all of them."]),
    ("Can I schedule my Mac's internet to turn off at night?",
     ["macOS has no built-in way to turn off the network at a set time. Screen Time's Downtime limits apps, but it doesn't take your Mac offline. With Vow, you can add a schedule, such as every weekday at 21:00 for 2 hours, and the session starts on its own."]),
    ("Will localhost and local AI models still work while I'm offline?",
     ["Yes, with Vow. The loopback interface stays up, so localhost, local dev servers, local containers via localhost ports, and local AI models such as Ollama keep working."]),
]

page("block-internet-on-mac",
     "How to Block the Internet on a Mac for a Set Time",
     "Every way to turn off the internet on a Mac: Wi-Fi, Terminal, Screen Time, routers and apps, plus how to make a block hold until the timer ends.",
     "How to block the internet on your Mac for a set time",
     "Block the internet on a Mac",
     "The quickest way is to turn off Wi-Fi, but it takes one click to undo. For a block that holds, you need something that turns off every connection and keeps it off until a timer ends, even if you quit apps or restart. This guide covers the built-in macOS options first, then how Vow does it.",
     pillar_body, pillar_faqs)

# ================================================================ 2. Freedom
fr_rows = [
 ["What it stops", VOW["stops"], "Sites and apps on your lists (or all websites)"],
 ["How it works", VOW["how"], "Local system proxy (or Non-Proxy browser filter) + app blocker"],
 ["Browser extensions", VOW["ext"], "Optional (Non-Proxy mode hides Firefox on Mac)"],
 ["Non-browser apps (Discord, Telegram, WhatsApp, Mail)", VOW["apps"], "Website blocks only filter proxy traffic; stopping an app closes/hides the app window"],
 ["Network settings &amp; VPNs", VOW["net"], "Modifies macOS system proxies by default (can conflict with work and commercial VPNs)"],
 ["Localhost and dev tools", VOW["local"], "Can conflict with the local proxy (needs localhost / 127.0.0.1 proxy bypass rules)"],
 ["Lists to keep up to date", VOW["lists"], "Yes (websites, apps and exceptions)"],
 ["If you quit the app", VOW["quit"], "Requires Locked Mode (Premium) + \"Block Activity Monitor\" enabled"],
 ["If an emergency happens", VOW["emerg"], "Instant cancel in standard mode, or locked until the timer ends in Locked Mode"],
 ["Account needed", VOW["acct"], "Yes (syncs with a cloud dashboard)"],
 ["Price", VOW["price"], "$8.99/mo, $39.99/yr, or $99.50 lifetime"],
 ["Runs on", VOW["runs"], "Mac, Windows, iPhone, iPad, Android, ChromeOS"],
]
fr_body = f'''  <h2>The short verdict</h2>
  <h3>Choose Freedom if…</h3>
  <ul>
    <li>You want one block across your Mac, Windows PC, iPhone, iPad, Android or Chromebook.</li>
    <li>You want to block specific sites and apps and keep the rest of the internet.</li>
    <li>You like managing sessions from a cloud dashboard.</li>
  </ul>
  <h3>Choose Vow if…</h3>
  <ul>
    <li>You want everything quiet, including Discord, Slack, Telegram, WhatsApp and Mail, without building lists.</li>
    <li>You use a work or commercial VPN, or rely on localhost and local dev tools.</li>
    <li>You'd rather pay once than subscribe, and you don't want an account.</li>
  </ul>

  <h2>Vow vs Freedom, side by side</h2>
{table("Vow vs Freedom on Mac (compared November 2026 from each app's public pages)", ["", "Vow", "Freedom"], fr_rows)}

  <h2>How blocking works differently</h2>
  <p>Freedom blocks what's on your lists. On a Mac it routes web traffic through a local system proxy (or a Non-Proxy browser filter) and adds an app blocker. That's flexible: you can block social media and keep everything else. But a system proxy can conflict with work and commercial VPNs, and local development servers need proxy bypass rules for localhost and 127.0.0.1.</p>
  <p>Vow doesn't filter anything. It turns off your Mac's network connections using built-in macOS tools, so every browser, app and terminal tool goes offline at once. There are no lists to maintain and no proxy to conflict with your VPN. localhost keeps working because the loopback interface stays up.</p>

  <h2>Staying locked</h2>
  <p>In Freedom's standard mode, you can cancel a session instantly. Locked Mode, part of Freedom Premium, keeps a session running until the timer ends. Stopping Freedom from being quit requires Locked Mode together with its "Block Activity Monitor" option.</p>
  <p>Vow has no instant cancel. You can request an early unlock, and your Mac stays offline for 15 more minutes first. A system helper holds the timer, so quitting Vow or restarting your Mac changes nothing.</p>
{fig("vow-offline-countdown.jpg", "An active Vow session: Offline, 4:50 left, back online at 15:37. Closing this window does not end the session.")}

  <h2>Price over time</h2>
{table("What Vow and Freedom cost over time (Freedom's published prices, November 2026)", ["", "Vow", "Freedom"], [
    ["1 year", "<strong>$9.99 once</strong>", "$39.99 yearly, or $107.88 monthly"],
    ["3 years", "<strong>$9.99 once</strong> (all 1.x updates included)", "$119.97 yearly, or $99.50 lifetime"],
    ["Devices", "Up to 2 personal Macs", "Mac, Windows, iPhone, iPad, Android, ChromeOS"],
])}
  <p>Freedom covers more devices, which is worth paying for if you need it. If you only need your Mac to go quiet, Vow costs less than three months of Freedom's monthly plan.</p>

  <h2>Switching from Freedom to Vow</h2>
  <ul>
    <li><strong>You don't need to rebuild your lists.</strong> Vow has none: the whole internet goes off.</li>
    <li><strong>Recreate recurring sessions as Vow schedules,</strong> for example weekdays at 9:00 for 2 hours.</li>
    <li><strong>Start with a short session</strong>, say 30 minutes, to see how working fully offline feels. You get 3 full sessions free.</li>
    <li><strong>Keep Freedom for your other devices</strong> if you use it on your phone. The two don't need to replace each other.</li>
  </ul>'''
fr_faqs = [
    ("Is Vow cheaper than Freedom?",
     ["Yes, for a Mac. Vow is $9.99 once with all 1.x updates included, for up to 2 personal Macs. Freedom is $8.99 a month, $39.99 a year, or $99.50 for lifetime, and it covers more types of devices."]),
    ("Can Vow block only certain websites, like Freedom?",
     ["No. Vow turns off your Mac's whole internet connection, so there are no lists. If you want to block some sites and keep the rest, Freedom or Cold Turkey is the better fit."]),
    ("Does Vow work on iPhone or Windows?",
     ["No. Vow is a Mac app and requires macOS 26 or later on Apple Silicon."]),
    ("Will Vow conflict with my VPN the way a proxy can?",
     ["No. Vow never touches proxies, /etc/hosts or DNS settings. During a session your VPN is offline along with everything else, and when the session ends your network is restored exactly as it was."]),
]
page("freedom-alternative",
     "Freedom Alternative for Mac: Vow vs Freedom",
     "Vow vs Freedom on Mac: whole-internet block vs blocklists, VPN and proxy behaviour, localhost, price over time, and when Freedom is the better pick.",
     "Vow vs Freedom: a one-time-purchase Freedom alternative for Mac",
     "Freedom alternative",
     "Freedom blocks the websites and apps on your lists and syncs across your devices. Vow turns off your Mac's whole internet connection until a timer ends, with nothing to set up. Pick Freedom to block some sites on several devices. Pick Vow to take your Mac fully offline for a while, for $9.99 once.",
     fr_body, fr_faqs)

# ================================================================ 3. Cold Turkey
ct_rows = [
 ["What it stops", VOW["stops"], "Sites and apps on your lists (or all websites via *.*)"],
 ["How it works", VOW["how"], "Browser extensions check every URL + a background agent quits blocked apps"],
 ["Browser extensions", VOW["ext"], "Required for website blocking (quits browsers without it; logs site stats by default)"],
 ["Non-browser apps (Discord, Telegram, WhatsApp, Mail)", VOW["apps"], "Website blocks (*.*) only work in browsers; stopping an app requires Pro and force-quits the app"],
 ["Network settings &amp; VPNs", VOW["net"], "Does not modify system proxies or VPN settings"],
 ["Localhost and dev tools", VOW["local"], "Needs manual Website Exceptions for localhost when blocking all sites (*.*)"],
 ["Lists to keep up to date", VOW["lists"], "Yes (websites, apps, exceptions and extensions)"],
 ["If you quit the app", VOW["quit"], "Background agent respawns automatically; extensions close browsers if stopped"],
 ["If an emergency happens", VOW["emerg"], "Configurable breaks/delays in Pro, or locked until the timer ends"],
 ["Account needed", VOW["acct"], "No (stored locally)"],
 ["Price", VOW["price"], "$45 once for Pro (free version is websites only)"],
 ["Runs on", VOW["runs"], "Mac and Windows"],
]
ct_body = f'''  <h2>The short verdict</h2>
  <h3>Choose Cold Turkey if…</h3>
  <ul>
    <li>You also use Windows and want the same blocker on both.</li>
    <li>You want fine control: specific sites and apps, exceptions, scheduled breaks and allowances.</li>
    <li>You only need website blocking, which Cold Turkey's free version covers.</li>
  </ul>
  <h3>Choose Vow if…</h3>
  <ul>
    <li>You want every app offline, not only browsers, without apps being force-quit.</li>
    <li>You don't want browser extensions that see every URL you visit.</li>
    <li>You'd rather not maintain lists of sites, apps and exceptions.</li>
    <li>You want a lower one-time price: $9.99 instead of $45.</li>
  </ul>

  <h2>Vow vs Cold Turkey, side by side</h2>
{table("Vow vs Cold Turkey on Mac (compared November 2026 from each app's public pages)", ["", "Vow", "Cold Turkey"], ct_rows)}

  <h2>How blocking works differently</h2>
  <p>Cold Turkey is a detailed blocker. Browser extensions check every URL against your lists, and a background agent quits apps you've blocked. Even its block-everything mode (*.*) only applies inside browsers. Messaging apps like Discord or Mail are stopped by force-quitting them, which requires Pro.</p>
  <p>Vow works one level lower. It turns off your Mac's network connections using built-in macOS tools, so every app and browser loses its connection at once, and no extension is involved. Your apps stay open, so you can still read old messages and finish a draft offline. Nothing new comes in until the session ends.</p>
{fig("vow-how-it-works-steps.jpg", "How Vow works: choose a duration from 5 minutes to 24 hours, no instant cancel, early unlock after 15 more minutes, automatic return.")}

  <h2>Staying locked</h2>
  <p>Cold Turkey is hard to get around: its background agent respawns if you quit it, and its extensions close browsers if they're disabled. With Pro you can set breaks and delays, or lock a block until it ends.</p>
  <p>Vow is just as hard to undo, with one deliberate exception. A system helper holds the timer across quit and restart, and there's no cancel button. If you have a real emergency, you can request an early unlock: your Mac stays offline for 15 more minutes first, and then the internet comes back. You're never trapped.</p>

  <h2>Price</h2>
  <p>Cold Turkey's free version blocks websites. Pro, which adds app blocking and more, is $45 once. Vow is $9.99 once for up to 2 personal Macs, with all 1.x updates included and 3 free sessions to try it first.</p>

  <h2>Switching from Cold Turkey to Vow</h2>
  <ul>
    <li><strong>No lists to move.</strong> Vow takes the whole Mac offline.</li>
    <li><strong>No extensions to install</strong> in Safari, Chrome, Firefox or any other browser.</li>
    <li><strong>Recreate scheduled blocks as Vow schedules,</strong> such as Monday to Friday at 18:00 for 1 hour.</li>
    <li><strong>Developers:</strong> you don't need localhost exceptions. Loopback stays up during a session.</li>
  </ul>'''
ct_faqs = [
    ("Is Vow a good Cold Turkey alternative for Mac?",
     ["Yes, if you want your whole Mac offline rather than a list of sites and apps blocked. Vow turns off every network connection until your timer ends, without browser extensions, and costs $9.99 once instead of $45 for Cold Turkey Pro."]),
    ("Does Vow need browser extensions like Cold Turkey?",
     ["No. Vow turns off your Mac's network connections, so it works in every browser automatically and never sees which sites you visit."]),
    ("Does Vow force-quit my apps?",
     ["No. Your apps stay open during a session, so you can read old messages and keep working offline. They just can't connect to the internet until the timer ends."]),
    ("Can Vow block just some websites?",
     ["No. Vow blocks the whole internet. If you want to block specific sites and keep the rest, Cold Turkey or Freedom is the better choice."]),
]
page("cold-turkey-alternative",
     "Cold Turkey Alternative for Mac: Vow vs Cold Turkey",
     "Vow vs Cold Turkey on Mac: whole-internet block vs extensions and lists, how apps are handled, localhost, price, and when Cold Turkey is the better pick.",
     "Vow vs Cold Turkey: a simpler Cold Turkey alternative for Mac",
     "Cold Turkey alternative",
     "Cold Turkey blocks the sites and apps on your lists, using browser extensions and a background agent, on Mac and Windows. Vow turns off your Mac's whole internet connection until a timer ends, with no extensions and nothing to set up. Pick Cold Turkey for detailed control. Pick Vow for total quiet, for $9.99 once.",
     ct_body, ct_faqs)

# ================================================================ 4. SelfControl
sc_rows = [
 ["Price", VOW["price"], "<strong>Free</strong>"],
 ["Source code", "Not open source; signed with an Apple Developer ID and notarized by Apple", "<strong>Open source</strong> (GNU GPL)"],
 ["What it blocks", VOW["stops"], "The websites on your blocklist"],
 ["Lists to keep up to date", VOW["lists"], "Yes (your blocklist)"],
 ["Ending a session early", "Request an early unlock; your Mac stays offline 15 more minutes first", "Not possible: blocked until the timer expires"],
 ["Restart or delete the app", "The session continues", "The block continues, even if you restart or delete the app"],
 ["Schedules", "Built in (for example, weekdays at 9:00)", "Not listed on its website"],
 ["Requirements", "macOS 26 or later, Apple Silicon", "Version 4.0.2 requires Mac OS X 10.10 or later"],
]
sc_body = f'''  <h2>The short verdict</h2>
  <h3>Choose SelfControl if…</h3>
  <ul>
    <li>You want a free, open-source tool.</li>
    <li>You want to block a specific list of websites and keep the rest of the internet.</li>
    <li>You want no way out at all until the timer ends.</li>
    <li>You have an older Mac. SelfControl runs on much older versions of macOS than Vow.</li>
  </ul>
  <h3>Choose Vow if…</h3>
  <ul>
    <li>You want the whole internet off, including messaging apps and anything not on a list.</li>
    <li>You'd rather not maintain a blocklist.</li>
    <li>You want built-in schedules.</li>
    <li>You want a safety valve for real emergencies: an early unlock after 15 more minutes offline.</li>
  </ul>

  <h2>Vow vs SelfControl, side by side</h2>
{table("Vow vs SelfControl (compared November 2026; SelfControl details from selfcontrolapp.com)", ["", "Vow", "SelfControl"], sc_rows)}

  <h2>Blocklist or the whole internet?</h2>
  <p>SelfControl blocks the websites you add to its blocklist for a period you set. Until the timer expires, you can't reach those sites, even if you restart your computer or delete the app. It's free, open source, and has helped a lot of people.</p>
  <p>A blocklist only covers what you thought to put on it. Vow doesn't use one: it turns off your Mac's network connections entirely, so there's no next site to drift to. Your files, apps, localhost and local AI models keep working offline.</p>
{fig("vow-duration-picker.jpg", "Vow's main window: Go offline for 1 hr, back online at 16:29, with 15 min, 30 min, 1 hr, 2 hr and Custom presets.")}

  <h2>Strict, or strict with a safety valve?</h2>
  <p>SelfControl is uncompromising: once a block starts, it runs until the timer ends. Some people want exactly that.</p>
  <p>Vow is strict by default, with one way out. There's no cancel button, and quitting or restarting changes nothing. But if something real comes up, you can request an early unlock. Your Mac stays offline for 15 more minutes, and you can change your mind during that time. That's usually long enough for an impulse to pass, while a genuine emergency still gets you online.</p>

  <h2>Price and requirements</h2>
  <p>SelfControl is free. Vow is $9.99 once for up to 2 personal Macs, with all 1.x updates included and 3 free sessions to try first. Vow requires macOS 26 or later on Apple Silicon. If your Mac is older, SelfControl is the practical choice.</p>'''
sc_faqs = [
    ("Is SelfControl free?",
     ["Yes. SelfControl is a free, open-source Mac app licensed under the GNU GPL. Vow is a paid app: $9.99 once, with 3 free sessions to try it."]),
    ("What's the main difference between Vow and SelfControl?",
     ["SelfControl blocks the websites on your blocklist. Vow turns off your Mac's whole internet connection, so every app and browser goes offline and there's no list to maintain."]),
    ("Can I end a session early?",
     ["Not in SelfControl: a block lasts until its timer expires. In Vow, you can request an early unlock, and your Mac stays offline for 15 more minutes before the internet comes back."]),
    ("Does Vow work on older Macs like SelfControl does?",
     ["No. Vow requires macOS 26 or later on a Mac with Apple Silicon. SelfControl supports much older versions of macOS."]),
]
page("selfcontrol-alternative",
     "SelfControl Alternative for Mac: Vow vs SelfControl",
     "Vow vs SelfControl: blocking the whole internet vs a website blocklist, early unlock, schedules and requirements. SelfControl is free and open source.",
     "Vow vs SelfControl: blocking the whole internet instead of a list",
     "SelfControl alternative",
     "SelfControl is a free, open-source Mac app that blocks the websites on your blocklist until a timer runs out. Vow turns off your Mac's whole internet connection instead, with built-in schedules and an emergency early unlock. Pick SelfControl for a free website blocker. Pick Vow to take your Mac fully offline.",
     sc_body, sc_faqs)

# ================================================================ 5. Changelog
cl_body = '''  <p>Vow checks for updates about once a day and verifies each update with a cryptographic signature before it installs. Update checks never happen while a session is running.</p>

  <div class="changelog">
    <div class="release" id="1-0-14">
      <h2>Vow 1.0.14</h2>
      <p class="release-date"><time datetime="2026-11">November 2026</time></p>
      <ul>
        <li>Smoother license key entry during the free trial.</li>
        <li>Refreshed interface polish.</li>
      </ul>
    </div>
    <div class="release" id="1-0-13">
      <h2>Vow 1.0.13</h2>
      <p class="release-date"><time datetime="2026-11">November 2026</time></p>
      <ul>
        <li>Automatic checkout in your local currency, with UPI support in India.</li>
        <li>Faster background updates.</li>
      </ul>
    </div>
    <div class="release" id="1-0-12">
      <h2>Vow 1.0.12</h2>
      <p class="release-date"><time datetime="2026-11">November 2026</time></p>
      <ul>
        <li>Scheduled deep-work sessions.</li>
        <li>Custom lock durations.</li>
      </ul>
    </div>
  </div>
  <p>Vow 1.0.12 was the first public release. Earlier versions were internal development builds.</p>'''
page("changelog",
     "Vow Changelog: What's New in Vow for Mac",
     "Release notes for Vow, the Mac app that turns off your internet until a timer ends. See what changed in each version, newest first.",
     "What's new in Vow",
     "Changelog",
     "Release notes for Vow, the Mac app that turns off your internet until your timer ends. The newest version is first. Every 1.x update is free for license holders.",
     cl_body, None)
