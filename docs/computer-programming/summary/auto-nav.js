(() => {
  const OWNER = "saturdayynightlive";
  const REPO = "saturdayynightlive.github.io";
  const BRANCH = "main";
  const REPO_PATH = "docs/computer-programming/summary";

  const sortKey = (file) => {
    const lower = file.toLowerCase();
    if (lower === "index.html") return [0, 0, lower];
    if (lower === "cheatsheet.html") return [1, 0, lower];
    if (lower === "snippets.html") return [2, 0, lower];
    const lecture = lower.match(/^lec(\d+)\.html$/);
    if (lecture) return [10, Number(lecture[1]), lower];
    const exam = lower.match(/^exam(\d*)\.html$/);
    if (exam) return [20, Number(exam[1] || "1"), lower];
    return [99, 0, lower];
  };

  const comparePages = (a, b) => {
    const ka = sortKey(a.file);
    const kb = sortKey(b.file);
    for (let i = 0; i < ka.length; i += 1) {
      if (ka[i] < kb[i]) return -1;
      if (ka[i] > kb[i]) return 1;
    }
    return 0;
  };

  const fallbackBadge = (file) => {
    const lower = file.toLowerCase();
    if (lower === "index.html") return "🏠";
    if (lower === "cheatsheet.html") return "⚡";
    if (lower === "snippets.html") return "&lt;/&gt;";
    const lecture = lower.match(/^lec(\d+)\.html$/);
    if (lecture) return `L${String(Number(lecture[1])).padStart(2, "0")}`;
    if (/^exam\d*\.html$/.test(lower)) return "★";
    return "•";
  };

  const labelFromFile = (file) => file.replace(/\.html$/i, "").replace(/[-_]+/g, " ");

  async function loadManifest() {
    try {
      const response = await fetch("pages.json", { cache: "no-store" });
      if (!response.ok) return [];
      const pages = await response.json();
      return Array.isArray(pages) ? pages : [];
    } catch (_) {
      return [];
    }
  }

  async function loadGithubPages(manifest) {
    if (!location.hostname.endsWith("github.io")) return manifest;
    const labels = new Map(manifest.map((page) => [page.file, page]));
    try {
      const url = `https://api.github.com/repos/${OWNER}/${REPO}/contents/${REPO_PATH}?ref=${BRANCH}`;
      const response = await fetch(url, { cache: "no-store" });
      if (!response.ok) return manifest;
      const contents = await response.json();
      if (!Array.isArray(contents)) return manifest;
      return contents
        .filter((item) => item.type === "file" && /\.html$/i.test(item.name))
        .map((item) => {
          const known = labels.get(item.name);
          return known || {
            file: item.name,
            label: labelFromFile(item.name),
            badge: fallbackBadge(item.name),
          };
        })
        .sort(comparePages);
    } catch (_) {
      return manifest;
    }
  }

  function renderNav(pages) {
    const list = document.querySelector("nav ul");
    if (!list || pages.length === 0) return;
    const current = decodeURIComponent(location.pathname.split("/").pop() || "index.html");
    list.innerHTML = pages.map((page) => {
      const active = page.file === current ? " class=\"active\"" : "";
      return `<li><a href="${page.file}"${active}><span class="badge">${page.badge || fallbackBadge(page.file)}</span>${page.label}</a></li>`;
    }).join("");
  }

  async function init() {
    const manifest = await loadManifest();
    const pages = await loadGithubPages(manifest);
    renderNav(pages.sort(comparePages));
  }

  init();
})();
