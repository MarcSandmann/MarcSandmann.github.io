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

function renderPresentations() {
  if (typeof PRESENTATIONS === "undefined") return;

  const homeList = document.querySelector("[data-home-presentations]");
  if (homeList) {
    if (PRESENTATIONS.length === 0) {
      homeList.innerHTML = `<p class="text-muted" style="margin:0;font-size:14px">Der Bereich wird gerade gefüllt. Die ersten Folien folgen im Herbst.</p>`;
    } else {
      PRESENTATIONS.slice(0, 3).forEach((p) => homeList.appendChild(entryLinkEl(p.title, p.file)));
    }
  }

  document.querySelectorAll("[data-count='praesentationen']").forEach((el) => {
    el.textContent = PRESENTATIONS.length === 0 ? "in Arbeit" : PRESENTATIONS.length;
  });

  const grid = document.querySelector("[data-presentations-grid]");
  if (grid) {
    if (PRESENTATIONS.length === 0) {
      grid.innerHTML = `
        <div class="presentations-empty">
          <h3>Der Bereich wird gerade aufgebaut.</h3>
          <p>Die ersten Vorträge aus dem Studium werden derzeit für die Veröffentlichung durchgesehen. Wenn du eine bestimmte Präsentation suchst, frag sie gern direkt an.</p>
        </div>`;
    } else {
      grid.className = "download-grid";
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
  renderPresentations();
});
