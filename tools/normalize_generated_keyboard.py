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


def inject_fn_guidance(text: str) -> str:
    text = re.sub(r'<p class="keyboard-note printscreen-fn-note">[\s\S]*?</p>', '', text, count=1)
    lang_match = re.search(r'<html\s+lang="([^"]+)"', text, re.I)
    lang = (lang_match.group(1) if lang_match else 'en').lower()
    messages = {
        'ko': 'Fn 키가 반응하지 않는 것처럼 보이면 Fn + PrintScreen을 함께 눌러 확인해보세요. 일부 노트북은 Fn 키 자체를 브라우저가 직접 인식하지 못하고, Fn 조합의 결과만 확인할 수 있습니다.',
        'en': 'If the Fn key appears not to respond, try Fn + PrintScreen together. On some laptops the browser cannot detect Fn itself and can only verify the result of an Fn combination.',
        'ja': 'Fnキーが反応しないように見える場合は、Fn + PrintScreenを同時に押して確認してください。一部のノートPCではブラウザがFnキー自体を直接検出できず、Fn組み合わせの結果だけを確認できます。',
        'es': 'Si la tecla Fn parece no responder, prueba Fn + PrintScreen a la vez. En algunos portátiles el navegador no puede detectar Fn directamente y solo puede comprobar el resultado de una combinación Fn.',
        'de': 'Wenn die Fn-Taste nicht zu reagieren scheint, drücke Fn + PrintScreen zusammen. Bei manchen Laptops kann der Browser Fn selbst nicht direkt erkennen, sondern nur das Ergebnis einer Fn-Kombination.',
        'fr': 'Si la touche Fn semble ne pas réagir, essayez Fn + PrintScreen ensemble. Sur certains portables, le navigateur ne peut pas détecter directement Fn et ne peut vérifier que le résultat d’une combinaison Fn.',
        'pt': 'Se a tecla Fn parecer não responder, tente Fn + PrintScreen juntos. Em alguns notebooks, o navegador não detecta a tecla Fn diretamente e só consegue verificar o resultado de uma combinação Fn.',
        'it': 'Se il tasto Fn sembra non rispondere, prova Fn + PrintScreen insieme. Su alcuni portatili il browser non rileva direttamente Fn e può verificare solo il risultato di una combinazione Fn.',
        'nl': 'Als de Fn-toets niet lijkt te reageren, probeer Fn + PrintScreen tegelijk. Op sommige laptops kan de browser Fn zelf niet rechtstreeks detecteren en alleen het resultaat van een Fn-combinatie controleren.',
        'id': 'Jika tombol Fn tampak tidak merespons, coba tekan Fn + PrintScreen bersamaan. Pada beberapa laptop, browser tidak dapat mendeteksi Fn secara langsung dan hanya dapat memeriksa hasil kombinasi Fn.',
        'vi': 'Nếu phím Fn có vẻ không phản hồi, hãy thử nhấn Fn + PrintScreen cùng lúc. Trên một số laptop, trình duyệt không thể nhận trực tiếp phím Fn mà chỉ có thể xác nhận kết quả của tổ hợp Fn.',
        'zh-cn': '如果 Fn 键看起来没有反应，请尝试同时按 Fn + PrintScreen。部分笔记本电脑的浏览器无法直接识别 Fn 键，只能确认 Fn 组合键产生的结果。',
        'ru': 'Если кажется, что клавиша Fn не реагирует, попробуйте нажать Fn + PrintScreen вместе. На некоторых ноутбуках браузер не может определить саму Fn и видит только результат комбинации Fn.',
    }
    note = f'<p class="keyboard-note printscreen-fn-note">{messages.get(lang, messages["en"])}</p>'
    anchor = '<div id="keyboard" class="keyboard"></div>'
    if anchor not in text:
        raise RuntimeError('keyboard anchor not found for Fn guidance')
    return text.replace(anchor, note + anchor, 1)


def inject_runtime_helper(text: str) -> str:
    text = re.sub(r'\n<style>\n/\* keyboard-(?:raw-diagnostics|runtime-helper)-v[0-9]+ \*/[\s\S]*?</style>\n(?=</head>)', '\n', text, count=1)
    text = re.sub(r'\n<script>\n/\* keyboard-(?:raw-diagnostics|runtime-helper)-v[0-9]+ \*/[\s\S]*?</script>\n(?=</body>)', '\n', text, count=1)
    text = re.sub(r'<div id="rawKeyEvents" class="raw-key-events">[\s\S]*?</div>', '', text, count=1)
    text = re.sub(r'<div id="fnEvidenceStatus" class="fn-evidence(?: detected)?">[\s\S]*?</div>', '', text, count=1)

    style = '''
<style>
/* keyboard-runtime-helper-v3 */
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
/* keyboard-runtime-helper-v3 */
(()=>{
  const families=['Shift','Control','Alt','Meta'];
  const verifiedSides=new Map(families.map(f=>[f,new Set()]));
  const inferredDown=new Map();
  const secondaryOutputs=new Set(['Insert','Delete','Home','End','PageUp','PageDown']);

  const familyFrom=e=>{
    const key=e.key||'',code=e.code||'';
    if(key==='Shift'||code.startsWith('Shift'))return 'Shift';
    if(key==='Control'||code.startsWith('Control'))return 'Control';
    if(key==='Alt'||key==='AltGraph'||code.startsWith('Alt'))return 'Alt';
    if(key==='Meta'||key==='OS'||code.startsWith('Meta')||code.startsWith('OS'))return 'Meta';
    return '';
  };
  const sideFrom=(family,e)=>{
    const code=(e.code||'').replace('OSLeft','MetaLeft').replace('OSRight','MetaRight');
    const loc=Number(e.location)||Number(e.keyLocation)||0;
    if(code===family+'Left'||loc===1)return family+'Left';
    if(code===family+'Right'||loc===2)return family+'Right';
    if(family==='Meta'){
      const kc=Number(e.keyCode)||0;
      if(kc===91)return 'MetaLeft';
      if(kc===92)return 'MetaRight';
    }
    return '';
  };
  const inferOpposite=(family)=>{
    const sides=verifiedSides.get(family);
    if(!sides||sides.size!==1)return '';
    return sides.has(family+'Left')?family+'Right':family+'Left';
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
    const key=e.key||'',code=e.code||'';
    const printScreen=key==='PrintScreen'||code==='PrintScreen'||code==='Snapshot';
    const remappedSecondary=secondaryOutputs.has(key)&&code&&code!==key;
    if(printScreen)setFnEvidence('PrintScreen');
    else if(remappedSecondary)setFnEvidence(`${key} (physical ${code})`);
  };
  const redispatch=(e,family,code)=>{
    const key=family==='Control'?'Control':family==='Meta'?'Meta':family;
    const synthetic=new KeyboardEvent(e.type,{key,code,location:code.endsWith('Left')?1:2,bubbles:true,cancelable:true,repeat:e.repeat,shiftKey:e.shiftKey,ctrlKey:e.ctrlKey,altKey:e.altKey,metaKey:e.metaKey});
    document.dispatchEvent(synthetic);
  };
  const onRaw=e=>{
    const family=familyFrom(e);
    if(family){
      const verified=sideFrom(family,e);
      if(verified)verifiedSides.get(family).add(verified);
      if(!verified){
        if(e.type==='keydown'&&!e.repeat){
          const inferred=inferOpposite(family);
          if(inferred){
            inferredDown.set(family,inferred);
            e.stopImmediatePropagation();
            redispatch(e,family,inferred);
            return;
          }
        }else if(e.type==='keyup'&&inferredDown.has(family)){
          const inferred=inferredDown.get(family);
          inferredDown.delete(family);
          e.stopImmediatePropagation();
          redispatch(e,family,inferred);
          return;
        }
      }
    }
    checkFnEvidence(e);
  };

  window.addEventListener('keydown',onRaw,true);
  window.addEventListener('keyup',onRaw,true);
  window.addEventListener('blur',()=>inferredDown.clear());
  document.addEventListener('visibilitychange',()=>{if(document.hidden)inferredDown.clear();});
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
    text = inject_fn_guidance(text)
    text = inject_runtime_helper(text)
    path.write_text(text, encoding='utf-8')

print('Copied canonical keyboard engine unchanged, added localized Fn guidance, and hardened unresolved Shift/Control/Alt/Meta side handling')
