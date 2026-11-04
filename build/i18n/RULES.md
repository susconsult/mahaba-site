# Vertaalregels mahababeach.com

Bron: `build/i18n/en.json` — elke sleutel is een Engelse tekst van de site (soms met inline HTML).
Uitvoer: `build/i18n/<taal>.json` — een JSON-object `{ "<exacte Engelse sleutel>": "<vertaling>" }` met **alle** sleutels.

Context: Mahaba Beach is a small, family-run beach resort (huts/rooms, beach camping) in the fishing village of Ununio, north of Dar es Salaam, Tanzania. Run by Bea and Saddy Msumi. Bloops (Bloops Tours) is their own boat for snorkel trips. Tone: warm, simple, personal, short sentences, like a friendly postcard. Not touristic marketing.

Rules:
1. Keep every HTML tag exactly as in the key (`<em class="...">`, `<br>`, `<small>`, `<span lang="sw">`), same attributes; you may move a tag to where it fits the grammar, but the same tags must be present and the emphasised words must stay emphasised.
2. Keep HTML entities as entities (`&amp;` stays `&amp;`). Do not introduce raw `<`, `>` or `&` elsewhere.
3. Do NOT translate (copy as-is): Mahaba, Mahaba Beach, Bloops, Bloops Tours, Bea, Saddy, Msumi, Ununio, Fungu Yasini, Mbudia, Dar es Salaam, Bagamoyo, DAR, Facebook, Google Maps, TSh amounts, prices in $, times.
4. Swahili words stay Swahili in every language: Karibu, Karibu tena, Karibu Mahaba, Karibu nyumbani, karibu chakula, lala salama, pole pole, twende baharini, hakuna matata, safari njema, asante sana, pole!, samaki wabichi, banda, dhow (may use the local word for dhow if natural). Keys that consist only of such Swahili words: return them unchanged. Inside `<span lang="sw">…</span>` keep the Swahili unchanged; translate only the text around it.
5. "Stay", "Food", "Getting here", "Book", "Home" are navigation labels: keep them short (1–2 words).
6. Keys starting with "Open photo: " → translate as "<your word for Open photo>: <translated description>", consistent with the separate description key.
7. Form labels must stay short. "E-mail" → normal word for e-mail. Keep "WhatsApp".
8. Use the polite-but-friendly register customary for hospitality: French "vous", Spanish "tú", German "du", Swahili natural everyday Swahili (Tanzanian).
9. "per room, 2 people" style price captions: short, lowercase like the source.
10. "×" stays "×".
11. Output valid JSON (UTF-8, no comments). Same number of keys as en.json. Values never empty.
