#!/usr/bin/env python3
"""
python build.py → docs/index.html 생성 (AES-GCM 암호화)
환경변수 BUILD_PASSWORD 또는 prompt로 비번 입력
"""
import os
import json
import base64
import getpass
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

DOCS = [
    ('roadmap',  '커리어 로드맵 (~2029)',   'career_roadmap.md'),
    ('summer',   '2026 여름방학 계획',     'summer_2026.md'),
    ('concepts', 'Transformer 개념',       'transformer_concepts.md'),
    ('workbook', 'Transformer 워크북',     'transformer_workbook.md'),
    ('guide',    '구현 가이드 (답안)',      'transformer_implementation.md'),
    ('paper',    '논문 투고 가이드',        'paper_submission_guide.md'),
]

PBKDF2_ITERATIONS = 250_000

def read(path):
    with open(path, encoding='utf-8') as f:
        return f.read()

def encrypt(plaintext: str, password: str) -> str:
    """PBKDF2-SHA256 + AES-256-GCM. Returns base64(salt|nonce|ciphertext)."""
    salt = os.urandom(16)
    nonce = os.urandom(12)
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32,
                     salt=salt, iterations=PBKDF2_ITERATIONS)
    key = kdf.derive(password.encode())
    ciphertext = AESGCM(key).encrypt(nonce, plaintext.encode(), None)
    return base64.b64encode(salt + nonce + ciphertext).decode()

def build():
    password = os.environ.get('BUILD_PASSWORD')
    if not password:
        password = getpass.getpass('Encryption password: ')
        confirm = getpass.getpass('Confirm: ')
        if password != confirm:
            raise SystemExit('Passwords do not match.')
    if len(password) < 4:
        raise SystemExit('Password must be at least 4 characters.')
    if len(password) < 8:
        print('⚠️  Warning: short password. Casual deterrent only.')

    contents = {key: read(path) for key, _, path in DOCS}

    payload = {
        'docs': {key: {'title': title, 'content': contents[key]}
                 for key, title, _ in DOCS},
        'first_key': DOCS[0][0],
        'nav': [(key, title) for key, title, _ in DOCS],
    }
    encrypted = encrypt(json.dumps(payload, ensure_ascii=False), password)

    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta name="robots" content="noindex, nofollow" />
  <title>🔒 Private Notes</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github.min.css" />
  <script src="https://cdnjs.cloudflare.com/ajax/libs/marked/9.1.6/marked.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

    :root {{
      --bg: #f9f8f6; --surface: #ffffff; --border: #e5e3df;
      --text: #1a1a1a; --muted: #666; --accent: #2563eb;
      --quote-bg: #fffbeb; --quote-border: #f59e0b; --code-bg: #f4f4f4;
    }}

    html {{ scroll-behavior: smooth; }}
    body {{ font-family: 'Inter', sans-serif; background: var(--bg); color: var(--text); min-height: 100vh; }}

    /* ── Password gate ── */
    .gate {{
      position: fixed; inset: 0; background: var(--bg);
      display: flex; align-items: center; justify-content: center;
      flex-direction: column; gap: 1rem; z-index: 100;
    }}
    .gate-card {{
      background: var(--surface); border: 1px solid var(--border);
      border-radius: 12px; padding: 2.5rem; width: min(90%, 420px);
      box-shadow: 0 8px 24px rgba(0,0,0,0.04);
    }}
    .gate h1 {{ font-size: 1rem; font-weight: 600; margin-bottom: 0.4rem; }}
    .gate p {{ font-size: 0.85rem; color: var(--muted); margin-bottom: 1.25rem; }}
    .gate input {{
      width: 100%; padding: 0.6rem 0.75rem; font-family: 'JetBrains Mono', monospace;
      font-size: 0.9rem; border: 1px solid var(--border); border-radius: 6px;
      background: var(--bg); color: var(--text); outline: none;
    }}
    .gate input:focus {{ border-color: var(--accent); }}
    .gate button {{
      width: 100%; margin-top: 0.75rem; padding: 0.6rem; font-family: 'Inter', sans-serif;
      font-size: 0.9rem; font-weight: 500; background: var(--text); color: white;
      border: none; border-radius: 6px; cursor: pointer; transition: opacity 0.15s;
    }}
    .gate button:hover {{ opacity: 0.85; }}
    .gate-error {{ color: #dc2626; font-size: 0.8rem; margin-top: 0.5rem; min-height: 1em; }}

    /* ── Main app (hidden until decrypted) ── */
    #app {{
      display: none;
      grid-template-rows: 48px 1fr; grid-template-columns: 240px 1fr;
      min-height: 100vh;
    }}
    #app.ready {{ display: grid; }}

    .topbar {{
      grid-column: 1 / -1; background: var(--surface); border-bottom: 1px solid var(--border);
      display: flex; align-items: center; padding: 0 1.5rem; gap: 1rem;
    }}
    .topbar a {{ font-size: 0.85rem; color: var(--muted); text-decoration: none; }}
    .topbar a:hover {{ color: var(--text); }}
    .topbar-sep {{ color: var(--border); }}
    .topbar-title {{ font-size: 0.9rem; font-weight: 500; color: var(--text); }}
    .topbar-lock {{
      margin-left: auto; font-size: 0.75rem; color: var(--muted);
      background: none; border: 1px solid var(--border); padding: 0.3rem 0.7rem;
      border-radius: 4px; cursor: pointer; font-family: inherit;
    }}
    .topbar-lock:hover {{ color: var(--text); border-color: var(--text); }}

    .sidebar {{
      background: var(--surface); border-right: 1px solid var(--border);
      padding: 1.5rem 1rem; position: sticky; top: 48px;
      height: calc(100vh - 48px); overflow-y: auto;
      display: flex; flex-direction: column; gap: 0.25rem;
    }}
    .sidebar-label {{
      font-size: 0.7rem; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase;
      color: var(--muted); padding: 0 0.5rem; margin-bottom: 0.5rem;
    }}
    .nav-item {{
      display: block; width: 100%; text-align: left; padding: 0.5rem 0.75rem;
      font-size: 0.875rem; font-family: 'Inter', sans-serif; color: var(--muted);
      background: none; border: none; border-radius: 6px; cursor: pointer;
      transition: background 0.1s, color 0.1s; line-height: 1.4;
    }}
    .nav-item:hover {{ background: var(--bg); color: var(--text); }}
    .nav-item.active {{ background: var(--bg); color: var(--text); font-weight: 500; }}

    .content {{ padding: 3rem 4rem; max-width: 860px; overflow-y: auto; }}

    .prose h1 {{ font-size: 1.75rem; font-weight: 600; letter-spacing: -0.02em; margin-bottom: 0.5rem; padding-bottom: 0.75rem; border-bottom: 1px solid var(--border); }}
    .prose h2 {{ font-size: 1.2rem; font-weight: 600; margin-top: 2.5rem; margin-bottom: 0.75rem; padding-bottom: 0.4rem; border-bottom: 1px solid var(--border); }}
    .prose h3 {{ font-size: 1rem; font-weight: 600; margin-top: 1.75rem; margin-bottom: 0.5rem; }}
    .prose h4 {{ font-size: 0.9rem; font-weight: 600; margin-top: 1.25rem; margin-bottom: 0.4rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.04em; }}
    .prose p {{ font-size: 0.95rem; line-height: 1.75; color: #333; margin-bottom: 1rem; }}
    .prose a {{ color: var(--accent); text-decoration: none; }}
    .prose a:hover {{ text-decoration: underline; }}
    .prose ul, .prose ol {{ padding-left: 1.5rem; margin-bottom: 1rem; }}
    .prose li {{ font-size: 0.95rem; line-height: 1.7; color: #333; margin-bottom: 0.2rem; }}
    .prose li input[type="checkbox"] {{ margin-right: 0.4rem; accent-color: var(--accent); }}
    .prose blockquote {{ background: var(--quote-bg); border-left: 3px solid var(--quote-border); padding: 0.75rem 1rem; margin: 1rem 0; border-radius: 0 6px 6px 0; }}
    .prose blockquote p {{ margin: 0; font-size: 0.9rem; color: #92400e; }}
    .prose code:not(pre code) {{ background: var(--code-bg); padding: 0.15em 0.4em; border-radius: 4px; font-family: 'JetBrains Mono', monospace; font-size: 0.85em; color: #c7254e; }}
    .prose pre {{ background: #1e1e1e; border-radius: 8px; padding: 1.25rem 1.5rem; overflow-x: auto; margin: 1rem 0 1.5rem; }}
    .prose pre code {{ font-family: 'JetBrains Mono', monospace; font-size: 0.83rem; line-height: 1.65; color: #d4d4d4; background: none; padding: 0; }}
    .prose pre .hljs {{ background: transparent; }}
    .prose table {{ width: 100%; border-collapse: collapse; margin: 1rem 0 1.5rem; font-size: 0.88rem; }}
    .prose th {{ background: var(--bg); border: 1px solid var(--border); padding: 0.5rem 0.75rem; text-align: left; font-weight: 600; }}
    .prose td {{ border: 1px solid var(--border); padding: 0.5rem 0.75rem; vertical-align: top; line-height: 1.5; }}
    .prose tr:hover td {{ background: var(--bg); }}
    .prose hr {{ border: none; border-top: 1px solid var(--border); margin: 2rem 0; }}

    @media (max-width: 768px) {{
      #app.ready {{ grid-template-columns: 1fr; grid-template-rows: 48px auto 1fr; }}
      .sidebar {{ position: static; height: auto; flex-direction: row; flex-wrap: wrap; padding: 0.75rem; gap: 0.25rem; border-right: none; border-bottom: 1px solid var(--border); }}
      .sidebar-label {{ display: none; }}
      .content {{ padding: 2rem 1.25rem; }}
    }}
  </style>
</head>
<body>

  <!-- Password gate -->
  <div class="gate" id="gate">
    <div class="gate-card">
      <h1>🔒 Private</h1>
      <p>이 페이지는 비밀번호로 보호되어 있다.</p>
      <form id="gate-form" autocomplete="off">
        <input type="password" id="pw" autofocus placeholder="비밀번호" />
        <button type="submit">열기</button>
        <div class="gate-error" id="gate-error"></div>
      </form>
    </div>
  </div>

  <!-- Main app (hidden until decrypted) -->
  <div id="app">
    <div class="topbar">
      <a href="/">← Hwan Ji</a>
      <span class="topbar-sep">·</span>
      <span class="topbar-title" id="topbar-title">Study Notes</span>
      <button class="topbar-lock" onclick="lock()">🔒 잠금</button>
    </div>

    <aside class="sidebar">
      <div class="sidebar-label">Documents</div>
      <div id="nav"></div>
    </aside>

    <main class="content">
      <article class="prose" id="prose"></article>
    </main>
  </div>

  <script>
    const ENCRYPTED = "{encrypted}";
    const ITERATIONS = {PBKDF2_ITERATIONS};
    let DOCS = null;

    // ── Crypto ──
    function b64ToBytes(b64) {{
      const bin = atob(b64);
      const bytes = new Uint8Array(bin.length);
      for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
      return bytes;
    }}

    async function decrypt(password) {{
      const blob = b64ToBytes(ENCRYPTED);
      const salt = blob.slice(0, 16);
      const nonce = blob.slice(16, 28);
      const ciphertext = blob.slice(28);
      const pwKey = await crypto.subtle.importKey(
        'raw', new TextEncoder().encode(password),
        'PBKDF2', false, ['deriveKey']
      );
      const key = await crypto.subtle.deriveKey(
        {{ name: 'PBKDF2', salt, iterations: ITERATIONS, hash: 'SHA-256' }},
        pwKey, {{ name: 'AES-GCM', length: 256 }}, false, ['decrypt']
      );
      const plain = await crypto.subtle.decrypt(
        {{ name: 'AES-GCM', iv: nonce }}, key, ciphertext
      );
      return JSON.parse(new TextDecoder().decode(plain));
    }}

    // ── Render ──
    marked.setOptions({{ breaks: false, gfm: true }});
    const renderer = new marked.Renderer();
    renderer.code = (code, lang) => {{
      const language = lang && hljs.getLanguage(lang) ? lang : 'plaintext';
      const highlighted = hljs.highlight(code, {{ language }}).value;
      return `<pre><code class="hljs language-${{language}}">${{highlighted}}</code></pre>`;
    }};
    marked.use({{ renderer }});

    function show(key) {{
      const doc = DOCS.docs[key];
      if (!doc) return;
      const prose = document.getElementById('prose');
      prose.innerHTML = marked.parse(doc.content);
      prose.querySelectorAll('li').forEach(li => {{
        const text = li.innerHTML;
        if (text.startsWith('[ ]') || text.startsWith('[x]') || text.startsWith('[X]')) {{
          const checked = !text.startsWith('[ ]');
          li.innerHTML = `<label style="display:flex;gap:0.4rem;align-items:flex-start;cursor:pointer"><input type="checkbox" ${{checked ? 'checked' : ''}} style="margin-top:0.25rem;flex-shrink:0" /><span>${{text.replace(/^\\[[ xX]\\]\\s*/, '')}}</span></label>`;
        }}
      }});
      document.getElementById('topbar-title').textContent = doc.title;
      document.title = doc.title;
      document.querySelectorAll('.nav-item').forEach(btn => {{
        btn.classList.toggle('active', btn.dataset.doc === key);
      }});
      history.replaceState(null, '', '#' + key);
      document.querySelector('.content').scrollTop = 0;
    }}

    function lock() {{
      sessionStorage.removeItem('pw');
      location.reload();
    }}

    function renderApp() {{
      const nav = document.getElementById('nav');
      nav.innerHTML = DOCS.nav.map(([key, title]) =>
        `<button class="nav-item" data-doc="${{key}}" onclick="show('${{key}}')">${{title}}</button>`
      ).join('');
      document.getElementById('gate').style.display = 'none';
      document.getElementById('app').classList.add('ready');
      const initial = location.hash.slice(1) || DOCS.first_key;
      show(DOCS.docs[initial] ? initial : DOCS.first_key);
    }}

    async function tryUnlock(password) {{
      try {{
        DOCS = await decrypt(password);
        sessionStorage.setItem('pw', password);
        renderApp();
        return true;
      }} catch (e) {{
        return false;
      }}
    }}

    document.getElementById('gate-form').addEventListener('submit', async (e) => {{
      e.preventDefault();
      const pw = document.getElementById('pw').value;
      const err = document.getElementById('gate-error');
      err.textContent = '복호화 중...';
      if (!(await tryUnlock(pw))) {{
        err.textContent = '비밀번호가 틀렸다.';
        document.getElementById('pw').select();
      }}
    }});

    // Auto-unlock if session has password
    const saved = sessionStorage.getItem('pw');
    if (saved) tryUnlock(saved);
  </script>
</body>
</html>"""

    os.makedirs('docs', exist_ok=True)
    out = 'docs/index.html'
    with open(out, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"✓  {out} 생성 완료 (암호화)")
    for key, title, path in DOCS:
        size = len(contents[key])
        print(f"   {path} ({size:,}자) → [{key}]")

if __name__ == '__main__':
    build()
