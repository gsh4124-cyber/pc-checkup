# PROJECT STATUS — DEVICE CHECKUP

- 마지막 갱신: 2026-09-02
- 상태: POC / PUBLIC DEPLOYED / GLOBAL SEARCH-MARKET BATCH 3 DEPLOYED + ARTIFACT QA PASS / RED TEAM PASS WITH FIXES / PC & CROSS-BROWSER QA PENDING
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

언어를 임의로 늘리지 않고 다음 축을 함께 본다.

1. 광고·수익가치: 광고시장 규모, 구매력, 광고주 경쟁 등
2. 제품 수요: keyboard/mouse/mic/webcam/dead-pixel/touch-test 계열 실제 검색·사용수요
3. 검색생태계: Google뿐 아니라 Baidu, Yandex, Bing, Naver/Daum 등 해당 시장에서 실제 점유율이 높은 검색엔진

같은 언어로 여러 국가를 커버할 수 있으면 국가별 사본보다 언어 단위 URL을 우선한다. 글로벌 배포 성공과 검색 색인·시장 성공은 구분한다.

## Global Batch 1 — 2026-09-02

- 언어: `ko / en / ja / es`
- 4개 언어 × 9개 실제 기능 페이지 = 36 URL
- 한국어 본체 기능 축소 없이 동일 기능 제공
- canonical / hreflang / x-default / Open Graph / Twitter / JSON-LD / 언어 선택기 / sitemap 적용
- 실제 Pages artifact QA PASS

## Global Batch 2 — 광고가치 × 수요 재선정 2026-09-02

추가 언어:
- `de` 독일어
- `fr` 프랑스어
- `pt` 포르투갈어
- `it` 이탈리아어
- `nl` 네덜란드어
- `id` 인도네시아어
- `vi` 베트남어

11개 언어 × 9개 기능 페이지 = 99 URL.

GitHub Pages run `33647035463` SUCCESS, 실제 artifact `9853199054`에서 HTML 99개 / sitemap 99 URL / 내부 참조 / 중복 ID / hreflang / 언어 선택기 / 신규 JS syntax를 검사해 PASS.

## Global Search-Market Batch 3 — 중국·러시아 2026-09-02

Google 비중만 보고 시장을 선정하지 않도록 검색생태계 기준을 추가했다.

### 중국
- 신규 언어: `zh-CN` 간체 중국어
- 중국 검색시장은 Baidu가 최대 점유율이고 Bing·Haosou 등도 의미 있는 비중을 가지므로 Google SEO만으로 중국 대응 완료로 보지 않음
- 중국어 페이지는 축소판이 아니라 기존 9개 실제 기능을 동일하게 제공
- 동적 상태/오류 메시지까지 중국어 현지화
- `Baiduspider`를 robots.txt에서 명시적으로 허용
- 표준 `sitemap.xml`에 중국어 9 URL 포함
- Baidu Search Resource Platform은 사이트 소유 확인 후 URL/Sitemap 제출을 별도 진행해야 함

### 러시아권
- 신규 언어: `ru` 러시아어
- 러시아권 검색 유통은 Yandex를 별도 핵심 검색엔진으로 취급
- 러시아어 페이지도 기존 9개 실제 기능 동일 제공
- 동적 상태/오류 메시지까지 러시아어 현지화
- `Yandex` crawler를 robots.txt에서 명시적으로 허용
- 표준 `sitemap.xml`에 러시아어 9 URL 포함
- Yandex 공식 가이드상 Webmaster 등록은 자체 도메인이 필요하므로 현재 `github.io` 하위 경로만으로는 정식 Yandex Webmaster 연결을 완료 상태로 취급하지 않음

### 현재 언어 / URL 수

`ko / en / ja / es / de / fr / pt / it / nl / id / vi / zh-CN / ru`

총 **13개 언어 × 9개 기능 페이지 = 117 indexable URL**.

### Batch 3 배포·QA 결과

- GitHub Pages run `33648724051`: **SUCCESS**
- Build localized site / Upload artifact / Deploy 전 단계 SUCCESS
- 실제 Pages artifact `9853839134` 다운로드 후 검사
- HTML: **117개**
- sitemap: **117 URL**
- 중국어 / 러시아어 각 9개 HTML 존재 확인
- 중국어 / 러시아어 `app.js` / `mobile.js` syntax PASS
- 중국어 / 러시아어 index / mobile / keyboard의 canonical, `zh-CN`/`ru` hreflang, 언어 선택기 selected 상태 확인
- robots.txt: 일반 crawler + Baiduspider + Yandex 허용, sitemap 명시

**Batch 3은 코드 구현 + GitHub Pages 배포 + artifact 구조 QA 기준 PASS.**

## 검색엔진/배포 Gate

현재 남은 것은 코드가 아니라 외부 계정·도메인/배포 인프라 Gate다.

- Baidu Search Resource Platform: 로그인 + 사이트 소유확인 + URL/Sitemap 제출 필요
- Yandex Webmaster: 자체 도메인 필요, 로그인 + 소유확인 + sitemap 등록 필요
- 중국 본토 안정성: `github.io`를 중국 주력 배포 기반으로 확정하지 않음. 중국 본토에서 안정적인 별도 도메인/호스팅 또는 CDN 경로를 선택한 뒤 실제 접근성을 검증해야 함
- Bing Webmaster / Google Search Console / Naver / Daum도 제출 성공과 실제 색인·검색 노출을 분리해서 관리

이 Gate가 해결되기 전에는 **중국어·러시아어 제품 배포는 완료**, **Baidu/Yandex 검색유통 등록은 미완료**, **중국 본토 안정적 호스팅은 미완료**로 구분한다.

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
- 중국어 간체 `/pc-checkup/zh-CN/`
- 러시아어 `/pc-checkup/ru/`

## 아직 미완료

- 실제 PC 물리 장비 정식 QA
- Android 6개 전체 항목 정식 체크리스트 QA
- iPhone Safari 실기기 QA
- Chrome / Edge / Firefox / Safari 교차 브라우저 QA
- 일부 현지어 네이티브 수준 검수
- Baidu / Yandex / Bing / Google 등 실제 검색 유통 등록·색인 확인
- 중국 본토 안정적 도메인·호스팅 경로 확정 및 접근성 QA
- 글로벌 검색 색인·실사용 데이터 기반 현실검증 및 Continue / Hold / Kill 판단

## 다음

검색시장별 외부 Gate 해결과 PC 실기기 QA를 병렬 진행 → Android 정식 체크 → iPhone/교차브라우저 QA → 국가·언어·검색엔진별 검색유입/사용 데이터 회수 → Continue / Hold / Kill 및 추가 시장 판단.
