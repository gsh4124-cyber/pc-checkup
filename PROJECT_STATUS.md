# PROJECT STATUS — DEVICE CHECKUP

- 마지막 갱신: 2026-09-07
- 저장소 역할: DEVICE CHECKUP 실제 코드·배포·기술상태 원본
- 저장소: `gsh4124-cyber/pc-checkup` (public)
- 현재 운영 주소: `https://pc-checkup.pages.dev/`
- 상위 사업상태: 황제 Vault `직장/바이브코딩/_INDEX.md`, `직장/바이브코딩/페이지형/_INDEX.md`

## 현재 단계

**PUBLIC PRODUCTION / GLOBAL 13-LANGUAGE DEPLOYED / ARTIFACT QA PASS WITH FIXES / RED TEAM PASS WITH FIXES / EXACT-REVISION PRODUCTION BROWSER QA PASS / PHYSICAL DEVICE QA PENDING / SEARCH ACCOUNT STATE PARTIAL-UNVERIFIED**

> 구현 완료 ≠ 정적 QA PASS ≠ 공개 배포 ≠ 현재 revision Production QA PASS ≠ 실제 하드웨어 사용 PASS ≠ 검색 색인·유입 ≠ 시장 성공

## 제품 범위

PC:
- 키보드
- 마우스
- 모니터
- 스피커·헤드폰
- 마이크
- 웹캠
- 5분 전체점검

휴대폰:
- 터치·멀티터치
- 화면 색상·불량화소
- 전·후면 카메라
- 마이크
- 스피커
- 진동·화면회전
- 결과/진행률 저장

핵심 판정 원칙:
- 브라우저가 신뢰성 있게 관찰할 수 있는 신호만 자동 판정한다.
- 화면 결함·실제 청취·진동 체감·카메라 화질처럼 사람 감각이 필요한 항목은 수동 판정을 유지한다.
- 권한 거부·브라우저 미지원만으로 하드웨어 고장을 판정하지 않는다.
- **브라우저가 볼 수 없는 것을 고장으로 판정하지 않는다.**

## 글로벌 배포

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

현재 production origin은 **Cloudflare Pages**다.

2026-09-04 전환 근거:
- `c54e5526ec3b30cfa0b3b28f37788b973dd22f4e` — generated production origin을 Cloudflare Pages로 전환
- `233bf556c819488a9cc1ad6af006e8c8adc0cb39` — robots sitemap을 Cloudflare Pages로 전환
- `5d9aab8ee3453c6f20826f910e53cfa26eed59f9` — 공개 URL을 `https://pc-checkup.pages.dev/`로 변경
- `6f9ee63c44561a7a413f854b36a606e55af2aa57` — source sitemap을 Cloudflare Pages로 전환
- `8bbe229ce8c7139399e6690da6c3a9bf83306a6e` — Cloudflare production origin / revision marker 검증
- `1287a87eb2671b7a001fc8f5a57ec3f2a4fe576c` — Production Smoke를 Cloudflare Pages 기준으로 이동
- `8bf38f877fc93f3ef6ccd2a1da5958d3517948ce` — exact Cloudflare Pages revision 확인 뒤 Production QA 수행

과거 GitHub Pages 기반 배포·QA 기록은 역사적 기준선이며 현재 production origin으로 복원하지 않는다.

## 자동 QA / Production QA

배포 artifact 기준으로 다음을 검사한다.
- 117 HTML / 117 sitemap URL / 13 locale 존재
- 내부 href/src 누락
- duplicate id
- canonical / hreflang / x-default
- 비한국어 raw Korean leakage
- JavaScript syntax
- 키보드 구조 invariant
- 예상하지 않은 외부 전송 / 네트워크 origin
- 대표 locale 모바일 레이아웃 / horizontal overflow
- 언어 선택기 중복·회귀
- 현재 공개 revision과 검사 revision 일치

Production Browser Smoke는 공개 revision을 확인한 뒤 실제 production을 검사한다.
- Chromium
- Firefox
- WebKit

2026-09-07 최신 주기 Production Browser Smoke도 **SUCCESS**로 확인됐다.

**Playwright WebKit PASS를 실제 iPhone Safari PASS라고 부르지 않는다.** 자동 엔진 호환성과 실제 물리기기·브라우저 권한·하드웨어 상호작용은 별도 Gate다.

## 키보드 / Fn 재발방지 핵심

과거 실제 회귀에서 다음을 확정했다.
- Shift / Ctrl / Alt / Meta modifier 판별: `event.code → event.location → 최소 fallback`
- Fn은 독립 고장검사가 아니라 **Fn 조합 확인** 보조기능
- Fn 전후 브라우저 이벤트가 같으면 `웹에서 판정 불가`; 고장으로 표현하지 않음
- modifier evidence는 `direct / assisted` 구분
- 한쪽을 직접 확인하지 않은 상태에서 좌우를 임의 추정하지 않음
- native/브라우저가 제공하지 않는 신호를 억지로 판정하지 않음

글로벌 생성 과정에서 UI 번역이 JS 함수명·DOM id·표준 key code까지 바꾸던 회귀가 있었고, 현재는 생성 후 canonical 동작구조 복원 + artifact validator로 재발을 막는다.

상세 과거 감사는 저장소 `QA_AUDIT_2026-09-03.md`와 Git 이력을 따른다.

## 광고 준비

실제 광고 provider는 아직 연결하지 않았다.

예약 슬롯:
- 랜딩 `index.html`
- PC 전체점검 `checkup.html`
- 모바일 전체점검 `mobile.html`

개별 검사 페이지와 fullscreen 검사 중에는 실제 광고를 넣지 않는다.

현재 상태:
`ADS_PREPARED / ADS_PROVIDER_NOT_CONNECTED`

## 검색 유통 상태

제품 코드 측면:
- 117 URL sitemap 구조
- robots.txt
- Cloudflare production origin
- 검색 메타데이터
은 준비돼 있다.

다만 Google Search Console / Naver Search Advisor / Bing Webmaster Tools / Daum의 **최종 계정 화면 완료 상태는 현재 저장된 증거만으로 확정하지 않는다.**

검색엔진 등록의 중앙 Canonical:
`황제 Vault 직장/바이브코딩/페이지형/검색엔진_등록_상태.md`

현재 판정:
`SEARCH_ENGINE_FINAL_ACCOUNT_STATE_UNVERIFIED`

등록 ≠ sitemap 제출 ≠ 크롤링 ≠ 색인 ≠ 노출 ≠ 실제 유입.

Baidu / Yandex / 중국 본토 안정적 배포 등은 시장 우선순위·자체도메인·소유확인 조건에 따라 별도 검토한다.

## 실제 물리·현실 QA

자동 QA와 실제 기기 PASS를 구분한다.

남은 고위험 확인:
- 다른 PC에서 좌/우 Shift·Ctrl·Alt·Win 실제 분리
- `assisted` 판정이 필요한 키보드 유형 추가 확인
- fullscreen에서 브라우저/OS 간섭
- Fn 조합을 여러 노트북·소형 키보드에서 재확인
- F1~F12 / Esc / 방향키 / Home-End 계열 간섭
- focus loss 후 stuck key 없음
- 마우스 실제 1클릭=1카운트
- 스피커 좌/우 청취
- 마이크 실제 입력
- 웹캠 실제 영상·장치선택
- 모니터 실제 시각검사
- Android 전체 흐름
- 실제 iPhone Safari
- 실제 Chrome / Edge / Firefox / Safari 권한·하드웨어 상호작용
- 현지어 자연스러움

## 현재 판정

- 구현: PASS
- 글로벌 빌드: PASS
- Cloudflare production 배포: PASS
- 정적/Artifact QA: **PASS WITH FIXES**
- Red Team: **PASS WITH FIXES**
- exact-revision Production Browser QA: **PASS**
- Chromium / Firefox / WebKit 자동검사: **PASS**
- 키보드/Fn artifact invariant: **PASS**
- 광고 슬롯 준비: PASS / 실광고 미연결
- 실제 PC 물리 QA: PARTIAL
- 실제 모바일·브라우저·하드웨어 QA: PENDING
- 검색엔진 최종 계정 등록상태: UNVERIFIED
- 실제 색인·유입·시장성: UNVERIFIED

## 다음 Gate

1. 인증된 브라우저에서 Google/Naver/Bing/Daum 실제 계정 상태 확인 → 누락된 등록 단계만 수행 → Vault 검색등록 Canonical 즉시 갱신
2. 실제 PC·Android·iPhone 물리기기/브라우저 상호작용 QA
3. 검색 색인·노출·실제 유입 관찰
4. 제품 가치·유입 신호를 본 뒤 광고/AdSense Gate를 별도로 연다

> **현재 제품을 다시 만드는 단계가 아니라, 공개 제품의 현실 사용·검색 유통·수익화 가능성을 검증하는 단계다.**

## AdSense 실행 상태 — 2026-09-10

`ADSENSE_REVIEW_SUBMITTED` — AdSense 사이트 추가, 공식 코드와 ads.txt 반영, Production 소유확인 통과, 검토 요청 제출. 자동 광고는 인페이지 중심으로 사용하며 앵커·사이드레일·모바일 전면광고는 비활성화. 개별 검사/fullscreen 화면 광고 금지 원칙 유지. ads.txt UI 재탐색 대기 중.
