# PROJECT STATUS — DEVICE CHECKUP

- 마지막 갱신: 2026-09-02
- 상태: POC / PUBLIC DEPLOYED / RED TEAM PASS WITH FIXES / SEO BASELINE DONE / PC & CROSS-BROWSER QA PENDING
- 저장소: `gsh4124-cyber/pc-checkup` (public)
- 공개 URL: `https://gsh4124-cyber.github.io/pc-checkup/`
- 목적: 새 PC·휴대폰 수령 직후 또는 중고 거래 전, 브라우저에서 약 5분 안에 기본 상태를 빠르게 점검하는 한국어 기기 점검 허브의 사용가치 검증
- 차별화 가설: 개별 테스트 기능 자체가 아니라 구매 직후·중고 거래 전의 ‘한 번에 점검’ 흐름 + 개별 검색 진입 페이지
- 공개 배포: GitHub Pages 배포 성공

## 현재 범위

### PC
- 키보드 입력 / 자동반복 / 동시입력
- 마우스 좌·우·중앙 / 휠 / 초고속 연속클릭 보조 감지
- 마이크 입력 레벨 / 파형
- 웹캠 미리보기 / 입력 해상도 / 장치 선택
- 스피커·헤드폰 좌 / 우 / 양쪽 테스트
- 모니터 단색 전체화면 점검
- 5분 전체 점검 결과 LocalStorage 저장

### 휴대폰
- 전체화면형 터치 / 멀티터치 커버리지 검사
- 단색 화면 기반 불량화소·색 이상 육안 점검
- 전면 / 후면 카메라
- 마이크 입력 레벨
- 스피커 테스트 톤
- 진동 API 지원 여부 / 진동 테스트
- 화면 세로·가로 방향 감지
- 6개 항목 정상 / 문제 / 미확인 결과와 진행률 LocalStorage 저장

## 자동 판정 원칙

브라우저가 실제로 측정할 수 있는 항목만 자동 판정한다.

- 터치: 검사 가능 전체 영역 100% + 멀티터치 감지 시 정상 자동 판정
- 카메라: 브라우저가 전·후면을 실제로 구분할 수 있는 facingMode 또는 서로 다른 deviceId를 제공한 경우에만 두 입력 확인 후 정상 자동 판정
- 마이크: 실제 입력 신호 반응이 기준 이상 감지되면 기본 입력 기능 정상 자동 판정
- 화면 불량화소 / 스피커 실제 청취 / 진동 체감 / 카메라 화질·렌즈 상태는 브라우저가 직접 관찰할 수 없어 수동 판정 유지
- 권한 거부 / API 미지원은 장치 불량으로 자동 판정하지 않음

## 전수감사 / Red Team — 2026-09-02

- 최신 main 저장소 전체 트리 확인: 예상 밖의 실행파일·숨김 사본 없음
- 실제 GitHub Pages 배포 아티팩트 다운로드 후 검사
- HTML 9개 내부 링크 / script / stylesheet 참조 누락 0
- HTML 중복 ID 0
- 완전 동일 중복 파일 0
- `app.js` / `mobile.js` JavaScript syntax PASS
- 모바일 390px 폭 기준 9개 페이지 수평 overflow 0
- PC 전체점검 모바일 요약 3칸 한 줄 확인
- PC 각 검사 카드 `검사 열기 / 정상 / 문제 / 미확인` 4버튼 한 줄 확인
- 모바일 결과 `정상 / 문제 있음 / 확인 못함` 한 줄 확인
- 외부 전송용 fetch / XMLHttpRequest / WebSocket / sendBeacon 없음
- 외부 분석·광고·추적 스크립트 없음
- TODO / FIXME / HACK / WIP 코드 표식 없음
- Pages workflow는 main push 기준 checkout → configure → SEO inject → artifact upload → deploy 자동 실행
- 최신 기능 수정 배포 job 전체 단계 SUCCESS

### Red Team에서 발견 및 수정한 결함

1. **터치 검사 100% 도달 구조 문제**
   - 종료 버튼이 오른쪽 위 검사 셀을 덮어 실제로 누를 수 없는 셀이 생길 수 있었음.
   - 수정: 상단 최소 제어영역 58px를 검사 범위에서 제외하고 그 아래 실제 터치 가능한 전체 영역을 100% 기준으로 사용.
   - 100% 도달 시 자동 종료 유지.

2. **모바일 카메라 거짓 정상 가능성**
   - 단순히 전면 요청 / 후면 요청이 둘 다 성공하면 같은 카메라 fallback이어도 정상 처리할 가능성이 있었음.
   - 수정: 실제 facingMode가 일치하거나 서로 다른 deviceId가 확인된 경우에만 전·후면을 구분된 입력으로 인정.
   - 식별정보를 주지 않는 브라우저에서는 자동 정상 판정 보류.
   - facingMode 미제공 브라우저에서도 두 deviceId가 서로 다르면 두 입력을 동시에 확인한 것으로 소급 인정하도록 보완.

3. **PC 전체점검 LocalStorage 손상 시 UI 중단 가능성**
   - 저장값이 깨진 JSON이면 `JSON.parse()` 예외로 전체 진행 UI 초기화가 중단될 수 있었음.
   - 수정: 파싱 오류 / 비객체 값을 안전하게 초기화하고 저장 실패도 UI 동작을 막지 않도록 방어.

4. **PC 마이크·웹캠 시작 중 오류 시 자원 잔존 가능성**
   - 권한 허용 후 AudioContext / video.play / 장치 열거 단계에서 추가 오류가 나면 스트림이 남을 가능성이 있었음.
   - 수정: 오류 경로에서도 스트림과 AudioContext를 정리하고 사용자용 오류 메시지는 유지.
   - 장치 열거 실패는 실제 입력 자체가 정상일 경우 검사 실패로 확대하지 않도록 분리.

5. **모바일 LocalStorage 저장 실패 예외**
   - 브라우저 저장공간 차단·오류 시 결과 저장이 UI 이벤트를 깨뜨릴 수 있었음.
   - 수정: get / set / remove를 방어적으로 처리하고 저장이 불가능해도 현재 세션 검사는 계속 동작하도록 함.

## Red Team 판정

**PASS WITH FIXES**

현재 확인된 범위에서 소프트 출시를 중단해야 할 치명적 결함, 숨겨진 외부 전송, 중복 실행파일, 자동 판정의 명백한 거짓 정상 경로는 발견된 범위 내 수정 완료했다.

단, Red Team PASS는 실제 모든 기기·브라우저에서의 물리 QA 완료 또는 시장 성공을 의미하지 않는다.

## SEO baseline — 2026-09-02

- `robots.txt` / `sitemap.xml` production URL 반영 유지
- 배포 시 `tools/inject_seo.py`가 모든 루트 HTML에 SEO 메타데이터를 정적으로 삽입
- canonical
- Open Graph: type / locale / site_name / title / description / url
- Twitter summary card
- JSON-LD `WebApplication` 구조화 데이터
- GitHub Pages workflow의 SEO inject 단계 SUCCESS
- 실제 배포 artifact에서 `index.html`, `checkup.html`, `mobile.html`, `keyboard.html` canonical / og:url / JSON-LD 존재 확인
- 개별 URL은 각 HTML 파일의 실제 production URL을 canonical로 사용하고 index는 `/pc-checkup/` 루트를 canonical로 사용

SEO 태그 배포 성공은 실제 색인·검색 노출을 의미하지 않는다. 검색엔진의 크롤링·색인과 유입은 현실 데이터로 별도 확인한다.

## 실제 사용 확인

- Android 실제 기기에서 공개 URL 접속 및 모바일 UI 확인 수행.
- 전체화면 터치 검사 화면, PC 전체점검 모바일 레이아웃, 마우스 검사 화면 등 실제 기기에서 확인.
- 사용자 관찰 기준으로 현재 전체 UI는 사용 가능 수준으로 판단됨.
- 단, Android 6개 휴대폰 검사를 체계적으로 모두 완료한 정식 QA와 iPhone QA는 아직 완료로 취급하지 않음.

## 구조상 중복

PC와 모바일 페이지에는 마이크·카메라·오디오·화면 검사 로직이 일부 중복 구현되어 있다. 현재는 각 흐름의 UI와 요구가 달라 POC 안정성을 위해 유지한다. 기능 중복 파일이나 동일 페이지 사본은 없으며, 반복 유지보수 비용이 커질 경우 공통 media utility로 추출한다.

## 의도적으로 제외

- CPU/GPU 벤치마크
- SSD 건강도 / RAM 심층 진단
- 배터리 실제 열화 판정
- 침수 / 수리 이력 판정
- 통신 안테나·속도 품질 판정

브라우저만으로 정확하게 보증하기 어려운 항목이므로 숨겨진 기능이나 미완성 기능이 아니라 현재 제품 범위에서 명시적으로 제외한다.

## 아직 미완료

- 실제 PC 물리 키보드·마우스·마이크·웹캠·오디오·모니터 정식 QA
- Android 휴대폰 6개 전체 항목 정식 체크리스트 QA
- iPhone Safari 실기기 QA
- Chrome / Edge / Firefox / Safari 교차 브라우저 QA
- 실제 검색·사용 데이터 기반 현실검증 및 Continue / Hold / Kill 판단

## 현재 판단

현재 POC 기능 범위에서 추가 검사 종류를 늘리는 것보다 실기기 QA와 실제 사용 데이터 회수가 우선이다. 브라우저 기반 제품으로서 자동 판정은 측정 가능한 항목에 한정하고, 사람의 시각·청각·촉각 판단이 필요한 항목은 명확한 통과 기준을 제시하는 구조가 현재 최선이다.

## 다음

PC 실기기 QA → Android 6개 정식 체크 → iPhone / 교차 브라우저 QA → 검색 노출·실사용 데이터 회수 → Continue / Hold / Kill 판단.
