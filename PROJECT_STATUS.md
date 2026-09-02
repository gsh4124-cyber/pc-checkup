# PROJECT STATUS — DEVICE CHECKUP

- 마지막 갱신: 2026-09-02
- 상태: POC / PUBLIC DEPLOYED / GLOBAL BATCH 2 DEPLOYED + ARTIFACT QA PASS / RED TEAM PASS WITH FIXES / PC & CROSS-BROWSER QA PENDING
- 저장소: `gsh4124-cyber/pc-checkup` (public)
- 공개 URL: `https://gsh4124-cyber.github.io/pc-checkup/`

## 제품 범위

PC 6종: 키보드, 마우스, 모니터, 스피커·헤드폰, 마이크, 웹캠 + 5분 전체점검.

휴대폰 6종: 전체화면 터치·멀티터치, 화면 색상·불량화소, 전·후면 카메라, 마이크, 스피커, 진동·화면회전 + 결과/진행률 저장.

브라우저가 실제 측정할 수 있는 항목만 자동 판정하며, 화면 결함·실제 청취·진동 체감·카메라 화질 등 사람의 감각이 필요한 항목은 통과 기준과 수동 판정을 유지한다.

## 기존 검증

- GitHub Pages 공개 배포 완료
- 정적·자동 QA PASS
- Android 실제 공개 URL 탐색 QA 수행
- Red Team: **PASS WITH FIXES**
- Red Team에서 터치 100% 영역, 카메라 거짓 정상 가능성, LocalStorage 손상/차단, 미디어 자원 정리 엣지케이스를 발견해 수정
- 외부 전송용 fetch / XMLHttpRequest / WebSocket / sendBeacon 및 외부 분석·추적 스크립트 없음

## 글로벌 확장 원칙

언어를 임의로 늘리지 않고 다음 두 축 중 하나라도 강한 시장을 우선한다.

1. 광고·수익가치: 광고시장 규모, 구매력, 광고주 경쟁 등
2. 제품 수요: keyboard/mouse/mic/webcam/dead-pixel/touch-test 계열 실제 검색·사용수요

같은 언어로 여러 국가를 커버할 수 있으면 국가별 사본보다 언어 단위 URL을 우선한다. 글로벌 배포 성공과 검색 색인·시장 성공은 구분한다.

## Global Batch 1 — 2026-09-02

- 언어: `ko / en / ja / es`
- 4개 언어 × 9개 실제 기능 페이지 = 36 URL
- 한국어 본체 기능 축소 없이 동일 기능 제공
- canonical / hreflang / x-default / Open Graph / Twitter / JSON-LD / 언어 선택기 / sitemap 적용
- 실제 Pages artifact QA PASS

## Global Batch 2 — 광고가치 × 수요 재선정 2026-09-02

외부 시장/경쟁 사이트 데이터를 다시 확인해 다음 7개 언어를 추가했다.

- `de` 독일어 — 독일의 높은 광고시장 가치 우선
- `fr` 프랑스어 — 프랑스의 높은 광고시장 가치 우선
- `pt` 포르투갈어 — 브라질이 기기 테스트 도구 실제 트래픽 상위권이면서 광고시장도 큰 편
- `it` 이탈리아어 — 높은 유럽 광고시장 가치
- `nl` 네덜란드어 — 작은 인구 대비 높은 광고·구매력 가치
- `id` 인도네시아어 — webcam 테스트 계열 실제 트래픽 강함
- `vi` 베트남어 — mic/webcam 테스트 계열 실제 트래픽 강함

인도는 관련 도구 수요가 매우 크지만 영어 검색이 강해 현재 영어판이 이미 상당 부분 커버하므로 힌디어는 이번 Batch 2에서 우선순위를 낮췄다. 중국어는 광고시장 자체는 크지만 Google 중심의 현재 배포/검색 유통 구조와 별도 검색생태계 검토가 필요해 이번 배치에서 보류했다.

### 현재 언어

`ko / en / ja / es / de / fr / pt / it / nl / id / vi`

총 11개 언어 × 9개 기능 페이지 = **99개 indexable URL**.

### 구현 구조

- Batch 1 공통 빌더로 `ko/en/ja/es` 생성
- `tools/expand_batch2.py`가 영어 완성본을 기반으로 Batch 2 언어를 build-time 생성
- 저장소에는 99개 완성 HTML/JS 사본을 중복 보관하지 않음
- 모든 11개 언어 페이지에 언어 선택기 제공
- 모든 페이지에 11개 언어 hreflang + x-default 제공
- sitemap을 99 URL로 자동 재생성
- 각 신규 언어 canonical / og:locale / JSON-LD inLanguage를 실제 언어 URL 기준으로 생성

### Batch 2 배포·QA 결과

- GitHub Pages run `33647035463`: **SUCCESS**
- Build localized site / Upload artifact / Deploy 전 단계 SUCCESS
- 실제 Pages artifact `9853199054` 다운로드 후 검사
- HTML: **99개** 존재 확인
- sitemap: **99 URL** 확인
- 내부 href/src 깨짐: 0
- HTML 중복 ID: 0
- 모든 11개 언어 페이지 hreflang 11개 + x-default 확인
- 모든 11개 언어 페이지 언어 선택기 11개 옵션 확인
- 신규 언어 `de/fr/pt/it/nl/id/vi`의 `app.js` / `mobile.js` syntax PASS
- 신규 언어 index title / canonical 현지화 확인

**Global Batch 2는 코드 구현 + GitHub Pages 배포 + 배포 artifact 구조 QA 기준 PASS.**

단, 번역 품질은 독일어·프랑스어·포르투갈어를 핵심 설명문까지 우선 현지화했고, 이탈리아어·네덜란드어·인도네시아어·베트남어는 핵심 UI·검색 진입문구 중심의 1차 현지화다. 실제 현지 사용자 반응이나 전문 번역 검수 완료를 의미하지 않는다.

## 현재 글로벌 진입 URL

- 한국어 `/pc-checkup/`
- 영어 `/pc-checkup/en/`
- 일본어 `/pc-checkup/ja/`
- 스페인어 `/pc-checkup/es/`
- 독일어 `/pc-checkup/de/`
- 프랑스어 `/pc-checkup/fr/`
- 포르투갈어 `/pc-checkup/pt/`
- 이탈리아어 `/pc-checkup/it/`
- 네덜란드어 `/pc-checkup/nl/`
- 인도네시아어 `/pc-checkup/id/`
- 베트남어 `/pc-checkup/vi/`

## 아직 미완료

- 실제 PC 물리 장비 정식 QA
- Android 6개 전체 항목 정식 체크리스트 QA
- iPhone Safari 실기기 QA
- Chrome / Edge / Firefox / Safari 교차 브라우저 QA
- Batch 2 현지어 표현의 네이티브 수준 검수
- 글로벌 검색 색인·실사용 데이터 기반 현실검증 및 Continue / Hold / Kill 판단
- Google Search Console / Bing 등 실제 검색 유통 등록·색인 확인은 별도 상태로 관리

## 다음

PC 실기기 QA와 병렬로 글로벌 검색 유통·색인 준비 → Android 정식 체크 → iPhone/교차브라우저 QA → 국가·언어별 검색유입/사용 데이터 회수 → Continue / Hold / Kill 및 추가 언어 판단.
