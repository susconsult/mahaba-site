#!/usr/bin/env python3
"""Taalversies van mahababeach.com.

De Engelse pagina's in public/*.html zijn de bron. Dit script:
  python3 build/i18n.py extract   -> build/i18n/en.json (alle te vertalen teksten)
  python3 build/i18n.py build     -> public/{sw,fr,es,de}/*.html + taalknop/hreflang in alle pagina's
Ontbreekt een vertaling, dan stopt het script met een lijst (niets half gebouwd).
Geen bouwstap op Cloudflare: de gemaakte bestanden worden mee gecommit.
"""
import html, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PUB = ROOT / "public"
I18N = ROOT / "build" / "i18n"
PAGES = ["index", "stay", "food", "bloops-tours", "getting-here", "thanks", "404"]
LANGS = {  # code: (naam in eigen taal, korte label)
    "en": ("English", "EN"),
    "sw": ("Kiswahili", "SW"),
    "fr": ("Français", "FR"),
    "es": ("Español", "ES"),
    "de": ("Deutsch", "DE"),
}
SITE = "https://mahababeach.com"
INLINE = {"em", "strong", "b", "i", "br", "small"}
ATTRS = ("alt", "aria-label", "placeholder", "title")
META = re.compile(r'(<meta (?:name="description"|property="og:title"|property="og:description") content=")([^"]*)(")')
LETTER = re.compile(r"[A-Za-zÀ-ÿ]")
# blokken die we niet aanraken: scripts, stijl, en eerder ingevoegde taalknop/scripts
SKIP_BLOCK = re.compile(r"(<script\b.*?</script>|<style\b.*?</style>|<!--i18n-->.*?<!--/i18n-->)", re.S)
TOKEN = re.compile(r"(<[^>]+>)")


def tag_name(t):
    m = re.match(r"</?\s*([a-zA-Z0-9]+)", t)
    return m.group(1).lower() if m else ""


def norm(s):
    return re.sub(r"\s+", " ", s).strip()


def units(fragment):
    """Splits een stuk HTML (zonder script/style) in tekst-eenheden.

    Een eenheid = aaneengesloten tekst + inline opmaak (em, br, span lang=sw ...).
    Geeft lijst van (start, end) posities in fragment terug.
    """
    toks = [(m.start(), m.end(), m.group(0)) for m in TOKEN.finditer(fragment)]
    # tekststukken tussen tags
    pieces, pos = [], 0
    for s, e, t in toks:
        if s > pos:
            pieces.append(("text", pos, s, fragment[pos:s]))
        pieces.append(("tag", s, e, t))
        pos = e
    if pos < len(fragment):
        pieces.append(("text", pos, len(fragment), fragment[pos:]))

    out, cur, span_stack, raw = [], None, [], None
    for kind, s, e, t in pieces:
        inline = False
        if kind == "tag":
            n = tag_name(t)
            if n in INLINE:
                inline = True
            elif n == "span" and not t.startswith("</"):
                is_sw = 'lang="sw"' in t
                span_stack.append(is_sw)
                inline = is_sw
            elif n == "span" and t.startswith("</"):
                inline = span_stack.pop() if span_stack else False
        if kind == "text" or inline:
            if cur is None:
                cur = [s, e]
            else:
                cur[1] = e
        else:
            if cur:
                out.append(tuple(cur))
            cur = None
    if cur:
        out.append(tuple(cur))
    res = []
    for s, e in out:
        txt = fragment[s:e]
        plain = re.sub(r"<[^>]+>", "", txt)
        if LETTER.search(html.unescape(plain)):
            # strip omringende witruimte uit het bereik
            ls = len(txt) - len(txt.lstrip())
            rs = len(txt) - len(txt.rstrip())
            res.append((s + ls, e - rs))
    return res


def split_doc(doc):
    """Geeft [(is_code, stuk)] waarbij code-stukken niet vertaald worden."""
    parts, pos = [], 0
    for m in SKIP_BLOCK.finditer(doc):
        parts.append((False, doc[pos:m.start()]))
        parts.append((True, m.group(0)))
        pos = m.end()
    parts.append((False, doc[pos:]))
    return parts


def walk(doc, fn):
    """Roept fn(soort, sleutel) op voor elke vertaalbare tekst en vervangt door het resultaat."""
    out = []
    for is_code, part in split_doc(doc):
        if is_code:
            out.append(part)
            continue
        # <title>
        part = re.sub(r"(<title>)(.*?)(</title>)", lambda m: m.group(1) + fn("title", norm(m.group(2))) + m.group(3), part, flags=re.S)
        part = META.sub(lambda m: m.group(1) + fn("meta", m.group(2)) + m.group(3), part)

        def attr_sub(m):
            t = m.group(0)
            for a in ATTRS:
                t = re.sub(r'(\s%s=")([^"]*)(")' % a,
                           lambda mm: mm.group(1) + (fn("attr", mm.group(2)) if LETTER.search(mm.group(2)) else mm.group(2)) + mm.group(3), t)
            return t
        # body-tekst: alleen binnen <body>
        b = part.find("<body")
        head, body = (part[:b], part[b:]) if b >= 0 else ("", part)
        if b < 0 and "<title>" in part:
            head, body = part, ""
        body = TOKEN.sub(attr_sub, body)
        res, pos = [], 0
        for s, e in units(body):
            res.append(body[pos:s])
            key = norm(body[s:e])
            res.append(fn("text", key))
            pos = e
        res.append(body[pos:])
        out.append(head + "".join(res))
    return "".join(out)


def source(page):
    return (PUB / f"{page}.html").read_text(encoding="utf-8")


def extract():
    keys = {}
    for p in PAGES:
        def fn(kind, k, p=p):
            keys.setdefault(k, {"pages": [], "kind": kind})
            if p not in keys[k]["pages"]:
                keys[k]["pages"].append(p)
            return k
        walk(strip_i18n(source(p)), fn)
    I18N.mkdir(parents=True, exist_ok=True)
    data = {k: v for k, v in keys.items()}
    (I18N / "en.json").write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    print(len(data), "teksten ->", I18N / "en.json")


# ---------- bouwen ----------

def strip_i18n(doc):
    return re.sub(r"<!--i18n-->.*?<!--/i18n-->", "", doc, flags=re.S)


def url_for(lang, page):
    slug = "" if page == "index" else page
    return f"/{slug}" if lang == "en" else f"/{lang}/{slug}"


def localize_links(doc, lang):
    if lang == "en":
        return doc
    def fix(m):
        attr, url = m.group(1), m.group(2)
        if url.startswith("/assets/") or url.startswith("/api/") or url.startswith("//") or not url.startswith("/"):
            return m.group(0)
        if re.match(r"^/(favicon|apple-touch|icon-|robots|sitemap|og-)", url):
            return m.group(0)
        return f'{attr}="/{lang}{url if url != "/" else "/"}"'
    return re.sub(r'(href)="(/[^"]*)"', fix, doc)


def switcher(lang, page):
    items = []
    for code, (name, short) in LANGS.items():
        cur = ' aria-current="true"' if code == lang else ""
        items.append(f'<li><a href="{url_for(code, page)}" hreflang="{code}" lang="{code}" data-setlang="{code}"{cur}>{name}</a></li>')
    return ('<!--i18n--><details class="lang-switch"><summary aria-label="Language">'
            f'{LANGS[lang][1]}</summary><ul>{"".join(items)}</ul></details><!--/i18n-->')


def head_links(lang, page):
    if page in ("thanks", "404"):
        return ""
    alt = "".join(f'<link rel="alternate" hreflang="{c}" href="{SITE}{url_for(c, page)}">' for c in LANGS)
    alt += f'<link rel="alternate" hreflang="x-default" href="{SITE}{url_for("en", page)}">'
    return alt + f'<link rel="canonical" href="{SITE}{url_for(lang, page)}">'


AUTO = """<script>
(function(){try{
var k='mb_lang',L=['sw','fr','es','de'],s=localStorage.getItem(k);
document.addEventListener('click',function(e){var a=e.target.closest&&e.target.closest('[data-setlang]');if(a)try{localStorage.setItem(k,a.getAttribute('data-setlang'))}catch(_){}});
if(s)return;
var cur=document.documentElement.lang;localStorage.setItem(k,cur);
if(cur!=='en')return;
var n=(navigator.languages&&navigator.languages[0]||navigator.language||'').slice(0,2).toLowerCase();
if(L.indexOf(n)<0)return;
localStorage.setItem(k,n);
location.replace('/'+n+(location.pathname==='/'?'/':location.pathname)+location.search+location.hash);
}catch(_){}})();
</script>"""


def decorate(doc, lang, page):
    doc = strip_i18n(doc)
    doc = re.sub(r'<html lang="[^"]*"', f'<html lang="{lang}"', doc, count=1)
    extra = head_links(lang, page)
    if page not in ("thanks", "404"):
        extra += AUTO
    doc = doc.replace("</head>", f"<!--i18n-->{extra}<!--/i18n-->\n</head>", 1)
    doc = doc.replace('<div class="header-actions">', '<div class="header-actions">' + switcher(lang, page), 1)
    # formulier: taal meesturen, zodat de bedankpagina in dezelfde taal komt
    doc = re.sub(r'(<form [^>]*class="bform[^>]*>)', r'\1' + f'<!--i18n--><input type="hidden" name="lang" value="{lang}"><!--/i18n-->', doc, count=1)
    return doc


def build():
    tr = {}
    missing = {}
    en = json.loads((I18N / "en.json").read_text(encoding="utf-8"))
    for lang in LANGS:
        if lang == "en":
            continue
        f = I18N / f"{lang}.json"
        tr[lang] = json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}
        miss = [k for k in en if not tr[lang].get(k)]
        if miss:
            missing[lang] = miss
    # nieuwe Engelse teksten die nog niet in en.json staan?
    new = set()
    for p in PAGES:
        walk(strip_i18n(source(p)), lambda kind, k: (new.add(k) if k not in en else None) or k)
    if new or missing:
        if new:
            print("Nieuwe Engelse teksten, eerst 'extract' en vertalen:", *sorted(new)[:20], sep="\n  ")
        for l, m in missing.items():
            print(f"{l}: {len(m)} vertalingen ontbreken, bv.", *m[:10], sep="\n  ")
        sys.exit(1)
    for p in PAGES:
        src = strip_i18n(source(p))
        (PUB / f"{p}.html").write_text(decorate(src, "en", p), encoding="utf-8")
        for lang, t in tr.items():
            doc = walk(src, lambda kind, k, t=t: t[k])
            doc = localize_links(doc, lang)
            doc = decorate(doc, lang, p)
            out = PUB / lang / f"{p}.html"
            out.parent.mkdir(exist_ok=True)
            out.write_text(doc, encoding="utf-8")
    sitemap()
    print("klaar:", ", ".join(tr), "x", len(PAGES), "pagina's")


def sitemap():
    rows = []
    for p in PAGES:
        if p in ("thanks", "404"):
            continue
        alts = "".join(f'<xhtml:link rel="alternate" hreflang="{c}" href="{SITE}{url_for(c, p)}"/>' for c in LANGS)
        for c in LANGS:
            rows.append(f"  <url><loc>{SITE}{url_for(c, p)}</loc>{alts}</url>")
    (PUB / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
        + "\n".join(rows) + "\n</urlset>\n", encoding="utf-8")


if __name__ == "__main__":
    {"extract": extract, "build": build}[sys.argv[1] if len(sys.argv) > 1 else "build"]()
