from pathlib import Path
import re

ROOT = Path('dist')
LOCALES = ['ja','es','de','fr','pt','it','nl','id','vi','zh-CN','ru']

# Translation builders may rewrite structural tokens by plain text replacement.
# After localization, copy the generated English keyboard behavior script verbatim
# to every locale. Do not modify the input engine here.

def canonical_behavior_script() -> str:
    text = (ROOT/'en'/'keyboard.html').read_text(encoding='utf-8')
    match = re.search(r'<script>\s*document\.addEventListener\([\s\S]*?</script>', text)
    if not match:
        raise RuntimeError('Canonical keyboard behavior script not found in en/keyboard.html')
    return match.group(0)


def normalize_markup(text: str) -> str:
    text = re.sub(
        r'<button id="[^"]+" type="button" class="fullscreen-exit">',
        '<button id="exitKeyboard" type="button" class="fullscreen-exit">',
        text,
        count=1,
    )
    text = re.sub(
        r'(<div class="keyboard-actions">\s*<button )id="[^"]+"',
        r'\1id="startKeyboard"',
        text,
        count=1,
    )
    text = re.sub(
        r'(<div class="controls">\s*<button )id="[^"]+"',
        r'\1id="resetKeyboard"',
        text,
        count=1,
    )
    text = re.sub(r'#start[^\s\{]*\{display:none\}', '#startKeyboard{display:none}', text)
    return text


def polish_fullscreen_ui(text: str) -> str:
    marker = '/* keyboard-fullscreen-ui-v4 */'
    override = '''\n<style>\n/* keyboard-fullscreen-ui-v4 */\n.keyboard-test-active .fullscreen-exit{top:22px!important;right:24px!important;min-width:72px;min-height:46px;padding:11px 18px!important;border-radius:14px!important;box-shadow:0 8px 26px rgba(0,0,0,.28)}\n.keyboard-test-active .tool-layout{padding-top:18px!important;padding-right:112px!important}\n@media(max-width:860px){.keyboard-test-active .fullscreen-exit{top:16px!important;right:16px!important}.keyboard-test-active .tool-layout{padding-right:96px!important}}\n</style>\n'''
    text = re.sub(r'\n<style>\n/\* keyboard-fullscreen-ui-v[0-9]+ \*/[\s\S]*?</style>\n(?=</head>)', '\n', text, count=1)
    if marker in text:
        return text
    return text.replace('</head>', override + '</head>', 1)

canonical = canonical_behavior_script()
all_paths = [ROOT/'keyboard.html', ROOT/'en'/'keyboard.html'] + [ROOT/l/'keyboard.html' for l in LOCALES]
for path in all_paths:
    if not path.exists():
        continue
    text = normalize_markup(path.read_text(encoding='utf-8'))
    text, count = re.subn(
        r'<script>\s*document\.addEventListener\([\s\S]*?</script>',
        lambda _: canonical,
        text,
        count=1,
    )
    if count != 1:
        raise RuntimeError(f'Keyboard behavior script not found: {path}')
    path.write_text(polish_fullscreen_ui(text), encoding='utf-8')

print('Copied canonical keyboard input engine unchanged to all locales and polished fullscreen UI')
