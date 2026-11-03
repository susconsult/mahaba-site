// Apps Script voor de sheet "Mahaba Beach – boekingsaanvragen" (account pieter@susconsult.be, map KLANTEN/Mahaba Beach).
// Publiceren: Implementeren > Nieuwe implementatie > Web-app, Uitvoeren als: Ik, Toegang: Iedereen.
// Na elke wijziging: Implementaties beheren > bewerken > Nieuwe versie. Alleen opslaan is niet genoeg.

const NOTIFY = 'pieter@susconsult.be';   // wie een mail krijgt bij een nieuwe aanvraag (komma's voor meerdere)
const SHEET = 'Aanvragen';
const HEAD = ['ID', 'Ontvangen', 'Naam', 'E-mail', 'WhatsApp', 'Wat', 'Aankomst', 'Vertrek', 'Personen', 'Bericht', 'Opgevolgd'];
const LABEL = { room: 'Kamer', camping: 'Kamperen', package: 'Mahaba package', bloops: 'Bloops tour', meal: 'Maaltijd' };

function doPost(e) {
  const lock = LockService.getScriptLock();
  try {
    lock.waitLock(20000);
    const d = JSON.parse(e.postData.contents);
    if (!d.id || !d.name || !d.email) return out({ ok: false, error: 'velden ontbreken' });

    const ss = SpreadsheetApp.getActiveSpreadsheet();
    let sh = ss.getSheetByName(SHEET);
    if (!sh) { sh = ss.insertSheet(SHEET); sh.appendRow(HEAD); sh.setFrozenRows(1); }

    const ids = sh.getLastRow() > 1 ? sh.getRange(2, 1, sh.getLastRow() - 1, 1).getValues().flat() : [];
    if (ids.indexOf(d.id) !== -1) return out({ ok: true, duplicate: true });

    const wat = LABEL[d.for] || d.for;
    sh.appendRow([d.id, new Date(d.created), d.name, d.email, d.phone, wat, d.arrival, d.departure, d.guests, d.message, '']);
    sh.getRange(sh.getLastRow(), HEAD.length).insertCheckboxes();

    MailApp.sendEmail({
      to: NOTIFY,
      replyTo: d.email,
      subject: 'Mahaba Beach – nieuwe aanvraag: ' + wat + ' (' + d.name + ')',
      body: [
        'Wat: ' + wat,
        'Naam: ' + d.name,
        'E-mail: ' + d.email,
        'WhatsApp: ' + (d.phone || '-'),
        'Aankomst / datum: ' + d.arrival,
        'Vertrek: ' + (d.departure || '-'),
        'Personen: ' + d.guests,
        '',
        d.message || '(geen bericht)',
        '',
        'Sheet: ' + ss.getUrl(),
      ].join('\n'),
    });
    return out({ ok: true });
  } catch (err) {
    return out({ ok: false, error: String(err) });
  } finally {
    lock.releaseLock();
  }
}

function out(o) {
  return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON);
}
