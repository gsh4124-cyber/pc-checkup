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
/* keyboard-fullscreen-ui-v5 */
.keyboard-test-active .fullscreen-exit{top:22px!important;right:24px!important;min-width:72px;min-height:46px;padding:11px 18px!important;border-radius:14px!important;box-shadow:0 8px 26px rgba(0,0,0,.28)}
.keyboard-test-active .tool-layout{padding-top:18px!important;padding-right:112px!important}
.keyboard-note{font-size:14px!important;line-height:1.7!important;max-width:1100px;color:#9fb0c3!important}
.printscreen-fn-note{margin-top:4px!important;padding:10px 12px;border-left:3px solid var(--accent);background:rgba(111,229,189,.05);border-radius:8px}
.side .notice{font-size:15px!important;line-height:1.75!important;padding:18px!important}
.side .notice strong{display:block;font-size:17px;margin-bottom:6px}
.eventlog{font-size:13px!important;line-height:1.55!important}
.keyboard-actions{align-items:center}
.fn-virtual-key{display:inline-flex;align-items:center;justify-content:center;min-width:86px;height:42px;padding:0 12px;border:1px solid var(--line);border-radius:11px;background:#0c141e;color:var(--muted);font-weight:900;font-size:13px}
.fn-virtual-key.active{border-color:#d6a84a;color:#e7c46c;background:rgba(214,168,74,.08)}
.fn-virtual-key.detected{border-color:var(--accent);color:var(--accent);background:rgba(111,229,189,.08)}
.modifier-note{margin-top:2px!important;padding:9px 12px;background:rgba(255,255,255,.025);border-radius:8px}
@media(max-width:860px){.keyboard-test-active .fullscreen-exit{top:16px!important;right:16px!important}.keyboard-test-active .tool-layout{padding-right:96px!important}.keyboard-note{font-size:13px!important}.side .notice{font-size:14px!important}}
</style>
'''
    text = re.sub(r'\n<style>\n/\* keyboard-fullscreen-ui-v[0-9]+ \*/[\s\S]*?</style>\n(?=</head>)', '\n', text, count=1)
    return text.replace('</head>', override + '</head>', 1)


def language_of(text: str) -> str:
    m = re.search(r'<html\s+lang="([^"]+)"', text, re.I)
    return (m.group(1) if m else 'en').lower()


def inject_guidance(text: str) -> str:
    text = re.sub(r'<p class="keyboard-note printscreen-fn-note">[\s\S]*?</p>', '', text, count=1)
    text = re.sub(r'<p class="keyboard-note modifier-note">[\s\S]*?</p>', '', text, count=1)
    lang = language_of(text)
    fn_messages = {
        'ko': 'Fn 키는 브라우저가 직접 식별하지 못하는 경우가 많습니다. Fn 확인을 켠 뒤 같은 물리키를 먼저 Fn 없이 한 번, 이어서 Fn과 함께 한 번 눌러 출력 차이를 비교하세요. Fn + PrintScreen처럼 조합 결과가 브라우저에 보이면 간접 확인됩니다.',
        'en': 'Browsers often cannot identify Fn directly. Turn on Fn check, press the same physical key once without Fn, then once with Fn and compare the output. A browser-visible result such as Fn + PrintScreen can verify Fn indirectly.',
        'ja': 'Fnキーはブラウザが直接識別できない場合があります。Fn確認をオンにし、同じ物理キーをFnなしで1回、続けてFnと一緒に1回押して出力差を比較してください。Fn + PrintScreenのように結果がブラウザに現れれば間接確認できます。',
        'es': 'El navegador a menudo no puede identificar Fn directamente. Activa la comprobación Fn, pulsa la misma tecla una vez sin Fn y luego con Fn para comparar la salida. Un resultado visible como Fn + PrintScreen permite una verificación indirecta.',
        'de': 'Browser können Fn oft nicht direkt erkennen. Aktiviere die Fn-Prüfung, drücke dieselbe Taste einmal ohne Fn und danach einmal mit Fn und vergleiche die Ausgabe. Ein sichtbares Ergebnis wie Fn + PrintScreen bestätigt Fn indirekt.',
        'fr': 'Le navigateur ne peut souvent pas identifier Fn directement. Activez la vérification Fn, appuyez sur la même touche une fois sans Fn puis avec Fn et comparez la sortie. Un résultat visible comme Fn + PrintScreen permet une vérification indirecte.',
        'pt': 'O navegador muitas vezes não identifica Fn diretamente. Ative a verificação de Fn, pressione a mesma tecla uma vez sem Fn e depois com Fn para comparar a saída. Um resultado visível como Fn + PrintScreen permite confirmação indireta.',
        'it': 'Il browser spesso non può identificare Fn direttamente. Attiva il controllo Fn, premi lo stesso tasto una volta senza Fn e poi con Fn e confronta l’output. Un risultato visibile come Fn + PrintScreen consente una verifica indiretta.',
        'nl': 'Browsers kunnen Fn vaak niet rechtstreeks herkennen. Zet Fn-controle aan, druk dezelfde toets één keer zonder Fn en daarna met Fn en vergelijk de uitvoer. Een zichtbaar resultaat zoals Fn + PrintScreen geeft indirecte bevestiging.',
        'id': 'Browser sering tidak dapat mengenali Fn secara langsung. Aktifkan pemeriksaan Fn, tekan tombol yang sama sekali tanpa Fn lalu sekali dengan Fn dan bandingkan hasilnya. Hasil yang terlihat seperti Fn + PrintScreen dapat mengonfirmasi Fn secara tidak langsung.',
        'vi': 'Trình duyệt thường không thể nhận trực tiếp phím Fn. Bật kiểm tra Fn, nhấn cùng một phím một lần không giữ Fn rồi một lần giữ Fn và so sánh đầu ra. Kết quả nhìn thấy như Fn + PrintScreen có thể xác nhận gián tiếp.',
        'zh-cn': '浏览器通常无法直接识别 Fn。开启 Fn 检查后，先不按 Fn 按一次同一个物理键，再按住 Fn 按一次并比较输出。像 Fn + PrintScreen 这样浏览器可见的结果可以作为间接确认。',
        'ru': 'Браузер часто не может определить Fn напрямую. Включите проверку Fn, нажмите ту же физическую клавишу один раз без Fn, затем с Fn и сравните результат. Видимый результат вроде Fn + PrintScreen даёт косвенное подтверждение.',
    }
    mod_messages = {
        'ko': '좌·우 Shift/Ctrl/Alt/Win은 일부 키보드에서 한쪽 위치 정보만 브라우저에 전달됩니다. 오른쪽 키가 바로 반응하지 않으면 먼저 왼쪽 같은 키를 한 번 누른 뒤 오른쪽을 눌러보세요. 반대쪽이 문제라면 순서를 반대로 하면 됩니다.',
        'en': 'Some keyboards expose side information for only one Shift/Ctrl/Alt/Win key. If the right-side key does not react, press the matching left-side key once first, then the right-side key. Reverse the order if the left side is the one not identified.',
        'ja': '一部のキーボードではShift/Ctrl/Alt/Winの片側だけ位置情報がブラウザに渡ります。右側が反応しない場合は同じ左側キーを一度押してから右側を押してください。左側が問題なら順序を逆にしてください。',
    }
    fn_note = f'<p class="keyboard-note printscreen-fn-note">{fn_messages.get(lang, fn_messages["en"])}</p>'
    mod_note = f'<p class="keyboard-note modifier-note">{mod_messages.get(lang, mod_messages["en"])}</p>'
    anchor = '<div id="keyboard" class="keyboard"></div>'
    if anchor not in text:
        raise RuntimeError('keyboard anchor not found for guidance')
    return text.replace(anchor, mod_note + fn_note + anchor, 1)


def inject_runtime_helper(text: str) -> str:
    text = re.sub(r'\n<style>\n/\* keyboard-(?:raw-diagnostics|runtime-helper)-v[0-9]+ \*/[\s\S]*?</style>\n(?=</head>)', '\n', text, count=1)
    text = re.sub(r'\n<script>\n/\* keyboard-(?:raw-diagnostics|runtime-helper)-v[0-9]+ \*/[\s\S]*?</script>\n(?=</body>)', '\n', text, count=1)
    text = re.sub(r'<div id="rawKeyEvents" class="raw-key-events">[\s\S]*?</div>', '', text, count=1)
    text = re.sub(r'<div id="fnEvidenceStatus" class="fn-evidence(?: detected| indeterminate)*">[\s\S]*?</div>', '', text, count=1)
    text = re.sub(r'<span id="fnVirtualKey" class="fn-virtual-key(?: active| detected)*">[\s\S]*?</span>', '', text, count=1)

    style = '''
<style>
/* keyboard-runtime-helper-v5 */
.fn-evidence{margin-top:9px;padding:11px 13px;border:1px solid var(--line);border-radius:10px;background:#0c141e;font-size:13px;font-weight:800;line-height:1.55;color:var(--muted)}
.fn-evidence.detected{border-color:var(--accent);color:var(--accent)}
.fn-evidence.indeterminate{border-color:#d6a84a;color:#e7c46c}
.keyboard-test-active .fn-evidence{flex:0 0 auto;margin-top:6px}
</style>
'''
    text = text.replace('</head>', style + '</head>', 1)
    if '<button id="fnArm"' not in text or '<div id="keyLog"' not in text:
        raise RuntimeError('Fn/keyLog anchor not found')
    text = re.sub(r'(<button id="fnArm"[^>]*>[^<]*</button>)', r'\1<span id="fnVirtualKey" class="fn-virtual-key">Fn · indirect</span>', text, count=1)
    panel = '<div id="fnEvidenceStatus" class="fn-evidence"></div>'
    text = text.replace('<div id="keyLog"', panel + '<div id="keyLog"', 1)

    script = '''
<script>
/* keyboard-runtime-helper-v5 */
(()=>{
  const lang=(document.documentElement.lang||'en').toLowerCase();
  const ko=lang.startsWith('ko');
  const t={
    idle:ko?'Fn \\uc0c1\\ud0dc: Fn \\ud655\\uc778\\uc744 \\ucf20 \\ub4a4 \\uac19\\uc740 \\ubb3c\\ub9ac\\ud0a4\\ub97c Fn \\uc5c6\\uc774 1\\ubc88, Fn\\uacfc \\ud568\\uaed8 1\\ubc88 \\ub20c\\ub7ec \\ube44\\uad50\\ud558\\uc138\\uc694.':'Fn status: turn on Fn check, then compare the same physical key once without Fn and once with Fn.',
    armed:ko?'Fn \\ud655\\uc778 ON: \\uba3c\\uc800 \\ub300\\uc0c1 \\ud0a4\\ub97c Fn \\uc5c6\\uc774 \\ud55c \\ubc88 \\ub204\\ub978 \\ub4a4, \\uac19\\uc740 \\ubb3c\\ub9ac\\ud0a4\\ub97c Fn\\uacfc \\ud568\\uaed8 \\ud55c \\ubc88 \\ub204\\ub974\\uc138\\uc694.':'Fn check ON: first press a target key once without Fn, then press the same physical key with Fn.',
    baseline:ko?'\\uae30\\uc900 \\uc785\\ub825 \\uc800\\uc7a5: ':'Baseline saved: ',
    next:ko?' · \\uc774\\uc81c Fn\\uc744 \\ub204\\ub978 \\ucc44 \\uac19\\uc740 \\ubb3c\\ub9ac\\ud0a4\\ub97c \\ub204\\ub974\\uc138\\uc694.':' · Now hold Fn and press the same physical key.',
    same:ko?'Fn \\ube44\\uad50 \\uc644\\ub8cc: Fn \\uc804\\ud6c4 \\uc785\\ub825\\uc774 \\ube0c\\ub77c\\uc6b0\\uc800\\uc5d0\\uc11c \\ub3d9\\uc77c\\ud569\\ub2c8\\ub2e4. \\uc774 \\uc870\\ud569\\uc740 \\uc5ec\\uae30\\uc11c \\uad6c\\ubd84\\ud560 \\uc218 \\uc5c6\\uc2b5\\ub2c8\\ub2e4.':'Fn comparison complete: the browser reports the same input with and without Fn. This combination cannot be distinguished here.',
    detected:ko?'Fn \\uc870\\ud569 \\ubcc0\\ud654 \\ud655\\uc778: ':'Fn combination output changed: ',
    print:ko?'Fn \\uc870\\ud569 \\uacb0\\uacfc \\ud655\\uc778: PrintScreen':'Fn combination output detected: PrintScreen',
    chipIdle:ko?'Fn · \\uac04\\uc811 \\ud655\\uc778':'Fn · indirect',
    chipOn:ko?'Fn · \\ud655\\uc778 \\uc911':'Fn · checking',
    chipOk:ko?'Fn · \\uc870\\ud569 \\ud655\\uc778':'Fn · verified'
  };
  const families=['Shift','Control','Alt','Meta'];
  const verifiedSides=new Map(families.map(f=>[f,new Set()]));
  const inferredDown=new Map();
  let fnBaseline=null;

  const familyFrom=e=>{const key=e.key||'',code=e.code||'';if(key==='Shift'||code.startsWith('Shift'))return'Shift';if(key==='Control'||code.startsWith('Control'))return'Control';if(key==='Alt'||key==='AltGraph'||code.startsWith('Alt'))return'Alt';if(key==='Meta'||key==='OS'||code.startsWith('Meta')||code.startsWith('OS'))return'Meta';return''};
  const sideFrom=(family,e)=>{const code=(e.code||'').replace('OSLeft','MetaLeft').replace('OSRight','MetaRight');const loc=Number(e.location)||Number(e.keyLocation)||0;if(code===family+'Left'||loc===1)return family+'Left';if(code===family+'Right'||loc===2)return family+'Right';if(family==='Meta'){const kc=Number(e.keyCode)||0;if(kc===91)return'MetaLeft';if(kc===92)return'MetaRight'}return''};
  const inferOpposite=family=>{const sides=verifiedSides.get(family);if(!sides||sides.size!==1)return'';return sides.has(family+'Left')?family+'Right':family+'Left'};
  const patchEventSide=(e,code)=>{const loc=code.endsWith('Left')?1:2;try{Object.defineProperty(e,'code',{configurable:true,value:code})}catch{}try{Object.defineProperty(e,'location',{configurable:true,value:loc})}catch{}try{Object.defineProperty(e,'keyLocation',{configurable:true,value:loc})}catch{}};
  const fnModeOn=()=>document.getElementById('fnArm')?.classList.contains('active')===true;
  const statusEl=()=>document.getElementById('fnEvidenceStatus');
  const chipEl=()=>document.getElementById('fnVirtualKey');
  const setChip=(mode='idle')=>{const c=chipEl();if(!c)return;c.classList.remove('active','detected');if(mode==='active'){c.classList.add('active');c.textContent=t.chipOn}else if(mode==='detected'){c.classList.add('detected');c.textContent=t.chipOk}else c.textContent=t.chipIdle};
  const setFnStatus=(msg,kind='')=>{const s=statusEl();if(!s)return;s.classList.remove('detected','indeterminate');if(kind)s.classList.add(kind);s.textContent=msg};
  const sig=e=>({key:e.key||'',code:e.code||'',location:Number(e.location)||0});
  const sameSig=(a,b)=>a&&b&&a.key===b.key&&a.code===b.code&&a.location===b.location;
  const isPrintScreen=e=>(e.key||'')==='PrintScreen'||(e.code||'')==='PrintScreen'||(e.code||'')==='Snapshot';
  const handleFn=e=>{if(e.type!=='keydown'||e.repeat||familyFrom(e)||!fnModeOn())return;if(isPrintScreen(e)){fnBaseline=null;setFnStatus(t.print,'detected');setChip('detected');return}const now=sig(e);if(!fnBaseline){fnBaseline=now;setFnStatus(t.baseline+(now.key||now.code)+t.next);setChip('active');return}if(sameSig(fnBaseline,now)){setFnStatus(t.same,'indeterminate');setChip('active')}else{setFnStatus(t.detected+(fnBaseline.key||fnBaseline.code)+' → '+(now.key||now.code),'detected');setChip('detected')}fnBaseline=null};
  const onRaw=e=>{const family=familyFrom(e);if(family){const verified=sideFrom(family,e);if(verified){verifiedSides.get(family).add(verified)}else if(e.type==='keydown'&&!e.repeat){const inferred=inferOpposite(family);if(inferred){inferredDown.set(family,inferred);patchEventSide(e,inferred)}}else if(e.type==='keyup'&&inferredDown.has(family)){const inferred=inferredDown.get(family);inferredDown.delete(family);patchEventSide(e,inferred)}}handleFn(e)};

  window.addEventListener('keydown',onRaw,true);window.addEventListener('keyup',onRaw,true);
  window.addEventListener('blur',()=>{inferredDown.clear();fnBaseline=null});
  document.addEventListener('visibilitychange',()=>{if(document.hidden){inferredDown.clear();fnBaseline=null}});
  document.addEventListener('DOMContentLoaded',()=>{setFnStatus(t.idle);setChip('idle');document.getElementById('fnArm')?.addEventListener('click',()=>setTimeout(()=>{fnBaseline=null;const on=fnModeOn();setFnStatus(on?t.armed:t.idle);setChip(on?'active':'idle')},0))});
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
    text = inject_guidance(text)
    text = inject_runtime_helper(text)
    path.write_text(text, encoding='utf-8')

print('Copied canonical keyboard engine unchanged, improved modifier guidance, Fn visibility/status localization, and keyboard-page readability')
