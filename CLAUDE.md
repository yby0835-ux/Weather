# 카카오톡 자동 날씨 연동

## 프로젝트 목적

매일 오전 5:40에 날씨 정보(기온, 강수 확률, 미세먼지)를 카카오톡으로 자동 수신.

## 환경

- **실행**: GitHub Actions (PC 종료 상관없음)
- **언어**: Python 3.11
- **전송 시각**: 매일 오전 5:40 KST → cron: `40 20 * * *` (UTC)

## 사용 API

| API | 출처 | 용도 |
|---|---|---|
| 기상청 단기예보 조회서비스 | data.go.kr | 기온, 강수 확률 |
| 에어코리아 대기오염정보 | data.go.kr | 미세먼지 PM10, PM2.5 |
| 카카오 메시지 API (나에게 보내기) | developers.kakao.com | 카카오톡 전송 |

## 파일 구조

```
E:\Claude\Weather\
├── .github/
│   └── workflows/
│       └── weather.yml   ← GitHub Actions 스케줄 (시각 변경은 여기서)
├── weather.py            ← 날씨 + 미세먼지 조회
├── kakao.py              ← 카카오 메시지 전송 + 토큰 갱신
├── main.py               ← 진입점
├── requirements.txt      ← Python 패키지 목록
└── CLAUDE.md             ← 이 파일
```

## API 키 보관 위치

GitHub 저장소 → Settings → Secrets and variables → Actions 에 등록:
- `DATA_GO_KR_KEY` : 공공데이터포털 서비스키
- `KAKAO_REST_API_KEY` : 카카오 REST API 키
- `KAKAO_REFRESH_TOKEN` : 카카오 refresh token

## 전송 시각 변경 방법

`.github/workflows/weather.yml` 에서 cron 표현식만 수정.
KST = UTC + 9 → 오전 6시로 변경하려면 `30 21 * * *`

## 진행 현황

- [x] 프로젝트 설계 완료
- [x] 실행 환경 결정: GitHub Actions
- [ ] GitHub 저장소 생성
- [ ] API 키 발급 (data.go.kr, kakao)
- [ ] 사용자 거주 지역 확인
- [ ] 코드 작성
- [ ] GitHub Secrets 등록
- [ ] 테스트 실행
