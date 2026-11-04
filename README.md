# Mahaba Beach – website

Website voor **Mahaba Beach**, een klein strandresort in het vissersdorp Ununio (Tanzania), tussen Dar es Salaam en Bagamoyo. Uitgebaat door Bea en Saddy Msumi. Bloops Tours is hun eigen snorkeltour-tak.

Wolfpakket van SUS Consult. Statische site, gepubliceerd als Cloudflare Worker `mahaba-site`.

## Pagina's

| Adres | Inhoud |
|---|---|
| `/` | Hero met drone-video, prijsband, intro, galerij (met foto vergroten), hosts |
| `/stay` | Kamers ($45 per nacht voor 2) en kamperen ($10 per persoon) |
| `/food` | Eten en de banda |
| `/bloops-tours` | Snorkeltrips met prijstabel en het $100-pakket |
| `/getting-here` | Ligging en boekingsformulier (in de postkaart, `#contact`) |
| `/thanks` | Bedankpagina na een aanvraag (noindex) |
| `404.html` | Eigen "Lost at sea?"-pagina |

## Hoe het gebouwd is

- Het ontwerp komt van Lovable (`pixel-perfect-replay-09755.lovable.app`).
- **Let op: `public/` is de bron.** `build/build.py` heeft de eerste versie gemaakt, maar loopt achter: latere wijzigingen (foto's, Saddy, eten op reservatie, formulier) zijn rechtstreeks in `public/` gebeurd. Niet meer draaien, anders gaan die verloren.
- Header en footer staan in elke pagina; een wijziging daaraan doorvoeren op alle pagina's.
- `public/assets/extra.css`: alles wat Lovable niet had (video-filter, prijstabel, pakket, gsm-menu, foto vergroten, formulier).

## Onderdelen

- **Boekingsformulier** op `/getting-here#contact`. Alle boekknoppen sturen daarheen, met `?for=room|camping|package|bloops|meal` om de keuze voor te vullen. Er staan **geen WhatsApp- of e-maillinks** meer op de site (keuze Pieter, nov 2026). Facebook staat nog als link in de footer.
- Werkt zonder JavaScript: het formulier post naar `/api/book` (`src/index.js`). Die controleert de velden, geeft elke aanvraag een ID en stuurt ze door naar het Apps Script van de Google Sheet. Alleen een antwoord `{"ok":true}` telt als geslaagd → `/thanks`. Anders terug naar het formulier met een foutmelding (`?error=1`).
- Spam-val: onzichtbaar veld `website`; is het ingevuld, dan wordt niets bewaard (bot ziet wel de bedankpagina).
- Apps Script: `apps-script/Code.gs` (kopie, de echte staat in de sheet). Schrijft een rij in tab `Aanvragen`, weigert dubbele ID's, zet per rij een vinkje "Opgevolgd" en stuurt een meldingsmail (`NOTIFY` bovenaan het script; antwoorden gaat rechtstreeks naar de gast).
- Alleen `/api/*` loopt langs de code (`run_worker_first` in `wrangler.jsonc`); al de rest zijn gewone bestanden.
- `sitemap.xml` en `robots.txt` voor mahababeach.com.
- Geen database, geen meetcodes, geen cookies. Externe bronnen: alleen Google Fonts.

## Variabelen in Cloudflare

| Naam | Type | Wat |
|---|---|---|
| `SHEET_URL` | Secret | het `.../exec`-adres van de Apps Script web-app |

Lokaal testen: `.dev.vars` met `SHEET_URL=...` (staat in `.gitignore`), dan `npx wrangler dev`.

## Talen

- Engels is de bron: `public/*.html`. Vertaalde kopieën staan in `public/sw/`, `public/fr/`, `public/es/`, `public/de/` (adressen `/fr/stay` enz.). **Die niet met de hand aanpassen**, ze worden gemaakt door `build/i18n.py`.
- Werkwijze bij een tekstwijziging: Engelse pagina aanpassen → `python3 build/i18n.py extract` → nieuwe/gewijzigde teksten vertalen in `build/i18n/{sw,fr,es,de}.json` (regels: `build/i18n/RULES.md`) → `python3 build/i18n.py build` → alles committen. Het script weigert te bouwen zolang er een vertaling ontbreekt.
- Wijziging aan header/footer of stijl: Engelse pagina's aanpassen en `build` draaien; de taalknop, hreflang/canonical en het verborgen veld `lang` in het formulier worden er telkens opnieuw in gezet (tussen `<!--i18n-->`-markeringen).
- Taalknop (EN/SW/FR/ES/DE) in de header. Eerste bezoek op een Engelse pagina: doorsturen naar de browsertaal als die sw/fr/es/de is; de keuze wordt onthouden in `localStorage` (`mb_lang`), daarna nooit meer automatisch doorsturen. Geen cookies.
- Formulier: veld `lang` → bedankpagina/foutmelding in dezelfde taal; in de sheet staat de taal vooraan in het bericht, bv. `[Français] ...`.
- Swahili labels (karibu, pole pole, hakuna matata ...) blijven in alle talen staan.
- Vertalingen gemaakt door Claude (nov 2026), niet nagekeken door moedertaalsprekers. Swahili: Bea/Saddy laten nakijken. Swahili prijslijst gebruikt Swahili-uren (saa 3 asubuhi = 9u).
- `sitemap.xml` bevat alle talen met hreflang.

## Beelden

`public/assets/img/` — foto's van Mahaba, verkleind voor het web. `public/assets/hero-drone.mp4` is een lus van 15 s uit de drone-video (zonder geluid). Begint met het zeeshot (bootjes langs het strand), dan de banda; geen fade naar zwart, eind vloeit naadloos over in het begin. Poster `hero-drone.jpg` = eerste beeld. Logo en badge: `public/assets/logo-mahaba-beach.png`, `public/assets/badge-mahaba-beach.png`.

## Wat staat waar

| Wat | Waar | Login |
|---|---|---|
| Code | GitHub `susconsult/mahaba-site` | SUS Consult GitHub |
| Hosting | Cloudflare Worker `mahaba-site`, gekoppeld aan deze repo (push naar main = live) — mahaba-site.pieter-2d7.workers.dev | Cloudflare-account SUS Consult |
| Ontwerp (bron) | Lovable-project `pixel-perfect-replay-09755` | Lovable-account Pieter |
| Domein | mahababeach.com, aan de Worker gekoppeld | Cloudflare-account SUS Consult |
| Aanvragen | Google Sheet "Mahaba Beach – boekingsaanvragen" (https://docs.google.com/spreadsheets/d/1SAf17Q0RiHTzsKwEaw-XszdsiTtqHLgsz4qokOxlMyM), map KLANTEN/Mahaba Beach, script-project "Mahaba Beach boekingen" | pieter@susconsult.be |

## Contact klant

- WhatsApp: +255 757 014 929
- E-mail: mahababeach@gmail.com
- Facebook: https://www.facebook.com/mahababeach/

## Open

- Instagram van Bea (@beatriceanthoniozmsumi) op de site zetten? Eerst haar akkoord vragen.
- Sinds welk jaar baten Bea en Saddy Mahaba uit (staat nu niet op de site).
- Lovable-tekst "Saddy is a local Rastafarian…" is weggelaten tot Pieter bevestigt dat het klopt.
- Foto van Bea en Saddy zelf (hosts-blok toont nu de badge).
- Drone-video in hogere resolutie (nu 960×540).

## Contact per onderdeel (nov 2026)
- Bea (+255 757 014 929): kamers, keuken, packages.
- Saddy (+255 689 182 161): Bloops boottochten.
- Geen van beide nummers staat nog op de site: alles loopt via het formulier.
- Open: betekenis van de naam BLOOPS toevoegen zodra Bea die geeft.
- Foto's (nov 2026): bar-wood, banda-wide, bbq-sign op /food; porch, room-bed, room-side op /stay; bloops-shop op /bloops-tours; beach-huts in de home-galerij. Geen foto van de Bloops-boot (niet nodig volgens Pieter).
- Foto's (nov 2026, 2e reeks): Bloops-galerij (boot, instappen, boeg, zandbank, gasten, video bloops-boat.mp4 zonder geluid, shop, materiaal); overlanders (Defender, Unimog) op /stay; mahaba-from-sea in home-galerij.
- Food: geen restaurant met menu; eten enkel op reservatie — ze kopen vers bij vissers en markt en koken het. Knop 'Reserve a meal' naar het formulier (`?for=meal`). Getting here: coast-from-sea en overland-saviem.
- Drukwerk voor Bea: **A4-poster** en **A5-flyer**. Flyer 5 pagina's: logo / kamers + restaurant / Bloops / contact (mail, website, WhatsApp, ligging) / package. Op drukwerk mag WhatsApp wel (op de site niet). Moet zowel in zwart-wit als in kleur goed printen (contrast niet enkel via kleur, geen tekst op foto zonder vlak erachter).
- Swahili-labels (nov 2026, `lang="sw"`): Karibu nyumbani, samaki wabichi (home), lala salama (stay), karibu chakula + pole pole (food), twende baharini + hakuna matata (bloops), safari njema (getting here), pole! (404). Nog niet door Bea nagekeken.
- Zandbank = Fungu Yasini (Bea schrijft "Yassini"; site houdt "Yasini").
- Open: welk mailadres de boekingsaanvragen moet krijgen (nu enkel pieter@susconsult.be; vermoedelijk ook mahababeach@gmail.com) — `NOTIFY` in het Apps Script.
