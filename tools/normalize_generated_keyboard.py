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


def inject_raw_diagnostics(text: str) -> str:
    """Add raw-event diagnostics plus conservative session-based Shift inference."""
    marker = 'keyboard-raw-diagnostics-v2'
    if marker in text:
        return text

    # Remove the previous temporary diagnostic block if it exists in a generated page.
    text = re.sub(r'\n<style>\n/\* keyboard-raw-diagnostics-v1 \*/[\s\S]*?</style>\n(?=</head>)', '\n', text, count=1)
    text = re.sub(r'\n<script>\n/\* keyboard-raw-diagnostics-v1 \*/[\s\S]*?</script>\n(?=</body>)', '\n', text, count=1)

    style = '''\n<style>\n/* keyboard-raw-diagnostics-v2 */\n.raw-key-events{margin-top:7px;padding:9px 10px;border:1px solid var(--line);border-radius:10px;background:#08111a;color:#d7e1ea;font:11px/1.45 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;white-space:pre-wrap;word-break:break-word;min-height:46px;max-height:190px;overflow:auto}\n.raw-key-events strong{color:#fbbf24}\n.keyboard-test-active .raw-key-events{flex:0 0 auto;max-height:145px;margin-top:5px}\n</style>\n'''
    text = text.replace('</head>', style + '</head>', 1)

    panel = '<div id="rawKeyEvents" class="raw-key-events"><strong>RAW INPUT DIAGNOSTIC</strong> — recent keyboard events appear here.</div>'
    # Avoid duplicating a panel from v1.
    text = re.sub(r'<div id="rawKeyEvents" class="raw-key-events">[\s\S]*?</div>', '', text, count=1)
    if '<div id="keyLog"' in text:
        text = text.replace('<div id="keyLog"', panel + '<div id="keyLog"', 1)
    else:
        raise RuntimeError('keyLog anchor not found for raw diagnostic panel')

    script = r'''\n<script>\n/* keyboard-raw-diagnostics-v2 */\n(()=>{\n  const rows=[];\n  const verifiedShiftSides=new Set();\n  let inferredShiftDown='';\n  const render=()=>{\n    const el=document.getElementById('rawKeyEvents');\n    if(!el)return;\n    el.textContent='RAW INPUT DIAGNOSTIC — newest first\\n'+(rows.length?rows.join('\\n'):'(no keyboard event yet)');\n  };\n  const add=line=>{rows.unshift(line);if(rows.length>10)rows.length=10;render()};\n  const sideFrom=e=>{\n    const code=e.code||'';\n    const loc=Number(e.location)||Number(e.keyLocation)||0;\n    if(code==='ShiftLeft'||loc===1)return 'ShiftLeft';\n    if(code==='ShiftRight'||loc===2)return 'ShiftRight';\n    return '';\n  };\n  const paint=(code,on)=>{\n    if(!code)return;\n    document.querySelectorAll(`[data-code="${CSS.escape(code)}"]`).forEach(k=>k.classList.toggle('active',on));\n  };\n  const inferOppositeShift=()=>{\n    if(verifiedShiftSides.size!==1)return '';\n    return verifiedShiftSides.has('ShiftLeft')?'ShiftRight':'ShiftLeft';\n  };\n  const raw=e=>{\n    let shiftState='?';\n    try{shiftState=String(e.getModifierState('Shift'))}catch{}\n    const verified=sideFrom(e);\n    if(verified)verifiedShiftSides.add(verified);\n\n    if(e.key==='Shift'&&!verified){\n      if(e.type==='keydown'&&!e.repeat){\n        const inferred=inferOppositeShift();\n        if(inferred){\n          inferredShiftDown=inferred;\n          paint(inferred,true);\n          const log=document.getElementById('keyLog');\n          if(log)log.textContent=`${inferred} inferred from verified opposite Shift | code: ${e.code||'(none)'} | location: ${e.location}`;\n          add(`INFERRED | ${inferred} | reason=opposite Shift already verified`);\n        }\n      }else if(e.type==='keyup'&&inferredShiftDown){\n        paint(inferredShiftDown,false);\n        inferredShiftDown='';\n      }\n    }\n\n    add(`${e.type} | key=${JSON.stringify(e.key)} | code=${JSON.stringify(e.code)} | location=${e.location} | keyCode=${e.keyCode||0} | which=${e.which||0} | repeat=${e.repeat?'Y':'N'} | ShiftState=${shiftState}`);\n  };\n  window.addEventListener('keydown',raw,true);\n  window.addEventListener('keyup',raw,true);\n  window.addEventListener('blur',()=>{if(inferredShiftDown)paint(inferredShiftDown,false);inferredShiftDown=''});\n  document.addEventListener('visibilitychange',()=>{if(document.hidden&&inferredShiftDown){paint(inferredShiftDown,false);inferredShiftDown=''}});\n  document.addEventListener('DOMContentLoaded',()=>{\n    render();\n    document.getElementById('fnArm')?.addEventListener('click',()=>setTimeout(()=>{\n      const b=document.getElementById('fnArm');\n      add(`UI | Fn button clicked | text=${JSON.stringify(b?.textContent||'')} | active=${b?.classList.contains('active')?'Y':'N'}`);\n    },0));\n  });\n})();\n</script>\n'''
    return text.replace('</body>', script + '</body>', 1)


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
    text = polish_fullscreen_ui(text)
    text = inject_raw_diagnostics(text)
    path.write_text(text, encoding='utf-8')

print('Copied canonical keyboard input engine unchanged, added raw diagnostics, and enabled conservative opposite-side Shift inference')
