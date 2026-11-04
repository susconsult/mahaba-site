// Mahaba Beach: alleen /api/book loopt langs deze code, de rest zijn gewone bestanden in public/.
// Een boekingsaanvraag wordt doorgestuurd naar het Apps Script van de Google Sheet.
// Variabele in Cloudflare (Runtime variables, type Secret): SHEET_URL = .../exec-adres van de web-app.

const FOR = ["room", "camping", "package", "bloops", "meal"];
const MAX = { name: 120, email: 200, phone: 40, message: 2000 };

function back(url, kind, params = "") {
  return Response.redirect(new URL(kind === "ok" ? "/thanks" : `/getting-here?error=1${params}#contact`, url), 303);
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname !== "/api/book") return env.ASSETS.fetch(request);
    if (request.method !== "POST") return new Response("Method not allowed", { status: 405, headers: { Allow: "POST" } });

    let f;
    try { f = await request.formData(); } catch { return back(url, "error"); }
    const get = (k) => String(f.get(k) ?? "").trim();

    // spam-val: mensen zien dit veld niet
    if (get("website")) return back(url, "ok");

    const b = {
      name: get("name").slice(0, MAX.name),
      email: get("email").slice(0, MAX.email),
      phone: get("phone").slice(0, MAX.phone),
      for: get("for"),
      arrival: get("arrival"),
      departure: get("departure"),
      guests: parseInt(get("guests"), 10),
      message: get("message").slice(0, MAX.message),
    };
    const date = /^\d{4}-\d{2}-\d{2}$/;
    const forParam = FOR.includes(b.for) ? `&for=${b.for}` : "";
    if (!b.name || !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(b.email) || !FOR.includes(b.for) ||
        !date.test(b.arrival) || (b.departure && !date.test(b.departure)) ||
        !(b.guests >= 1 && b.guests <= 50)) {
      return back(url, "error", forParam);
    }
    if (!env.SHEET_URL) { console.error("SHEET_URL ontbreekt"); return back(url, "error", forParam); }

    const record = { id: crypto.randomUUID(), created: new Date().toISOString(), ...b };
    try {
      const r = await fetch(env.SHEET_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(record),
        redirect: "follow",
      });
      const text = await r.text();
      let ok = false;
      try { ok = JSON.parse(text).ok === true; } catch {}
      if (!ok) { console.error("Sheet gaf geen bevestiging", r.status, text.slice(0, 300)); return back(url, "error", forParam); }
    } catch (e) {
      console.error("Sheet niet bereikbaar", e);
      return back(url, "error", forParam);
    }
    return back(url, "ok");
  },
};
