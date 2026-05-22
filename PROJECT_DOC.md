# 📱 카카오톡 자동 날씨 알림 시스템

> 매일 오전 6시, 파주시 날씨를 카카오톡으로 자동 수신하는 개인 알림 시스템

---

## 📌 프로젝트 개요

| 항목 | 내용 |
|---|---|
| **목적** | 매일 아침 날씨 정보를 별도 확인 없이 카카오톡으로 자동 수신 |
| **대상** | 경기도 파주시 |
| **발송 시각** | 매일 KST 06:00 |
| **수신 채널** | 카카오톡 나와의 채팅 |
| **실행 환경** | GitHub Actions (PC 꺼져 있어도 동작) |
| **개발 언어** | Python 3.11 |

---

## 🎯 PRD (Product Requirements Document)

### 핵심 요구사항

| 우선순위 | 기능 | 상태 |
|---|---|---|
| P0 | 매일 자동 발송 (스케줄링) | ✅ 완료 |
| P0 | 기상청 날씨 데이터 수집 | ✅ 완료 |
| P0 | 카카오톡 전송 | ✅ 완료 |
| P1 | 미세먼지 (PM10, PM2.5) | ✅ 완료 |
| P1 | 시간대별 날씨 (9개 시간대) | ✅ 완료 |
| P1 | 체감온도 / 습도 / 풍속 | ✅ 완료 |
| P1 | 내일 날씨 요약 | ✅ 완료 |
| P2 | 이미지 기반 차트 | ❌ 텍스트로 대체 |
| P2 | 인터랙티브 웹 페이지 | ❌ 복잡도로 제외 |

### 메시지 요구사항

- 현재 기온 + 체감온도
- 최저/최고 기온
- 습도, 풍속
- 미세먼지 등급 및 수치
- 시간대별 예보 (오전 6·7·8 / 낮 11·12·13 / 저녁 17·18·19시)
- 내일 날씨 요약
- 강수확률 0%는 생략, 있을 때만 표시

---

## 🏗 시스템 아키텍처

```
┌─────────────────────────────────────────────┐
│              GitHub Actions                  │
│         cron: 매일 KST 06:00                │
└──────────────────┬──────────────────────────┘
                   │
          ┌────────▼────────┐
          │   weather.py    │
          │  기상청 단기예보  │──→ 기온, 강수확률, 날씨
          │  에어코리아 API  │──→ PM10, PM2.5
          └────────┬────────┘
                   │
          ┌────────▼────────┐
          │    main.py      │
          │  메시지 포맷 생성 │──→ 텍스트 + 이모지
          └────────┬────────┘
                   │
          ┌────────▼────────┐
          │    kakao.py     │
          │  OAuth 토큰 갱신 │──→ refresh → access token
          │  메시지 전송     │──→ 카카오톡 나와의 채팅
          └─────────────────┘
```

### 데이터 흐름

```
기상청 API (data.go.kr)
  └─ 단기예보 (nx=37, ny=133)
      └─ TMP(기온), REH(습도), WSD(풍속)
      └─ SKY(하늘), PTY(강수형태), POP(강수확률)
      └─ TMN(최저), TMX(최고)

에어코리아 API (data.go.kr) - HTTPS 필수
  └─ 측정소: 파주
      └─ pm10Value, pm10Grade
      └─ pm25Value, pm25Grade

카카오 OAuth
  └─ refresh_token (GitHub Secret)
      └─ POST /oauth/token → access_token
          └─ POST /v2/api/talk/memo/default/send
```

---

## 📁 파일 구조

```
Weather/
├── .github/
│   └── workflows/
│       └── weather.yml     # 스케줄 + 실행 설정
├── weather.py              # 날씨·미세먼지 API 호출
├── kakao.py                # OAuth + 카카오 메시지 전송
├── main.py                 # 진입점 + 메시지 빌더
├── get_token.py            # refresh_token 최초 발급 (로컬 전용)
├── requirements.txt        # requests
├── .gitignore
└── CLAUDE.md
```

---

## 🔧 GitHub Secrets

| Secret | 설명 |
|---|---|
| `DATA_GO_KR_KEY` | 공공데이터포털 API 키 (기상청) |
| `AIR_KOREA_KEY` | 공공데이터포털 API 키 (에어코리아) |
| `KAKAO_REST_API_KEY` | 카카오 앱 REST API 키 |
| `KAKAO_CLIENT_SECRET` | 카카오 클라이언트 시크릿 |
| `KAKAO_REFRESH_TOKEN` | 카카오 OAuth refresh token (60일 갱신) |

---

## 🐛 이슈 해결 이력

### Issue 1 — 카카오 OAuth KOE010 `invalid_client`

| 항목 | 내용 |
|---|---|
| **증상** | 토큰 교환 시 `KOE010 Bad client credentials` 반복 |
| **시도** | redirect URI 변경 3회 (`localhost/oauth` → `localhost:8080` → `https://example.com`) |
| **원인** | 카카오 REST API 키는 **client_secret이 기본 활성화** 상태로 생성됨. 토큰 요청에 `client_secret` 파라미터 미포함 시 무조건 실패 |
| **해결** | `get_token.py` 및 `kakao.py` 토큰 요청에 `client_secret` 추가 |
| **참고** | redirect URI 등록 위치: 플랫폼 키 > REST API 키 (카카오 로그인 메뉴 아님) |

---

### Issue 2 — 에어코리아 API 403 Forbidden

| 항목 | 내용 |
|---|---|
| **증상** | `403 Forbidden` 반복, 로컬/GitHub Actions 모두 동일 |
| **원인** | 에어코리아 API 엔드포인트가 **HTTPS만 허용** (`http://` 차단) |
| **해결** | `http://apis.data.go.kr/...` → `https://apis.data.go.kr/...` 변경 |

---

### Issue 3 — 에어코리아 API 키 분리

| 항목 | 내용 |
|---|---|
| **증상** | 기존 `DATA_GO_KR_KEY`로 에어코리아 호출 시 401 |
| **원인** | 에어코리아는 별도 신청이 필요한 API. 기존 키에는 권한 없음 |
| **해결** | data.go.kr에서 `한국환경공단_에어코리아_대기오염정보` 별도 신청 → `AIR_KOREA_KEY` Secret 추가 |

---

### Issue 4 — catbox.moe 이미지 업로드 412

| 항목 | 내용 |
|---|---|
| **증상** | 이미지 업로드 시 `412 Precondition Failed` |
| **원인** | GitHub Actions IP가 catbox.moe에서 차단됨 |
| **시도** | GitHub Releases API로 대체 (GITHUB_TOKEN 활용) → 성공 |
| **최종** | 이미지 방식 전체를 텍스트로 전환하면서 해당 문제 소멸 |

---

### Issue 5 — UI 방향 전환

| 항목 | 내용 |
|---|---|
| **시도 1** | matplotlib 차트 이미지 → 카카오톡 피드 템플릿 전송 |
| **문제** | 모바일에서 가독성 낮음, 크기 조절 어려움 |
| **시도 2** | GitHub Pages HTML 인터랙티브 페이지 + 카카오 링크 전송 |
| **문제** | 구현 복잡도 대비 사용성 개선 미미 |
| **최종** | 텍스트 + 이모지 방식으로 복귀. 오전/낮/저녁 섹션 구분 |

---

## 📬 최종 메시지 형태

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

## 🔄 운영 가이드

### 발송 시각 변경

`.github/workflows/weather.yml`의 cron 수정.
KST = UTC + 9

| 원하는 시각 | cron 값 |
|---|---|
| 오전 6시 | `0 21 * * *` |
| 오전 7시 | `0 22 * * *` |
| 오전 8시 | `0 23 * * *` |

### refresh_token 갱신 (60일마다)

1. 브라우저에서 인가 코드 획득
   ```
   https://kauth.kakao.com/oauth/authorize?client_id=d40c837591e55451fddf671490367d0d&redirect_uri=https://example.com&response_type=code&scope=talk_message
   ```
2. 로컬에서 실행
   ```bash
   python get_token.py
   ```
3. 출력된 `refresh_token` 값을 GitHub Secrets `KAKAO_REFRESH_TOKEN`에 업데이트

### 시간대 변경

`weather.py` 내 아래 목록 수정

```python
for h in [6, 7, 8, 11, 12, 13, 17, 18, 19]:
```

---

## 📅 개발 이력

| 날짜 | 작업 |
|---|---|
| 2026-05-22 | 프로젝트 초기 세팅, 기상청 API 연동 |
| 2026-05-22 | 에어코리아 API graceful 처리 |
| 2026-05-22 | 카카오 OAuth KOE010 해결 (client_secret) |
| 2026-05-22 | 에어코리아 HTTPS 전환 + 별도 API 키 분리 |
| 2026-05-22 | 시간대별/체감온도/습도/풍속/내일예보 추가 |
| 2026-05-22 | matplotlib 이미지 차트 시도 → 텍스트로 복귀 |
| 2026-05-22 | GitHub Pages 시도 → 텍스트로 복귀 |
| 2026-05-22 | 오전/낮/저녁 3구간 그룹화, 9개 시간대 고정 |
| 2026-05-22 | 발송 시각 06:00 KST 확정, 코드 정리 |
