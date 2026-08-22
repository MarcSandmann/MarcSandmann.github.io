#!/usr/bin/env python3
"""Baut die Essay-Seiten aus essays/*.md.

Ausführen mit:  python3 build_essays.py

Was passiert:
- Jede essays/*.md wird zu essays/<dateiname>.html (Zeitungsartikel).
- essays.html (Übersichtsseite) wird komplett neu geschrieben.
- Der Essay-Block auf index.html wird zwischen den Markern
  <!-- ESSAYS_COUNT_START/END --> und <!-- ESSAYS_LIST_START/END -->
  ersetzt, der Rest von index.html bleibt unverändert.

Neuen Essay ergänzen: eine neue essays/<name>.md anlegen (Frontmatter mit
title/datum/optional kicker, danach der Text in einfachem Markdown:
## Zwischenüberschriften, *kursiv*, **fett**, > Zitate), dann dieses
Skript erneut ausführen.
"""

import html
import re
from pathlib import Path

ROOT = Path(__file__).parent
ESSAYS_DIR = ROOT / "essays"

MONTHS = [
    "Januar", "Februar", "März", "April", "Mai", "Juni",
    "Juli", "August", "September", "Oktober", "November", "Dezember",
]

NAV = """  <nav class="nav">
    <a class="nav-brand" href="{home}index.html" style="text-decoration:none">Marc Sandmann</a>
    <a href="{home}hausarbeiten.html">Hausarbeiten</a>
    <a href="{home}praesentationen.html">Präsentationen</a>
    <a href="{home}essays.html"{current}>Essays</a>
    <a href="{home}index.html#werdegang">Werdegang</a>
    <a href="{home}kontakt.html">Kontakt</a>
  </nav>"""


def parse_frontmatter(text):
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", text, re.DOTALL)
    if not m:
        raise ValueError("Keine gültige Frontmatter gefunden (--- ... ---).")
    raw_meta, body = m.group(1), m.group(2)
    meta = {}
    for line in raw_meta.splitlines():
        if not line.strip() or ":" not in line:
            continue
        key, value = line.split(":", 1)
        meta[key.strip()] = value.strip().strip('"').strip("'")
    return meta, body.strip()


def format_date_de(iso_date):
    y, mo, d = iso_date.split("-")
    return f"{int(d)}. {MONTHS[int(mo) - 1]} {y}"


def inline_format(text):
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
    return text


def markdown_to_html(body):
    escaped = html.escape(body, quote=False)
    blocks = re.split(r"\n\s*\n", escaped.strip())
    html_blocks = []
    plain_text_parts = []
    first_paragraph_done = False

    for block in blocks:
        block = block.strip()
        if not block:
            continue
        if block.startswith("## "):
            heading = inline_format(block[3:].strip())
            html_blocks.append(f"<h2>{heading}</h2>")
        elif all(line.startswith("&gt;") for line in block.splitlines()):
            quote_lines = [line[4:].strip() for line in block.splitlines()]
            quote = inline_format(" ".join(quote_lines))
            html_blocks.append(f"<blockquote><p>{quote}</p></blockquote>")
            plain_text_parts.append(" ".join(quote_lines))
        else:
            joined = " ".join(line.strip() for line in block.splitlines())
            plain_text_parts.append(joined)
            formatted = inline_format(joined)
            if not first_paragraph_done:
                first_char, rest = formatted[0], formatted[1:]
                html_blocks.append(
                    f'<p class="lede"><span class="dropcap">{first_char}</span>{rest}</p>'
                )
                first_paragraph_done = True
            else:
                html_blocks.append(f"<p>{formatted}</p>")

    plain_text = " ".join(plain_text_parts)
    return "\n".join(html_blocks), plain_text


def reading_minutes(plain_text):
    words = len(plain_text.split())
    return max(1, round(words / 200))


def excerpt(plain_text, limit=140):
    text = re.sub(r"\s+", " ", plain_text).strip()
    if len(text) <= limit:
        return text
    return text[:limit].rsplit(" ", 1)[0] + " …"


def build_article(slug, meta, body_html, minutes, date_de):
    title = html.escape(meta.get("title", slug))
    kicker = html.escape(meta.get("kicker", "Essay"))
    nav = NAV.format(home="../", current="")
    return f"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — Essays — Marc Sandmann</title>
<link rel="stylesheet" href="../styles.css">
<link rel="stylesheet" href="../site.css">
<link rel="stylesheet" href="../newspaper.css">
</head>
<body>
<div class="page-shell">
{nav}

  <article class="article">
    <div class="article-head">
      <span class="article-kicker">{kicker}</span>
      <h1>{title}</h1>
      <div class="article-byline">Von Marc Sandmann · {date_de} · {minutes} min Lesezeit</div>
    </div>
    <div class="article-body">
{body_html}
    </div>
  </article>
  <div class="article-footer">
    <a class="btn btn-ghost" href="../essays.html">← Zurück zur Übersicht</a>
  </div>

  <footer class="site-footer text-muted">
    © 2026 Marc Sandmann
  </footer>

</div>
</body>
</html>
"""


def build_front_page(essays):
    nav = NAV.format(home="", current=' aria-current="page"')
    if essays:
        teasers = []
        for e in essays:
            teasers.append(f"""    <a class="teaser" href="essays/{e['slug']}.html">
      <span class="teaser-kicker">{html.escape(e['kicker'])}</span>
      <h2>{html.escape(e['title'])}</h2>
      <p>{html.escape(e['excerpt'])}</p>
      <span class="teaser-meta text-muted">{e['date_de']} · {e['minutes']} min</span>
    </a>""")
        grid = f'  <section class="teaser-grid">\n{"".join(t + chr(10) for t in teasers)}  </section>'
    else:
        grid = '  <div class="newspaper-empty">Noch keine Essays online.</div>'

    return f"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Essays — Marc Sandmann</title>
<meta name="description" content="Kürzere Texte zu Themen, die mich gerade beschäftigen.">
<link rel="stylesheet" href="styles.css">
<link rel="stylesheet" href="site.css">
<link rel="stylesheet" href="newspaper.css">
</head>
<body>
<div class="page-shell">
{nav}

  <header class="hero newspaper-masthead">
    <h6 class="text-muted">Essays</h6>
    <h1>Kürzere Texte zu Themen, die mich gerade beschäftigen.</h1>
  </header>

{grid}

  <div class="register-footer">
    <a class="btn btn-primary" href="index.html">Zur Startseite</a>
  </div>

  <footer class="site-footer text-muted">
    © 2026 Marc Sandmann
  </footer>

</div>
</body>
</html>
"""


def update_homepage(essays):
    index_path = ROOT / "index.html"
    text = index_path.read_text(encoding="utf-8")

    text = re.sub(
        r"(<!-- ESSAYS_COUNT_START -->).*?(<!-- ESSAYS_COUNT_END -->)",
        rf"\g<1>{len(essays)}\g<2>",
        text,
        flags=re.DOTALL,
    )

    if essays:
        items = "\n".join(
            f'        <a class="entry" href="essays/{e["slug"]}.html">{html.escape(e["title"])}'
            f'<span class="entry-meta text-muted">{e["date_de"]}</span></a>'
            for e in essays[:3]
        )
        list_html = f"\n{items}\n        "
    else:
        list_html = ""

    text = re.sub(
        r"(<!-- ESSAYS_LIST_START -->).*?(<!-- ESSAYS_LIST_END -->)",
        lambda m: f"{m.group(1)}{list_html}{m.group(2)}",
        text,
        flags=re.DOTALL,
    )

    index_path.write_text(text, encoding="utf-8")


def main():
    md_files = sorted(ESSAYS_DIR.glob("*.md"))
    essays = []

    for md_file in md_files:
        meta, body = parse_frontmatter(md_file.read_text(encoding="utf-8"))
        if "title" not in meta or "datum" not in meta:
            raise ValueError(f"{md_file.name}: 'title' und 'datum' sind Pflichtfelder in der Frontmatter.")

        body_html, plain_text = markdown_to_html(body)
        minutes = reading_minutes(plain_text)
        date_de = format_date_de(meta["datum"])
        slug = md_file.stem

        essays.append({
            "slug": slug,
            "title": meta["title"],
            "kicker": meta.get("kicker", "Essay"),
            "datum": meta["datum"],
            "date_de": date_de,
            "minutes": minutes,
            "excerpt": excerpt(plain_text),
        })

        article_html = build_article(slug, meta, body_html, minutes, date_de)
        (ESSAYS_DIR / f"{slug}.html").write_text(article_html, encoding="utf-8")

    essays.sort(key=lambda e: e["datum"], reverse=True)

    (ROOT / "essays.html").write_text(build_front_page(essays), encoding="utf-8")
    update_homepage(essays)

    print(f"{len(essays)} Essay(s) gebaut: {', '.join(e['slug'] for e in essays) or '(keine)'}")


if __name__ == "__main__":
    main()
