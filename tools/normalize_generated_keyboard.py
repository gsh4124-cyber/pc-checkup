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


def harden_keyboard_input(script: str) -> str:
    """Restore explicit Fn checking and make Shift input visible without guessing its side."""
    old_state = "let presses=0,repeats=0,unique=new Set(),current=new Set(),maxSimul=0,focusMode=false,fnArmed=false;"
    new_state = old_state + "\n let pendingShift=false;"
    if old_state not in script:
        raise RuntimeError('Keyboard state anchor not found')
    script = script.replace(old_state, new_state, 1)

    old_paint = "const paint=(code,on)=>{if(!code)return;host.querySelectorAll(`[data-code=\"${CSS.escape(code)}\"]`).forEach(k=>k.classList.toggle('active',on))};"
    new_paint = old_paint + "\n const paintShiftUnknown=on=>['ShiftLeft','ShiftRight'].forEach(code=>host.querySelectorAll(`[data-code=\"${code}\"]`).forEach(k=>k.classList.toggle('shift-unknown',on)));"
    if old_paint not in script:
        raise RuntimeError('Keyboard paint anchor not found')
    script = script.replace(old_paint, new_paint, 1)

    old_clear = "const clearPressed=()=>{current.clear();modifierDown.clear();releaseTimers.forEach(clearTimeout);releaseTimers.clear();fnVisualDown.forEach(v=>paint(v,false));fnVisualDown.clear();host.querySelectorAll('.key.active').forEach(k=>k.classList.remove('active'))};"
    new_clear = "const clearPressed=()=>{current.clear();modifierDown.clear();pendingShift=false;paintShiftUnknown(false);releaseTimers.forEach(clearTimeout);releaseTimers.clear();fnVisualDown.forEach(v=>paint(v,false));fnVisualDown.clear();host.querySelectorAll('.key.active').forEach(k=>k.classList.remove('active'))};"
    if old_clear not in script:
        raise RuntimeError('Keyboard clearPressed anchor not found')
    script = script.replace(old_clear, new_clear, 1)

    old_down = "const onDown=e=>{const code=physicalCode(e);if(focusMode)e.preventDefault();if(!code){text('keyLog',`key: ${e.key} | code: ${e.code||'(none)'} | location: ${e.location} | unresolved`);return}const family=modifierFamilyFromEvent(e);if(family)modifierDown.set(family,code);if(e.repeat)repeats++;else{presses++;unique.add(code);current.add(code);maxSimul=Math.max(maxSimul,current.size)}paint(code,true);armRelease(code);\n   if(fnArmed&&fnFunctions.has(e.key||'')){const out=e.key;paint(out,true);fnVisualDown.set(code,out);text('keyLog',`Fn check ON | physical: ${e.code||code} | output: ${out} | location: ${e.location}`)}else{text('keyLog',`Fn check ${fnArmed?'ON':'OFF'} | key: ${e.key} | code: ${e.code||'(none)'} | physical: ${code} | location: ${e.location} | repeat: ${e.repeat?'yes':'no'}`)}update()};"
    new_down = "const onDown=e=>{const code=physicalCode(e);if(focusMode)e.preventDefault();const family=modifierFamilyFromEvent(e);if(!code){if(family==='Shift'){pendingShift=true;paintShiftUnknown(true);if(!e.repeat){presses++;current.add('ShiftPending');maxSimul=Math.max(maxSimul,current.size);update()}text('keyLog',`Shift detected; side pending | code: ${e.code||'(none)'} | location: ${e.location} | keyCode: ${e.keyCode||0} | which: ${e.which||0}`);return}text('keyLog',`key: ${e.key} | code: ${e.code||'(none)'} | location: ${e.location} | unresolved`);return}if(family)modifierDown.set(family,code);if(e.repeat)repeats++;else{presses++;unique.add(code);current.add(code);maxSimul=Math.max(maxSimul,current.size)}paint(code,true);armRelease(code);\n   if(fnArmed&&fnFunctions.has(e.key||'')){const out=e.key;paint(out,true);armRelease(out);fnVisualDown.set(code,out);text('keyLog',`Fn check ON | physical: ${e.code||code} | output: ${out} | location: ${e.location}`)}else{text('keyLog',`Fn check ${fnArmed?'ON':'OFF'} | key: ${e.key} | code: ${e.code||'(none)'} | physical: ${code} | location: ${e.location} | repeat: ${e.repeat?'yes':'no'}`)}update()};"
    if old_down not in script:
        raise RuntimeError('Keyboard keydown anchor not found')
    script = script.replace(old_down, new_down, 1)

    old_up = "const onUp=e=>{const family=modifierFamilyFromEvent(e);let code=family?modifierDown.get(family)||resolveModifier(family,e):physicalCode(e);release(code);const out=fnVisualDown.get(code);if(out){paint(out,false);fnVisualDown.delete(code)}if(e.key==='PrintScreen'||e.code==='PrintScreen'){paint('PrintScreen',true);setTimeout(()=>paint('PrintScreen',false),260)}};"
    new_up = "const onUp=e=>{const family=modifierFamilyFromEvent(e);if(family==='Shift'&&pendingShift){const resolved=resolveModifier('Shift',e);pendingShift=false;current.delete('ShiftPending');paintShiftUnknown(false);if(!resolved){text('keyLog',`Shift detected; side unresolved | code: ${e.code||'(none)'} | location: ${e.location} | keyCode: ${e.keyCode||0} | which: ${e.which||0}`);update();return}text('keyLog',`Shift side resolved on keyup | code: ${e.code||'(none)'} | location: ${e.location} | resolved: ${resolved}`);unique.add(resolved);paint(resolved,true);setTimeout(()=>paint(resolved,false),260);update();return}let code=family?modifierDown.get(family)||resolveModifier(family,e):physicalCode(e);release(code);const out=fnVisualDown.get(code);if(out){release(out);fnVisualDown.delete(code)}if(fnArmed&&fnFunctions.has(e.key||''))release(e.key);if(e.key==='PrintScreen'||e.code==='PrintScreen'){paint('PrintScreen',true);setTimeout(()=>paint('PrintScreen',false),260)}};"
    if old_up not in script:
        raise RuntimeError('Keyboard keyup anchor not found')
    script = script.replace(old_up, new_up, 1)

    return script


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
    marker = '/* keyboard-fullscreen-ui-v3 */'
    override = '''\n<style>\n/* keyboard-fullscreen-ui-v3 */\n.key.shift-unknown{background:rgba(251,191,36,.18)!important;border-color:#fbbf24!important;color:#fde68a!important;box-shadow:0 0 0 2px rgba(251,191,36,.25) inset!important}\n.keyboard-test-active .fullscreen-exit{top:22px!important;right:24px!important;min-width:72px;min-height:46px;padding:11px 18px!important;border-radius:14px!important;box-shadow:0 8px 26px rgba(0,0,0,.28)}\n.keyboard-test-active .tool-layout{padding-top:18px!important;padding-right:112px!important}\n@media(max-width:860px){.keyboard-test-active .fullscreen-exit{top:16px!important;right:16px!important}.keyboard-test-active .tool-layout{padding-right:96px!important}}\n</style>\n'''
    # Remove older injected fullscreen override before applying the current one.
    text = re.sub(r'\n<style>\n/\* keyboard-fullscreen-ui-v[0-9]+ \*/[\s\S]*?</style>\n(?=</head>)', '\n', text, count=1)
    if marker in text:
        return text
    return text.replace('</head>', override + '</head>', 1)

canonical = harden_keyboard_input(canonical_behavior_script())

# Apply the canonical behavior to every deployed keyboard page, including
# Korean/English. Visible translated labels remain untouched.
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

print('Restored explicit Fn checking, improved Shift feedback, canonicalized keyboard behavior, and polished fullscreen UI')
