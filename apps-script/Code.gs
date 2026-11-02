// Mahaba Beach — boekingsaanvragen van mahababeach.com naar deze sheet + meldingsmail.
// Plakken in: Extensies > Apps Script (in de sheet "Mahaba Beach boekingen").
// Publiceren als web-app: Uitvoeren als "Ik", Toegang "Iedereen".
// Na elke wijziging: Implementeren > Implementaties beheren > bewerken > Nieuwe versie.

const NOTIFY = 'mahababeach@gmail.com'; // meerdere adressen: met komma scheiden
const SHEET_NAME = 'Aanvragen';

const HEADERS = ['ID', 'Ontvangen', 'Type', 'Tour', 'Aankomst', 'Vertrek', 'Datum',
  'Volwassenen', 'Kinderen', 'Naam', 'E-mail', 'WhatsApp/telefoon', 'Bericht', 'Pagina'];

const TYPE_LABEL = { room: 'Room', camping: 'Beach camping', trip: 'Bloops boat trip', package: 'Mahaba package', meal: 'Meal' };
const TOUR_LABEL = { 'fungu-half': 'Fungu Yasini, half day', 'fungu-full': 'Fungu Yasini, full day',
  mbudia: 'Mbudia Island', 'fungu-mbudia': 'Fungu Yasini & Mbudia', 'not-sure': 'Not sure yet' };

function out(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}

function sheet() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sh = ss.getSheetByName(SHEET_NAME);
  if (!sh) sh = ss.insertSheet(SHEET_NAME);
  if (sh.getLastRow() === 0) {
    sh.appendRow(HEADERS);
    sh.setFrozenRows(1);
    sh.getRange(1, 1, 1, HEADERS.length).setFontWeight('bold');
  }
  return sh;
}

function doPost(e) {
  const lock = LockService.getScriptLock();
  try {
    lock.waitLock(20000);
    const d = JSON.parse(e.postData.contents);
    if (!d.id || !d.name || !d.email) return out({ ok: false, error: 'invalid' });

    const sh = sheet();
    const last = sh.getLastRow();
    if (last > 1) {
      const ids = sh.getRange(2, 1, last - 1, 1).getValues().flat();
      if (ids.indexOf(d.id) >= 0) return out({ ok: true, id: d.id, duplicate: true });
    }

    const type = TYPE_LABEL[d.type] || d.type;
    const tour = TOUR_LABEL[d.tour] || d.tour || '';
    // Tekst met ' ervoor zodat Sheets niets als formule of getal leest
    const t = (v) => (v === undefined || v === null || v === '') ? '' : "'" + String(v);
    sh.appendRow([d.id, new Date(), type, tour, t(d.arrival), t(d.departure), t(d.date),
      d.adults, d.children, t(d.name), t(d.email), t(d.phone), t(d.message), d.page || '']);

    const when = d.arrival ? (d.arrival + ' to ' + d.departure) : d.date;
    const body = [
      'New booking request from mahababeach.com', '',
      'Reference: ' + d.id,
      'What: ' + type + (tour ? ' (' + tour + ')' : ''),
      'When: ' + when,
      'People: ' + d.adults + ' adults, ' + d.children + ' children',
      'Name: ' + d.name,
      'E-mail: ' + d.email,
      'WhatsApp/phone: ' + (d.phone || '-'),
      '', 'Message:', d.message || '-', '',
      'Reply to this e-mail to answer the guest directly.'
    ].join('\n');
    MailApp.sendEmail({ to: NOTIFY, replyTo: d.email, subject: 'Booking request ' + d.id + ': ' + type + ', ' + when, body: body });

    return out({ ok: true, id: d.id });
  } catch (err) {
    return out({ ok: false, error: String(err) });
  } finally {
    lock.releaseLock();
  }
}
