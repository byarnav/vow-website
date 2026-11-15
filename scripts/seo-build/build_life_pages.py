#!/usr/bin/env python3
"""Generate Vow's newer guide pages (ADHD, block websites, adult sites, free blockers, focus, social media addiction, research).

Usage: python3 -I build_life_pages.py ~/Developer/Apps/Mac/Vow/website
Writes only the pages defined here. (build.py is older; the other pages have been hand-edited since,
so don't re-run build.py over the site.) The footer here must match FOOTER in the website pages.
"""
import html, json, sys, os

ROOT = sys.argv[1]
BASE = "https://vow.byarnav.com"
CSS_V = "14"
DMG = "https://raw.githubusercontent.com/byarnav/offline-lock-releases/main/Vow.dmg"
ORG = {"@type": "Organization", "@id": BASE + "/#org", "name": "byArnav", "url": "https://byarnav.com"}

FOOTER = '''<footer class="foot">
  <div class="foot-inner">
    <nav class="foot-cols" aria-label="Footer">
      <div>
        <p class="foot-h">Guides</p>
        <ul>
          <li><a href="/block-internet-on-mac/">Block the internet on a Mac</a></li>
          <li><a href="/block-websites-on-mac/">Block websites on a Mac</a></li>
          <li><a href="/block-adult-sites-on-mac/">Block adult sites on a Mac</a></li>
          <li><a href="/free-internet-blocker-mac/">Free internet blockers for Mac</a></li>
          <li><a href="/stay-focused-on-mac/">Stay focused on a Mac</a></li>
        </ul>
      </div>
      <div>
        <p class="foot-h">Habits &amp; focus</p>
        <ul>
          <li><a href="/social-media-addiction/">Social media addiction</a></li>
          <li><a href="/adhd-focus-mac/">ADHD focus on a Mac</a></li>
          <li><a href="/research/">What the research says</a></li>
        </ul>
      </div>
      <div>
        <p class="foot-h">Vow</p>
        <ul>
          <li><a href="/#pricing">Pricing</a></li>
          <li><a href="/#faq">FAQ</a></li>
          <li><a href="/changelog/">Changelog</a></li>
          <li><a href="https://raw.githubusercontent.com/byarnav/offline-lock-releases/main/Vow.dmg">Download free</a></li>
          <li><a href="/freedom-alternative/">Vow vs Freedom</a></li>
          <li><a href="/cold-turkey-alternative/">Vow vs Cold Turkey</a></li>
          <li><a href="/selfcontrol-alternative/">Vow vs SelfControl</a></li>
        </ul>
      </div>
      <div>
        <p class="foot-h">Help</p>
        <ul>
          <li><a href="/activation.html">Manage activation</a></li>
          <li>{LOST_KEY}</li>
          <li><a href="/refunds.html">Refunds</a></li>
          <li><a href="/privacy.html">Privacy</a></li>
          <li><a href="/terms.html">Terms</a></li>
          <li><a href="mailto:support@byarnav.com">support@byarnav.com</a></li>
        </ul>
      </div>
    </nav>
    <p class="foot-legal">Signed with an Apple Developer ID and notarized by Apple. No analytics. &copy; 2026 <a href="https://byarnav.com">byArnav</a></p>
  </div>
</footer>'''
LOST_KEY_LINK = '<a href="/#lost-key">Lost your key?</a>'
LOST_KEY_BUTTON = '<button type="button" class="link-btn" data-open-lost-key>Lost your key?</button>'


def strip_tags(s):
    out, inside = [], False
    for ch in s:
        if ch == "<": inside = True
        elif ch == ">": inside = False
        elif not inside: out.append(ch)
    return " ".join(html.unescape("".join(out)).split())


def faq_block(faqs):
    items = ""
    for q, ps in faqs:
        items += "    <details>\n      <summary>" + q + "</summary>\n" + "".join(f"      <p>{p}</p>\n" for p in ps) + "    </details>\n"
    return f'''  <h2 id="faq">Questions</h2>
  <div class="faq">
{items}  </div>'''


def sources_block(srcs):
    lis = "".join(f"    <li id=\"src-{i}\">{s}</li>\n" for i, s in enumerate(srcs, 1))
    return f'''  <h2 id="sources">Sources</h2>
  <ol class="sources">
{lis}  </ol>'''


def cite(n):
    return f'<sup class="cite"><a href="#src-{n}" aria-label="Source {n}">[{n}]</a></sup>'


CTA = f'''  <div class="article-cta">
    <h2>Try Vow free</h2>
    <p>Vow is a Mac app that turns off your internet and keeps it off until your timer ends, from 5 minutes to 24 hours. Try 3 full sessions free, then pay $9.99 once. Requires macOS 26 or later on Apple Silicon.</p>
    <div class="actions">
      <a class="btn primary" href="/#pricing">Buy Vow &middot; $9.99</a>
      <a class="btn secondary" href="{DMG}">Try 3 sessions free</a>
    </div>
  </div>'''


def page(slug, title, desc, h1, crumb, summary, body, faqs, sources, iso, human):
    url = f"{BASE}/{slug}/"
    assert len(html.unescape(title)) <= 60, (slug, len(html.unescape(title)))
    assert len(html.unescape(desc)) <= 155, (slug, len(html.unescape(desc)))
    graph = [
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Vow", "item": BASE + "/"},
            {"@type": "ListItem", "position": 2, "name": crumb, "item": url}]},
        {"@type": "Article", "@id": url + "#article", "headline": strip_tags(h1), "description": html.unescape(desc),
         "datePublished": iso, "dateModified": iso, "inLanguage": "en",
         "author": ORG, "publisher": ORG, "image": BASE + "/images/og-image.jpg",
         "mainEntityOfPage": url, "about": {"@id": BASE + "/#app"},
         "citation": [strip_tags(s) for s in sources]},
    ]
    if faqs:
        graph.append({"@type": "FAQPage", "@id": url + "#faq", "mainEntity": [
            {"@type": "Question", "name": strip_tags(q),
             "acceptedAnswer": {"@type": "Answer", "text": " ".join(strip_tags(p) for p in ps)}} for q, ps in faqs]})
    ld = json.dumps({"@context": "https://schema.org", "@graph": graph}, indent=2, ensure_ascii=False).replace("</", "<\\/")
    doc = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="color-scheme" content="light dark">
<link rel="canonical" href="{url}">
<meta name="theme-color" content="#ffffff" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#000000" media="(prefers-color-scheme: dark)">
<meta property="og:type" content="article">
<meta property="og:site_name" content="Vow">
<meta property="og:url" content="{url}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
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
  <p class="updated">Last updated: <time datetime="{iso}">{human}</time></p>
  <p class="summary">{summary}</p>

{body}
{faq_block(faqs) if faqs else ''}
{CTA}
{sources_block(sources)}
</article>
</main>

{FOOTER.replace("{LOST_KEY}", LOST_KEY_LINK)}
</body>
</html>
'''
    os.makedirs(f"{ROOT}/{slug}", exist_ok=True)
    with open(f"{ROOT}/{slug}/index.html", "w", encoding="utf-8") as f:
        f.write(doc)
    print(f"wrote /{slug}/  title={len(html.unescape(title))}  desc={len(html.unescape(desc))}  faqs={len(faqs or [])}  sources={len(sources)}")


ISO, HUMAN = "2026-11-14", "November 14, 2026"

# Shared, verified sources (checked 2026-11-14; every DOI resolves).
S_CASTELO = 'Castelo, N., Kushlev, K., Ward, A. F., Esterman, M., &amp; Reiner, P. B. (2025). Blocking mobile internet on smartphones improves sustained attention, mental health, and subjective well-being. <em>PNAS Nexus</em>, 4(2), pgaf017. <a href="https://doi.org/10.1093/pnasnexus/pgaf017">doi.org/10.1093/pnasnexus/pgaf017</a>'
S_WARD = 'Ward, A. F., Duke, K., Gneezy, A., &amp; Bos, M. W. (2017). Brain drain: The mere presence of one&rsquo;s own smartphone reduces available cognitive capacity. <em>Journal of the Association for Consumer Research</em>, 2(2), 140&ndash;154. <a href="https://doi.org/10.1086/691462">doi.org/10.1086/691462</a>'
S_MARK = 'Mark, G. (2023). <em>Attention Span: A Groundbreaking Way to Restore Balance, Happiness and Productivity</em>. Hanover Square Press. Summary in: University of California, &ldquo;How to sharpen your attention and meet your goals in 2024&rdquo;. <a href="https://www.universityofcalifornia.edu/news/how-sharpen-your-attention-and-meet-your-goals-2024">universityofcalifornia.edu</a>'
S_RA = 'Ra, C. K., Cho, J., Stone, M. D., et al. (2018). Association of digital media use with subsequent symptoms of attention-deficit/hyperactivity disorder among adolescents. <em>JAMA</em>, 320(3), 255&ndash;263. <a href="https://doi.org/10.1001/jama.2018.8931">doi.org/10.1001/jama.2018.8931</a>'
S_BARKLEY = 'Barkley, R. A., with Benton, C. M. (2021). <em>Taking Charge of Adult ADHD</em> (2nd ed.). Guilford Press. <a href="https://www.guilford.com/books/Taking-Charge-of-Adult-ADHD/Russell-Barkley/9781462546855">guilford.com</a>'
S_HUNT = 'Hunt, M. G., Marx, R., Lipson, C., &amp; Young, J. (2018). No more FOMO: Limiting social media decreases loneliness and depression. <em>Journal of Social and Clinical Psychology</em>, 37(10), 751&ndash;768. <a href="https://doi.org/10.1521/jscp.2018.37.10.751">doi.org/10.1521/jscp.2018.37.10.751</a>'
S_ALLCOTT = 'Allcott, H., Braghieri, L., Eichmeyer, S., &amp; Gentzkow, M. (2020). The welfare effects of social media. <em>American Economic Review</em>, 110(3), 629&ndash;676. <a href="https://doi.org/10.1257/aer.20190658">doi.org/10.1257/aer.20190658</a>'
S_SATICI = 'Satici, S. A., Gocet Tekin, E., Deniz, M. E., &amp; Satici, B. (2023). Doomscrolling scale: Its association with personality traits, psychological distress, social media use, and wellbeing. <em>Applied Research in Quality of Life</em>, 18(2), 833&ndash;847. <a href="https://doi.org/10.1007/s11482-022-10110-7">doi.org/10.1007/s11482-022-10110-7</a>'
S_SANA = 'Sana, F., Weston, T., &amp; Cepeda, N. J. (2013). Laptop multitasking hinders classroom learning for both users and nearby peers. <em>Computers &amp; Education</em>, 62, 24&ndash;31. <a href="https://doi.org/10.1016/j.compedu.2012.10.003">doi.org/10.1016/j.compedu.2012.10.003</a>'
S_WHO = 'World Health Organization. &ldquo;Gaming disorder&rdquo; (questions and answers on ICD-11). <a href="https://www.who.int/standards/classifications/frequently-asked-questions/gaming-disorder">who.int</a>'
S_NCPG = 'National Council on Problem Gambling, National Problem Gambling Helpline (US). <a href="https://ncpgambling.org/help-treatment/national-helpline-1-800-522-4700/">ncpgambling.org</a>'
S_GAMCARE = 'GamCare, National Gambling Helpline (UK). <a href="https://www.gamcare.org.uk/get-support/talk-to-us-now/">gamcare.org.uk</a>'
S_TELEMANAS = 'Ministry of Health and Family Welfare, Government of India, Tele MANAS. <a href="https://telemanas.mohfw.gov.in/">telemanas.mohfw.gov.in</a>'

# ================================================================ /adhd-focus-mac/
adhd_src = [S_BARKLEY, S_WARD, S_MARK, S_RA, S_CASTELO]
c = {s: i for i, s in enumerate(adhd_src, 1)}
adhd_body = f'''  <h2>Why &ldquo;just don&rsquo;t open YouTube&rdquo; doesn&rsquo;t work</h2>
  <p>With ADHD, the problem usually isn&rsquo;t knowing what to do. It&rsquo;s doing it at the moment it counts. ADHD researcher Russell Barkley describes ADHD as a problem of doing what you know, not of knowing what to do. His advice is to put help at the &ldquo;point of performance&rdquo;: the place and moment where the work happens.{cite(c[S_BARKLEY])}</p>
  <p>A browser is the opposite of that. The next video, thread or headline is always one click away, and every click is a new choice to resist. Resisting has a cost too. In one well-known study, just having your own phone on the desk, even switched off and face down, lowered people&rsquo;s scores on memory and thinking tests. The effect was biggest for the people who leaned on their phones most.{cite(c[S_WARD])}</p>
  <p>Screens also pull everyone&rsquo;s attention around. Psychologist Gloria Mark&rsquo;s studies from 2016 to 2020 found people stayed on one screen for about <strong>47 seconds</strong> on average before switching.{cite(c[S_MARK])} With ADHD, that pull is usually stronger.</p>
  <p>So the plan that works best isn&rsquo;t more willpower. It&rsquo;s making the distraction impossible for a while.</p>

  <h2>What research says about screens and ADHD</h2>
  <p>Be careful with big claims here. This is what the studies actually show:</p>
  <ul>
    <li><strong>Heavy screen use and ADHD symptoms go together, a little.</strong> A JAMA study followed 2,587 teenagers for two years. Teens who used more kinds of digital media many times a day were slightly more likely to report new ADHD symptoms later (about 10% higher odds for each extra activity). It shows a link, not proof that screens cause ADHD.{cite(c[S_RA])}</li>
    <li><strong>Less internet improved attention in a trial.</strong> In a 2025 study, 467 adults blocked the internet on their phones for two weeks. 91% got better on at least one of attention, mental health or well-being, and their attention improved by about as much as it normally declines over 10 years of ageing. This study was not about ADHD, and it blocked phones, not computers.{cite(c[S_CASTELO])}</li>
    <li><strong>No study shows that an internet blocker treats ADHD.</strong> Vow is a tool for your surroundings, not a treatment. For diagnosis, medication or therapy, talk to a doctor.</li>
  </ul>

  <h2>A Mac setup that works with an ADHD brain</h2>
  <ol>
    <li><strong>Pick one small task first.</strong> Write it down in one line, like &ldquo;Write the intro of my essay.&rdquo; A vague goal is easy to escape.</li>
    <li><strong>Get what you need before you go offline.</strong> Open the PDF, download the slides, save the article. Then nothing sends you back to the browser.</li>
    <li><strong>Start short.</strong> Try 15 to 30 minutes. A short session you finish beats a long one you dread. Grow it later.</li>
    <li><strong>Keep the time in view.</strong> Barkley suggests making time visible, because ADHD makes it hard to feel time passing.{cite(c[S_BARKLEY])} Vow shows how much time is left and when you&rsquo;ll be back online.</li>
    <li><strong>Put your phone in another room.</strong> In the &ldquo;brain drain&rdquo; study, people with their phone in another room did best.{cite(c[S_WARD])}</li>
    <li><strong>Keep a &ldquo;look it up later&rdquo; list.</strong> When you need to search something, write it on paper and keep going. Check the list when the session ends.</li>
    <li><strong>Let a schedule start it for you.</strong> Remembering to start is often the hard part. In Vow, click <strong>Schedules</strong>, then <strong>Add Schedule</strong>, and pick a time, like weekdays at 9:00 for 2 hours. You decide once.</li>
  </ol>

  <h2>Why block the whole internet, not just a few sites</h2>
  <p>Block YouTube, and Reddit fills the gap. Block Reddit, and the news does. A brain that loves new things will always find the next one. Vow doesn&rsquo;t use a list. It turns off your Mac&rsquo;s internet, so every browser and app goes quiet at once and there&rsquo;s nothing new to find.</p>
  <p>Vow also has no instant cancel button. If you really need to get online, you can ask to unlock early, but your Mac stays offline for 15 more minutes first. That wait is often enough for the urge to pass. Quitting Vow or restarting your Mac won&rsquo;t bring the internet back early.</p>
  <p>Your Mac still works offline: your files, notes, writing apps and anything saved on your Mac keep working.</p>

  <h2>What Vow can&rsquo;t do</h2>
  <ul>
    <li><strong>It doesn&rsquo;t touch your phone.</strong> Vow works on your Mac only. Keep your phone in another room, or use Screen Time on it.</li>
    <li><strong>It&rsquo;s all or nothing.</strong> If a task really needs the web, split it: research online first, then go offline to write.</li>
    <li><strong>It isn&rsquo;t medical care.</strong> It can make focus easier. It doesn&rsquo;t replace a doctor.</li>
  </ul>
  <p>For more ways to go offline, including free options built into macOS, read <a href="/block-internet-on-mac/">how to block the internet on a Mac</a>.</p>'''
adhd_faqs = [
    ("Is there a Mac app that helps with ADHD focus?",
     ["Yes. Apps that remove distractions can help, because they change your surroundings instead of relying on willpower. Vow is a Mac app that turns off your internet until a timer ends, from 5 minutes to 24 hours. It isn&rsquo;t an ADHD treatment, and it works on your Mac only."]),
    ("Does blocking the internet help with ADHD?",
     ["No study has tested internet blockers as an ADHD treatment. But in a 2025 trial, adults who blocked the internet on their phones for two weeks got better at keeping their attention, and many people with ADHD find it easier to remove a distraction than to resist it."]),
    ("How long should a focus session be with ADHD?",
     ["There&rsquo;s no single right length. Start with 15 to 30 minutes, the length you can finish, and add time as it gets easier. Vow sessions can be anywhere from 5 minutes to 24 hours."]),
    ("Can I still use my files and notes while offline?",
     ["Yes. Vow only turns off the internet. Your files, notes, writing apps and anything saved on your Mac keep working."]),
    ("What if I need something from the internet during a session?",
     ["Write it on a &ldquo;look it up later&rdquo; list and keep going. If it really can&rsquo;t wait, open Vow and ask to unlock early. Your Mac stays offline for 15 more minutes, then the internet comes back."]),
]
page("adhd-focus-mac",
     "ADHD Focus on a Mac: Take the Internet Out of Reach",
     "Why willpower fails with ADHD, what research says about screens and attention, and a simple Mac setup that makes distractions impossible for a while.",
     "ADHD and focus on a Mac: take the internet out of reach",
     "ADHD focus on a Mac",
     "With ADHD, &ldquo;just don&rsquo;t open YouTube&rdquo; rarely works, because the next distraction is always one click away. What helps more is changing your surroundings so the distraction isn&rsquo;t there. This guide covers what research says, a simple setup for your Mac, and how Vow, a Mac app that turns off your internet until a timer ends, fits in.",
     adhd_body, adhd_faqs, adhd_src, ISO, HUMAN)

# ================================================================ more verified sources (checked 2026-11-14)
S_BRAGHIERI = 'Braghieri, L., Levy, R., &amp; Makarin, A. (2022). Social media and mental health. <em>American Economic Review</em>, 112(11), 3660&ndash;3693. <a href="https://doi.org/10.1257/aer.20211218">doi.org/10.1257/aer.20211218</a>'
S_ANDREASSEN = 'Andreassen, C. S., Torsheim, T., Brunborg, G. S., &amp; Pallesen, S. (2012). Development of a Facebook addiction scale. <em>Psychological Reports</em>, 110(2), 501&ndash;517. <a href="https://doi.org/10.2466/02.09.18.PR0.110.2.501-517">doi.org/10.2466/02.09.18.PR0.110.2.501-517</a>'
S_KRAUS = 'Kraus, S. W., Krueger, R. B., Briken, P., et al. (2018). Compulsive sexual behaviour disorder in the ICD-11. <em>World Psychiatry</em>, 17(1), 109&ndash;110. <a href="https://doi.org/10.1002/wps.20499">doi.org/10.1002/wps.20499</a>'
S_APPLE_ST = 'Apple. &ldquo;Change Apps &amp; Websites Restrictions settings in Screen Time on Mac.&rdquo; Mac User Guide. <a href="https://support.apple.com/guide/mac-help/egx28nwl2h1k/mac">support.apple.com</a>'
S_CLOUDFLARE = 'Cloudflare. &ldquo;Introducing 1.1.1.1 for Families.&rdquo; Cloudflare blog, April 2020. <a href="https://blog.cloudflare.com/introducing-1-1-1-1-for-families/">blog.cloudflare.com</a>'


def steps_screen_time(site_hint="the website"):
    return f'''<ol>
    <li>Click the Apple menu, then <strong>System Settings</strong>, then <strong>Screen Time</strong>.</li>
    <li>Click <strong>Apps &amp; Websites</strong>, then <strong>Restrictions</strong>.</li>
    <li>Under Websites, click <strong>Filtering</strong> and choose <strong>Limit Adult Websites</strong>. Then click <strong>Customize</strong>.</li>
    <li>Under <strong>Restricted</strong>, click <strong>+</strong>, type {site_hint}, and click <strong>Done</strong>.</li>
    <li>Back in Screen Time, turn on <strong>Lock Screen Time Settings</strong> and set a passcode, so the block can&rsquo;t be switched off in one click.</li>
  </ol>'''


# ================================================================ /block-websites-on-mac/
bw_src = [S_APPLE_ST]
c = {s: i for i, s in enumerate(bw_src, 1)}
SITES = [
    ("instagram", "Instagram", "instagram.com", "Reels and Explore are built to never end. On a Mac you mostly use Instagram in the browser, so blocking the website is enough for the Mac. Your phone needs its own limit."),
    ("tiktok", "TikTok", "tiktok.com", "The For You feed is the hardest one to put down. Block the website on your Mac, and keep the phone app out of reach while you work."),
    ("youtube", "YouTube", "youtube.com, youtu.be and m.youtube.com", "Autoplay and the sidebar turn one video into an evening. Block all three addresses, or links from other sites will still open videos. Need one video for class? Download it first, then block."),
    ("x-twitter", "X (Twitter)", "x.com and twitter.com", "Block both names. Old links still use twitter.com and quietly send you to X."),
    ("reddit", "Reddit", "reddit.com, www.reddit.com and old.reddit.com", "Reddit has several addresses. If you block only one, the others still work."),
    ("facebook", "Facebook", "facebook.com and messenger.com", "Block Messenger too if chats are what pull you back in."),
]
site_sections = "".join(f'''
  <h3 id="{sid}">How to block {name} on a Mac</h3>
  <p>Add <strong>{doms}</strong> to the Restricted list above. {tip}</p>''' for sid, name, doms, tip in SITES)
bw_body = f'''  <h2>The quick answer</h2>
  <ul>
    <li><strong>To block a few sites for free:</strong> use Screen Time, which is already on your Mac. Steps below.</li>
    <li><strong>To block one site for a set time:</strong> use a free blocker like SelfControl. See <a href="/free-internet-blocker-mac/">free internet blockers for Mac</a>.</li>
    <li><strong>If you block one site and just open another:</strong> block the whole internet for a while instead. That&rsquo;s what Vow does.</li>
  </ul>

  <h2>How to block a website on a Mac with Screen Time (free)</h2>
  <p>Screen Time is built into every Mac and MacBook. It costs nothing and needs no download.{cite(c[S_APPLE_ST])}</p>
  {steps_screen_time("the website, like instagram.com")}
  <p><strong>Good to know:</strong> Apple only promises it works in Safari. Other browsers, like Chrome or Firefox, may not follow it. And if you set the passcode yourself, you know how to undo it. If that&rsquo;s a problem, ask a friend or family member to set the passcode for you.</p>

  <h2>Which addresses to block for each site</h2>
  <p>Most sites use more than one address. Block all of them, or the block has a hole.</p>
{site_sections}

  <h2>Why blocking one site often doesn&rsquo;t work</h2>
  <p>Block Instagram, and you open TikTok. Block TikTok, and you open YouTube. Block YouTube, and Reddit fills the gap. You end up adding sites to a list forever, and the list always has one you forgot.</p>
  <p>If that sounds like you, stop blocking sites one by one. Turn off the whole internet for a set time instead. Then Instagram, TikTok, YouTube, X, Reddit and every other site are blocked at once, in every browser and app, and there&rsquo;s nothing left to switch to.</p>

  <h2>The toughest option: block everything until the timer ends</h2>
  <p>Vow is a Mac app that turns off your Mac&rsquo;s internet for anywhere from 5 minutes to 24 hours.</p>
  <ul>
    <li><strong>Every site and app:</strong> Safari, Chrome, Firefox, Instagram, TikTok, YouTube, Discord and the rest, all at once.</li>
    <li><strong>No list to keep up:</strong> nothing to forget, no extension to turn off.</li>
    <li><strong>Hard to undo:</strong> quitting Vow or restarting your Mac won&rsquo;t bring the internet back. To end early, you ask, then wait 15 more minutes. Usually the urge passes.</li>
    <li><strong>On a schedule:</strong> in Vow, click <strong>Schedules</strong>, then <strong>Add Schedule</strong>. For example, every weekday at 9:00 for 3 hours.</li>
  </ul>
  <p>Vow can&rsquo;t block just one site and keep the rest. If that&rsquo;s what you need, use Screen Time or a free blocker. For adult sites, see <a href="/block-adult-sites-on-mac/">how to block adult sites on a Mac</a>.</p>'''
bw_faqs = [
    ("How do I block Instagram on my Mac?",
     ["Open System Settings, click Screen Time, then Apps &amp; Websites, then Restrictions. Under Websites, click Filtering, choose Limit Adult Websites, click Customize, and add instagram.com to the Restricted list. To block Instagram and everything else at once, use Vow to turn off your Mac&rsquo;s internet until a timer ends."]),
    ("How do I block YouTube on my MacBook?",
     ["Add youtube.com, youtu.be and m.youtube.com to the Restricted list in Screen Time. Block all three, or links from other sites will still open videos."]),
    ("Can I block TikTok and X (Twitter) on a Mac for free?",
     ["Yes. Screen Time is free and built in. Add tiktok.com, x.com and twitter.com to its Restricted list. Free apps like SelfControl can also block sites until a timer ends."]),
    ("Does Screen Time block websites in Chrome?",
     ["Not reliably. Apple only promises it works in Safari, and other browsers may not follow it. To block every browser at once, turn off the whole internet with an app like Vow."]),
    ("Can Vow block just Instagram?",
     ["No. Vow turns off your Mac&rsquo;s whole internet, so Instagram is blocked along with everything else. To block only some sites, use Screen Time or a website blocker."]),
]
page("block-websites-on-mac",
     "How to Block Websites on a Mac: Instagram, YouTube, TikTok",
     "Block Instagram, YouTube, TikTok, X (Twitter) and Reddit on your Mac or MacBook for free with Screen Time, or block every site at once until a timer ends.",
     "How to block websites on a Mac (Instagram, YouTube, TikTok, X)",
     "Block websites on a Mac",
     "You can block any website on a Mac or MacBook for free with Screen Time, which is already built in. This guide shows the steps and the exact addresses to block for Instagram, TikTok, YouTube, X (Twitter), Reddit and Facebook. If you block one site and just open another, the stronger fix is to turn off the whole internet for a set time.",
     bw_body, bw_faqs, bw_src, ISO, HUMAN)

# ================================================================ /block-adult-sites-on-mac/
ad_src = [S_APPLE_ST, S_CLOUDFLARE, S_KRAUS, S_TELEMANAS]
c = {s: i for i, s in enumerate(ad_src, 1)}
ad_body = f'''  <h2>The quick answer</h2>
  <ul>
    <li><strong>Free, built in:</strong> Screen Time&rsquo;s <strong>Limit Adult Websites</strong> setting blocks many adult sites in Safari.</li>
    <li><strong>Free, works in every browser:</strong> switch your Mac to a family-safe DNS, like Cloudflare&rsquo;s 1.1.1.3.</li>
    <li><strong>Hardest to get around:</strong> take the whole Mac offline at the times you struggle most, like late at night, with Vow.</li>
  </ul>

  <h2>1. Turn on Limit Adult Websites in Screen Time</h2>
  <p>This is free and already on your Mac or MacBook. Apple&rsquo;s filter blocks many adult sites automatically, and you can add more yourself.{cite(c[S_APPLE_ST])}</p>
  {steps_screen_time("any extra site you want to block")}
  <p>Apple says the filter isn&rsquo;t perfect: it can miss some adult sites and block some normal ones. Apple also only promises it works in Safari, so other browsers may not follow it.</p>

  <h2>2. Use a family-safe DNS (all browsers)</h2>
  <p>DNS is like your Mac&rsquo;s phone book for websites. A family-safe DNS refuses to look up adult sites, in every browser and app. Cloudflare&rsquo;s free &ldquo;1.1.1.1 for Families&rdquo; uses <strong>1.1.1.3</strong> and <strong>1.0.0.3</strong> to block adult content and malware.{cite(c[S_CLOUDFLARE])}</p>
  <ol>
    <li>Open <strong>System Settings</strong> and click <strong>Network</strong>.</li>
    <li>Click <strong>Wi-Fi</strong>, then <strong>Details</strong> next to your network.</li>
    <li>Click <strong>DNS</strong>. Under DNS Servers, click <strong>+</strong> and add <strong>1.1.1.3</strong>, then <strong>1.0.0.3</strong>.</li>
    <li>Click <strong>OK</strong>. If you also use Ethernet, repeat for it.</li>
  </ol>
  <p><strong>Good to know:</strong> anyone with your Mac&rsquo;s password can remove it in a minute, and some browsers have their own &ldquo;secure DNS&rdquo; setting that can skip it.</p>

  <h2>3. Make the hard hours offline</h2>
  <p>Filters miss things, and new sites appear every day. Many people find the urge comes at the same times: late at night, alone, bored or stressed. For those hours, the strongest fix isn&rsquo;t a better list. It&rsquo;s no internet at all.</p>
  <p>Vow is a Mac app that turns off your Mac&rsquo;s whole internet until a timer ends. Open Vow, click <strong>Schedules</strong>, then <strong>Add Schedule</strong>, and pick your hard hours, for example every night from 23:00 for 7 hours. Quitting Vow or restarting your Mac won&rsquo;t bring the internet back. To end early, you have to wait 15 more minutes first, and urges often fade in that time.</p>
  <p>Vow works on your Mac only. Keep your phone out of the bedroom, or use Screen Time on it too.</p>

  <h2>If it feels like more than a habit</h2>
  <p>If you keep going back even though it&rsquo;s hurting your sleep, work, studies or relationships, you&rsquo;re not alone, and it isn&rsquo;t just weak willpower. The World Health Organization recognizes compulsive sexual behaviour disorder as a condition doctors can diagnose and treat.{cite(c[S_KRAUS])}</p>
  <ul>
    <li>Talk to a doctor, therapist or counselor you trust. This is a normal thing to ask for help with.</li>
    <li><strong>India:</strong> Tele MANAS, the government&rsquo;s free mental health helpline, 14416 or 1-800-891-4416, day and night.{cite(c[S_TELEMANAS])}</li>
    <li>If you ever feel unsafe, call your local emergency number.</li>
  </ul>
  <p>Blocking helps by putting a gap between the urge and the action. Support helps with the rest.</p>'''
ad_faqs = [
    ("How do I block adult sites on my Mac for free?",
     ["Open System Settings, click Screen Time, then Apps &amp; Websites, then Restrictions. Under Websites, click Filtering and choose Limit Adult Websites. For every browser, also set your Mac&rsquo;s DNS to 1.1.1.3 and 1.0.0.3 (Cloudflare for Families) in System Settings, Network."]),
    ("Does Screen Time block adult sites in Chrome?",
     ["Not reliably. Apple only promises it works in Safari. A family-safe DNS like 1.1.1.3 covers every browser, and turning off the internet with Vow blocks everything."]),
    ("How do I stop myself from turning the block off?",
     ["Ask someone you trust to set the Screen Time passcode, so you don&rsquo;t know it. For your hardest hours, use Vow: once a session starts, quitting or restarting won&rsquo;t end it, and ending early means waiting 15 more minutes."]),
    ("Can Vow block only adult sites?",
     ["No. Vow turns off your Mac&rsquo;s whole internet for a set time. Use it with Screen Time: the filter for the day, and Vow for the hours you find hardest."]),
]
page("block-adult-sites-on-mac",
     "How to Block Adult Sites on a Mac or MacBook",
     "Block adult websites on a Mac for free with Screen Time and a family-safe DNS, and make your hardest hours fully offline so there's nothing to open.",
     "How to block adult sites on a Mac or MacBook",
     "Block adult sites on a Mac",
     "You can block adult websites on a Mac or MacBook for free with Screen Time&rsquo;s Limit Adult Websites setting, and in every browser with a family-safe DNS. Filters always miss some sites, so for the hours you find hardest, the strongest step is to turn off the whole internet until a timer ends.",
     ad_body, ad_faqs, ad_src, ISO, HUMAN)

# ================================================================ /free-internet-blocker-mac/
fr_src = [S_APPLE_ST, S_CLOUDFLARE]
c = {s: i for i, s in enumerate(fr_src, 1)}
fr_body = f'''  <h2>The quick answer</h2>
  <p>The best free options are <strong>Screen Time</strong> (built in, blocks sites you choose), <strong>SelfControl</strong> (free app, blocks a list of sites until a timer ends) and simply <strong>turning off Wi-Fi</strong>. None of them can take your whole Mac offline and keep it off until a timer ends. If you need that, Vow does it, with 3 free sessions to try.</p>

  <h2>Free ways to block the internet or websites on a Mac</h2>
  <div class="table-scroll">
    <table>
      <caption>Free blockers for Mac compared (November 2026)</caption>
      <thead><tr><th scope="col"></th><th scope="col">What it blocks</th><th scope="col">Timer you can&rsquo;t cancel?</th><th scope="col">How easy to undo</th></tr></thead>
      <tbody>
        <tr><th scope="row">Turn off Wi-Fi</th><td>All internet over Wi-Fi</td><td>No</td><td>One click</td></tr>
        <tr><th scope="row">Screen Time</th><td>Websites you list, adult sites (Safari)</td><td>No</td><td>Easy if you know the passcode</td></tr>
        <tr><th scope="row">SelfControl</th><td>Websites on your list</td><td>Yes</td><td>Hard until the timer ends</td></tr>
        <tr><th scope="row">Cold Turkey (free version)</th><td>Websites on your list</td><td>Timed blocks; locking needs Pro</td><td>Easier without a lock</td></tr>
        <tr><th scope="row">Browser extensions (like LeechBlock NG)</th><td>Websites, in that browser only</td><td>Sometimes</td><td>Open another browser</td></tr>
        <tr><th scope="row">Family-safe DNS</th><td>Adult and harmful sites</td><td>No</td><td>A minute in Settings</td></tr>
      </tbody>
    </table>
  </div>

  <h3>Turn off Wi-Fi</h3>
  <p>Click the Wi-Fi icon in the menu bar and switch it off. It&rsquo;s instant and free, but it&rsquo;s one click to turn back on, there&rsquo;s no timer, and an Ethernet cable or iPhone hotspot still gets you online.</p>

  <h3>Screen Time</h3>
  <p>Built into every Mac. Block the sites you choose, or turn on Limit Adult Websites.{cite(c[S_APPLE_ST])} Steps: <a href="/block-websites-on-mac/">how to block websites on a Mac</a>.</p>

  <h3>SelfControl</h3>
  <p>A free, open-source Mac app. Add websites to a list, set a timer, and those sites stay blocked until it ends, even if you restart. It only blocks the sites on your list. More: <a href="/selfcontrol-alternative/">Vow vs SelfControl</a>.</p>

  <h3>Cold Turkey Blocker (free version)</h3>
  <p>The free version blocks websites on a timer. Blocking apps, schedules and its locking features need the paid Pro version. More: <a href="/cold-turkey-alternative/">Vow vs Cold Turkey</a>.</p>

  <h3>Browser extensions</h3>
  <p>Free extensions like LeechBlock NG block sites inside one browser. They&rsquo;re easy to get around: open a different browser.</p>

  <h3>Family-safe DNS</h3>
  <p>Cloudflare&rsquo;s free 1.1.1.3 blocks adult and harmful sites in every browser.{cite(c[S_CLOUDFLARE])} Steps: <a href="/block-adult-sites-on-mac/">how to block adult sites on a Mac</a>.</p>

  <h2>What free blockers can&rsquo;t do</h2>
  <p>Every free option above has the same weak spot: it blocks a list, or it&rsquo;s easy to undo. Block Instagram, and you open TikTok. Block TikTok, and you open YouTube. Turn off Wi-Fi, and you turn it back on.</p>

  <h2>The toughest blocker for Mac: the whole internet, off until the timer ends</h2>
  <p>Vow is a Mac app that turns off your Mac&rsquo;s whole internet, from 5 minutes to 24 hours. Wi-Fi, Ethernet, USB adapters and iPhone hotspots all go off. Every browser and app goes quiet. Quitting Vow or restarting your Mac won&rsquo;t bring it back. To end early, you ask, then wait 15 more minutes.</p>
  <ul>
    <li><strong>Try it free:</strong> 3 full sessions, no account, no card.</li>
    <li><strong>Then $9.99 once:</strong> no subscription, for up to 2 of your Macs.</li>
    <li><strong>Needs:</strong> macOS 26 or later on Apple Silicon.</li>
  </ul>
  <p>Vow isn&rsquo;t the right pick if you want to block only some sites and keep the rest. Then a free blocker above is a better fit.</p>'''
fr_faqs = [
    ("What is the best free internet blocker for Mac?",
     ["For blocking a few sites, Screen Time (built in) or SelfControl (a free app). For turning off the internet quickly, switch off Wi-Fi. None of them takes the whole Mac offline until a timer ends. Vow does, and you can try 3 sessions free."]),
    ("Is Vow free?",
     ["You can try 3 full sessions free, with no account and no card. After that, Vow is $9.99 once. No subscription."]),
    ("What is the toughest website blocker for Mac?",
     ["SelfControl and Cold Turkey Pro are strict about the sites on their lists. Vow is stricter about the whole internet: every site and app goes offline, quitting or restarting won&rsquo;t end it, and ending early means a 15-minute wait."]),
    ("Can I turn off the internet on my Mac for a set time for free?",
     ["Not with a timer that holds. You can switch off Wi-Fi, but it&rsquo;s one click to undo. Vow&rsquo;s 3 free sessions let you try a timer that holds before you buy."]),
]
page("free-internet-blocker-mac",
     "Free Internet Blockers for Mac (and the Toughest One)",
     "The best free ways to block the internet or websites on a Mac: Screen Time, SelfControl, Cold Turkey and more, and what to use when free isn't enough.",
     "Free internet blockers for Mac, and the toughest one",
     "Free internet blockers for Mac",
     "You can block websites on a Mac for free with Screen Time or SelfControl, and turn off the internet with the Wi-Fi switch. Free tools either block a list of sites or are easy to undo. If you need your whole Mac offline until a timer ends, Vow does that, with 3 free sessions to try.",
     fr_body, fr_faqs, fr_src, ISO, HUMAN)

# ================================================================ /stay-focused-on-mac/
sf_src = [S_MARK, S_WARD, S_SANA]
c = {s: i for i, s in enumerate(sf_src, 1)}
sf_body = f'''  <h2>Why it&rsquo;s so hard to focus on a Mac</h2>
  <p>Your Mac is where you work, and also where every distraction lives. In Gloria Mark&rsquo;s studies, people stayed on one screen for about 47 seconds on average before switching.{cite(c[S_MARK])} Every alert, tab and &ldquo;quick check&rdquo; pulls you away. The fix is to remove as many of them as you can before you start.</p>

  <h2>7 steps to stay focused on your Mac</h2>
  <ol>
    <li><strong>Turn on Do Not Disturb.</strong> Click Control Center in the menu bar, click <strong>Focus</strong>, then <strong>Do Not Disturb</strong>. To pick which people and apps can still reach you, open <strong>System Settings</strong> and click <strong>Focus</strong>.</li>
    <li><strong>Turn off notifications you don&rsquo;t need.</strong> Open <strong>System Settings</strong>, click <strong>Notifications</strong>, click an app, and turn off <strong>Allow notifications</strong>. Start with chat, social and news apps.</li>
    <li><strong>Use one window, full screen.</strong> Click the green button at the top left of a window. Everything else disappears.</li>
    <li><strong>Close the tabs you aren&rsquo;t using.</strong> Bookmark them if you&rsquo;re scared to lose them.</li>
    <li><strong>Put your phone in another room.</strong> In one study, just having a phone on the desk, even switched off, lowered scores on thinking tests.{cite(c[S_WARD])}</li>
    <li><strong>Block the sites that pull you in.</strong> Screen Time can block Instagram, YouTube, TikTok and others for free. See <a href="/block-websites-on-mac/">how to block websites on a Mac</a>.</li>
    <li><strong>Go fully offline for your hardest work.</strong> Pick a time and turn the internet off until it ends. Vow does this from 5 minutes to 24 hours, and quitting or restarting won&rsquo;t end it early.</li>
  </ol>

  <h2 id="students">For students: SAT, JEE, NEET, UPSC and finals</h2>
  <p>When you&rsquo;re studying for a big exam, &ldquo;just one video&rdquo; is the biggest thief of time. It costs focus too. In one study, students who multitasked on a laptop during a lecture scored lower on a test, and so did students sitting near them.{cite(c[S_SANA])}</p>
  <ul>
    <li>Download practice papers, notes and recorded lectures before you start.</li>
    <li>Study in blocks, like 2 hours, then take a break.</li>
    <li>Use a schedule so the block starts on its own. In Vow, click <strong>Schedules</strong>, then <strong>Add Schedule</strong>, for example every day at 7:00 for 2 hours.</li>
    <li>Write down anything you need to look up, and search it in your break.</li>
  </ul>

  <h2>Doesn&rsquo;t Focus mode do this already?</h2>
  <p>No. Focus mode hides notifications, but the internet stays on. YouTube, Instagram and the news are still one click away. Focus mode helps with interruptions from others. A blocker helps with interruptions you start yourself.</p>
  <p>For ADHD-specific tips, see <a href="/adhd-focus-mac/">ADHD and focus on a Mac</a>.</p>'''
sf_faqs = [
    ("How do I stay focused on my Mac?",
     ["Turn on Do Not Disturb, turn off notifications you don&rsquo;t need, work in one full-screen window, and put your phone in another room. For your hardest work, turn the internet off until a timer ends."]),
    ("Does Focus mode on Mac block websites?",
     ["No. Focus mode hides notifications, but the internet stays on. To block websites, use Screen Time or a blocker. To block everything, turn off the internet with Vow."]),
    ("How can I study on my MacBook without distractions?",
     ["Download what you need first, then go offline for one study block, like 2 hours. A Vow schedule can start the block at the same time every day."]),
]
page("stay-focused-on-mac",
     "How to Stay Focused on Your Mac: 7 Steps That Work",
     "Stay focused on your Mac or MacBook: Do Not Disturb, notifications, full screen, blocking sites, and going offline for deep work or exam study.",
     "How to stay focused on your Mac",
     "Stay focused on a Mac",
     "To stay focused on a Mac or MacBook, turn on Do Not Disturb, switch off the notifications you don&rsquo;t need, work in one full-screen window, and keep your phone in another room. For your hardest work, like studying for an exam, turn the internet off until a timer ends, so there&rsquo;s nothing to check.",
     sf_body, sf_faqs, sf_src, ISO, HUMAN)

# ================================================================ /social-media-addiction/
sm_src = [S_ANDREASSEN, S_BRAGHIERI, S_HUNT, S_ALLCOTT, S_CASTELO, S_SATICI, S_WHO, S_NCPG, S_GAMCARE, S_TELEMANAS]
c = {s: i for i, s in enumerate(sm_src, 1)}
sm_body = f'''  <h2>Signs it&rsquo;s more than &ldquo;a lot of use&rdquo;</h2>
  <p>Researchers who built one of the first social media addiction scales looked for six signs.{cite(c[S_ANDREASSEN])} Ask yourself how often these are true:</p>
  <ul>
    <li>You think about the app a lot, even when you&rsquo;re not on it.</li>
    <li>You need more and more time on it to feel the same.</li>
    <li>You use it to forget your problems or escape bad feelings.</li>
    <li>You&rsquo;ve tried to cut down and couldn&rsquo;t.</li>
    <li>You feel restless or upset when you can&rsquo;t use it.</li>
    <li>It&rsquo;s hurting your work, studies, sleep or relationships.</li>
  </ul>
  <p>This isn&rsquo;t a diagnosis. But if several sound like you, it&rsquo;s worth acting.</p>

  <h2>Why Instagram, TikTok, YouTube and Reddit are so hard to stop</h2>
  <ul>
    <li><strong>Instagram:</strong> Reels and Explore never run out, and other people&rsquo;s best moments make your normal day look worse.</li>
    <li><strong>TikTok:</strong> each video is short, so &ldquo;one more&rdquo; always feels small.</li>
    <li><strong>YouTube:</strong> autoplay and the sidebar choose the next video for you.</li>
    <li><strong>Reddit and X (Twitter):</strong> one more thread, one more reply, one more refresh, often full of bad news.</li>
  </ul>
  <p>The comparison part is real. When Facebook arrived at US colleges, students&rsquo; mental health got worse, and researchers linked it to comparing themselves with others.{cite(c[S_BRAGHIERI])} People who scroll bad news a lot also report more stress and lower well-being.{cite(c[S_SATICI])}</p>

  <h2>What happened when people cut back</h2>
  <ul>
    <li><strong>Three weeks, 10 minutes a day:</strong> students who limited Facebook, Instagram and Snapchat to 10 minutes each a day felt less lonely and less depressed.{cite(c[S_HUNT])}</li>
    <li><strong>Four weeks off:</strong> people who turned off Facebook spent more time offline, felt a bit happier, and used it less even afterwards.{cite(c[S_ALLCOTT])}</li>
    <li><strong>Two weeks without phone internet:</strong> 91% of 467 adults got better in attention, mental health or well-being.{cite(c[S_CASTELO])}</li>
  </ul>
  <p>More studies: <a href="/research/">what the research says</a>.</p>

  <h2>How to stop on your Mac or MacBook</h2>
  <ol>
    <li><strong>Find your scroll hours.</strong> Late at night, after work, or when a task gets hard. Write them down.</li>
    <li><strong>Log out and remove shortcuts.</strong> Sign out of Instagram, TikTok, YouTube, Reddit and X in your browser. Remove them from bookmarks.</li>
    <li><strong>Block the worst sites.</strong> Screen Time can block them for free. Here are the steps and exact addresses: <a href="/block-websites-on-mac/">how to block websites on a Mac</a>.</li>
    <li><strong>Make your scroll hours offline.</strong> If you block one app and just open another, turn off the whole internet instead. In Vow, click <strong>Schedules</strong>, then <strong>Add Schedule</strong>, for example every night at 22:30 for 8 hours. Quitting Vow or restarting won&rsquo;t end it early.</li>
    <li><strong>Charge your phone outside the bedroom.</strong> Vow works on your Mac only. If your phone is next to you, the scrolling just moves.</li>
    <li><strong>Have something ready instead.</strong> A book, a downloaded podcast, a walk, a friend to call.</li>
  </ol>

  <h2 id="help">When you can&rsquo;t stop: gambling, gaming and adult sites</h2>
  <p>Sometimes it&rsquo;s not social media but betting sites, online games or adult sites. The World Health Organization lists gaming disorder as a health condition.{cite(c[S_WHO])} If you can&rsquo;t stop even though it&rsquo;s hurting you, it isn&rsquo;t just weak willpower, and help works.</p>
  <ul>
    <li><strong>Gambling, US:</strong> National Problem Gambling Helpline, call or text 1-800-MY-RESET (1-800-697-3738), or chat online, any time.{cite(c[S_NCPG])}</li>
    <li><strong>Gambling, UK:</strong> National Gambling Helpline, 0808 8020 133, free, any time.{cite(c[S_GAMCARE])}</li>
    <li><strong>India:</strong> Tele MANAS, the government&rsquo;s free mental health helpline, 14416 or 1-800-891-4416, day and night.{cite(c[S_TELEMANAS])}</li>
    <li><strong>Adult sites:</strong> see <a href="/block-adult-sites-on-mac/">how to block adult sites on a Mac</a>, and talk to a doctor or counselor.</li>
    <li>If you ever feel unsafe, call your local emergency number.</li>
  </ul>
  <p>Vow can help by putting a gap between the urge and the action: ending a session early means waiting 15 more minutes. It isn&rsquo;t treatment. If gambling is the problem, also ask your bank about blocking gambling payments.</p>'''
sm_faqs = [
    ("How do I stop Instagram addiction on my Mac?",
     ["Block instagram.com with Screen Time, sign out in your browser, and make your worst hours offline. If you block Instagram and open TikTok or YouTube instead, use Vow to turn off the whole internet until a timer ends."]),
    ("How do I stop TikTok and YouTube addiction?",
     ["Find the hours you scroll most and make them offline. Block the sites on your Mac, keep your phone in another room, and have something else ready to do."]),
    ("Is internet addiction real?",
     ["&ldquo;Internet addiction&rdquo; isn&rsquo;t an official diagnosis, but gaming disorder and gambling disorder are. Many people struggle to control their social media use. If it&rsquo;s hurting your life, talk to a doctor or counselor."]),
    ("Does Vow block my phone too?",
     ["No. Vow works on your Mac only. Keep your phone in another room, or set limits on it with Screen Time."]),
]
page("social-media-addiction",
     "Social Media Addiction: Instagram, TikTok, YouTube, Reddit",
     "Signs of Instagram, TikTok, YouTube or Reddit addiction, what studies found when people cut back, and how to stop scrolling on your Mac or MacBook.",
     "Instagram, TikTok, YouTube and Reddit addiction: how to stop on your Mac",
     "Social media addiction",
     "If you open Instagram, TikTok, YouTube, Reddit or X without thinking and can&rsquo;t stop even when you want to, you&rsquo;re not alone. Apps are built to keep you scrolling. Studies found that people who cut back felt less lonely and less depressed. This guide covers the signs, what research shows, and simple steps that work on a Mac.",
     sm_body, sm_faqs, sm_src, ISO, HUMAN)

# ================================================================ /research/
rs_src = [S_CASTELO, S_MARK, S_WARD, S_SANA, S_ALLCOTT, S_HUNT, S_BRAGHIERI, S_SATICI, S_RA]
c = {s: i for i, s in enumerate(rs_src, 1)}
def finding(stat, text, src):
    return f'''  <div class="finding">
    <p class="finding-stat">{stat}</p>
    <p>{text}{cite(c[src])}</p>
  </div>'''
rs_body = f'''  <p>These studies looked at phones, social media and laptops, not at Vow. They help explain why less internet often means more focus and a better mood. We&rsquo;ve kept each one in plain words and linked the original.</p>

  <h2>Attention and focus</h2>
  <div class="findings">
{finding("91%", "467 adults blocked the internet on their phones for two weeks. 91% got better in attention, mental health or well-being. Their attention improved by about as much as it normally declines over 10 years of ageing.", S_CASTELO)}
{finding("47 sec", "How long people stayed on one screen, on average, before switching, across studies from 2016 to 2020. In 2004 it was about two and a half minutes.", S_MARK)}
{finding("Even off", "Just having your own phone on the desk, switched off and face down, lowered scores on memory and thinking tests. People did best with the phone in another room.", S_WARD)}
{finding("Lower scores", "Students who multitasked on a laptop during a lecture scored lower on a test afterwards, and so did students who could see their screens.", S_SANA)}
  </div>

  <h2>Mood and well-being</h2>
  <div class="findings">
{finding("4 weeks", "People who turned off Facebook for four weeks spent more time offline, felt a bit happier, and kept using it less afterwards.", S_ALLCOTT)}
{finding("10 min", "Students who limited Facebook, Instagram and Snapchat to 10 minutes each a day for three weeks felt less lonely and less depressed.", S_HUNT)}
{finding("Colleges", "When Facebook arrived at US colleges, students&rsquo; mental health got worse, especially depression. Researchers linked it to comparing themselves with others.", S_BRAGHIERI)}
{finding("Stress", "People who scroll bad news more also report more stress and anxiety and lower well-being. This is a link, not proof of cause.", S_SATICI)}
  </div>

  <h2>Screens and ADHD symptoms</h2>
  <div class="findings">
{finding("+10% odds", "For each extra kind of digital media teens used many times a day, their odds of new ADHD symptoms over two years rose by about 10%. A link, not proof that screens cause ADHD.", S_RA)}
  </div>

  <h2>What this means for you</h2>
  <p>You don&rsquo;t have to quit the internet. The studies point to something simpler: less of it, at the right times, helps. Pick the hours that matter, like study time, deep work or late at night, and make them offline. Guides: <a href="/stay-focused-on-mac/">how to stay focused on a Mac</a>, <a href="/social-media-addiction/">social media addiction</a>, <a href="/adhd-focus-mac/">ADHD focus on a Mac</a>.</p>'''
page("research",
     "Screen Time, Focus and Mood: What the Research Says",
     "Plain-English summaries of studies on phones, social media, attention and mood, with links to every original paper.",
     "What the research says about the internet, focus and mood",
     "Research",
     "Studies show that less time online tends to mean better attention and a better mood. In one 2025 trial, 91% of people who blocked the internet on their phones for two weeks improved. Here are the key studies in plain words, with links to every original paper.",
     rs_body, None, rs_src, ISO, HUMAN)
