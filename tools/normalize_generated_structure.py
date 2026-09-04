from pathlib import Path
import re

ROOT = Path('dist')
PAGES = ['index.html','checkup.html','mobile.html','keyboard.html','mouse.html','mic.html','webcam.html','speaker.html','display.html']
LOCALES = ['ja','es','de','fr','pt','it','nl','id','vi','zh-CN','ru']

TAG_RE = re.compile(r'<(?!/|!)([A-Za-z][\w:-]*)([^<>]*)>')
STRUCTURAL_ATTRS = ['id', 'class', 'for', 'name']


def attr_value(tag: str, name: str):
    m = re.search(rf'\s{name}="([^"]*)"', tag)
    return m.group(1) if m else None


def data_attrs(tag: str):
    return dict(re.findall(r'\s(data-[\w:-]+)="([^"]*)"', tag))


def set_attr(tag: str, name: str, value):
    pattern = re.compile(rf'(\s{name}=)"[^"]*"')
    if value is None:
        return pattern.sub('', tag)
    if pattern.search(tag):
        return pattern.sub(lambda m: f'{m.group(1)}"{value}"', tag, count=1)
    return tag[:-1] + f' {name}="{value}">' if tag.endswith('>') else tag


def restore_structure(canonical: str, localized: str, label: str) -> str:
    canon_tags = list(TAG_RE.finditer(canonical))
    local_tags = list(TAG_RE.finditer(localized))
    if len(canon_tags) != len(local_tags):
        raise RuntimeError(f'{label}: tag count diverged: canonical={len(canon_tags)} localized={len(local_tags)}')

    replacements = []
    for c, l in zip(canon_tags, local_tags):
        if c.group(1).lower() != l.group(1).lower():
            raise RuntimeError(f'{label}: tag order diverged: {c.group(1)} != {l.group(1)}')
        ctag = c.group(0)
        ltag = l.group(0)
        fixed = ltag
        for name in STRUCTURAL_ATTRS:
            fixed = set_attr(fixed, name, attr_value(ctag, name))
        cdata = data_attrs(ctag)
        ldata = data_attrs(fixed)
        for name in set(cdata) | set(ldata):
            fixed = set_attr(fixed, name, cdata.get(name))
        if fixed != ltag:
            replacements.append((l.start(), l.end(), fixed))

    for start, end, fixed in reversed(replacements):
        localized = localized[:start] + fixed + localized[end:]
    return localized


for page in PAGES:
    canonical_path = ROOT / 'en' / page
    if not canonical_path.exists():
        continue
    canonical = canonical_path.read_text(encoding='utf-8')
    for locale in LOCALES:
        path = ROOT / locale / page
        if not path.exists():
            continue
        text = path.read_text(encoding='utf-8')
        text = restore_structure(canonical, text, f'{locale}/{page}')
        path.write_text(text, encoding='utf-8')

print('Restored canonical DOM ids/classes/data attributes across generated locales without changing visible translations')
