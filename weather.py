import requests
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import os

KEY     = os.environ['DATA_GO_KR_KEY']
AIR_KEY = os.environ['AIR_KOREA_KEY']
KST     = ZoneInfo('Asia/Seoul')
NX, NY  = 37, 133

GRADE     = {'1': '좋음', '2': '보통', '3': '나쁨', '4': '매우나쁨'}
SKY_MAP   = {'1': '맑음', '3': '구름많음', '4': '흐림'}
PTY_MAP   = {'0': '', '1': '비', '2': '비/눈', '3': '눈', '4': '소나기'}
SKY_EMOJI = {'1': '☀️', '3': '⛅', '4': '☁️'}
PTY_EMOJI = {'1': '🌧', '2': '🌨', '3': '❄️', '4': '🌦'}


def _base_datetime():
    now = datetime.now(KST)
    hours = [2, 5, 8, 11, 14, 17, 20, 23]
    for h in reversed(hours):
        if now.hour > h or (now.hour == h and now.minute >= 10):
            return now.strftime('%Y%m%d'), f'{h:02d}00'
    prev = now - timedelta(days=1)
    return prev.strftime('%Y%m%d'), '2300'


def _feel_temp(tmp, wsd):
    try:
        t, v = float(tmp), float(wsd)
    except (ValueError, TypeError):
        return tmp
    if t <= 10 and v * 3.6 >= 4.8:
        vk = v * 3.6
        feel = 13.12 + 0.6215*t - 11.37*(vk**0.16) + 0.3965*t*(vk**0.16)
        return str(round(feel))
    return str(round(t))


def _weather(sky_val, pty_val):
    if pty_val and pty_val != '0':
        return PTY_EMOJI.get(pty_val, '🌧'), PTY_MAP.get(pty_val, '')
    return SKY_EMOJI.get(sky_val, '☀️'), SKY_MAP.get(sky_val, '맑음')


def get_forecast():
    base_date, base_time = _base_datetime()
    url = 'http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst'
    params = {
        'serviceKey': KEY,
        'numOfRows':  1000,
        'dataType':   'JSON',
        'base_date':  base_date,
        'base_time':  base_time,
        'nx':         NX,
        'ny':         NY,
    }
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    items = resp.json()['response']['body']['items']['item']

    now      = datetime.now(KST)
    today    = now.strftime('%Y%m%d')
    tomorrow = (now + timedelta(days=1)).strftime('%Y%m%d')
    now_hhmm = now.strftime('%H%M')

    data = {today: {}, tomorrow: {}}
    for item in items:
        d = item['fcstDate']
        if d not in data:
            continue
        cat, t, val = item['category'], item['fcstTime'], item['fcstValue']
        data[d].setdefault(cat, {})[t] = val

    td, tm = data[today], data[tomorrow]

    def nearest(d, cat):
        if cat not in d:
            return '-'
        times = sorted(d[cat])
        for t in times:
            if t >= now_hhmm:
                return d[cat][t]
        return d[cat][times[-1]]

    tmp_vals = [int(v) for v in td.get('TMP', {}).values()]
    am_pops  = [int(v) for t, v in td.get('POP', {}).items() if t <= '1200']
    pm_pops  = [int(v) for t, v in td.get('POP', {}).items() if t > '1200']

    cur_tmp  = nearest(td, 'TMP')
    cur_wsd  = nearest(td, 'WSD')
    sky_val  = nearest(td, 'SKY')
    pty_val  = nearest(td, 'PTY')
    cur_emoji, cur_weather = _weather(sky_val, pty_val)

    # 시간대별 (06~23시, 1시간 간격)
    hourly = []
    for h in range(6, 24):
        hhmm = f'{h:02d}00'
        if hhmm not in td.get('TMP', {}):
            continue
        s_val = td.get('SKY', {}).get(hhmm, '1')
        p_val = td.get('PTY', {}).get(hhmm, '0')
        emoji, weather = _weather(s_val, p_val)
        hourly.append({
            'time':    f"{h}시",
            'tmp':     td.get('TMP', {}).get(hhmm, '-'),
            'emoji':   emoji,
            'weather': weather,
            'pop':     td.get('POP', {}).get(hhmm, '-'),
        })

    # 내일 요약
    tmr_tmp_vals = [int(v) for v in tm.get('TMP', {}).values()]
    tmr_am_pops  = [int(v) for t, v in tm.get('POP', {}).items() if t <= '1200']
    tmr_pm_pops  = [int(v) for t, v in tm.get('POP', {}).items() if t > '1200']
    tmr_sky      = tm.get('SKY', {}).get('1200') or tm.get('SKY', {}).get('1500') or '1'
    tmr_pty      = tm.get('PTY', {}).get('1200') or tm.get('PTY', {}).get('1500') or '0'
    tmr_emoji, tmr_weather = _weather(tmr_sky, tmr_pty)

    return {
        'tmp':      cur_tmp,
        'feel_tmp': _feel_temp(cur_tmp, cur_wsd),
        'tmp_min':  min(tmp_vals) if tmp_vals else '-',
        'tmp_max':  max(tmp_vals) if tmp_vals else '-',
        'emoji':    cur_emoji,
        'weather':  cur_weather,
        'am_pop':   max(am_pops) if am_pops else '-',
        'pm_pop':   max(pm_pops) if pm_pops else '-',
        'humidity': nearest(td, 'REH'),
        'wind':     cur_wsd,
        'hourly':   hourly,
        'tomorrow': {
            'tmp_min': min(tmr_tmp_vals) if tmr_tmp_vals else '-',
            'tmp_max': max(tmr_tmp_vals) if tmr_tmp_vals else '-',
            'emoji':   tmr_emoji,
            'weather': tmr_weather,
            'am_pop':  max(tmr_am_pops) if tmr_am_pops else '-',
            'pm_pop':  max(tmr_pm_pops) if tmr_pm_pops else '-',
        }
    }


def get_air():
    try:
        url = 'https://apis.data.go.kr/B552584/ArpltnInforInqireSvc/getMsrstnAcctoRltmMesureDnsty'
        params = {
            'serviceKey':  AIR_KEY,
            'returnType':  'json',
            'numOfRows':   1,
            'stationName': '파주',
            'dataTerm':    'DAILY',
            'ver':         '1.0',
        }
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        items = resp.json()['response']['body']['items']
        if not items:
            return None
        item = items[0]
        return {
            'pm10':       item.get('pm10Value', '-'),
            'pm10_grade': GRADE.get(item.get('pm10Grade', ''), '-'),
            'pm25':       item.get('pm25Value', '-'),
            'pm25_grade': GRADE.get(item.get('pm25Grade', ''), '-'),
        }
    except Exception as e:
        print(f"미세먼지 API 오류: {e}")
        return None
