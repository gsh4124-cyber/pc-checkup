from pathlib import Path
import re

ROOT = Path('dist')
KEYBOARDS = sorted(ROOT.glob('keyboard.html')) + sorted(ROOT.glob('*/keyboard.html'))

SIDE_RE = re.compile(
    r'(<aside class="side">\s*)<div class="notice"><strong>([^<]+)</strong><br>([\s\S]*?)</div>',
    re.I,
)
LEGACY_FN_RE = re.compile(
    r'(<div class="keyboard-actions">[\s\S]*?<button id="fnArm"[\s\S]*?</div>)\s*<p class="keyboard-note">[\s\S]*?</p>',
    re.I,
)

STYLE = '''\n<style>\n/* keyboard-help-final-v1 */\n.side .side-help{padding:0!important;overflow:hidden}\n.side .side-help summary{cursor:pointer;list-style:none;padding:14px 16px;font-size:15px;font-weight:900;color:#edf3f8;display:flex;align-items:center;justify-content:space-between;gap:12px}\n.side .side-help summary::-webkit-details-marker{display:none}\n.side .side-help summary::after{content:'+';font-size:18px;line-height:1;color:var(--accent)}\n.side .side-help[open] summary{border-bottom:1px solid var(--line)}\n.side .side-help[open] summary::after{content:'−'}\n.side .side-help-body{padding:13px 16px 16px;font-size:14px;line-height:1.68;color:#aebdcd}\n@media(max-width:860px){.side .side-help summary{padding:12px 14px;font-size:14px}.side .side-help-body{padding:12px 14px 14px;font-size:13px}}\n</style>\n'''

changed = []
for path in KEYBOARDS:
    text = path.read_text(encoding='utf-8')

    # Remove older output from this finalizer so builds remain idempotent.
    text = re.sub(
        r'\n<style>\n/\* keyboard-help-final-v[0-9]+ \*/[\s\S]*?</style>\n(?=</head>)',
        '\n',
        text,
        count=1,
    )

    # Collapse the side "How to check" notice. Do not use a global
    # "side-help in text" shortcut because CSS selectors can contain that token
    # even when the actual <details> element was never created.
    if '<details class="notice side-help">' not in text:
        text, side_count = SIDE_RE.subn(
            lambda m: (
                m.group(1)
                + '<details class="notice side-help"><summary>'
                + m.group(2).strip()
                + '</summary><div class="side-help-body">'
                + m.group(3).strip()
                + '</div></details>'
            ),
            text,
            count=1,
        )
        if side_count != 1:
            raise RuntimeError(f'Could not collapse side help: {path}')

    # The older always-visible Fn paragraph duplicates the new contextual Fn
    # guidance and wastes test workspace. Remove only the paragraph immediately
    # following the keyboard action row that contains #fnArm.
    text, legacy_count = LEGACY_FN_RE.subn(r'\1', text, count=1)
    if legacy_count != 1:
        raise RuntimeError(f'Could not remove legacy Fn paragraph: {path}')

    if '<details class="keyboard-help">' not in text:
        raise RuntimeError(f'Collapsible modifier/Fn help missing: {path}')
    if '<details class="notice side-help">' not in text:
        raise RuntimeError(f'Collapsible side help missing after rewrite: {path}')

    text = text.replace('</head>', STYLE + '</head>', 1)
    path.write_text(text, encoding='utf-8')
    changed.append(path)

if len(changed) != 13:
    raise RuntimeError(f'Expected 13 keyboard pages, finalized {len(changed)}')

print(f'Finalized collapsed keyboard help on {len(changed)} locale pages; removed duplicate always-visible Fn paragraph')
