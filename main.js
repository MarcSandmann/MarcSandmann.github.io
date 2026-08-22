function escapeHtml(str) {
  return String(str).replace(/[&<>"']/g, (c) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  }[c]));
}

function entryLinkEl(title, href, meta) {
  const a = document.createElement("a");
  a.className = "entry";
  a.href = href;
  a.innerHTML = meta
    ? `${escapeHtml(title)}<span class="entry-meta text-muted">${escapeHtml(meta)}</span>`
    : escapeHtml(title);
  return a;
}

function renderHausarbeiten() {
  if (typeof HAUSARBEITEN === "undefined") return;

  const homeList = document.querySelector("[data-home-list='hausarbeiten']");
  if (homeList) {
    HAUSARBEITEN.slice(0, 3).forEach((e) => homeList.appendChild(entryLinkEl(e.title, e.href)));
  }

  document.querySelectorAll("[data-count='hausarbeiten']").forEach((el) => {
    el.textContent = HAUSARBEITEN.length;
  });

  const registerList = document.querySelector("[data-register-list='hausarbeiten']");
  if (registerList) {
    HAUSARBEITEN.forEach((e) => registerList.appendChild(entryLinkEl(e.title, e.href)));
  }

  document.querySelectorAll("[data-entry-count='hausarbeiten']").forEach((el) => {
    el.textContent = HAUSARBEITEN.length;
  });
}

function renderPresentations() {
  if (typeof PRESENTATIONS === "undefined") return;

  const homeList = document.querySelector("[data-home-presentations]");
  if (homeList) {
    if (PRESENTATIONS.length === 0) {
      homeList.innerHTML = `<p class="text-muted" style="margin:0;font-size:14px">Bald verfügbar.</p>`;
    } else {
      PRESENTATIONS.slice(0, 3).forEach((p) => homeList.appendChild(entryLinkEl(p.title, p.file)));
    }
  }

  document.querySelectorAll("[data-count='praesentationen']").forEach((el) => {
    el.textContent = PRESENTATIONS.length;
  });

  const grid = document.querySelector("[data-presentations-grid]");
  if (grid) {
    if (PRESENTATIONS.length === 0) {
      grid.innerHTML = `<div class="download-empty">Noch keine Präsentationen online. PDF/PPTX unter <code>/praesentationen/</code> ablegen und in <code>presentations-data.js</code> eintragen.</div>`;
    } else {
      PRESENTATIONS.forEach((p) => {
        const card = document.createElement("div");
        card.className = "download-card";
        card.innerHTML = `<span class="download-card-title">${escapeHtml(p.title)}</span><a class="btn btn-primary" href="${p.file}" download>Download</a>`;
        grid.appendChild(card);
      });
    }
  }
}

document.addEventListener("DOMContentLoaded", () => {
  renderHausarbeiten();
  renderPresentations();
});
