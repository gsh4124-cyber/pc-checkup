# DEVICE CHECKUP

새 PC·휴대폰 수령 직후 또는 중고 거래 전, 브라우저에서 약 5분 안에 기본 입출력 상태를 확인하는 기기 점검 허브입니다.

공개 사이트: https://gsh4124-cyber.github.io/pc-checkup/

## 기능

PC: 키보드, 마우스, 모니터, 스피커/헤드폰, 마이크, 웹캠, 5분 전체점검.

휴대폰: 터치/멀티터치, 화면 색상/불량화소, 전·후면 카메라, 마이크, 스피커, 진동/회전, 5분 전체점검 결과 저장.

브라우저가 직접 측정할 수 있는 반응만 자동 판정하며 화면 결함·실제 청취·진동 체감처럼 사람의 감각이 필요한 항목은 통과 기준을 제시하고 수동 판정합니다.

## 글로벌 구조

현재 `ko / en / ja / es / de / fr / pt / it / nl / id / vi / zh-CN / ru` 총 13개 언어를 지원합니다. 한국어 본체와 별도의 축소 해외판을 만들지 않고 모든 언어에서 같은 9개 기능 페이지를 제공합니다.

총 indexable URL은 13개 언어 × 9개 기능 페이지 = 117개입니다.

배포 시 공통 빌더와 후처리 스크립트가 `dist/`를 생성합니다.

- `tools/build_global.py.gz`: 기본 `ko/en/ja/es` 생성
- `tools/expand_batch2.py`: 광고가치·실제 검색수요 기준 `de/fr/pt/it/nl/id/vi` 생성
- `tools/append_cn_ru.py`: 중국·러시아 검색생태계 대응용 `zh-CN/ru` 생성

언어별 완성 HTML/JS를 저장소에 중복 보관하지 않으며, 각 페이지에는 canonical, hreflang, x-default, Open Graph, Twitter card, JSON-LD를 실제 URL 기준으로 정적으로 생성합니다. sitemap은 117개 URL로 생성됩니다.

## 검색시장 대응

글로벌 배포를 Google만으로 보지 않습니다. 광고·수익가치, 실제 제품 수요와 함께 각 시장의 검색생태계를 봅니다.

- 일반 글로벌: Google + Bing
- 한국: Google + Naver + Daum
- 중국: Baidu 중심 + Bing/기타 중국 검색시장 검토
- 러시아권: Yandex를 별도 핵심 검색엔진으로 취급

`robots.txt`는 Baiduspider와 Yandex crawler를 포함해 검색 crawler 접근을 허용하고 sitemap을 제공합니다. 다만 언어판 배포 완료, 검색엔진 등록 완료, 실제 색인·검색유입 발생은 서로 다른 상태로 관리합니다.

현재 GitHub Pages 기반 중국어 페이지 배포는 완료했지만, 중국 본토의 안정적 접근성을 보장하는 별도 도메인/호스팅과 Baidu 사이트 소유확인·제출은 아직 외부 Gate입니다. Yandex Webmaster 정식 연결도 자체 도메인 및 소유확인 Gate가 남아 있습니다.

## 개인정보 / 한계

카메라·마이크·키 입력을 서버로 전송하는 기능을 두지 않습니다. 배터리 실제 열화, 침수, 수리 이력, SSD/RAM 심층 상태, 통신 품질 등 브라우저로 신뢰성 있게 판정하기 어려운 항목은 범위에서 제외합니다.

## 현재 검증 상태

- 정적·자동 QA PASS
- Android 공개 URL 탐색 QA 수행
- Red Team PASS WITH FIXES
- 13개 언어 / 117개 Pages 배포 artifact 구조 QA PASS
- 실제 PC 물리 장비 정식 QA, Android 6개 정식 QA, iPhone Safari 및 교차 브라우저 QA는 아직 미완료
- 실제 검색 색인·유입·시장성 검증은 아직 미완료

상세 최신 기술 상태는 `PROJECT_STATUS.md`를 기준으로 합니다.
