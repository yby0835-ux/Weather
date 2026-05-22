import json
import base64
import requests
from datetime import datetime
from zoneinfo import ZoneInfo

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>파주시 날씨</title>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/chart.js@4/dist/chart.umd.min.js"></script>
<style>
* { margin:0; padding:0; box-sizing:border-box; -webkit-tap-highlight-color:transparent; }
body {
  font-family: 'Noto Sans KR', sans-serif;
  background: #EBF0F5;
  min-height: 100vh;
  padding-bottom: 24px;
}
.container { max-width: 480px; margin: 0 auto; padding: 0 12px; }

/* ── 헤더 ── */
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 4px 12px;
}
.location { font-size: 22px; font-weight: 700; color: #1a1a2e; }
.updated   { font-size: 11px; color: #888; }

/* ── 현재 날씨 카드 ── */
.current-card {
  background: linear-gradient(135deg, #4A90D9 0%, #2C6FAC 100%);
  border-radius: 24px;
  padding: 28px 24px 24px;
  color: white;
  text-align: center;
  margin-bottom: 14px;
  box-shadow: 0 8px 24px rgba(74,144,217,0.35);
}
.weather-icon-big { font-size: 56px; line-height: 1; margin-bottom: 6px; }
.temp-big   { font-size: 72px; font-weight: 700; line-height: 1; letter-spacing: -2px; }
.weather-name { font-size: 20px; font-weight: 500; margin: 8px 0; opacity: 0.92; }
.temp-range { font-size: 14px; opacity: 0.8; margin-bottom: 16px; }
.details-row {
  display: flex;
  justify-content: center;
  gap: 18px;
  background: rgba(255,255,255,0.18);
  border-radius: 12px;
  padding: 10px 0;
}
.detail-item { display: flex; flex-direction: column; align-items: center; gap: 2px; }
.detail-label { font-size: 10px; opacity: 0.75; }
.detail-value { font-size: 15px; font-weight: 500; }

/* ── 정보 카드 행 ── */
.info-cards {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin-bottom: 14px;
}
.info-card {
  background: white;
  border-radius: 18px;
  padding: 16px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.06);
}
.card-label { font-size: 11px; color: #888; margin-bottom: 4px; }
.card-grade { font-size: 20px; font-weight: 700; margin-bottom: 2px; }
.card-value { font-size: 12px; color: #666; }
.good      .card-grade { color: #43A047; }
.normal    .card-grade { color: #FB8C00; }
.bad       .card-grade { color: #E53935; }
.verybad   .card-grade { color: #8E24AA; }

/* ── 시간대별 섹션 ── */
.section-card {
  background: white;
  border-radius: 20px;
  padding: 18px 16px;
  margin-bottom: 14px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.06);
}
.section-title {
  font-size: 14px;
  font-weight: 600;
  color: #555;
  margin-bottom: 14px;
}

/* 차트 */
.chart-wrap { position: relative; height: 110px; margin-bottom: 4px; }

/* 시간대별 스크롤 */
.hourly-scroll {
  display: flex;
  overflow-x: auto;
  gap: 2px;
  padding: 4px 0 8px;
  scrollbar-width: none;
  -webkit-overflow-scrolling: touch;
}
.hourly-scroll::-webkit-scrollbar { display: none; }
.hourly-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 50px;
  gap: 4px;
  padding: 6px 4px;
  border-radius: 10px;
  transition: background 0.15s;
}
.hourly-item:active { background: #f0f4f8; }
.h-time  { font-size: 11px; color: #888; }
.h-icon  { font-size: 22px; }
.h-temp  { font-size: 14px; font-weight: 600; color: #222; }
.h-pop   { font-size: 10px; color: #4A90D9; font-weight: 500; }
.h-pop.zero { color: #ccc; }

/* ── 내일 예보 ── */
.tomorrow-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}
.tmr-icon    { font-size: 28px; }
.tmr-weather { font-size: 16px; font-weight: 500; color: #333; flex: 1; }
.tmr-range   { font-size: 14px; color: #555; }
.tmr-pop     { font-size: 12px; color: #888; padding-left: 38px; }

/* ── 푸터 ── */
.footer { text-align: center; font-size: 10px; color: #bbb; margin-top: 8px; }
</style>
</head>
<body>
<div class="container">

  <div class="header">
    <div class="location">📍 파주시</div>
    <div class="updated">PLACEHOLDER_DATE</div>
  </div>

  <div class="current-card">
    <div class="weather-icon-big">PLACEHOLDER_EMOJI</div>
    <div class="temp-big">PLACEHOLDER_TEMP°</div>
    <div class="weather-name">PLACEHOLDER_WEATHER</div>
    <div class="temp-range">최저 PLACEHOLDER_MIN° / 최고 PLACEHOLDER_MAX°</div>
    <div class="details-row">
      <div class="detail-item">
        <span class="detail-label">체감온도</span>
        <span class="detail-value">PLACEHOLDER_FEEL°</span>
      </div>
      <div class="detail-item">
        <span class="detail-label">습도</span>
        <span class="detail-value">PLACEHOLDER_HUMIDITY%</span>
      </div>
      <div class="detail-item">
        <span class="detail-label">바람</span>
        <span class="detail-value">PLACEHOLDER_WINDm/s</span>
      </div>
    </div>
  </div>

  <div class="info-cards">
    <div class="info-card PLACEHOLDER_PM10_CLASS">
      <div class="card-label">미세먼지 (PM10)</div>
      <div class="card-grade">PLACEHOLDER_PM10_GRADE</div>
      <div class="card-value">PLACEHOLDER_PM10 ㎍/㎥</div>
    </div>
    <div class="info-card PLACEHOLDER_PM25_CLASS">
      <div class="card-label">초미세먼지 (PM2.5)</div>
      <div class="card-grade">PLACEHOLDER_PM25_GRADE</div>
      <div class="card-value">PLACEHOLDER_PM25 ㎍/㎥</div>
    </div>
  </div>

  <div class="section-card">
    <div class="section-title">⏰ 시간대별 날씨</div>
    <div class="chart-wrap">
      <canvas id="tempChart"></canvas>
    </div>
    <div class="hourly-scroll" id="hourlyScroll">
      PLACEHOLDER_HOURLY
    </div>
  </div>

  <div class="section-card">
    <div class="section-title">📅 내일 예보</div>
    <div class="tomorrow-row">
      <span class="tmr-icon">PLACEHOLDER_TMR_EMOJI</span>
      <span class="tmr-weather">PLACEHOLDER_TMR_WEATHER</span>
      <span class="tmr-range">PLACEHOLDER_TMR_MIN° / PLACEHOLDER_TMR_MAX°</span>
    </div>
    <div class="tmr-pop">강수확률 오전 PLACEHOLDER_TMR_AM%  ·  오후 PLACEHOLDER_TMR_PM%</div>
  </div>

  <div class="footer">기상청 단기예보 · 에어코리아 실시간 측정</div>
</div>

<script>
const D = PLACEHOLDER_JSON;

const ctx = document.getElementById('tempChart').getContext('2d');
new Chart(ctx, {
  type: 'line',
  data: {
    labels: D.hours,
    datasets: [{
      data: D.temps,
      borderColor: '#4A90D9',
      backgroundColor: 'rgba(74,144,217,0.10)',
      fill: true,
      tension: 0.4,
      pointBackgroundColor: '#fff',
      pointBorderColor: '#4A90D9',
      pointBorderWidth: 2,
      pointRadius: 3,
      pointHoverRadius: 5,
    }]
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        callbacks: { label: ctx => ctx.parsed.y + '°C' }
      }
    },
    scales: {
      x: {
        display: false,
      },
      y: {
        display: false,
        min: Math.min(...D.temps) - 2,
        max: Math.max(...D.temps) + 4,
      }
    }
  }
});

// 현재 시각에 해당하는 시간대로 스크롤
const now = new Date().getHours();
const scroll = document.getElementById('hourlyScroll');
const items = scroll.querySelectorAll('.hourly-item');
items.forEach((el, i) => {
  const h = parseInt(D.hours[i]);
  if (h <= now && (i === items.length-1 || parseInt(D.hours[i+1]) > now)) {
    el.style.background = '#EBF4FF';
    el.style.fontWeight = '600';
    setTimeout(() => el.scrollIntoView({behavior:'smooth', block:'nearest', inline:'center'}), 200);
  }
});
</script>
</body>
</html>"""


def generate_page(forecast, air):
    now      = datetime.now(ZoneInfo('Asia/Seoul'))
    date_str = now.strftime('%Y년 %m월 %d일 %H:%M 기준')

    # 시간대별 HTML
    hourly_items = ''
    for h in forecast['hourly']:
        pop     = int(h['pop'])
        pop_cls = '' if pop > 0 else ' zero'
        pop_txt = f"💧{pop}%" if pop > 0 else f"0%"
        hourly_items += (
            f'<div class="hourly-item">'
            f'<span class="h-time">{h["time"]}</span>'
            f'<span class="h-icon">{h["emoji"]}</span>'
            f'<span class="h-temp">{h["tmp"]}°</span>'
            f'<span class="h-pop{pop_cls}">{pop_txt}</span>'
            f'</div>'
        )

    grade_class = {'좋음': 'good', '보통': 'normal', '나쁨': 'bad', '매우나쁨': 'verybad'}
    pm10_grade  = air['pm10_grade'] if air else '-'
    pm25_grade  = air['pm25_grade'] if air else '-'
    pm10_val    = air['pm10']       if air else '-'
    pm25_val    = air['pm25']       if air else '-'

    tmr = forecast['tomorrow']

    chart_json = json.dumps({
        'hours': [h['time'] for h in forecast['hourly']],
        'temps': [int(h['tmp']) for h in forecast['hourly']],
    }, ensure_ascii=False)

    replacements = {
        'PLACEHOLDER_DATE':       date_str,
        'PLACEHOLDER_EMOJI':      forecast['emoji'],
        'PLACEHOLDER_TEMP':       forecast['tmp'],
        'PLACEHOLDER_WEATHER':    forecast['weather'],
        'PLACEHOLDER_MIN':        forecast['tmp_min'],
        'PLACEHOLDER_MAX':        forecast['tmp_max'],
        'PLACEHOLDER_FEEL':       forecast['feel_tmp'],
        'PLACEHOLDER_HUMIDITY':   forecast['humidity'],
        'PLACEHOLDER_WIND':       forecast['wind'],
        'PLACEHOLDER_PM10_CLASS': grade_class.get(pm10_grade, ''),
        'PLACEHOLDER_PM10_GRADE': pm10_grade,
        'PLACEHOLDER_PM10':       pm10_val,
        'PLACEHOLDER_PM25_CLASS': grade_class.get(pm25_grade, ''),
        'PLACEHOLDER_PM25_GRADE': pm25_grade,
        'PLACEHOLDER_PM25':       pm25_val,
        'PLACEHOLDER_HOURLY':     hourly_items,
        'PLACEHOLDER_TMR_EMOJI':  tmr['emoji'],
        'PLACEHOLDER_TMR_WEATHER':tmr['weather'],
        'PLACEHOLDER_TMR_MIN':    tmr['tmp_min'],
        'PLACEHOLDER_TMR_MAX':    tmr['tmp_max'],
        'PLACEHOLDER_TMR_AM':     str(tmr['am_pop']),
        'PLACEHOLDER_TMR_PM':     str(tmr['pm_pop']),
        'PLACEHOLDER_JSON':       chart_json,
    }
    html = HTML_TEMPLATE
    for k, v in replacements.items():
        html = html.replace(k, str(v))
    return html


def deploy_to_github(html_content, token, repo):
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept':        'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28',
    }
    base = f'https://api.github.com/repos/{repo}'

    # gh-pages 브랜치 없으면 생성
    r = requests.get(f'{base}/git/refs/heads/gh-pages', headers=headers)
    if r.status_code == 404:
        r2 = requests.get(f'{base}/git/refs/heads/main', headers=headers)
        sha = r2.json()['object']['sha']
        requests.post(f'{base}/git/refs', headers=headers,
                      json={'ref': 'refs/heads/gh-pages', 'sha': sha})

    # 기존 index.html SHA
    r = requests.get(f'{base}/contents/index.html',
                     params={'ref': 'gh-pages'}, headers=headers)
    sha = r.json().get('sha') if r.status_code == 200 else None

    body = {
        'message': 'Update weather page',
        'content': base64.b64encode(html_content.encode('utf-8')).decode(),
        'branch':  'gh-pages',
    }
    if sha:
        body['sha'] = sha

    r = requests.put(f'{base}/contents/index.html', headers=headers, json=body)
    r.raise_for_status()

    owner = repo.split('/')[0]
    repo_name = repo.split('/')[1]
    return f'https://{owner}.github.io/{repo_name}/'
