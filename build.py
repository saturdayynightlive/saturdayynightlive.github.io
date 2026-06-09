#!/usr/bin/env python3
"""
Build the public /docs study hub.

This copies selected course-summary folders into docs/ and injects a small
navigation loader so newly added HTML pages can appear in the left sidebar
without hand-editing every page.
"""

from __future__ import annotations

import html
import json
import re
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DOCS_DIR = ROOT / "docs"
GITHUB_OWNER = "saturdayynightlive"
GITHUB_REPO = "saturdayynightlive.github.io"
GITHUB_BRANCH = "main"

COURSES = [
    {
        "slug": "computer-programming",
        "title": "컴퓨터프로그래밍",
        "subtitle": "2026-1 Java/C++ 기말 요약",
        "source": ROOT.parent / "study" / "2026-1" / "컴퓨터프로그래밍" / "summary",
        "summary_path": "computer-programming/summary",
    },
]


def strip_tags(raw: str) -> str:
    text = re.sub(r"<[^>]+>", "", raw)
    return html.unescape(re.sub(r"\s+", " ", text)).strip()


def nav_label_from_anchor(body: str) -> str:
    body = re.sub(
        r"<span\b[^>]*class=[\"'][^\"']*\bbadge\b[^\"']*[\"'][^>]*>.*?</span>",
        "",
        body,
        flags=re.IGNORECASE | re.DOTALL,
    )
    label = strip_tags(body)
    label = re.sub(r"^[🏠⚡★•]\s*", "", label).strip()
    return label or "Untitled"


def title_from_html(path: Path) -> str:
    text = path.read_text(encoding="utf-8", errors="ignore")
    for pattern in (r"<title[^>]*>(.*?)</title>", r"<h1[^>]*>(.*?)</h1>"):
        match = re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL)
        if match:
            return strip_tags(match.group(1))
    return path.stem


def existing_nav_labels(index_html: Path) -> dict[str, str]:
    if not index_html.exists():
        return {}
    text = index_html.read_text(encoding="utf-8", errors="ignore")
    nav = re.search(r"<nav\b[^>]*>(.*?)</nav>", text, flags=re.IGNORECASE | re.DOTALL)
    if nav:
        text = nav.group(1)
    labels: dict[str, str] = {}
    for href, body in re.findall(
        r"<a\s+[^>]*href=[\"']([^\"']+)[\"'][^>]*>(.*?)</a>",
        text,
        flags=re.IGNORECASE | re.DOTALL,
    ):
        if href.endswith(".html"):
            labels.setdefault(href, nav_label_from_anchor(body))
    return labels


def page_sort_key(path: Path) -> tuple[int, int, str]:
    name = path.name.lower()
    if name == "index.html":
        return (0, 0, name)
    if name == "cheatsheet.html":
        return (1, 0, name)
    if name == "snippets.html":
        return (2, 0, name)
    lecture = re.match(r"lec(\d+)\.html$", name)
    if lecture:
        return (10, int(lecture.group(1)), name)
    exam = re.match(r"exam(\d*)\.html$", name)
    if exam:
        number = int(exam.group(1) or "1")
        return (20, number, name)
    return (99, 0, name)


def badge_for(file_name: str) -> str:
    lower = file_name.lower()
    if lower == "index.html":
        return "🏠"
    if lower == "cheatsheet.html":
        return "⚡"
    if lower == "snippets.html":
        return "&lt;/&gt;"
    lecture = re.match(r"lec(\d+)\.html$", lower)
    if lecture:
        return f"L{int(lecture.group(1)):02d}"
    if re.match(r"exam\d*\.html$", lower):
        return "★"
    return "•"


def discover_pages(dest: Path, labels: dict[str, str]) -> list[dict[str, str]]:
    pages = []
    for page in sorted(dest.glob("*.html"), key=page_sort_key):
        file_name = page.name
        pages.append(
            {
                "file": file_name,
                "label": labels.get(file_name) or title_from_html(page),
                "badge": badge_for(file_name),
            }
        )
    return pages


def inject_page_helpers(page: Path) -> None:
    text = page.read_text(encoding="utf-8")
    viewport = '<meta name="viewport" content="width=device-width, initial-scale=1.0" />'
    if 'name="viewport"' not in text and "</head>" in text:
        text = text.replace("</head>", f"{viewport}\n</head>")
    favicon = '<link rel="icon" href="data:," />'
    if favicon not in text and "</head>" in text:
        text = text.replace("</head>", f"{favicon}\n</head>")
    marker = '<script src="auto-nav.js" defer></script>'
    if marker not in text and "</body>" in text:
        text = text.replace("</body>", f"{marker}\n</body>")
    page.write_text(text, encoding="utf-8")


def write_auto_nav(dest: Path, repo_path: str) -> None:
    script = f"""(() => {{
  const OWNER = "{GITHUB_OWNER}";
  const REPO = "{GITHUB_REPO}";
  const BRANCH = "{GITHUB_BRANCH}";
  const REPO_PATH = "docs/{repo_path}";

  const sortKey = (file) => {{
    const lower = file.toLowerCase();
    if (lower === "index.html") return [0, 0, lower];
    if (lower === "cheatsheet.html") return [1, 0, lower];
    if (lower === "snippets.html") return [2, 0, lower];
    const lecture = lower.match(/^lec(\\d+)\\.html$/);
    if (lecture) return [10, Number(lecture[1]), lower];
    const exam = lower.match(/^exam(\\d*)\\.html$/);
    if (exam) return [20, Number(exam[1] || "1"), lower];
    return [99, 0, lower];
  }};

  const comparePages = (a, b) => {{
    const ka = sortKey(a.file);
    const kb = sortKey(b.file);
    for (let i = 0; i < ka.length; i += 1) {{
      if (ka[i] < kb[i]) return -1;
      if (ka[i] > kb[i]) return 1;
    }}
    return 0;
  }};

  const fallbackBadge = (file) => {{
    const lower = file.toLowerCase();
    if (lower === "index.html") return "🏠";
    if (lower === "cheatsheet.html") return "⚡";
    if (lower === "snippets.html") return "&lt;/&gt;";
    const lecture = lower.match(/^lec(\\d+)\\.html$/);
    if (lecture) return `L${{String(Number(lecture[1])).padStart(2, "0")}}`;
    if (/^exam\\d*\\.html$/.test(lower)) return "★";
    return "•";
  }};

  const labelFromFile = (file) => file.replace(/\\.html$/i, "").replace(/[-_]+/g, " ");

  async function loadManifest() {{
    try {{
      const response = await fetch("pages.json", {{ cache: "no-store" }});
      if (!response.ok) return [];
      const pages = await response.json();
      return Array.isArray(pages) ? pages : [];
    }} catch (_) {{
      return [];
    }}
  }}

  async function loadGithubPages(manifest) {{
    if (!location.hostname.endsWith("github.io")) return manifest;
    const labels = new Map(manifest.map((page) => [page.file, page]));
    try {{
      const url = `https://api.github.com/repos/${{OWNER}}/${{REPO}}/contents/${{REPO_PATH}}?ref=${{BRANCH}}`;
      const response = await fetch(url, {{ cache: "no-store" }});
      if (!response.ok) return manifest;
      const contents = await response.json();
      if (!Array.isArray(contents)) return manifest;
      return contents
        .filter((item) => item.type === "file" && /\\.html$/i.test(item.name))
        .map((item) => {{
          const known = labels.get(item.name);
          return known || {{
            file: item.name,
            label: labelFromFile(item.name),
            badge: fallbackBadge(item.name),
          }};
        }})
        .sort(comparePages);
    }} catch (_) {{
      return manifest;
    }}
  }}

  function renderNav(pages) {{
    const list = document.querySelector("nav ul");
    if (!list || pages.length === 0) return;
    const current = decodeURIComponent(location.pathname.split("/").pop() || "index.html");
    list.innerHTML = pages.map((page) => {{
      const active = page.file === current ? " class=\\"active\\"" : "";
      return `<li><a href="${{page.file}}"${{active}}><span class="badge">${{page.badge || fallbackBadge(page.file)}}</span>${{page.label}}</a></li>`;
    }}).join("");
  }}

  async function init() {{
    const manifest = await loadManifest();
    const pages = await loadGithubPages(manifest);
    renderNav(pages.sort(comparePages));
  }}

  init();
}})();
"""
    (dest / "auto-nav.js").write_text(script, encoding="utf-8")


def append_responsive_css(style_path: Path) -> None:
    if not style_path.exists():
        return
    text = style_path.read_text(encoding="utf-8")
    marker = "/* injected responsive layout */"
    if marker in text:
        return
    text += f"""

{marker}
img, table, pre, .hier {{
  max-width: 100%;
}}

@media (max-width: 760px) {{
  body {{
    display: block;
    min-width: 0;
  }}

  nav {{
    position: static;
    width: 100%;
    min-width: 0;
    height: auto;
    max-height: 44vh;
    border-right: none;
    border-bottom: 1px solid #e0e0e0;
    padding: 12px 0;
  }}

  nav h2 {{
    padding: 0 14px 10px;
  }}

  nav ul {{
    display: flex;
    flex-wrap: nowrap;
    gap: 4px;
    overflow-x: auto;
    padding: 8px 12px 2px;
  }}

  nav ul li {{
    flex: 0 0 auto;
  }}

  nav ul li a {{
    border-radius: 5px;
    padding: 6px 10px;
    white-space: nowrap;
  }}

  main {{
    width: 100%;
    max-width: none;
    margin-left: 0;
    padding: 24px 16px 40px;
    overflow-x: hidden;
  }}

  h1 {{
    font-size: 22px;
  }}

  table {{
    display: block;
    overflow-x: auto;
    white-space: nowrap;
  }}

  .hier {{
    white-space: pre-wrap;
    overflow-x: auto;
  }}

  p, li, td, .card, .card * {{
    min-width: 0;
    overflow-wrap: anywhere;
  }}

  .card-grid {{
    grid-template-columns: minmax(0, 1fr);
  }}
}}
"""
    style_path.write_text(text, encoding="utf-8")


def write_course_index() -> None:
    cards = "\n".join(
        f"""
        <a class="course-card" href="{course['summary_path']}/index.html">
          <span class="course-code">2026-1</span>
          <strong>{html.escape(course['title'])}</strong>
          <small>{html.escape(course['subtitle'])}</small>
        </a>"""
        for course in COURSES
    )
    html_doc = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta name="robots" content="noindex, nofollow" />
  <link rel="icon" href="data:," />
  <title>Study Notes</title>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; }}
    :root {{
      --bg: #f7f6f2;
      --surface: #ffffff;
      --text: #191714;
      --muted: #6c675f;
      --border: #ded9ce;
      --accent: #2563eb;
    }}
    body {{
      margin: 0;
      min-height: 100vh;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      color: var(--text);
      background: var(--bg);
      display: grid;
      place-items: center;
      padding: 2rem;
    }}
    main {{
      width: min(760px, 100%);
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 2rem;
      box-shadow: 0 16px 40px rgba(33, 29, 20, 0.08);
    }}
    .top-link {{
      display: inline-block;
      margin-bottom: 2rem;
      color: var(--muted);
      text-decoration: none;
      font-size: 0.9rem;
    }}
    .top-link:hover {{ color: var(--text); }}
    h1 {{
      margin: 0;
      font-size: clamp(1.8rem, 5vw, 3rem);
      line-height: 1.05;
      letter-spacing: 0;
    }}
    p {{
      margin: 0.8rem 0 1.8rem;
      color: var(--muted);
      line-height: 1.7;
    }}
    .course-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 0.85rem;
    }}
    .course-card {{
      display: grid;
      gap: 0.45rem;
      min-height: 150px;
      padding: 1.2rem;
      color: inherit;
      text-decoration: none;
      border: 1px solid var(--border);
      border-radius: 8px;
      background: #fbfaf7;
      transition: border-color 0.15s, transform 0.15s, box-shadow 0.15s;
    }}
    .course-card:hover {{
      border-color: var(--accent);
      transform: translateY(-2px);
      box-shadow: 0 10px 24px rgba(37, 99, 235, 0.12);
    }}
    .course-code {{
      color: var(--accent);
      font-size: 0.78rem;
      font-weight: 700;
      letter-spacing: 0.04em;
    }}
    .course-card strong {{ font-size: 1.2rem; }}
    .course-card small {{ color: var(--muted); line-height: 1.5; }}
    @media (max-width: 520px) {{
      body {{ padding: 1rem; }}
      main {{ padding: 1.4rem; }}
    }}
  </style>
</head>
<body>
  <main>
    <a class="top-link" href="/">← Hwan Ji</a>
    <h1>과목 선택</h1>
    <p>열람할 과목 요약을 선택하세요.</p>
    <section class="course-grid" aria-label="Courses">{cards}
    </section>
  </main>
</body>
</html>
"""
    DOCS_DIR.mkdir(exist_ok=True)
    (DOCS_DIR / "index.html").write_text(html_doc, encoding="utf-8")


def build_course(course: dict[str, object]) -> None:
    source = Path(course["source"])
    if not source.exists():
        raise SystemExit(f"Missing source folder: {source}")
    dest = DOCS_DIR / str(course["summary_path"])
    if dest.exists():
        shutil.rmtree(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, dest)

    labels = existing_nav_labels(dest / "index.html")
    pages = discover_pages(dest, labels)
    (dest / "pages.json").write_text(
        json.dumps(pages, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    append_responsive_css(dest / "style.css")
    write_auto_nav(dest, str(course["summary_path"]))
    for page in dest.glob("*.html"):
        inject_page_helpers(page)
    print(f"✓ {source} -> {dest}")
    print(f"  {len(pages)} html pages indexed")


def main() -> None:
    DOCS_DIR.mkdir(exist_ok=True)
    write_course_index()
    for course in COURSES:
        build_course(course)
    print("✓ docs build complete")


if __name__ == "__main__":
    main()
