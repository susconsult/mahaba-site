# Mahaba Beach – website

Website voor **Mahaba Beach**, een klein strandresort in het vissersdorp Ununio (Tanzania), tussen Dar es Salaam en Bagamoyo. Uitgebaat door Bea en Sadi Msumi. Bloops Tours is hun eigen snorkeltour-tak.

Wolfpakket van SUS Consult. Statische site, gepubliceerd als Cloudflare Worker `mahaba-site`.

## Pagina's

| Adres | Inhoud |
|---|---|
| `/` | Hero met drone-video, prijsband, intro, galerij (met foto vergroten), hosts |
| `/stay` | Kamers ($45 per nacht voor 2) en kamperen ($10 per persoon) |
| `/food` | Eten en de banda |
| `/bloops-tours` | Snorkeltrips met prijstabel en het $100-pakket |
| `/getting-here` | Ligging en boeken (postkaart, met WhatsApp, e-mail en Facebook) |
| `404.html` | Eigen "Lost at sea?"-pagina |

## Hoe het gebouwd is

- Het ontwerp is **1-op-1 het Lovable-ontwerp** (`pixel-perfect-replay-09755.lovable.app`). De HTML-blokken van Lovable staan in `build/lovable/*.html`, de stylesheet in `build/lovable/lovable.css`.
- `build/build.py` vult de echte inhoud in, verdeelt de blokken over de pagina's en schrijft alles naar `public/`.
- `build/extra.css` bevat alleen wat Lovable niet had: warme filter over de video, prijstabel, pakketblok, actief menu-item, foto vergroten.
- Er is geen bouwstap op Cloudflare: de gegenereerde bestanden in `public/` worden mee gecommit.

**Iets aanpassen:** wijzig `build/build.py` (teksten, prijzen, contact) of `build/extra.css`, draai `python3 build/build.py`, en commit `build/` én `public/` samen. Lovable-tekst die niet meer gevonden wordt, laat het script stoppen met een melding.

Contactgegevens en prijzen staan bovenaan en in de functies van `build/build.py`.

## Onderdelen

- Geen formulier, geen database, geen meetcodes, geen cookies. Boeken gaat via WhatsApp-links (`wa.me/255757014929`) en e-mail.
- Facebook (facebook.com/mahababeach) staat als gewone link in de postkaart en de footer, bewust niet ingesloten (een embed laadt Facebook-scripts en cookies en vraagt dan een cookiebanner).
- Menu op gsm: hamburgerknop naast "Book" (`<details class="mnav">`, zonder JavaScript), toegevoegd omdat Lovable het menu onder 768px verbergt.
- Geen variabelen of secrets in Cloudflare.
- Externe bronnen: alleen Google Fonts (Fraunces, Manrope, Caveat).

## Beelden

`public/assets/img/` — foto's van Mahaba, verkleind voor het web. `public/assets/hero-drone.mp4` is een lus van 20 s uit de drone-video (zonder geluid, groene close-ups eruit). Logo en badge: `public/assets/logo-mahaba-beach.png`, `public/assets/badge-mahaba-beach.png`.

## Wat staat waar

| Wat | Waar | Login |
|---|---|---|
| Code | GitHub `susconsult/mahaba-site` | SUS Consult GitHub |
| Hosting | Cloudflare Worker `mahaba-site` | Cloudflare-account SUS Consult |
| Ontwerp (bron) | Lovable-project `pixel-perfect-replay-09755` | Lovable-account Pieter |
| Domein | nog te bepalen (in de video staat mahababeachresort.com) | ? |

## Contact klant

- WhatsApp: +255 757 014 929
- E-mail: mahababeach@gmail.com
- Facebook: https://www.facebook.com/mahababeach/

## Open

- Worker `mahaba-site` koppelen aan deze repository (bestond al met een "Hello world"-code; workers.dev-adres stond uit).
- Domein: is mahababeachresort.com van hen, en wie beheert het? Daarna `sitemap.xml` toevoegen met de juiste domeinnaam.
- Instagram van Bea (@beatriceanthoniozmsumi) op de site zetten? Eerst haar akkoord vragen.
- Sinds welk jaar baten Bea en Sadi Mahaba uit (staat nu niet op de site).
- Lovable-tekst "Sadi is a local Rastafarian…" is weggelaten tot Pieter bevestigt dat het klopt.
- Foto van Bea en Sadi zelf (hosts-blok toont nu de badge).
- Drone-video in hogere resolutie (nu 960×540).
