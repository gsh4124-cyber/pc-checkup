from pathlib import Path
import re

ROOT = Path('dist')
LOCALES = ['ja','es','de','fr','pt','it','nl','id','vi','zh-CN','ru']


def canonical_behavior_script() -> str:
    text = (ROOT/'en'/'keyboard.html').read_text(encoding='utf-8')
    match = re.search(r'<script>\s*document\.addEventListener\([\s\S]*?</script>', text)
    if not match:
        raise RuntimeError('Canonical keyboard behavior script not found in en/keyboard.html')
    return match.group(0)


def normalize_markup(text: str) -> str:
    text = re.sub(r'<button id="[^"]+" type="button" class="fullscreen-exit">', '<button id="exitKeyboard" type="button" class="fullscreen-exit">', text, count=1)
    text = re.sub(r'(<div class="keyboard-actions">\s*<button )id="[^"]+"', r'\1id="startKeyboard"', text, count=1)
    text = re.sub(r'(<div class="controls">\s*<button )id="[^"]+"', r'\1id="resetKeyboard"', text, count=1)
    text = re.sub(r'#start[^\s\{]*\{display:none\}', '#startKeyboard{display:none}', text)
    return text


def polish_fullscreen_ui(text: str) -> str:
    override = '''
<style>
/* keyboard-fullscreen-ui-v4 */
.keyboard-test-active .fullscreen-exit{top:22px!important;right:24px!important;min-width:72px;min-height:46px;padding:11px 18px!important;border-radius:14px!important;box-shadow:0 8px 26px rgba(0,0,0,.28)}
.keyboard-test-active .tool-layout{padding-top:18px!important;padding-right:112px!important}
@media(max-width:860px){.keyboard-test-active .fullscreen-exit{top:16px!important;right:16px!important}.keyboard-test-active .tool-layout{padding-right:96px!important}}
</style>
'''
    text = re.sub(r'\n<style>\n/\* keyboard-fullscreen-ui-v[0-9]+ \*/[\s\S]*?</style>\n(?=</head>)', '\n', text, count=1)
    return text.replace('</head>', override + '</head>', 1)


def inject_runtime_helper(text: str) -> str:
    text = re.sub(r'\n<style>\n/\* keyboard-(?:raw-diagnostics|runtime-helper)-v[0-9]+ \*/[\s\S]*?</style>\n(?=</head>)', '\n', text, count=1)
    text = re.sub(r'\n<script>\n/\* keyboard-(?:raw-diagnostics|runtime-helper)-v[0-9]+ \*/[\s\S]*?</script>\n(?=</body>)', '\n', text, count=1)
    text = re.sub(r'<div id="rawKeyEvents" class="raw-key-events">[\s\S]*?</div>', '', text, count=1)
    text = re.sub(r'<div id="fnEvidenceStatus" class="fn-evidence(?: detected)?">[\s\S]*?</div>', '', text, count=1)

    style = '''
<style>
/* keyboard-runtime-helper-v1 */
.fn-evidence{margin-top:7px;padding:8px 10px;border:1px solid var(--line);border-radius:10px;background:#0c141e;font-size:12px;font-weight:800;color:var(--muted)}
.fn-evidence.detected{border-color:var(--accent);color:var(--accent)}
.keyboard-test-active .fn-evidence{flex:0 0 auto;margin-top:5px}
</style>
'''
    text = text.replace('</head>', style + '</head>', 1)
    if '<div id="keyLog"' not in text:
        raise RuntimeError('keyLog anchor not found')
    panel = '<div id="fnEvidenceStatus" class="fn-evidence">Fn status: click Fn check, then press a physical Fn combination.</div>'
    text = text.replace('<div id="keyLog"', panel + '<div id="keyLog"', 1)

    script = '''
<script>
/* keyboard-runtime-helper-v1 */
(()=>{
  const verifiedShiftSides=new Set();
  const secondaryOutputs=new Set(['Insert','Delete','Home','End','PageUp','PageDown']);
  let inferredShiftDown='';

  const sideFrom=e=>{
    const code=e.code||'';
    const loc=Number(e.location)||Number(e.keyLocation)||0;
    if(code==='ShiftLeft'||loc===1)return 'ShiftLeft';
    if(code==='ShiftRight'||loc===2)return 'ShiftRight';
    return '';
  };
  const paint=(code,on)=>{
    if(!code)return;
    document.querySelectorAll(`[data-code="${CSS.escape(code)}"]`).forEach(k=>k.classList.toggle('active',on));
  };
  const inferOppositeShift=()=>{
    if(verifiedShiftSides.size!==1)return '';
    return verifiedShiftSides.has('ShiftLeft')?'ShiftRight':'ShiftLeft';
  };
  const fnModeOn=()=>document.getElementById('fnArm')?.classList.contains('active')===true;
  const setFnEvidence=output=>{
    const status=document.getElementById('fnEvidenceStatus');
    if(status){status.classList.add('detected');status.textContent=`Fn output detected: ${output}`;}
    const log=document.getElementById('keyLog');
    if(log)log.textContent=`Fn output detected: ${output} | browser-visible secondary result`;
  };
  const checkFnEvidence=e=>{
    if(e.type!=='keydown'||e.repeat||!fnModeOn())return;
    const key=e.key||'';
    const code=e.code||'';
    const printScreen=key==='PrintScreen'||code==='PrintScreen'||code==='Snapshot';
    const remappedSecondary=secondaryOutputs.has(key)&&code&&code!==key;
    if(printScreen)setFnEvidence('PrintScreen');
    else if(remappedSecondary)setFnEvidence(`${key} (physical ${code})`);
  };
  const onRaw=e=>{
    const verified=sideFrom(e);
    if(verified)verifiedShiftSides.add(verified);
    if(e.key==='Shift'&&!verified){
      if(e.type==='keydown'&&!e.repeat){
        const inferred=inferOppositeShift();
        if(inferred){
          inferredShiftDown=inferred;
          paint(inferred,true);
          const log=document.getElementById('keyLog');
          if(log)log.textContent=`${inferred} inferred from verified opposite Shift`;
        }
      }else if(e.type==='keyup'&&inferredShiftDown){
        paint(inferredShiftDown,false);
        inferredShiftDown='';
      }
    }
    checkFnEvidence(e);
  };

  window.addEventListener('keydown',onRaw,true);
  window.addEventListener('keyup',onRaw,true);
  window.addEventListener('blur',()=>{if(inferredShiftDown)paint(inferredShiftDown,false);inferredShiftDown='';});
  document.addEventListener('visibilitychange',()=>{if(document.hidden&&inferredShiftDown){paint(inferredShiftDown,false);inferredShiftDown='';}});
  document.addEventListener('DOMContentLoaded',()=>{
    document.getElementById('fnArm')?.addEventListener('click',()=>setTimeout(()=>{
      const b=document.getElementById('fnArm');
      const status=document.getElementById('fnEvidenceStatus');
      if(!status)return;
      status.classList.remove('detected');
      status.textContent=b?.classList.contains('active')
        ? 'Fn status: waiting for a browser-visible Fn output...'
        : 'Fn status: click Fn check, then press a physical Fn combination.';
    },0));
  });
})();
</script>
'''
    return text.replace('</body>', script + '</body>', 1)


canonical = canonical_behavior_script()
all_paths = [ROOT/'keyboard.html', ROOT/'en'/'keyboard.html'] + [ROOT/l/'keyboard.html' for l in LOCALES]
for path in all_paths:
    if not path.exists():
        continue
    text = normalize_markup(path.read_text(encoding='utf-8'))
    text, count = re.subn(r'<script>\s*document\.addEventListener\([\s\S]*?</script>', lambda _: canonical, text, count=1)
    if count != 1:
        raise RuntimeError(f'Keyboard behavior script not found: {path}')
    text = polish_fullscreen_ui(text)
    text = inject_runtime_helper(text)
    path.write_text(text, encoding='utf-8')

print('Copied canonical keyboard engine unchanged and added validator-safe Shift/Fn runtime helper')
