# PROJECT STATUS — DEVICE CHECKUP

- 마지막 갱신: 2026-09-02
- 상태: POC / PUBLIC DEPLOYED / GLOBAL BATCH 1 DEPLOYING / RED TEAM PASS WITH FIXES / PC & CROSS-BROWSER QA PENDING
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

## 글로벌 확장 Batch 1 — 2026-09-02

- 한국어 본체 기능을 축소하지 않고 동일한 9개 기능 URL 구조를 언어별로 생성하는 build-time localization 구현
- 언어: `ko / en / ja / es`
- 각 언어: index + PC 전체점검 + 휴대폰 전체점검 + 키보드 + 마우스 + 마이크 + 웹캠 + 스피커 + 모니터 = 9개 URL
- 총 indexable URL: 36개
- 본문·버튼·동적 오류/상태 메시지 현지화
- 모든 페이지 언어 선택기
- canonical / hreflang / x-default / Open Graph / Twitter / JSON-LD를 언어별 실제 URL 기준으로 정적 생성
- sitemap 36 URL 자동 생성
- 언어별 완성 HTML/JS 사본은 저장소에 두지 않고 압축 locale 데이터 `i18n/*.json.gz` + 공통 배포 빌더로 생성
- 로컬 빌드 및 정적 QA: 내부 참조, 중복 ID, SEO 필수 태그, 비한국어 페이지 한국어 누출, app.js/mobile.js syntax, sitemap URL 수 모두 PASS
- 현재 GitHub Pages 글로벌 배포 run 트리거 단계

현재 단계에서는 **코드 구현 완료 ≠ 글로벌 배포 성공 ≠ 검색 색인 ≠ 시장 성공**으로 구분한다. 실제 Pages artifact와 공개 URL 검증 전에는 Global Batch 1 배포 완료로 취급하지 않는다.

## 아직 미완료

- Global Batch 1 실제 Pages 배포 및 다국어 배포 artifact QA
- 실제 PC 물리 장비 정식 QA
- Android 6개 전체 항목 정식 체크리스트 QA
- iPhone Safari 실기기 QA
- Chrome / Edge / Firefox / Safari 교차 브라우저 QA
- 글로벌 검색 색인·실사용 데이터 기반 현실검증 및 Continue / Hold / Kill 판단

## 다음

Global Batch 1 Pages 배포·artifact QA → 공개 en/ja/es URL 확인 → PC 실기기 QA → Android 정식 체크 → iPhone/교차브라우저 QA → 글로벌 색인·실사용 데이터 회수.
