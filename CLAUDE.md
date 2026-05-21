# 카카오톡 자동 날씨 알림 프로젝트

## 프로젝트 목적
매일 오전 5:40 (KST) 경기도 파주시의 날씨 정보(기온, 강수확률, 미세먼지)를
카카오톡 '나와의 채팅'으로 자동 수신하는 시스템.

PC가 꺼져 있어도 동작하도록 GitHub Actions를 실행 엔진으로 사용.

---

## 전체 동작 흐름

```
[GitHub Actions 스케줄러]
    ↓ 매일 KST 05:40 (UTC 20:40) 자동 트리거
[weather.py]
    ↓ 기상청 단기예보 API 호출 → 기온, 강수확률, 날씨 파싱
    ↓ 에어코리아 API 호출 → PM10, PM2.5 파싱 (실패 시 생략)
[main.py]
    ↓ 날씨 데이터 → 메시지 포맷 생성
[kakao.py]
    ↓ refresh_token → access_token 갱신 (Kakao OAuth)
    ↓ access_token으로 '나에게 메시지 보내기' API 호출
[카카오톡 수신]
```

---

## 연동 방식

### 날씨 데이터
| 항목 | API | 출처 | 상태 |
|---|---|---|---|
| 기온, 강수확률, 날씨 | 기상청 단기예보 | data.go.kr | ✅ 정상 |
| 미세먼지 PM10, PM2.5 | 에어코리아 대기오염 | data.go.kr | ⏳ 승인 대기 |

- 지역: 경기도 파주시 (기상청 격자 nx=37, ny=133, 측정소=파주)
- API 키: GitHub Secrets `DATA_GO_KR_KEY`에 저장

### 카카오톡 전송
- 방식: **카카오 OAuth 2.0 Authorization Code Flow**
- 엔드포인트: `POST https://kapi.kakao.com/v2/api/talk/memo/default/send`
- 인증: refresh_token → access_token 갱신 → Bearer 토큰으로 전송
- 수신: 카카오톡 '나와의 채팅' (본인에게만 발송)
- 필요 스코프: `talk_message`

### GitHub Actions
- 스케줄: `cron: '40 20 * * *'` (UTC) = 매일 KST 05:40
- 수동 실행: workflow_dispatch 지원
- 실행환경: ubuntu-latest, Python 3.11

---

## 파일 구조

```
E:\Claude\Weather\
├── .github/
│   └── workflows/
│       └── weather.yml     ← 스케줄 및 실행 설정 (시각 변경은 여기서)
├── weather.py              ← 기상청 + 에어코리아 API 호출
├── kakao.py                ← access_token 갱신 + 카카오 메시지 전송
├── main.py                 ← 진입점: 데이터 조회 → 포맷 → 전송
├── requirements.txt        ← 의존성: requests
├── get_token.py            ← 최초 1회 refresh_token 발급용 (GitHub 미포함)
├── .gitignore              ← get_token.py, .env 제외
└── CLAUDE.md               ← 이 파일
```

---

## GitHub Secrets (저장소 설정)
```
https://github.com/yby0835-ux/Weather/settings/secrets/actions
```

| Secret 이름 | 설명 | 상태 |
|---|---|---|
| `DATA_GO_KR_KEY` | 공공데이터포털 API 키 | ✅ 등록됨 |
| `KAKAO_REST_API_KEY` | 카카오 앱 REST API 키 (Weather2) | ✅ 등록됨 |
| `KAKAO_CLIENT_SECRET` | 카카오 앱 클라이언트 시크릿 | ✅ 등록됨 |
| `KAKAO_REFRESH_TOKEN` | 카카오 OAuth refresh token | ✅ 등록됨 |

---

## 카카오 앱 정보
| 앱 이름 | 앱 ID | REST API 키 | 상태 |
|---|---|---|---|
| Weather | 1464105 | `14e18f9524e416e05ae3499c90c7e88a` | 구 앱 |
| Weather2 | 1464201 | `d40c837591e55451fddf671490367d0d` | **현재 시도 중** |

- 카카오 개발자 콘솔: https://developers.kakao.com
- 동의항목: 카카오톡 메시지 전송 (talk_message) 선택 동의 설정됨

---

## 현재 상태 및 미해결 문제

### ✅ 전체 정상 작동 (2026-05-22 완료)
- 기상청 날씨 API 데이터 수집
- GitHub Actions 스케줄 실행 (매일 KST 05:40)
- 메시지 포맷 생성
- 에어코리아 API 실패 시 graceful 처리
- 카카오 OAuth 토큰 발급 및 갱신
- 카카오톡 '나와의 채팅' 메시지 전송

### 카카오 OAuth 해결 기록
**원인**: 카카오 REST API 키는 `client_secret`이 기본 활성화 상태로 생성됨.
토큰 요청 시 `client_secret` 파라미터를 반드시 포함해야 함.
- `get_token.py`: `client_secret` 추가
- `kakao.py`: `KAKAO_CLIENT_SECRET` 환경변수로 `client_secret` 추가
- `weather.yml`: `KAKAO_CLIENT_SECRET` secrets 참조 추가

---

## 전송 시각 변경 방법
`.github/workflows/weather.yml`에서 cron 표현식 수정.
KST = UTC + 9 → 오전 6시로 변경 시: `30 21 * * *`
