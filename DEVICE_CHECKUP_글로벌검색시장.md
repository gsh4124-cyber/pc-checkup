---
type: canonical
status: confirmed
source_role: emperor
updated: 2026-09-03
---

# DEVICE CHECKUP — 글로벌 검색시장 운영

## 황제 확정 방향

DEVICE CHECKUP의 글로벌 확장은 Google만 기준으로 보지 않는다.

시장 우선순위는 다음을 함께 본다.

1. 광고·수익가치
2. 실제 제품 검색·사용수요
3. 해당 국가에서 실제 점유율이 높은 검색엔진 생태계

따라서 Google 비중이 낮더라도 시장 규모·제품수요가 크면 Baidu, Yandex, Bing, Naver/Daum 등 별도 검색생태계를 직접 고려한다.

## 현재 글로벌 배포 상태 — 2026-09-03

실제 코드·기술 상태 원본은 `gsh4124-cyber/pc-checkup` 최신 `main`과 `PROJECT_STATUS.md`다.

현재 언어:

`ko / en / ja / es / de / fr / pt / it / nl / id / vi / zh-CN / ru`

13개 언어 × 동일한 9개 실제 기능 페이지 = **117 indexable URL**.

해외판은 검색용 축소판이 아니라 한국어 본체와 동일한 PC·휴대폰 검사 기능을 유지한다.

## 공개 Production QA — 2026-09-03

정적 Artifact QA와 실제 공개 사이트 QA를 분리해 코드 저장소의 `Production Browser Smoke`로 검증한다.

첫 공개 검증에서는 최신 `#languagePicker`와 구형 `.lang-switch`가 동시에 생성되는 실제 회귀를 발견했다. 구형 선택기를 숨기는 대신 글로벌 빌드에서 물리적으로 제거했고, 이후 공개 QA가 정확히 1개의 canonical 선택기와 legacy 선택기 0개를 직접 검사하도록 강화했다.

또 기존 공개 QA는 새 commit 배포가 끝나기 전에 이전 공개본을 검사해도 PASS할 수 있는 race가 있었다. 이를 막기 위해 Pages 산출물에 `build-revision.txt`로 실제 `GITHUB_SHA`를 기록하고, push 기반 Production QA는 공개 revision이 검사 대상 SHA와 정확히 일치한 뒤에만 시작한다.

현재 자동 엔진 검증:
- Chromium
- Firefox
- WebKit

push/수동 검증에서는 세 엔진을 독립 실행하고, 6시간 heartbeat는 Chromium만 실행한다.

최종 확인:
- Pages deploy run `33752636144`: **SUCCESS**
- Production Browser Smoke run `33752636269`: **SUCCESS**
- Chromium job: SUCCESS
- Firefox job: SUCCESS
- WebKit job: SUCCESS
- 세 job 모두 exact deployed revision 확인: SUCCESS

공개 QA 범위:
- 현재 commit과 실제 공개 배포 revision 일치
- sitemap 117 URL 실제 접근
- 대표 `ko / en / ja / zh-CN / ru` 모바일 공개 화면
- 대표 영어·중국어·러시아어 기능 페이지
- 언어 선택기 정확히 1개
- retired `.lang-switch` 0개
- pageerror 없음
- 대표 홈 모바일 horizontal overflow 없음
- 예상하지 않은 외부 네트워크 origin 없음

현재 판정:

`EXACT_REVISION_MULTI_ENGINE_PRODUCTION_QA_PASS / PHYSICAL_DEVICE_AND_REAL_BROWSER_QA_PENDING`

Playwright WebKit PASS를 실제 iPhone Safari PASS로 간주하지 않는다. 자동 엔진 호환성은 확인됐지만 실제 기기 권한·입력장치·카메라·마이크·스피커·브라우저 UI 상호작용은 별도 현실검증 Gate다.

## 중국

- 간체 중국어 `zh-CN` 완제품 배포 완료.
- 중국은 Google 중심으로 보지 않고 Baidu를 핵심 검색엔진으로 별도 취급한다.
- Bing·Haosou 등도 보조 검색경로 후보로 본다.
- `Baiduspider`를 robots.txt에서 허용.
- 표준 sitemap에 중국어 9개 URL 포함.
- Baidu Search Resource Platform의 URL/Sitemap 제출은 사이트 소유확인과 로그인 후 별도 처리한다.
- 현재 `github.io` 주소를 중국 본토 주력 인프라로 확정하지 않는다. 별도 도메인/호스팅 또는 CDN 경로를 선택한 뒤 본토 접근성을 실제 검증해야 한다.

## 러시아권

- 러시아어 `ru` 완제품 배포 완료.
- Yandex를 Google과 별도의 핵심 검색엔진으로 취급한다.
- `Yandex` crawler를 robots.txt에서 허용.
- 표준 sitemap에 러시아어 9개 URL 포함.
- Yandex 공식 Webmaster 등록은 자체 도메인이 필요하므로 현재 github.io 하위 경로만으로 정식 연결 완료로 취급하지 않는다.

## 정적 배포·Artifact QA

기존 전수 Artifact QA에서 확인된 현재 기반:
- HTML 117개
- sitemap 117 URL
- 13개 언어 × 9개 기능 페이지 존재
- 내부 href/src, duplicate id, canonical, x-default/hreflang 검증
- 비한국어 raw Korean leakage 검증
- locale JS 및 inline JS syntax 검증
- 키보드 구조 invariant 검증
- 외부 전송용 `fetch / XMLHttpRequest / WebSocket / sendBeacon` 없음
- Google Analytics / Tag Manager 없음
- 실제 광고 provider script 없음

정적/Artifact QA와 공개 Production QA는 별도 Gate로 유지한다.

## 현재 Gate

외부 계정·소유권·인프라가 필요한 부분은 `BLOCKED_GATE`로 구분한다.

- Baidu Search Resource Platform 로그인·소유확인·URL/Sitemap 제출
- Yandex Webmaster 자체 도메인·로그인·소유확인·Sitemap 등록
- 중국 본토 안정적 별도 도메인/호스팅/CDN 경로 선택과 실제 접근성 QA
- Bing / Google / Naver / Daum 등 검색엔진 등록·색인 확인

제품 자체 현실검증 Gate:
- 다른 PC에서 Left/Right Shift, Ctrl, Alt와 fullscreen/Windows 시작키/Fn 보조키 실제 확인
- 마우스·스피커·마이크·웹캠·모니터 실기기 확인
- Android 정식 6/6
- 실제 iPhone Safari
- 실제 Chrome / Edge / Firefox / Safari 환경의 권한·하드웨어 상호작용
- 현지어 네이티브 수준 검수

검색엔진 제출 성공, 색인, 검색 노출, 실제 유입, 시장 성공을 서로 구분한다.

## 사용데이터·수익화

현재 DEVICE CHECKUP에는 제품 사용 telemetry를 설치하지 않았다. 이를 장애나 0명으로 해석하지 않는다.

공개 주소가 `gsh4124-cyber.github.io/pc-checkup/`의 경로형 GitHub Pages URL이므로 AdSense는 현재 `PRODUCT_QA_IN_PROGRESS_AND_ADSENSE_ADDRESSABILITY_BLOCKED`로 관리한다.

## 다음

> 자동 공개 QA 감시 유지 → 실제 PC·Android·iPhone·브라우저 하드웨어 상호작용 QA → 발견된 오류만 수정 → 검색시장별 외부 Gate와 실제 노출·유입 검증 → 주소구조/AdSense 판단

순서로 진행한다.

자동 QA 성공만으로 물리기기·색인·시장 성공을 완료 처리하지 않는다.
