from pathlib import Path
import re
import subprocess
import tempfile
import sys

ROOT = Path('dist')
PAGES = ['index.html','checkup.html','mobile.html','keyboard.html','mouse.html','mic.html','webcam.html','speaker.html','display.html']
LOCALES = ['ko','en','ja','es','de','fr','pt','it','nl','id','vi','zh-CN','ru']
DIRS = {'ko': ROOT, **{x: ROOT/x for x in LOCALES if x != 'ko'}}
errors = []


def err(path, kind, detail=''):
    errors.append(f'{path}: {kind}{": " + detail if detail else ""}')

# Required 13 languages × 9 HTML pages.
for lang, folder in DIRS.items():
    for page in PAGES:
        if not (folder/page).exists():
            err(f'{lang}/{page}', 'missing page')

html_files = sorted(ROOT.rglob('*.html'))
if len(html_files) != 117:
    err('dist', 'HTML count', f'expected 117, got {len(html_files)}')

# Sitemap must contain exactly one URL per indexable HTML page.
sitemap = (ROOT/'sitemap.xml').read_text(encoding='utf-8') if (ROOT/'sitemap.xml').exists() else ''
loc_count = sitemap.count('<loc>')
if loc_count != 117:
    err('sitemap.xml', 'URL count', f'expected 117, got {loc_count}')

for path in html_files:
    rel = path.relative_to(ROOT)
    text = path.read_text(encoding='utf-8')

    # Duplicate IDs.
    ids = re.findall(r'\bid="([^"]+)"', text)
    dup = sorted({x for x in ids if ids.count(x) > 1})
    if dup:
        err(str(rel), 'duplicate IDs', ', '.join(dup))

    # Internal href/src references.
    for attr, value in re.findall(r'\b(href|src)="([^"]+)"', text):
        if not value or value.startswith(('http://','https://','#','mailto:','tel:','data:','javascript:')):
            continue
        clean = value.split('#',1)[0].split('?',1)[0]
        if not clean:
            continue
        target = (path.parent/clean).resolve()
        try:
            target.relative_to(ROOT.resolve())
        except ValueError:
            continue
        if not target.exists():
            err(str(rel), 'missing internal reference', value)

    # SEO structure required on every indexable page.
    if 'rel="canonical"' not in text:
        err(str(rel), 'missing canonical')
    if 'hreflang="x-default"' not in text:
        err(str(rel), 'missing x-default hreflang')

    # No accidental raw Korean text in non-Korean generated pages except the
    # intentional language-selector label 한국어.
    if rel.parts and rel.parts[0] in {x for x in LOCALES if x != 'ko'}:
        clean = text.replace('한국어','')
        if re.search(r'[가-힣]', clean):
            err(str(rel), 'KOREAN_LEAK')

    # Inline JavaScript syntax. Ignore JSON-LD scripts.
    scripts = []
    for m in re.finditer(r'<script([^>]*)>(.*?)</script>', text, re.S|re.I):
        attrs, body = m.group(1), m.group(2)
        if re.search(r'\bsrc=', attrs, re.I):
            continue
        if re.search(r'type=["\']application/ld\+json["\']', attrs, re.I):
            continue
        if body.strip():
            scripts.append(body)
    if scripts:
        with tempfile.NamedTemporaryFile('w', suffix='.js', encoding='utf-8', delete=False) as f:
            f.write('\n'.join(scripts))
            tmp = f.name
        result = subprocess.run(['node','--check',tmp],capture_output=True,text=True)
        Path(tmp).unlink(missing_ok=True)
        if result.returncode:
            err(str(rel), 'inline JS syntax', result.stderr.splitlines()[0] if result.stderr else 'node --check failed')

# External JS files syntax across all locales.
for path in sorted(list(ROOT.rglob('app.js')) + list(ROOT.rglob('mobile.js'))):
    result = subprocess.run(['node','--check',str(path)],capture_output=True,text=True)
    if result.returncode:
        err(str(path.relative_to(ROOT)), 'JS syntax', result.stderr.splitlines()[0] if result.stderr else 'node --check failed')

# Keyboard regression invariants.
for lang, folder in DIRS.items():
    path = folder/'keyboard.html'
    if not path.exists():
        continue
    text = path.read_text(encoding='utf-8')
    for required in ['id="startKeyboard"','id="exitKeyboard"','id="resetKeyboard"','fitKeyboard','fnArmed','MetaLeft','MetaRight']:
        if required not in text:
            err(str(path.relative_to(ROOT)), 'keyboard invariant missing', required)
    # Match only the obsolete identifiers themselves. Do not reject new helper
    # names merely because they contain one of these strings as a substring.
    for forbidden in ['ShiftUnknown','shiftArm','initKeyboard']:
        if re.search(rf'\b{re.escape(forbidden)}\b', text):
            err(str(path.relative_to(ROOT)), 'obsolete keyboard path present', forbidden)

# Reserved ad slots: exactly one on the three non-invasive surfaces per locale.
for lang, folder in DIRS.items():
    for page in ['index.html','checkup.html','mobile.html']:
        text = (folder/page).read_text(encoding='utf-8')
        if text.count('data-ad-slot=') != 1:
            err(str((folder/page).relative_to(ROOT)), 'ad slot count', f'expected 1, got {text.count("data-ad-slot=")}')
    for page in ['keyboard.html','mouse.html','mic.html','webcam.html','speaker.html','display.html']:
        text = (folder/page).read_text(encoding='utf-8')
        if 'data-ad-slot=' in text:
            err(str((folder/page).relative_to(ROOT)), 'ad slot inside individual test')

# No runtime network/analytics/ad code yet. Reserved slots must stay inert until
# an ad provider is intentionally integrated.
for path in list(ROOT.rglob('*.js')) + html_files:
    text = path.read_text(encoding='utf-8')
    for token in ['XMLHttpRequest','WebSocket','sendBeacon','googletagmanager','google-analytics','adsbygoogle']:
        if token in text:
            err(str(path.relative_to(ROOT)), 'unexpected runtime network/analytics token', token)

if errors:
    print('\n'.join('ERROR ' + x for x in errors))
    print(f'Validation failed: {len(errors)} issue(s)')
    sys.exit(2)

print(f'Validation PASS: {len(html_files)} HTML, {loc_count} sitemap URLs, {len(LOCALES)} locales')
