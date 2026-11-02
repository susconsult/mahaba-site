#!/usr/bin/env python3
"""Bouwt de pagina's van mahaba-site (Mahaba Beach).

Het ontwerp is 1-op-1 overgenomen van het Lovable-ontwerp
(pixel-perfect-replay-09755.lovable.app): de HTML-blokken staan in
build/lovable/*.html en de stylesheet in build/lovable/lovable.css.
Dit script vult de echte inhoud in, verdeelt de blokken over aparte
pagina's en schrijft alles naar public/. Cloudflare hoeft niets te bouwen.

Gebruik:
  python3 build/build.py                    -> schrijft public/
  python3 build/build.py --preview MAP      -> kopie met relatieve links
Daarna de bestanden in public/ mee committen.
"""
import os, re, shutil, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOV = os.path.join(ROOT, "build", "lovable")

WA_NUMBER = "+255 757 014 929"
WA_LINK = "https://wa.me/255757014929?text=Hi%20Mahaba%20Beach%2C%20I%27d%20like%20to%20book."
EMAIL = "mahababeach@gmail.com"
FACEBOOK = "https://www.facebook.com/mahababeach/"


def part(name):
    with open(os.path.join(LOV, name + ".html"), encoding="utf-8") as f:
        html = f.read()
    # Lovable asset urls -> our own files
    html = re.sub(r'/__l5e/assets-v1/[0-9a-f-]+/((?:logo|badge)-mahaba-beach\.png)', r'/assets/\1', html)
    html = re.sub(r'/__l5e/assets-v1/[0-9a-f-]+/([a-z0-9-]+\.jpg)', r'/assets/img/\1', html)
    return html


def sub(html, old, new, count=1):
    if old not in html:
        raise SystemExit(f"Tekst niet gevonden in Lovable-blok: {old[:70]!r}")
    return html.replace(old, new, count)


HEADER = part("header")
BTN_CLASS = re.search(r'<a href="#contact" class="([^"]+)">Book</a>', HEADER).group(1)
BTN_BIG = BTN_CLASS.replace("h-11 px-6 text-sm", "h-13 px-8 text-base")

# ---------------------------------------------------------------- blocks

def header(active):
    h = HEADER
    h = sub(h, 'href="#top"', 'href="/"')
    for anchor, slug in [("stay", "stay"), ("food", "food"), ("tours", "bloops-tours"), ("where", "getting-here")]:
        cur = ' aria-current="page"' if slug == active else ""
        h = sub(h, f'href="#{anchor}" class=', f'href="/{slug}"{cur} class=')
    h = sub(h, 'href="#contact"', 'href="/getting-here#contact"')
    # menu voor gsm (Lovable verbergt het menu onder 768px)
    items = "".join(
        f'<li><a href="/{s}"{" aria-current=\"page\"" if s == active else ""}>{label}</a></li>'
        for s, label in [("", "Home"), ("stay", "Stay"), ("food", "Food"), ("bloops-tours", "Bloops Tours"), ("getting-here", "Getting here")])
    mnav = ('<details class="mnav"><summary aria-label="Menu"><span class="mnav-bars" aria-hidden="true"><i></i><i></i><i></i></span></summary>'
            f'<nav aria-label="Menu"><ul>{items}</ul></nav></details>')
    h = sub(h, '<a href="/getting-here#contact" class=', '<div class="header-actions">' + mnav + '<a href="/getting-here#contact" class=')
    h = sub(h, '>Book</a>', '>Book</a></div>')
    return h


def hero():
    h = part("hero")
    h = re.sub(r'<img src="/assets/img/beach-huts\.jpg"[^>]*>',
               '<video class="photo bg-paper absolute inset-0 -z-30 h-full rounded-none hero-video" autoplay muted loop playsinline preload="auto" '
               'poster="/assets/hero-drone.jpg" aria-hidden="true"><source src="/assets/hero-drone.mp4" type="video/mp4"></video>'
               '<div aria-hidden="true" class="hero-warm absolute inset-0 -z-20"></div>', h)
    h = sub(h, 'href="#contact"', 'href="/getting-here#contact"')
    h = sub(h, 'href="#tours"', 'href="/bloops-tours"')
    return h


def ticker():
    t = part("ticker")
    t = t.replace('>Beach camping</span>', '>$10</span>').replace('>bring your tent</span>', '>beach camping, per person</span>')
    t = t.replace('>Own boat</span>', '>$100</span>').replace('>Bloops snorkel tours</span>', '>night + snorkel trip, per person</span>')
    return t


def stay():
    s = part("stay")
    s = sub(s, '<mark class="placeholder-text">PLACEHOLDER: <!-- -->camping price</mark>', '$10 per person, per night')
    s = sub(s, 'href="#contact"', f'href="{WA_LINK}" target="_blank" rel="noopener"')
    s = sub(s, '<h2 class="display-lg mt-5">Rooms a few steps from <em class="text-ocean">the sand</em></h2>',
               '<h1 class="display-lg mt-5">Rooms a few steps from <em class="text-ocean">the sand</em></h1>')
    return s


def food():
    f = part("food")
    return sub(f, '<h2 class="display-lg mt-5">From the dhow to the <em class="text-sun-gradient">barbecue</em></h2>',
                  '<h1 class="display-lg mt-5">From the dhow to the <em class="text-sun-gradient">barbecue</em></h1>')


TOUR_TABLE = '''<table class="tour-prices">
  <thead><tr><th>Per person</th><th>1–2 ppl</th><th>3–5 ppl</th><th>6+</th></tr></thead>
  <tbody>
    <tr><td>Fungu Yasini, half day<small>9 am – 1 pm</small></td><td>TSh 80,000</td><td>60,000</td><td>50,000</td></tr>
    <tr><td>Fungu Yasini, full day<small>9 am – 4 pm</small></td><td>TSh 120,000</td><td>90,000</td><td>75,000</td></tr>
    <tr><td>Mbudia Island</td><td>TSh 100,000</td><td>75,000</td><td>65,000</td></tr>
    <tr><td>Fungu Yasini &amp; Mbudia</td><td>TSh 120,000</td><td>100,000</td><td>80,000</td></tr>
  </tbody>
</table>
<p class="tour-note">Snorkel gear, fruit, water and local crew included. Marine reserve fees not included.</p>'''


def tours():
    t = part("tours")
    t = sub(t, 'We take you out on our own boat to snorkel around Mbudya Island and Yassini <mark class="placeholder-text">PLACEHOLDER: <!-- -->island names to confirm</mark>.',
               'We take you out on our own boat, straight from the beach in front of Mahaba, to snorkel at the sandbank of Fungu Yasini and around Mbudia Island.')
    t = sub(t, '<p class="mt-2"><mark class="placeholder-text">PLACEHOLDER: <!-- -->tour prices</mark></p>', TOUR_TABLE)
    t = sub(t, 'href="#contact"', f'href="{WA_LINK}" target="_blank" rel="noopener"')
    t = sub(t, '<h2 class="display-lg mt-3">Snorkel trips on <em class="text-sun-gradient">our own boat</em></h2>',
               '<h1 class="display-lg mt-3">Snorkel trips on <em class="text-sun-gradient">our own boat</em></h1>')
    return t


PACKAGE = f'''<section class="package-wrap">
  <div class="mx-auto w-full max-w-6xl px-5 md:px-10">
    <div class="package grain">
      <div>
        <p class="hand package-hand">the Mahaba package</p>
        <h2 class="display-lg package-title">One night, a morning on the sandbank, <em class="text-sun-gradient">lunch back on the beach</em></h2>
        <ul class="package-list">
          <li><span aria-hidden="true" class="dot dot-chili"></span>Sleep one night at Mahaba</li>
          <li><span aria-hidden="true" class="dot dot-sun"></span>Morning Bloops trip to snorkel at Fungu Yasini</li>
          <li><span aria-hidden="true" class="dot dot-palm"></span>Back at Mahaba for lunch</li>
        </ul>
      </div>
      <div class="package-price">
        <div class="package-stamp"><div><span class="package-amount">$100</span><span class="eyebrow package-per">per person</span></div></div>
        <a href="{WA_LINK}" target="_blank" rel="noopener" class="{BTN_BIG}">Book the package</a>
      </div>
    </div>
  </div>
</section>'''


def gallery():
    return part("gallery")


def hosts():
    h = part("hosts")
    return sub(h, 'Bea and Sadi have run Mahaba for<!-- --> <mark class="placeholder-text">PLACEHOLDER: <!-- -->number of</mark> years. They cook, they run the boat, and they know every fisherman on this coast. Sadi is a local Rastafarian, and that is where the red, gold and green in our logo come from.',
                  'Bea and Sadi run Mahaba together with their team. They cook, they run the boat, and they know every fisherman on this coast.')


def contact(as_page):
    c = part("contact")
    if as_page:
        c = sub(c, '<h2 class="display-lg mt-5">Send us a <em class="text-ocean">postcard</em></h2>',
                   '<h1 class="display-lg mt-5">Send us a <em class="text-ocean">postcard</em></h1>')
    dt = '<div class="border-b border-dashed border-ink/30 pb-3"><dt class="text-sm text-muted-foreground">{}</dt><dd class="mt-1 font-bold">{}</dd></div>'
    ph = '<mark class="placeholder-text">PLACEHOLDER: <!-- -->{}</mark>'
    c = sub(c, dt.format("From Dar es Salaam city centre", ph.format("travel time")),
               dt.format("Where", "On the coast along the Bagamoyo Road, north of Dar es Salaam"))
    c = sub(c, dt.format("From Bagamoyo", ph.format("travel time")), "")
    c = sub(c, dt.format("From the airport (DAR)", ph.format("travel time")),
               dt.format("From the airport (DAR)", "About 45 min – 1.5 h, depending on traffic"))
    c = sub(c, dt.format("WhatsApp", ph.format("WhatsApp number")), dt.format("WhatsApp", WA_NUMBER))
    c = sub(c, dt.format("E-mail", ph.format("e-mail address")),
               dt.format("E-mail", f'<a href="mailto:{EMAIL}" class="underline decoration-dashed underline-offset-4">{EMAIL}</a>'))
    c = sub(c, dt.format("Instagram", ph.format("Instagram handle")),
               dt.format("Facebook", f'<a href="{FACEBOOK}" target="_blank" rel="noopener" class="underline decoration-dashed underline-offset-4">facebook.com/mahababeach</a>'))
    c = re.sub(r'<div class="flex flex-col items-start gap-3"><button class="[^"]*" disabled="">Message on WhatsApp</button><mark class="placeholder-text">PLACEHOLDER: <!-- -->button goes live once the WhatsApp number is added</mark></div>',
               f'<a href="{WA_LINK}" target="_blank" rel="noopener" class="{BTN_BIG}">Message on WhatsApp</a>', c)
    if "PLACEHOLDER" in c:
        raise SystemExit("Er staat nog een placeholder in het contactblok")
    return c


def footer():
    f = part("footer")
    return sub(f, '<p class="text-sm text-deep-foreground/80">Mahaba Beach · Ununio, Dar es Salaam, Tanzania</p>',
                  '<p class="text-sm text-deep-foreground/80">Mahaba Beach · Ununio, Dar es Salaam, Tanzania</p>'
                  f'<p class="text-sm text-deep-foreground/80"><a href="https://wa.me/255757014929" target="_blank" rel="noopener" class="underline decoration-dashed underline-offset-4">WhatsApp {WA_NUMBER}</a> · '
                  f'<a href="mailto:{EMAIL}" class="underline decoration-dashed underline-offset-4">{EMAIL}</a> · '
                  f'<a href="{FACEBOOK}" target="_blank" rel="noopener" class="underline decoration-dashed underline-offset-4">Facebook</a></p>')


LIGHTBOX = '''<dialog id="lightbox" class="lightbox" aria-label="Photo"><form method="dialog"><button class="lightbox-close" aria-label="Close photo">×</button></form><img alt=""></dialog>
<script>
(function(){
  var d=document.getElementById('lightbox'); if(!d||!d.showModal) return;
  var im=d.querySelector('img');
  document.querySelectorAll('button[aria-label^="Open photo"]').forEach(function(b){
    b.addEventListener('click',function(){var s=b.querySelector('img'); im.src=s.currentSrc||s.src; im.alt=s.alt; d.showModal();});
  });
  d.addEventListener('click',function(e){ if(e.target===d) d.close(); });
})();
</script>'''

# ---------------------------------------------------------------- pages

PAGES = [
    ("index", None, "Mahaba Beach – Beach stay in Ununio, Tanzania",
     "Small beach resort in the fishing village of Ununio, between Dar es Salaam and Bagamoyo. Rooms from $45 for two, beach camping, fresh fish from the dhows and Bloops snorkel trips.",
     lambda: hero() + ticker() + part("intro") + gallery() + hosts(), True),
    ("stay", "stay", "Stay – Mahaba Beach, Ununio",
     "Rooms at Mahaba Beach for $45 per night for two people, with mosquito net, private bathroom and air conditioning. Beach camping $10 per person.",
     lambda: '<div class="page-top"></div>' + stay(), False),
    ("food", "food", "Food – Mahaba Beach, Ununio",
     "Fresh fish from the Ununio fishermen on the charcoal grill: kingfish, tuna, lobster and prawns, under the big banda at Mahaba Beach.",
     lambda: '<div class="page-top"></div>' + food() + part("banda"), False),
    ("bloops-tours", "bloops-tours", "Bloops Tours – Snorkel trips from Mahaba Beach",
     "Snorkel trips on our own boat to the Fungu Yasini sandbank and Mbudia Island. Prices per person, gear, fruit and crew included.",
     lambda: '<div class="page-top"></div>' + tours() + PACKAGE, False),
    ("getting-here", "getting-here", "Getting here & booking – Mahaba Beach, Ununio",
     "How to reach Mahaba Beach in Ununio, north of Dar es Salaam, and how to book a room, camping spot or snorkel trip by WhatsApp or e-mail.",
     lambda: '<div class="page-top"></div>' + contact(True), False),
    ("404", None, "Page not found – Mahaba Beach", "This page does not exist.",
     lambda: '<div class="page-top"></div><section class="notfound"><div class="mx-auto w-full max-w-3xl px-5 md:px-10 text-center">'
             '<p class="hand text-2xl md:text-3xl rotate-[-2deg] text-sunset">oops</p>'
             '<h1 class="display-lg mt-5">Lost at <em class="text-ocean">sea?</em></h1>'
             '<p class="mt-8 text-xl leading-relaxed text-muted-foreground">This page does not exist. Head back to the beach.</p>'
             f'<p class="mt-10"><a href="/" class="{BTN_BIG}">Back to Mahaba Beach</a></p></div></section>', False),
]


def render(slug, active, title, desc, body, lightbox):
    extra = ""
    if slug == "404":
        extra = '<meta name="robots" content="noindex">\n'
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
{extra}<meta name="theme-color" content="#3B2414">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="website">
<meta property="og:image" content="/assets/og-image.jpg">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght,SOFT,WONK@0,9..144,400..900,0..100,0..1;1,9..144,400..900,0..100,0..1&amp;family=Manrope:wght@400;500;600;700;800&amp;family=Caveat:wght@500;600;700&amp;display=swap">
<link rel="stylesheet" href="/assets/lovable.css">
<link rel="stylesheet" href="/assets/extra.css">
</head>
<body>
{header(active)}<main>{body()}</main>{footer()}
{LIGHTBOX if lightbox else ""}
</body>
</html>
'''


def build(out, preview=False):
    os.makedirs(os.path.join(out, "assets"), exist_ok=True)
    for slug, active, title, desc, body, lb in PAGES:
        html = render(slug, active, title, desc, body, lb)
        if preview:
            html = html.replace('href="/"', 'href="index.html"')
            html = re.sub(r'href="/(stay|food|bloops-tours|getting-here)(#[a-z-]+)?"', r'href="\1.html\2"', html)
            html = html.replace('"/assets/', '"assets/').replace('href="/favicon.ico"', 'href="favicon.ico"').replace('href="/apple-touch-icon.png"', 'href="apple-touch-icon.png"')
        with open(os.path.join(out, f"{slug}.html"), "w", encoding="utf-8") as f:
            f.write(html)
    for css in ("lovable.css", "extra.css"):
        shutil.copy2(os.path.join(LOV if css == "lovable.css" else os.path.join(ROOT, "build"), css), os.path.join(out, "assets", css))


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--preview":
        out = sys.argv[2]
        src = os.path.join(ROOT, "public")
        for item in os.listdir(src):
            if item.endswith(".html") or item in ("sitemap.xml", "robots.txt"):
                continue
            s, d = os.path.join(src, item), os.path.join(out, item)
            if os.path.isdir(s):
                shutil.copytree(s, d, dirs_exist_ok=True)
            else:
                shutil.copy2(s, d)
        build(out, preview=True)
    else:
        build(os.path.join(ROOT, "public"))
    print("ok")
