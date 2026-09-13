# PROJECT STATUS — DEVICE CHECKUP

- 마지막 갱신: 2026-09-13
- 저장소 역할: DEVICE CHECKUP 실제 코드·배포·기술상태 원본
- 저장소: `gsh4124-cyber/pc-checkup` (public)
- 현재 운영 주소: `https://pc-checkup.pages.dev/`
- 상위 사업상태: 황제 Vault `직장/바이브코딩/_INDEX.md`, `직장/바이브코딩/페이지형/_INDEX.md`

## 현재 단계

**PUBLIC PRODUCTION / GLOBAL 13-LANGUAGE DEPLOYED / ADSENSE_REVIEW_SUBMITTED / HUMAN LAPTOP QA APPROVED / CURRENT-REVISION PRODUCTION BROWSER QA PASS / SEARCH ACCOUNT STATE PARTIAL-UNVERIFIED**

> 구현 완료 ≠ 정적 QA PASS ≠ 공개 배포 ≠ Production Browser QA PASS ≠ 실제 색인·유입 ≠ 시장 성공

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

Production Browser Smoke는 공개 revision을 확인한 뒤 Chromium / Firefox / WebKit으로 실제 production을 검사한다.

### 2026-09-13 AdSense RUM pageerror 오탐 복구

`cc1d26338a7ca0b8748d536dba842794bc718296`에서 Chromium만 `Uncaught Error: int64`로 반복 실패했고, 회수한 stack의 모든 frame이 `https://pagead2.googlesyndication.com/.../rum.js`에 있었다. Firefox와 WebKit은 같은 identity에서 PASS했고 제품 코드 frame은 확인되지 않았다.

ROOT_CAUSE_FIRST 결과:
- `FAIL_EVIDENCE`: Production Browser Smoke #105 Chromium 실패, 동일 실행 Firefox/WebKit PASS, stack 전체가 AdSense `rum.js`.
- `ROOT_CAUSE`: 제품 회귀가 아니라 제3자 AdSense RUM 예외를 출처 구분 없이 제품 pageerror로 처리한 QA 경계 문제.
- `PRESERVE`: 제품 동작, 하드웨어 검사 로직, locale, 외부-origin allowlist, 미확인/제품-origin pageerror fail-closed.
- `CHANGE_SCOPE`: `tools/production-smoke.mjs`의 pageerror 분류만 수정.
- `EXPECTED_MECHANISM`: 정확히 `int64 + pagead2.googlesyndication.com + /rum.js + product frame 없음`인 경우만 third-party noise로 분류.
- `PASS_CRITERIA`: 그 서명만 제외하면서 다른 pageerror/외부-origin guard는 유지하고, 같은 repair identity의 Security Guardrails와 3-engine Production Browser Smoke가 성공.

repair commit `cf393ccaad11792d01434947b8c867cfe6b24347`에서 위 exact source-bound 분류만 추가했다. Google 도메인 전체, message-only 매칭, `csp.withgoogle.com` allowlist는 추가하지 않았다.

같은 SHA 결과:
- Security Guardrails #10: **SUCCESS**
- Deploy workflow #173: **SUCCESS**
- Production Browser Smoke #107: **SUCCESS**
  - Chromium: **SUCCESS**
  - Firefox: **SUCCESS**
  - WebKit: **SUCCESS**

따라서 이 회귀는 **RECOVERED / CURRENT-REVISION PRODUCTION BROWSER QA PASS**로 닫는다.

## 키보드 / Fn 재발방지 핵심

- Shift / Ctrl / Alt / Meta modifier 판별: `event.code → event.location → 최소 fallback`
- Fn은 독립 고장검사가 아니라 **Fn 조합 확인** 보조기능
- Fn 전후 브라우저 이벤트가 같으면 `웹에서 판정 불가`; 고장으로 표현하지 않음
- modifier evidence는 `direct / assisted` 구분
- 한쪽을 직접 확인하지 않은 상태에서 좌우를 임의 추정하지 않음
- native/브라우저가 제공하지 않는 신호를 억지로 판정하지 않음

글로벌 생성 과정에서 UI 번역이 JS 함수명·DOM id·표준 key code까지 바꾸던 회귀가 있었고, 현재는 생성 후 canonical 동작구조 복원 + artifact validator로 재발을 막는다.

## 인간 체감 QA — 완료 상태

황제가 **실제 노트북에서 DEVICE CHECKUP을 직접 점검하고 승인한 뒤 공개**했다. 이 검수로 현재 제품의 인간 체감 QA는 완료된 것으로 고정한다.

- PC·Android·iPhone을 별도 반복 인간 QA Gate로 다시 요구하지 않는다.
- 이후 제품 경험을 실질적으로 바꾸는 큰 UI·기능 변경이 생겨 새 인간 판단이 필요한 경우에만 새로운 황제 QA Gate를 연다.
- 자동 Production QA·CI 실패는 인간 QA와 분리된 기술운영 문제로 자동복구가 먼저 처리한다.

## AdSense 실행 상태

`ADSENSE_REVIEW_SUBMITTED`

- AdSense 사이트 추가 완료
- 공식 AdSense 코드 반영 완료
- `ads.txt` 반영 완료
- Production 소유확인 통과
- 검토 요청 제출 완료
- 자동 광고는 인페이지 중심
- 앵커·사이드레일·모바일 전면광고 비활성화
- 개별 검사 페이지와 fullscreen 검사 화면에는 광고를 두지 않는 원칙 유지
- `ads.txt` 재탐색/심사 결과는 외부 대기

승인 완료나 광고수익 발생으로 승격하지 않는다.

## 검색 유통 상태

제품 코드 측면의 117 URL sitemap 구조, robots.txt, Cloudflare production origin, 검색 메타데이터는 준비돼 있다.

검색엔진 등록 중앙 Canonical:
`황제 Vault 직장/바이브코딩/페이지형/검색엔진_등록_상태.md`

현재 판정:
`SEARCH_ENGINE_FINAL_ACCOUNT_STATE_UNVERIFIED`

등록 ≠ sitemap 제출 ≠ 크롤링 ≠ 색인 ≠ 노출 ≠ 실제 유입.

## 현재 판정

- 구현: PASS
- 글로벌 빌드: PASS
- Cloudflare production 배포: PASS
- 정적/Artifact QA: **PASS WITH FIXES**
- Red Team: **PASS WITH FIXES**
- current-revision Production Browser QA: **PASS** (`cf393cca...`, run #107)
- Security Guardrails: **PASS** (`cf393cca...`, run #10)
- 인간 체감 QA: **APPROVED — 황제 노트북 검수 완료 / 반복 기기 Gate 없음**
- AdSense: **REVIEW SUBMITTED / 외부 결과 대기**
- 검색엔진 최종 계정 등록상태: UNVERIFIED
- 실제 색인·유입·시장성: UNVERIFIED

## 다음 Gate

1. AdSense 심사 결과와 `ads.txt` 상태 관찰
2. 검색 색인·노출·실제 유입 관찰
3. Production/CI 자동관제 지속
4. 새 기술 FAIL이 있을 때만 ROOT_CAUSE_FIRST로 복구
5. 큰 UI·기능 변경으로 새 인간 판단이 실제 필요할 때만 황제 QA Gate 재개방

> **현재 제품은 다시 검수하라고 황제에게 되돌리는 단계가 아니라, 공개 제품의 자동운영·검색 유통·수익화 결과를 관찰하는 단계다.**