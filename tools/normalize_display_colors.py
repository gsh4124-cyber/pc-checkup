from pathlib import Path
import re

ROOT = Path('dist')

LABELS = {
    'ko': {'gray':'회색','yellow':'노랑','cyan':'청록'},
    'en': {'gray':'Gray','yellow':'Yellow','cyan':'Cyan'},
    'ja': {'gray':'グレー','yellow':'黄色','cyan':'シアン'},
    'es': {'gray':'Gris','yellow':'Amarillo','cyan':'Cian'},
    'de': {'gray':'Grau','yellow':'Gelb','cyan':'Cyan'},
    'fr': {'gray':'Gris','yellow':'Jaune','cyan':'Cyan'},
    'pt': {'gray':'Cinza','yellow':'Amarelo','cyan':'Ciano'},
    'it': {'gray':'Grigio','yellow':'Giallo','cyan':'Ciano'},
    'nl': {'gray':'Grijs','yellow':'Geel','cyan':'Cyaan'},
    'id': {'gray':'Abu-abu','yellow':'Kuning','cyan':'Sian'},
    'vi': {'gray':'Xám','yellow':'Vàng','cyan':'Xanh lơ'},
    'zh-cn': {'gray':'灰色','yellow':'黄色','cyan':'青色'},
    'ru': {'gray':'Серый','yellow':'Жёлтый','cyan':'Бирюзовый'},
}

COLORS = {
    '#808080': 'gray',
    '#ffff00': 'yellow',
    '#ff0': 'yellow',
    '#00ffff': 'cyan',
    '#0ff': 'cyan',
}

def lang_of(text: str) -> str:
    m = re.search(r'<html[^>]*\blang="([^"]+)"', text, re.I)
    return (m.group(1) if m else 'en').lower()


def replace_button_text(text: str, attr: str, color: str, label: str) -> str:
    pattern = re.compile(rf'(<button\b[^>]*\b{re.escape(attr)}="{re.escape(color)}"[^>]*>)[^<]*(</button>)', re.I)
    return pattern.sub(rf'\1{label}\2', text)


changed = 0
for path in [*ROOT.rglob('display.html'), *ROOT.rglob('mobile.html')]:
    text = path.read_text(encoding='utf-8')
    lang = lang_of(text)
    labels = LABELS.get(lang, LABELS['en'])
    before = text
    for color, key in COLORS.items():
        label = labels[key]
        text = replace_button_text(text, 'data-color', color, label)
        text = replace_button_text(text, 'data-open-screen', color, label)
        text = replace_button_text(text, 'data-set-screen', color, label)
    if text != before:
        path.write_text(text, encoding='utf-8')
        changed += 1

print(f'Normalized display color labels on {changed} localized pages')
