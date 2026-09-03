from pathlib import Path
import re

ROOT = Path('dist')
LOCALES = ['de','fr','pt','it','nl','id','vi']

# expand_batch2.py translates visible HTML by plain string replacement. Some
# translations can accidentally rewrite structural identifiers containing
# "Keyboard" (for example fitKeyboard -> fitBàn phím). Keep visible copy
# localized, but restore code/DOM identifiers to their canonical names.

def normalize(text: str) -> str:
    # DOM ids and CSS selectors.
    for prefix, canonical in (
        ('start', 'startKeyboard'),
        ('exit', 'exitKeyboard'),
        ('reset', 'resetKeyboard'),
    ):
        text = re.sub(rf'id="{prefix}[^"<>\s]*?(?:\s+[^"<>]*?)?"', lambda m: f'id="{canonical}"' if 'Keyboard' not in m.group(0) else m.group(0), text)

    # The regex above cannot safely infer multi-word translated IDs in every
    # language, so use the known structural contexts too.
    text = re.sub(r'#start[^\{\s]+(?:\s+[^\{]*)?\{display:none\}', '#startKeyboard{display:none}', text)

    # Canonicalize quoted DOM id lookups by their role.
    text = re.sub(r"getElementById\('start[^']*'\)", "getElementById('startKeyboard')", text)
    text = re.sub(r"getElementById\('exit[^']*'\)", "getElementById('exitKeyboard')", text)
    text = re.sub(r"getElementById\('reset[^']*'\)", "getElementById('resetKeyboard')", text)

    # Canonicalize the fit function declaration and all requestAnimationFrame
    # calls that reference the translated identifier.
    m = re.search(r'const\s+(fit.*?)=\(\)=>\{board\.style\.transform=', text, re.S)
    if m:
        bad = m.group(1)
        text = text.replace(bad, 'fitKeyboard')

    # Finally normalize any translated structural IDs present in markup using
    # their unique element roles/classes.
    text = re.sub(r'<button id="[^"]+" type="button" class="fullscreen-exit">', '<button id="exitKeyboard" type="button" class="fullscreen-exit">', text)
    text = re.sub(r'<button id="[^"]+" type="button" class="test-btn">Start keyboard test</button>', '<button id="startKeyboard" type="button" class="test-btn">Start keyboard test</button>', text)
    text = re.sub(r'<button id="[^"]+" class="btn">([^<]*)</button></div></section>', r'<button id="resetKeyboard" class="btn">\1</button></div></section>', text)
    return text

for locale in LOCALES:
    path = ROOT / locale / 'keyboard.html'
    if not path.exists():
        continue
    original = path.read_text(encoding='utf-8')
    fixed = normalize(original)
    path.write_text(fixed, encoding='utf-8')

print('Normalized generated keyboard structural identifiers')
