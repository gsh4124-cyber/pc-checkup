# PROJECT STATUS — DEVICE CHECKUP

- 마지막 갱신: 2026-09-03
- 상태: **POC / PUBLIC DEPLOYED / GLOBAL 13-LANGUAGE DEPLOYED / AUTOMATED ARTIFACT QA PASS WITH FIXES / RED TEAM PASS WITH FIXES / EXACT-REVISION MULTI-ENGINE PRODUCTION QA PASS / PHYSICAL DEVICE & REAL-BROWSER QA PENDING**
- 저장소: `gsh4124-cyber/pc-checkup` (public)
- 공개 URL: `https://gsh4124-cyber.github.io/pc-checkup/`

## 제품 범위

PC 6종:
- 키보드
- 마우스
- 모니터
- 스피커·헤드폰
- 마이크
- 웹캠
- 5분 전체점검

휴대폰 6종:
- 터치·멀티터치
- 화면 색상·불량화소
- 전·후면 카메라
- 마이크
- 스피커
- 진동·화면회전
- 결과/진행률 저장

원칙:
- 브라우저가 신뢰성 있게 측정 가능한 신호만 자동 판정한다.
- 화면 결함, 실제 청취, 진동 체감, 카메라 화질 등 사람의 감각이 필요한 항목은 수동 판정을 유지한다.
- 권한 거부·브라우저 미지원만으로 하드웨어 고장 판정을 하지 않는다.

## 현재 배포

지원 언어:
`ko / en / ja / es / de / fr / pt / it / nl / id / vi / zh-CN / ru`

총 **13개 언어 × 9개 기능 페이지 = 117 indexable URL**.

검색 기본 구조:
- canonical
- hreflang
- x-default
- Open Graph / Twitter
- JSON-LD WebApplication
- sitemap.xml
- robots.txt
- Baiduspider / Yandex crawler 허용

외부 Gate:
- Baidu Search Resource Platform 소유확인/제출
- Yandex Webmaster 자체도메인·소유확인·제출
- 중국 본토 안정적 도메인·호스팅 경로
- Google/Bing/Naver/Daum 등 실제 등록·색인·노출 검증

## 2026-09-03 키보드 회귀 복구

최근 키보드 수정 중 Shift / Fn / fullscreen / Keyboard Lock 회귀가 반복되어 이전 실제 작동 구현과 최신 구현을 비교해 입력 판별 구조를 복원했다.

현재 구조:
- Shift / Ctrl / Alt / Meta modifier 판별을 공통 규칙으로 통일
- 우선순위: `event.code` → `event.location` → 최소 fallback
- `ShiftUnknown`, 화면에서 Shift 선선택, 구형 `initKeyboard()` 경로 제거
- Fn은 자동 추론만 사용하지 않고 명시적 `Fn check` + `fnArmed` 상태 복원
- Fn check ON에서 Home / End / PageUp / PageDown / Insert / Delete 보조출력을 별도 확인
- fullscreen 검사 유지
- Keyboard Lock은 검사 흐름 방해 키를 선택적으로 차단
- Windows 시작키 대응을 위해 `MetaLeft / MetaRight`도 fullscreen lock 대상에 포함
- stuck-key 안전 해제 유지

실제 Left/Right Shift 최종 물리 QA는 다른 PC에서 재확인 예정.

## 2026-09-03 전수 Artifact QA

실제 GitHub Pages artifact를 다운로드해 독립 검사했다.

검증 기준 run:
- run 83: `33728647123`
- head: `16fcae97c387b1457102c19e4403088892c31be7`
- artifact: `9882948962`

결과:
- HTML 117개 PASS
- sitemap 117 URL PASS
- 13개 언어 × 9페이지 존재 PASS
- 내부 href/src 누락 0
- duplicate id 0
- canonical 누락 0
- x-default hreflang 누락 0
- 비한국어 raw Korean leakage 0 (언어선택기의 `한국어` 제외)
- 모든 locale `app.js / mobile.js` syntax PASS
- 모든 inline JavaScript syntax PASS
- 키보드 구조 invariant 전 언어 PASS
- 외부 전송용 `fetch / XMLHttpRequest / WebSocket / sendBeacon` 없음
- Google Analytics / Tag Manager 없음
- 실제 광고 provider script 없음

### 전수검사에서 발견한 실제 회귀 — 수정 완료

글로벌 번역기가 HTML 전체에 단순 문자열 치환을 적용하면서 UI 문구뿐 아니라 인라인 JS와 DOM 구조까지 번역하는 문제가 발견됐다.

실제 위험:
- `fitKeyboard` 함수명 변형
- `startKeyboard / exitKeyboard / resetKeyboard` DOM id 변형
- `ShiftLeft / ShiftRight / MetaLeft / MetaRight / ArrowLeft / ArrowRight` 같은 브라우저 표준 키 코드 변형
- 베트남어에서는 변형된 함수명에 공백이 생겨 실제 JS syntax error 발생

수정:
- `tools/normalize_generated_keyboard.py`
  - 모든 언어 생성 완료 후 영어 키보드 동작 JS를 canonical 구조 원본으로 복원
  - DOM 구조 id canonical 유지
- `tools/validate_dist.py`
  - 배포 전 117 HTML 전체 구조/SEO/참조/JS syntax/키보드 invariant/광고슬롯 검증
- Pages workflow에 `Validate localized artifact` 단계를 추가
  - 검증 실패 시 Upload/Deploy 차단

상세 기록: `QA_AUDIT_2026-09-03.md`

## 2026-09-03 공개 Production QA

정적 산출물 PASS와 실제 공개 GitHub Pages PASS를 분리하기 위해 `Production Browser Smoke`를 운영한다.

### 실제 공개 회귀 발견과 수정

첫 공개 검증에서 언어 선택기가 2개 생성되는 회귀를 발견했다.

확인된 원인:
- 최신 canonical 선택기 `#languagePicker`
- 오래된 글로벌 빌드 단계가 남기던 `.lang-switch`

숨김 처리 대신 글로벌 빌드에서 구형 `.lang-switch`를 물리적으로 제거했다.

재발 방지:
- `d1ec3263536e01fe23f4392095ba68f63a5c28a3` — legacy duplicate selector 실제 삭제
- `22e2140c554d431add5a7918188bfe14b6ce8086` — locale-aware 공개 QA와 selector 중복·잘못된 locale redirect 검사 추가

### 오래된 배포를 현재 PASS로 착각하는 경로 제거

기존 Production Smoke는 공개 sitemap이 117 URL인지 확인한 뒤 테스트했기 때문에, 새 commit의 GitHub Pages 배포가 아직 끝나지 않은 순간에는 **이전 배포본을 새 commit의 PASS로 잘못 검사할 가능성**이 있었다.

이를 막기 위해:
- Pages 빌드가 `dist/build-revision.txt`에 실제 `GITHUB_SHA`를 기록한다.
- push 기반 Production QA는 공개 `build-revision.txt`가 현재 `GITHUB_SHA`와 정확히 같아질 때까지 기다린다.
- 일치하지 않으면 QA를 시작하지 않고 실패한다.
- 문서만 바뀐 commit은 불필요한 Pages 재배포·Production Smoke를 만들지 않는다.

### 자동 다중 엔진 검증

`tools/production-smoke.mjs`를 browser-engine selectable로 만들고 push/수동 실행에서는 다음 세 엔진을 독립 실행한다.

- Chromium
- Firefox
- WebKit

6시간 주기 heartbeat는 비용·시간을 줄이기 위해 Chromium만 실행한다.

최종 검증:
- Pages deploy run `33752636144`: **SUCCESS**
- Production Browser Smoke run `33752636269`: **SUCCESS**
- `Production QA · Chromium`: SUCCESS
- `Production QA · firefox`: SUCCESS
- `Production QA · webkit`: SUCCESS
- 세 job 모두 `Wait for exact deployed revision`: SUCCESS

현재 공개 QA 범위:
- 현재 commit과 실제 공개 배포 revision 일치
- sitemap 117 URL 실제 접근
- 대표 `ko / en / ja / zh-CN / ru` 모바일 공개 화면
- 대표 영어·중국어·러시아어 기능 페이지
- `#languagePicker` 정확히 1개
- retired `.lang-switch` 0개
- 헤더 language select 1개
- pageerror 없음
- 대표 홈 모바일 horizontal overflow 없음
- 예상하지 않은 외부 네트워크 origin 없음

**Playwright WebKit PASS를 실제 iPhone Safari PASS로 부르지 않는다.** 자동 엔진 호환성은 확인됐지만 실제 기기·브라우저 UI·권한·하드웨어 동작은 별도 Gate다.

## 광고 준비 상태

실제 광고 네트워크 코드는 아직 연결하지 않았다.

예약 광고 슬롯만 배치:
- 랜딩 `index.html`: 1곳
- PC 전체점검 `checkup.html`: 1곳
- 모바일 전체점검 `mobile.html`: 1곳

원칙:
- 개별 기능 검사 페이지에는 광고 슬롯을 넣지 않음
- fullscreen 검사 중 광고 없음
- 실제 광고 provider 연결 전까지 inert placeholder 상태

현재 artifact 기준 13개 언어 모두 위 3개 페이지에 슬롯 1개씩 존재함.

## 기존 기능 검토 결과

PC:
- 마우스: 좌/우/중앙/휠, 초고속 반복입력 후보 보조표시
- 마이크: 권한 처리, meter/waveform, stop/unload 자원정리
- 웹캠: 영상/해상도/장치선택, 자원정리
- 스피커: 좌/우/양쪽 tone, 실제 청취 수동 판정
- 모니터: 단색 fullscreen, 시각 수동 판정
- 전체점검: safe LocalStorage, 진행률, reset, print/PDF

모바일:
- 터치: 8×13 검사영역, 100% 자동종료, 멀티터치 포함 시 자동 정상
- 카메라: 실제 전/후면 구분 근거 있을 때만 자동 정상
- 마이크: 실제 입력 threshold 기반 자동 정상
- 스피커/화면: 수동 판정
- 회전 자동감지, 진동 미지원은 고장 판정하지 않음
- pagehide 자원정리

## 아직 미완료 — 실제 물리/현실 QA

자동 엔진 QA와 실제 하드웨어·실제 기기 PASS를 구분한다.

필수 남은 QA:
- 다른 PC에서 Left Shift / Right Shift 실제 분리 확인
- Left/Right Ctrl, Alt 재확인
- fullscreen에서 Windows 시작키 차단 실제 확인
- Fn check ON/OFF 실제 노트북 보조키 확인
- F1~F12 / Esc / 방향키 / Home-End 계열 browser interference 확인
- focus loss 후 stuck key 없음 확인
- 마우스 실제 1클릭=1카운트 확인
- 스피커 실제 좌/우 청취
- 마이크 실제 입력
- 웹캠 실제 영상/장치선택
- 모니터 실제 시각검사
- Android 정식 6/6
- 실제 iPhone Safari
- 실제 Chrome / Edge / Firefox / Safari 환경에서 권한·하드웨어 상호작용 확인
- 현지어 네이티브 수준 검수
- 실제 검색 색인·유입·사용 데이터

## 현재 판정

- 구현: PASS
- 글로벌 빌드: PASS
- 배포: PASS
- 정적/Artifact QA: **PASS WITH FIXES**
- Red Team: PASS WITH FIXES
- 공개 exact-revision Production QA: **PASS WITH FIXES**
- 자동 Chromium / Firefox / WebKit: **PASS**
- 광고 슬롯 준비: PASS (실광고 미연결)
- 실제 PC 물리 QA: PENDING
- 실제 모바일·브라우저·하드웨어 QA: PENDING
- 검색/시장 현실검증: PENDING

다음 Gate는 **실제 PC 물리 QA + 실제 Android/iPhone/브라우저 하드웨어 상호작용 QA**다. 이후 광고 provider 연결/AdSense Gate, 검색유통, 실제 사용·시장 데이터를 분리해 진행한다.
