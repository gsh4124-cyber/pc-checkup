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
        'ko': 'Fn 키가 반응하지 않는 것처럼 보이면 Fn + PrintScreen을 함께 눌러 확인해보세요. 작은 키보드나 노트북에서는 Fn 확인을 켠 뒤 같은 물리키를 먼저 Fn 없이 한 번, 이어서 Fn과 함께 한 번 눌러 출력이 달라지는지도 확인할 수 있습니다.',
        'en': 'If Fn appears not to respond, try Fn + PrintScreen. On compact keyboards or laptops, turn on Fn check, press the same physical key once without Fn, then once with Fn to compare the browser-visible output.',
        'ja': 'Fnキーが反応しないように見える場合はFn + PrintScreenを試してください。小型キーボードやノートPCではFn確認をオンにし、同じ物理キーをFnなしで1回、続けてFnと一緒に1回押して出力の違いも確認できます。',
        'es': 'Si Fn parece no responder, prueba Fn + PrintScreen. En teclados compactos o portátiles, activa la comprobación Fn, pulsa la misma tecla física una vez sin Fn y luego otra vez con Fn para comparar la salida visible del navegador.',
        'de': 'Wenn Fn nicht zu reagieren scheint, probiere Fn + PrintScreen. Bei kompakten Tastaturen oder Laptops: Fn-Prüfung einschalten, dieselbe physische Taste einmal ohne Fn und danach einmal mit Fn drücken und die Browser-Ausgabe vergleichen.',
        'fr': 'Si Fn semble ne pas réagir, essayez Fn + PrintScreen. Sur un clavier compact ou un portable, activez la vérification Fn, appuyez une fois sur la même touche sans Fn puis une fois avec Fn afin de comparer la sortie visible du navigateur.',
        'pt': 'Se Fn parecer não responder, tente Fn + PrintScreen. Em teclados compactos ou notebooks, ative a verificação de Fn, pressione a mesma tecla física uma vez sem Fn e depois uma vez com Fn para comparar a saída visível no navegador.',
        'it': 'Se Fn sembra non rispondere, prova Fn + PrintScreen. Su tastiere compatte o portatili, attiva il controllo Fn, premi lo stesso tasto fisico una volta senza Fn e poi una volta con Fn per confrontare l’output visibile nel browser.',
        'nl': 'Als Fn niet lijkt te reageren, probeer Fn + PrintScreen. Zet op compacte toetsenborden of laptops Fn-controle aan, druk dezelfde fysieke toets één keer zonder Fn en daarna één keer met Fn om de browseruitvoer te vergelijken.',
        'id': 'Jika Fn tampak tidak merespons, coba Fn + PrintScreen. Pada keyboard ringkas atau laptop, aktifkan pemeriksaan Fn, tekan tombol fisik yang sama sekali tanpa Fn lalu sekali dengan Fn untuk membandingkan keluaran yang terlihat di browser.',
        'vi': 'Nếu Fn có vẻ không phản hồi, hãy thử Fn + PrintScreen. Với bàn phím nhỏ hoặc laptop, bật kiểm tra Fn, nhấn cùng một phím vật lý một lần không giữ Fn rồi một lần giữ Fn để so sánh đầu ra mà trình duyệt nhìn thấy.',
        'zh-cn': '如果 Fn 看起来没有反应，请尝试 Fn + PrintScreen。对于小型键盘或笔记本电脑，可开启 Fn 检查，先不按 Fn 按一次同一个物理按键，再按住 Fn 按一次，以比较浏览器可见的输出。',
        'ru': 'Если Fn кажется неработающей, попробуйте Fn + PrintScreen. На компактной клавиатуре или ноутбуке включите проверку Fn, нажмите ту же физическую клавишу один раз без Fn, затем один раз с Fn и сравните видимый браузеру результат.',
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
/* keyboard-runtime-helper-v4 */
.fn-evidence{margin-top:7px;padding:8px 10px;border:1px solid var(--line);border-radius:10px;background:#0c141e;font-size:12px;font-weight:800;color:var(--muted)}
.fn-evidence.detected{border-color:var(--accent);color:var(--accent)}
.fn-evidence.indeterminate{border-color:#d6a84a;color:#e7c46c}
.keyboard-test-active .fn-evidence{flex:0 0 auto;margin-top:5px}
</style>
'''
    text = text.replace('</head>', style + '</head>', 1)
    if '<div id="keyLog"' not in text:
        raise RuntimeError('keyLog anchor not found')
    panel = '<div id="fnEvidenceStatus" class="fn-evidence">Fn status: turn on Fn check, then compare the same physical key without Fn and with Fn.</div>'
    text = text.replace('<div id="keyLog"', panel + '<div id="keyLog"', 1)

    script = '''
<script>
/* keyboard-runtime-helper-v4 */
(()=>{
  const families=['Shift','Control','Alt','Meta'];
  const verifiedSides=new Map(families.map(f=>[f,new Set()]));
  const inferredDown=new Map();
  let fnBaseline=null;

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
  const inferOpposite=family=>{
    const sides=verifiedSides.get(family);
    if(!sides||sides.size!==1)return '';
    return sides.has(family+'Left')?family+'Right':family+'Left';
  };
  const patchEventSide=(e,code)=>{
    const loc=code.endsWith('Left')?1:2;
    try{Object.defineProperty(e,'code',{configurable:true,value:code});}catch{}
    try{Object.defineProperty(e,'location',{configurable:true,value:loc});}catch{}
    try{Object.defineProperty(e,'keyLocation',{configurable:true,value:loc});}catch{}
  };
  const fnModeOn=()=>document.getElementById('fnArm')?.classList.contains('active')===true;
  const statusEl=()=>document.getElementById('fnEvidenceStatus');
  const setFnStatus=(msg,kind='')=>{
    const s=statusEl();if(!s)return;
    s.classList.remove('detected','indeterminate');
    if(kind)s.classList.add(kind);
    s.textContent=msg;
  };
  const sig=e=>({key:e.key||'',code:e.code||'',location:Number(e.location)||0});
  const sameSig=(a,b)=>a&&b&&a.key===b.key&&a.code===b.code&&a.location===b.location;
  const isPrintScreen=e=>(e.key||'')==='PrintScreen'||(e.code||'')==='PrintScreen'||(e.code||'')==='Snapshot';
  const handleFn=e=>{
    if(e.type!=='keydown'||e.repeat||familyFrom(e)||!fnModeOn())return;
    if(isPrintScreen(e)){
      fnBaseline=null;
      setFnStatus('Fn combination output detected: PrintScreen','detected');
      return;
    }
    const now=sig(e);
    if(!fnBaseline){
      fnBaseline=now;
      setFnStatus(`Baseline saved: ${now.key||now.code}. Now hold Fn and press the same physical key.`);
      return;
    }
    if(sameSig(fnBaseline,now)){
      setFnStatus('Fn comparison complete: the browser reports the same input with and without Fn. This combination cannot be distinguished here.','indeterminate');
    }else{
      setFnStatus(`Fn combination output changed: ${fnBaseline.key||fnBaseline.code} → ${now.key||now.code}`,'detected');
    }
    fnBaseline=null;
  };
  const onRaw=e=>{
    const family=familyFrom(e);
    if(family){
      const verified=sideFrom(family,e);
      if(verified){
        verifiedSides.get(family).add(verified);
      }else if(e.type==='keydown'&&!e.repeat){
        const inferred=inferOpposite(family);
        if(inferred){inferredDown.set(family,inferred);patchEventSide(e,inferred);}
      }else if(e.type==='keyup'&&inferredDown.has(family)){
        const inferred=inferredDown.get(family);inferredDown.delete(family);patchEventSide(e,inferred);
      }
    }
    handleFn(e);
  };

  window.addEventListener('keydown',onRaw,true);
  window.addEventListener('keyup',onRaw,true);
  window.addEventListener('blur',()=>{inferredDown.clear();fnBaseline=null;});
  document.addEventListener('visibilitychange',()=>{if(document.hidden){inferredDown.clear();fnBaseline=null;}});
  document.addEventListener('DOMContentLoaded',()=>{
    document.getElementById('fnArm')?.addEventListener('click',()=>setTimeout(()=>{
      fnBaseline=null;
      const on=fnModeOn();
      setFnStatus(on
        ? 'Fn check ON: first press a target key once without Fn, then press the same physical key with Fn.'
        : 'Fn status: turn on Fn check, then compare the same physical key without Fn and with Fn.');
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

print('Copied canonical keyboard engine unchanged, normalized unresolved modifier sides on the original event, and added two-step compact Fn verification')
