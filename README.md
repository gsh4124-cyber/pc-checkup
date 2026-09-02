# PC CHECKUP MVP

한국어 브라우저 기반 PC·주변기기 점검 허브 POC.

## 포함 기능
- 키보드 입력 / 동시입력
- 마우스 버튼 / 휠 / 빠른 연속클릭 감지
- 마이크 레벨 / 파형
- 웹캠 미리보기 / 해상도
- 스피커·헤드폰 L/R 테스트
- 모니터 단색 전체화면
- 5분 전체 점검 체크리스트(LocalStorage)

## 실행
정적 파일이므로 로컬 서버에서 실행하는 것을 권장합니다.

```bash
python -m http.server 8080
```

브라우저에서 `http://localhost:8080` 접속.

카메라/마이크는 브라우저 보안 정책상 HTTPS 또는 localhost에서 권한이 정상 동작합니다.

## 상태
POC / QA RETEST v2. 공개 배포 전 실기기 QA와 Red Team이 필요합니다.
