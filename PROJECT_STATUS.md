# PROJECT STATUS — PC CHECKUP

- 마지막 갱신: 2026-09-02
- 상태: POC / QA RETEST v2 / 독립 GitHub 저장소 이관 완료
- 저장소: `gsh4124-cyber/pc-checkup`
- 목적: 한국어 5분 PC·주변기기 전체 점검 허브의 사용가치와 구현 가능성 검증
- MVP: 키보드 / 마우스 / 마이크 / 웹캠 / 스피커 L-R / 모니터 불량화소 / 전체 점검
- 차별화 가설: 범용 도구 나열이 아니라 새 장비 구매 직후·중고 거래 전의 ‘한 번에 점검’ 흐름 + 개별 검색 진입 페이지
- 공개 배포: 미실행

## RETEST v2 변경

- 키보드: 실제 keydown 시작과 OS 자동반복(`event.repeat`)을 분리 집계
- 마우스: 250ms 기준의 과도한 빠른 클릭 판정을 제거하고 80ms 미만을 보조 신호로만 표시
- 마우스: 자동 불량 판정이 아니라 한 번 클릭했는데 카운트가 복수 증가하는지 직접 확인하도록 안내 강화
- 전체 점검: 진행률과 `다음 미확인 검사 시작` 동선 추가
- 전체 점검: 새 탭 강제 사용 제거
- 정적 QA: JavaScript syntax PASS / 로컬 파일 참조 PASS
- 개인정보/네트워크: 외부 전송 코드 미검출, 마이크·웹캠은 getUserMedia, 결과는 LocalStorage만 사용
- 독립 GitHub 저장소 생성 및 RETEST v2 기준 코드 이관 완료

## 아직 미완료

- 실제 Chrome/Edge/Firefox/Safari 브라우저 QA
- 실제 키보드·마우스·마이크·웹캠·오디오·모니터 실기기 QA
- 모바일/터치 환경 QA
- 독립 Red Team 최종판
- 실제 도메인 기준 sitemap/canonical/OG/구조화 데이터
- 공개 배포 Gate

## 다음

실제 브라우저/실기기 QA → 독립 Red Team → 필요 수정 → 공개 배포 Gate
