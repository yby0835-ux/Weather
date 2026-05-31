# 📱 카카오톡 자동 날씨 알림 시스템

> 매일 오전 6시, 파주시 날씨를 카카오톡으로 자동 수신하는 개인 알림 시스템

---

## 📌 프로젝트 개요

| 항목 | 내용 |
|---|---|
| **목적** | 매일 아침 날씨 정보를 별도 확인 없이 카카오톡으로 자동 수신 |
| **대상 지역** | 경기도 파주시 |
| **발송 시각** | 매일 KST 06:00 |
| **수신 채널** | 카카오톡 나와의 채팅 |
| **실행 환경** | GitHub Actions (PC 꺼져 있어도 동작) |
| **개발 언어** | Python 3.11 |
| **저장소** | https://github.com/yby0835-ux/Weather |

---

## 🎯 PRD

### 기능 현황

| 우선순위 | 기능 | 상태 |
|---|---|---|
| P0 | 매일 자동 발송 (KST 06:00) | ✅ |
| P0 | 기상청 날씨 데이터 수집 | ✅ |
| P0 | 카카오톡 자동 전송 | ✅ |
| P1 | 미세먼지 PM10 / PM2.5 | ✅ |
| P1 | 시간대별 날씨 9개 (오전/낮/저녁) | ✅ |
| P1 | 체감온도 / 습도 / 풍속 | ✅ |
| P1 | 내일 날씨 요약 | ✅ |
| P1 | refresh_token 자동 갱신 | ✅ |
| P2 | 이미지 기반 차트 | ❌ 텍스트로 대체 |
| P2 | GitHub Pages 인터랙티브 페이지 | ❌ 복잡도로 제외 |

---

## 🏗 시스템 아키텍처

```
┌─────────────────────────────────────────────┐
│     Pipedream (외부 스케줄러)                 │
│     매일 09:00 PM UTC (= KST 06:00) 정확히   │
└──────────────────┬──────────────────────────┘
                   │ POST workflow_dispatch (GitHub API)
┌──────────────────▼──────────────────────────┐
│              GitHub Actions                  │
│         workflow_dispatch 수신 즉시 실행      │
└──────────────────┬──────────────────────────┘
                   │
          ┌────────▼────────┐
          │   weather.py    │
          │  기상청 단기예보  │──→ 기온, 강수확률, 날씨, 습도, 풍속
          │  에어코리아 API  │──→ PM10, PM2.5  (HTTPS 필수)
          └────────┬────────┘
                   │
          ┌────────▼────────┐
          │    main.py      │
          │  메시지 포맷 생성 │──→ 텍스트 + 이모지
          │  오전/낮/저녁    │──→ 시간대 그룹화
          └────────┬────────┘
                   │
          ┌────────▼────────┐
          │    kakao.py     │
          │  OAuth 토큰 갱신 │──→ refresh_token → access_token
          │  자동 토큰 갱신  │──→ 새 token 수신 시 GH_PAT로 Secret 업데이트
          │  메시지 전송     │──→ 카카오톡 나와의 채팅
          └─────────────────┘
```

### API 연동 상세

```
기상청 단기예보 API
  └─ 격자: nx=37, ny=133 (파주시)
  └─ 파싱: TMP(기온) REH(습도) WSD(풍속) SKY(하늘)
           PTY(강수형태) POP(강수확률) TMN(최저) TMX(최고)
  └─ 표시 시간: 6, 7, 8, 11, 12, 13, 17, 18, 19시

에어코리아 실시간 측정 API  ← HTTPS 필수
  └─ 측정소: 파주
  └─ 파싱: pm10Value, pm10Grade, pm25Value, pm25Grade

카카오 OAuth 2.0
  └─ 앱: Weather2 (ID: 1464201)
  └─ Redirect URI: https://example.com
  └─ 스코프: talk_message
  └─ client_secret 필수 (기본 활성화)
  └─ 자동 갱신: 만료 30일 전 → GH_PAT로 GitHub Secret 업데이트
```

---

## 📁 파일 구조

```
Weather/
├── .github/
│   └── workflows/
│       └── weather.yml     # 스케줄(KST 06:00) + 실행 설정
├── weather.py              # 날씨·미세먼지 API 호출 및 파싱
├── kakao.py                # OAuth 갱신 + 자동 갱신 + 메시지 전송
├── main.py                 # 진입점 + 메시지 빌더
├── get_token.py            # refresh_token 최초 발급 (로컬 전용)
├── requirements.txt        # requests, PyNaCl
├── CLAUDE.md               # 개발자용 빠른 참조
└── PROJECT_DOC.md          # 이 파일
```

---

## 🔧 GitHub Secrets

| Secret | 설명 | 갱신 |
|---|---|---|
| `DATA_GO_KR_KEY` | 공공데이터포털 API 키 (기상청) | 영구 |
| `AIR_KOREA_KEY` | 공공데이터포털 API 키 (에어코리아) | 영구 |
| `KAKAO_REST_API_KEY` | 카카오 앱 REST API 키 | 영구 |
| `KAKAO_CLIENT_SECRET` | 카카오 클라이언트 시크릿 | 영구 |
| `KAKAO_REFRESH_TOKEN` | 카카오 OAuth refresh token | **자동 갱신** |
| `GH_PAT` | GitHub PAT (Secrets 쓰기 권한) | 만료일 확인 |

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

## 🐛 이슈 해결 이력

### Issue 1 — 카카오 OAuth KOE010

| | |
|---|---|
| **증상** | 토큰 교환 시 `KOE010 Bad client credentials` 반복 |
| **원인** | 카카오 REST API 키는 client_secret 기본 활성화. 미포함 시 무조건 실패 |
| **해결** | 토큰 요청에 `client_secret` 파라미터 추가 |

### Issue 2 — 에어코리아 403 Forbidden

| | |
|---|---|
| **증상** | `403 Forbidden` (로컬·GitHub Actions 동일) |
| **원인** | 에어코리아 API는 HTTP 차단, HTTPS만 허용 |
| **해결** | `http://` → `https://` 변경 |

### Issue 3 — 에어코리아 API 키 분리

| | |
|---|---|
| **증상** | 기존 `DATA_GO_KR_KEY`로 에어코리아 호출 시 `401` |
| **원인** | 에어코리아는 별도 신청 API, 기존 키에 권한 없음 |
| **해결** | data.go.kr에서 별도 신청 → `AIR_KOREA_KEY` Secret 추가 |

### Issue 4 — 이미지 업로드 catbox.moe 412

| | |
|---|---|
| **증상** | `412 Precondition Failed` |
| **원인** | GitHub Actions IP가 catbox.moe에서 차단 |
| **시도** | GitHub Releases API 대체 → 성공 |
| **최종** | 텍스트 방식 전환으로 자연 소멸 |

### Issue 5 — UI 방향 전환

| 시도 | 결과 |
|---|---|
| matplotlib 차트 이미지 | 가독성 낮음, 크기 조절 어려움 |
| GitHub Pages 인터랙티브 | 복잡도 대비 사용성 개선 미미 |
| **텍스트 + 이모지** (최종) | 단순·빠름·유지보수 용이 |

### Issue 6 — `secrets: write` 잘못된 권한값

| | |
|---|---|
| **증상** | `Invalid Argument - failed to parse workflow` 로 실행 불가 |
| **원인** | GitHub Actions `permissions`에 `secrets`는 지원하지 않는 값 |
| **해결** | `permissions: secrets: write` 제거 |

### Issue 8 — GitHub Actions cron 스케줄 지연 (44~87분)

| | |
|---|---|
| **증상** | 매일 KST 06:00 예약이지만 실제 알림은 06:43~07:26에 도착 |
| **원인** | UTC 21:00은 전 세계 레포가 집중 예약하는 피크 타임. GitHub이 큐에 쌓아 처리하여 평균 67분 지연 발생 |
| **해결** | GitHub cron 제거 → Pipedream 외부 스케줄러가 매일 09:00 PM UTC에 `workflow_dispatch` API 호출 |
| **결과** | 지연 없이 KST 06:00 정각에 알림 수신 |

### Issue 7 — refresh_token 자동 갱신 구현

| | |
|---|---|
| **문제** | `GITHUB_TOKEN`은 Repository Secret 수정 권한 없음 |
| **해결** | Fine-grained PAT (`GH_PAT`) 발급 → Secrets 쓰기 권한 부여 |
| **동작** | 만료 30일 전부터 새 token 수신 시 GitHub Secrets API 자동 업데이트 |

---

## 🔄 운영 가이드

### 발송 시각 변경

| 원하는 시각 | cron 값 (`weather.yml`) |
|---|---|
| 오전 6시 | `0 21 * * *` |
| 오전 7시 | `0 22 * * *` |
| 오전 8시 | `0 23 * * *` |

### 시간대 변경

`weather.py`:
```python
for h in [6, 7, 8, 11, 12, 13, 17, 18, 19]:
```

### refresh_token 최초 발급

```bash
# 1. 브라우저에서 인가 코드 획득
https://kauth.kakao.com/oauth/authorize?client_id=d40c837591e55451fddf671490367d0d&redirect_uri=https://example.com&response_type=code&scope=talk_message

# 2. 로컬 실행
python get_token.py

# 3. GitHub Secrets KAKAO_REFRESH_TOKEN 등록 → 이후 자동 갱신
```

### GH_PAT 만료 시 재발급

```
https://github.com/settings/personal-access-tokens
→ Weather-AutoRenew 토큰 재생성
→ GitHub Secrets GH_PAT 업데이트
```

### 수동 실행

```
https://github.com/yby0835-ux/Weather/actions/workflows/weather.yml
→ Run workflow
```

---

## 📅 개발 이력

| 날짜 | 작업 |
|---|---|
| 2026-05-22 | 프로젝트 초기 세팅, 기상청 API 연동 |
| 2026-05-22 | 에어코리아 API graceful 처리 |
| 2026-05-22 | 카카오 OAuth KOE010 해결 (client_secret) |
| 2026-05-22 | 에어코리아 HTTPS 전환 + 별도 API 키 분리 |
| 2026-05-22 | 시간대별·체감온도·습도·풍속·내일예보 추가 |
| 2026-05-22 | matplotlib 이미지 차트 시도 → 텍스트 복귀 |
| 2026-05-22 | GitHub Pages 시도 → 텍스트 복귀 |
| 2026-05-22 | 오전/낮/저녁 그룹화, 9개 시간대 고정 |
| 2026-05-22 | 발송 시각 KST 06:00, 불필요 파일 정리 |
| 2026-05-22 | refresh_token 자동 갱신 구현 (GH_PAT + PyNaCl) |
| 2026-05-22 | `secrets: write` 권한 오류 수정, 전체 정상 동작 확인 ✅ |
| 2026-05-31 | GitHub cron 지연 문제 분석 (평균 67분) → Pipedream 외부 스케줄러로 전환 ✅ |
