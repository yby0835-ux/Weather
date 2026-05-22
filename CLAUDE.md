# 카카오톡 자동 날씨 알림 프로젝트

## 프로젝트 목적
매일 오전 6:00 (KST) 경기도 파주시의 날씨 정보(기온, 강수확률, 미세먼지)를
카카오톡 '나와의 채팅'으로 자동 수신하는 시스템.

PC가 꺼져 있어도 동작하도록 GitHub Actions를 실행 엔진으로 사용.

---

## 전체 동작 흐름

```
[GitHub Actions 스케줄러]
    ↓ 매일 KST 06:00 (UTC 21:00) 자동 트리거
[weather.py]
    ↓ 기상청 단기예보 API → 기온, 강수확률, 날씨 파싱
    ↓ 에어코리아 API → PM10, PM2.5 파싱
[main.py]
    ↓ 날씨 데이터 → 텍스트+이모지 메시지 포맷 생성
[kakao.py]
    ↓ refresh_token → access_token 갱신 (Kakao OAuth)
    ↓ access_token으로 '나에게 메시지 보내기' API 호출
[카카오톡 수신]
```

---

## 파일 구조

```
E:\Claude\Weather\
├── .github/
│   └── workflows/
│       └── weather.yml   ← 스케줄 및 실행 설정
├── weather.py             ← 기상청 + 에어코리아 API 호출
├── kakao.py               ← access_token 갱신 + 카카오 메시지 전송
├── main.py                ← 진입점: 데이터 조회 → 포맷 → 전송
├── requirements.txt       ← 의존성: requests
├── get_token.py           ← 최초 1회 refresh_token 발급용 (GitHub 미포함)
├── .gitignore             ← get_token.py, .env 제외
└── CLAUDE.md              ← 이 파일
```

---

## 메시지 형태

```
☀️  파주시 날씨
📅  5월 22일 (금)

  🌡  20°C    체감 19°C
  맑음
  ↓ 최저 17°   ↑ 최고 24°
  💧 습도 65%    💨 1.5m/s

  🌫  미세먼지
  PM10    🟢 좋음   11㎍/㎥
  PM2.5   🟢 좋음   8㎍/㎥

  ⏰  시간대별

  🌅 오전
    6시  ☀️  17°
    7시  ☀️  18°
    8시  ☀️  19°

  ☀️  낮
   11시  ☀️  22°
   12시  ☀️  23°  💧20%
   13시  ☀️  24°  💧20%

  🌆 저녁
   17시  ⛅  21°  💧30%
   18시  ⛅  20°  💧30%
   19시  ☁️  19°  💧30%

  📅  내일 예보
  ⛅  구름많음
  ↓ 15°   ↑ 25°
  💧 오전 10%   오후 40%
```

---

## 연동 방식

### 날씨 데이터
| 항목 | API | 출처 | 상태 |
|---|---|---|---|
| 기온, 강수확률, 날씨 | 기상청 단기예보 | data.go.kr | ✅ 정상 |
| 미세먼지 PM10, PM2.5 | 에어코리아 대기오염 | data.go.kr | ✅ 정상 |

- 지역: 경기도 파주시 (기상청 격자 nx=37, ny=133, 측정소=파주)
- 에어코리아 API: **HTTPS** 필수 (`https://apis.data.go.kr/...`)
- 표시 시간대: 6, 7, 8, 11, 12, 13, 17, 18, 19시 (9개)

### 카카오톡 전송
- 방식: 카카오 OAuth 2.0 Authorization Code Flow
- 엔드포인트: `POST https://kapi.kakao.com/v2/api/talk/memo/default/send`
- 인증: refresh_token → access_token 갱신 → Bearer 토큰
- **client_secret 필수**: REST API 키는 기본 활성화 상태
- 앱: Weather2 (앱 ID: 1464201)
- Redirect URI: `https://example.com` (플랫폼 키 > REST API 키에 등록)

### GitHub Actions
- 스케줄: `cron: '0 21 * * *'` (UTC) = 매일 KST 06:00
- 수동 실행: workflow_dispatch 지원
- 실행환경: ubuntu-latest, Python 3.11

---

## GitHub Secrets

```
https://github.com/yby0835-ux/Weather/settings/secrets/actions
```

| Secret 이름 | 설명 | 상태 |
|---|---|---|
| `DATA_GO_KR_KEY` | 공공데이터포털 API 키 (기상청용) | ✅ |
| `AIR_KOREA_KEY` | 공공데이터포털 API 키 (에어코리아용) | ✅ |
| `KAKAO_REST_API_KEY` | 카카오 앱 REST API 키 (Weather2) | ✅ |
| `KAKAO_CLIENT_SECRET` | 카카오 앱 클라이언트 시크릿 | ✅ |
| `KAKAO_REFRESH_TOKEN` | 카카오 OAuth refresh token | ✅ |

---

## 주요 해결 이력

### 카카오 OAuth KOE010 해결
- **원인**: 카카오 REST API 키는 client_secret이 기본 활성화
- **해결**: 토큰 요청 시 `client_secret` 파라미터 포함

### 에어코리아 API 403 해결
- **원인**: HTTP로 호출 시 403 반환
- **해결**: `https://apis.data.go.kr/...` HTTPS로 변경

---

## 전송 시각 변경 방법

`.github/workflows/weather.yml`에서 cron 표현식 수정.
KST = UTC + 9이므로:
- 오전 6시 → `0 21 * * *`
- 오전 7시 → `0 22 * * *`

## refresh_token 재발급 방법

refresh_token 만료(60일) 시:
1. 브라우저에서 인가 코드 획득:
   ```
   https://kauth.kakao.com/oauth/authorize?client_id=d40c837591e55451fddf671490367d0d&redirect_uri=https://example.com&response_type=code&scope=talk_message
   ```
2. `python E:\Claude\Weather\get_token.py` 실행
3. 출력된 refresh_token을 GitHub Secrets `KAKAO_REFRESH_TOKEN`에 업데이트
