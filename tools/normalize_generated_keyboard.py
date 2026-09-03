from pathlib import Path
import re

ROOT = Path('dist')
LOCALES = ['ja','es','de','fr','pt','it','nl','id','vi','zh-CN','ru']

# Translation builders intentionally localize visible HTML copy, but plain text
# replacement must never rewrite browser key codes, function names, or DOM ids.
# Use the generated English keyboard behavior as the structural source of truth
# after all locale builders have finished.

def canonical_behavior_script() -> str:
    text = (ROOT/'en'/'keyboard.html').read_text(encoding='utf-8')
    match = re.search(r'<script>\s*document\.addEventListener\([\s\S]*?</script>', text)
    if not match:
        raise RuntimeError('Canonical keyboard behavior script not found in en/keyboard.html')
    return match.group(0)


def normalize_markup(text: str) -> str:
    # Structural element ids are selected by their unique UI role, not by
    # translated text, so visible labels remain localized.
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
    # Translation may also have rewritten the fullscreen CSS selector.
    text = re.sub(r'#start[^\s\{]*\{display:none\}', '#startKeyboard{display:none}', text)
    return text


def polish_fullscreen_ui(text: str) -> str:
    marker = '/* keyboard-fullscreen-ui-v2 */'
    if marker in text:
        return text
    override = '''\n<style>\n/* keyboard-fullscreen-ui-v2 */\n.keyboard-test-active .fullscreen-exit{top:22px!important;right:24px!important;min-width:72px;min-height:46px;padding:11px 18px!important;border-radius:14px!important;box-shadow:0 8px 26px rgba(0,0,0,.28)}\n.keyboard-test-active .tool-layout{padding-top:18px!important;padding-right:112px!important}\n@media(max-width:860px){.keyboard-test-active .fullscreen-exit{top:16px!important;right:16px!important}.keyboard-test-active .tool-layout{padding-right:96px!important}}\n</style>\n'''
    return text.replace('</head>', override + '</head>', 1)

canonical = canonical_behavior_script()
for locale in LOCALES:
    path = ROOT/locale/'keyboard.html'
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
    path.write_text(text, encoding='utf-8')

# Apply the same fullscreen spacing to every deployed keyboard page, including
# Korean and English, without touching input behavior.
for path in [ROOT/'keyboard.html', ROOT/'en'/'keyboard.html'] + [ROOT/l/'keyboard.html' for l in LOCALES]:
    if path.exists():
        path.write_text(polish_fullscreen_ui(path.read_text(encoding='utf-8')), encoding='utf-8')

print('Normalized localized keyboard markup, restored canonical behavior script, and polished fullscreen exit UI')
