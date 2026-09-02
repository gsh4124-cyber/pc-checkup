# PROJECT STATUS — DEVICE CHECKUP

- 마지막 갱신: 2026-09-02
- 상태: POC / PUBLIC DEPLOYED / PC·MOBILE REAL-DEVICE QA PENDING
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
- 터치 / 멀티터치
- 단색 화면 기반 불량화소·색 이상 육안 점검
- 전면 / 후면 카메라
- 마이크 입력 레벨
- 스피커 테스트 톤
- 진동 API 지원 여부 / 진동 테스트
- 화면 세로·가로 방향 감지

## 전수검사 및 수정 — 2026-09-02

- 저장소 전체 트리 재확인: `.github` 포함 총 19개 파일, 예상 밖의 숨김 실행파일·중복 사본 없음
- TODO / FIXME / HACK / WIP 표식 검색: 없음
- 외부 전송용 `fetch / XMLHttpRequest / WebSocket / sendBeacon` 사용 없음
- `app.js` JavaScript syntax PASS
- `mobile.js` JavaScript syntax PASS
- GitHub Pages 최신 배포 run `33622960032`: SUCCESS
- 모바일 추가 후 sitemap에 `mobile.html` 포함 확인
- 모바일 마이크를 반복 시작할 때 이전 스트림/AudioContext가 남을 수 있던 자원 누수 가능성 수정
- 모바일 카메라 전환 시 이전 영상 객체를 명시적으로 정리하도록 수정
- 페이지 이탈 시 카메라·마이크·진동 자원을 정리하도록 `pagehide` cleanup 추가
- README가 PC 전용 / 배포 전 상태로 남아 있던 문서 불일치 수정

## 구조상 중복

PC와 모바일 페이지에는 마이크·카메라·오디오·화면 검사 로직이 일부 중복 구현되어 있다. 현재는 각 흐름의 UI와 요구가 달라 POC 안정성을 위해 유지한다. 기능 중복 파일이나 동일 페이지 사본은 없으며, 실제 반복 유지보수 비용이 커질 경우 공통 media utility로 추출한다.

## 의도적으로 아직 하지 않은 것

- CPU/GPU 벤치마크
- SSD 건강도 / RAM 심층 진단
- 배터리 실제 열화 판정
- 침수 / 수리 이력 판정
- 통신 안테나·속도 품질 판정

브라우저만으로 정확하게 보증하기 어려운 항목이므로 ‘숨겨진 기능’이나 미완성 기능이 아니라 현재 제품 범위에서 명시적으로 제외한다.

## 아직 미완료

- 실제 PC 물리 키보드·마우스·마이크·웹캠·오디오·모니터 실기기 QA
- 실제 Android / iPhone 휴대폰 터치·카메라·마이크·스피커·화면·회전 QA
- Chrome / Edge / Firefox / Safari 교차 브라우저 실기기 QA
- HTML canonical / OG / 구조화 데이터 SEO 정리
- 독립 Red Team
- 실제 검색·사용 데이터 기반 현실검증 및 Continue / Hold / Kill 판단

## 다음

휴대폰 공개 URL 실기기 QA → 문제 수정 → PC 실기기 QA → Red Team → SEO 잔여 정리 → 실제 사용·검색 데이터 회수.
