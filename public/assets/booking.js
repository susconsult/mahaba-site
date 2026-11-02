// Boekingsformulier op /getting-here#contact
(function () {
  var form = document.getElementById("booking-form");
  if (!form) return;
  var done = document.getElementById("booking-done");
  var errBox = document.getElementById("bk-error");
  var btn = document.getElementById("bk-submit");

  // Type alvast kiezen via ?type=room|camping|trip|package|meal
  var q = new URLSearchParams(location.search).get("type");
  if (q) {
    var r = form.querySelector('input[name="type"][value="' + q + '"]');
    if (r) r.checked = true;
  }

  // Datums: niet in het verleden
  var today = new Date();
  var iso = new Date(today.getTime() - today.getTimezoneOffset() * 60000).toISOString().slice(0, 10);
  form.querySelectorAll('input[type="date"]').forEach(function (i) { i.min = iso; });
  var arr = document.getElementById("bk-arrival"), dep = document.getElementById("bk-departure");
  arr.addEventListener("change", function () {
    if (arr.value) {
      var n = new Date(arr.value + "T12:00:00"); n.setDate(n.getDate() + 1);
      dep.min = n.toISOString().slice(0, 10);
      if (!dep.value || dep.value < dep.min) dep.value = dep.min;
    }
  });

  function type() {
    var c = form.querySelector('input[name="type"]:checked');
    return c ? c.value : "";
  }

  // Juiste velden tonen per type
  function sync() {
    var t = type();
    var stay = t === "room" || t === "camping" || t === "package";
    document.getElementById("bk-stay").hidden = !stay;
    document.getElementById("bk-day").hidden = stay || !t;
    document.getElementById("bk-tour").hidden = t !== "trip";
    document.getElementById("bk-day-label").textContent = t === "meal" ? "Date of the meal" : "Date of the trip";
    arr.required = dep.required = stay;
    document.getElementById("bk-date").required = !stay && !!t;
    document.getElementById("bk-tour-select").required = t === "trip";
  }
  form.addEventListener("change", function (e) { if (e.target.name === "type") sync(); });
  sync();

  function newId() {
    var d = new Date(), p = function (n) { return String(n).padStart(2, "0"); };
    return "MB-" + d.getFullYear() + p(d.getMonth() + 1) + p(d.getDate()) + "-" +
      Math.random().toString(36).slice(2, 6).toUpperCase();
  }
  var id = newId(); // blijft gelijk bij opnieuw proberen, zodat er geen dubbele rij komt

  var MSG = {
    type: "Choose what you would like to book.",
    tour: "Choose a tour.",
    arrival: "Choose your arrival date.",
    departure: "Choose a departure date after your arrival.",
    date: "Choose a date.",
    adults: "At least 1 adult.",
    name: "Fill in your name.",
    email: "Fill in a valid e-mail address, so we can reply.",
  };

  function showError(text) { errBox.textContent = text; errBox.hidden = false; }

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    errBox.hidden = true;
    if (!type()) { showError(MSG.type); return; }
    if (!form.reportValidity()) return;

    var f = new FormData(form), data = { id: id, page: location.pathname };
    f.forEach(function (v, k) { data[k] = typeof v === "string" ? v : ""; });
    if (["room", "camping", "package"].indexOf(data.type) >= 0) { data.date = ""; data.tour = ""; }
    else { data.arrival = ""; data.departure = ""; if (data.type !== "trip") data.tour = ""; }

    btn.disabled = true; btn.textContent = "Sending...";
    fetch("/api/booking", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(data) })
      .then(function (r) { return r.json().catch(function () { return {}; }); })
      .then(function (out) {
        if (out && out.ok === true) {
          document.getElementById("bk-ref").textContent = id;
          form.hidden = true; done.hidden = false;
          done.scrollIntoView({ behavior: "smooth", block: "center" });
        } else if (out && out.error === "invalid" && out.fields && out.fields.length) {
          showError(MSG[out.fields[0]] || "Please check the form.");
        } else {
          showError("Your request could not be sent. Please try again, or e-mail mahababeach@gmail.com.");
        }
      })
      .catch(function () {
        showError("No connection. Check your internet and try again, or e-mail mahababeach@gmail.com.");
      })
      .finally(function () { btn.disabled = false; btn.textContent = "Send booking request"; });
  });
})();
