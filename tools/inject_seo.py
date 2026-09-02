from pathlib import Path
import html
import json
import re

BASE = "https://gsh4124-cyber.github.io/pc-checkup/"
SITE = "DEVICE CHECKUP"


def extract(pattern, text, default=""):
    m = re.search(pattern, text, re.I | re.S)
    return html.unescape(m.group(1).strip()) if m else default


def meta_block(filename, text):
    title = extract(r"<title>(.*?)</title>", text, SITE)
    desc = extract(r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']', text, "PC와 휴대폰의 기본 기능을 브라우저에서 빠르게 점검합니다.")
    url = BASE if filename == "index.html" else BASE + filename
    schema = {
        "@context": "https://schema.org",
        "@type": "WebApplication",
        "name": title,
        "url": url,
        "description": desc,
        "applicationCategory": "UtilitiesApplication",
        "operatingSystem": "Any",
        "isAccessibleForFree": True,
        "offers": {"@type": "Offer", "price": "0", "priceCurrency": "KRW"},
    }
    esc_title = html.escape(title, quote=True)
    esc_desc = html.escape(desc, quote=True)
    esc_url = html.escape(url, quote=True)
    schema_json = json.dumps(schema, ensure_ascii=False).replace("</", "<\\/")
    return (
        f'<link rel="canonical" href="{esc_url}">'
        f'<meta property="og:type" content="website">'
        f'<meta property="og:locale" content="ko_KR">'
        f'<meta property="og:site_name" content="{SITE}">'
        f'<meta property="og:title" content="{esc_title}">'
        f'<meta property="og:description" content="{esc_desc}">'
        f'<meta property="og:url" content="{esc_url}">'
        f'<meta name="twitter:card" content="summary">'
        f'<script type="application/ld+json">{schema_json}</script>'
    )


for path in sorted(Path(".").glob("*.html")):
    text = path.read_text(encoding="utf-8")
    if 'rel="canonical"' in text or "rel='canonical'" in text:
        continue
    block = meta_block(path.name, text)
    if "</head>" not in text.lower():
        raise SystemExit(f"Missing </head>: {path}")
    text = re.sub(r"</head>", block + "</head>", text, count=1, flags=re.I)
    path.write_text(text, encoding="utf-8")
    print(f"SEO injected: {path.name}")
