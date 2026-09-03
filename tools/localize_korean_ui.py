from pathlib import Path

ROOT = Path('dist')

# Korean pages may intentionally keep standard physical key labels such as Shift,
# Ctrl, Enter, Home, End, etc. User-facing prose, buttons, status text and ad
# placeholders must be Korean.

COMMON_REPLACEMENTS = {
    '<span>Advertisement</span>': '<span>광고</span>',
    'aria-label="Language"': 'aria-label="언어 선택"',
}

KEYBOARD_REPLACEMENTS = {
    '>Exit</button>': '>나가기</button>',
    'Full-size · Numpad': '풀사이즈 · 숫자패드',
    'TKL · No Numpad': '텐키리스 · 숫자패드 없음',
    'Common ANSI-style layout. Korean 106-key and other regional keyboards may have extra or differently shaped keys.': '일반적인 ANSI형 배열입니다. 한국 106키 등 지역별 키보드는 추가 키가 있거나 키 모양이 다를 수 있습니다.',
    '>Start keyboard test</button>': '>키보드 테스트 시작</button>',
    '>Fn check</button>': '>Fn 확인</button>',
    'Use Fn check only while testing secondary Home / End / Page Up / Page Down / Insert / Delete functions. Fullscreen blocks browser shortcuts where supported, including Windows keys when Keyboard Lock is available.': 'Fn 확인은 Home / End / Page Up / Page Down / Insert / Delete의 보조 기능을 확인할 때만 사용하세요. 전체화면에서는 브라우저가 지원하는 범위에서 단축키를 차단하며, Keyboard Lock을 지원하면 Windows 키도 포함됩니다.',
    "b.textContent=on?'Fn check ON':'Fn check'": "b.textContent=on?'Fn 확인 ON':'Fn 확인'",
    "on?'Fn check ON: hold Fn and press the secondary-function key.':'Fn check OFF: normal physical-key test.'": "on?'Fn 확인 ON: 실제 Fn을 누른 채 보조 기능 키를 눌러보세요.':'Fn 확인 OFF: 일반 키 입력을 확인합니다.'",
    "start.textContent=on?'Exit keyboard test':'Start keyboard test'": "start.textContent=on?'키보드 테스트 종료':'키보드 테스트 시작'",
    "b.textContent='Start keyboard test'": "b.textContent='키보드 테스트 시작'",
    'Fn status: click Fn check, then press a physical Fn combination.': 'Fn 상태: Fn 확인을 누른 뒤 실제 Fn 조합키를 눌러보세요.',
    'Fn status: waiting for a browser-visible Fn output...': 'Fn 상태: 브라우저에서 확인 가능한 Fn 출력을 기다리는 중...',
    'Fn output detected: ${output}': 'Fn 출력 감지: ${output}',
    ' | browser-visible secondary result': ' | 브라우저에서 확인 가능한 보조 출력',
    '${inferred} inferred from verified opposite Shift': '${inferred} | 확인된 반대쪽 Shift를 기준으로 추론',
}

root_pages = sorted(p for p in ROOT.glob('*.html'))
for path in root_pages:
    text = path.read_text(encoding='utf-8')
    for old, new in COMMON_REPLACEMENTS.items():
        text = text.replace(old, new)
    if path.name == 'keyboard.html':
        for old, new in KEYBOARD_REPLACEMENTS.items():
            text = text.replace(old, new)
    path.write_text(text, encoding='utf-8')

# Guard the Korean keyboard against the exact accidental English UI phrases that
# previously leaked into production. Standard keycap names are intentionally not
# forbidden.
ko_keyboard = (ROOT / 'keyboard.html').read_text(encoding='utf-8')
for forbidden in [
    'Start keyboard test',
    'Exit keyboard test',
    'Fn check',
    'Fn status:',
    'Common ANSI-style layout.',
    'browser-visible secondary result',
]:
    if forbidden in ko_keyboard:
        raise RuntimeError(f'Korean keyboard UI still contains English phrase: {forbidden}')

for path in root_pages:
    text = path.read_text(encoding='utf-8')
    if '<span>Advertisement</span>' in text:
        raise RuntimeError(f'Korean page still contains English ad placeholder: {path}')

print(f'Localized visible Korean UI across {len(root_pages)} root HTML pages')
