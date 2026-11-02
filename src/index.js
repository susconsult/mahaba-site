// Mahaba Beach: alleen /api/booking komt hier binnen (zie run_worker_first in wrangler.jsonc).
// Al de rest serveert Cloudflare rechtstreeks uit public/.
//
// Een boekingsaanvraag wordt doorgestuurd naar het Apps Script van de Google Sheet
// (variabele SHEET_URL in Cloudflare). Alleen een antwoord {"ok":true} telt als geslaagd.

const TYPES = ["room", "camping", "trip", "package", "meal"];
const TOURS = ["fungu-half", "fungu-full", "mbudia", "fungu-mbudia", "not-sure"];

function json(body, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" },
  });
}

function clean(v, max = 200) {
  return typeof v === "string" ? v.trim().slice(0, max) : "";
}

function isDate(v) {
  return /^\d{4}-\d{2}-\d{2}$/.test(v);
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname !== "/api/booking") return env.ASSETS.fetch(request);
    if (request.method !== "POST") return json({ ok: false, error: "method" }, 405);

    let d;
    try {
      d = await request.json();
    } catch {
      return json({ ok: false, error: "bad-request" }, 400);
    }

    // Spam-val: dit veld is onzichtbaar voor mensen. Ingevuld = bot. Doe alsof het lukte.
    if (clean(d.website)) return json({ ok: true, id: clean(d.id, 40) });

    const b = {
      id: clean(d.id, 40),
      type: clean(d.type, 20),
      tour: clean(d.tour, 20),
      arrival: clean(d.arrival, 10),
      departure: clean(d.departure, 10),
      date: clean(d.date, 10),
      adults: Math.max(0, Math.min(50, parseInt(d.adults, 10) || 0)),
      children: Math.max(0, Math.min(50, parseInt(d.children, 10) || 0)),
      name: clean(d.name, 120),
      email: clean(d.email, 160),
      phone: clean(d.phone, 40),
      message: clean(d.message, 2000),
      page: clean(d.page, 200),
    };

    const errors = [];
    if (!/^[A-Za-z0-9-]{6,40}$/.test(b.id)) errors.push("id");
    if (!TYPES.includes(b.type)) errors.push("type");
    if (b.type === "trip" && !TOURS.includes(b.tour)) errors.push("tour");
    if (["room", "camping", "package"].includes(b.type)) {
      if (!isDate(b.arrival)) errors.push("arrival");
      if (!isDate(b.departure) || b.departure <= b.arrival) errors.push("departure");
    } else if (!isDate(b.date)) errors.push("date");
    if (b.adults < 1) errors.push("adults");
    if (!b.name) errors.push("name");
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(b.email)) errors.push("email");
    if (errors.length) return json({ ok: false, error: "invalid", fields: errors }, 400);

    if (!env.SHEET_URL) return json({ ok: false, error: "not-configured" }, 503);

    try {
      const r = await fetch(env.SHEET_URL, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify(b),
        redirect: "follow",
      });
      const out = await r.json().catch(() => null);
      if (out && out.ok === true) return json({ ok: true, id: b.id });
      return json({ ok: false, error: "sheet" }, 502);
    } catch {
      return json({ ok: false, error: "sheet" }, 502);
    }
  },
};
