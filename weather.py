import requests
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import os

KEY = os.environ['DATA_GO_KR_KEY']
KST = ZoneInfo('Asia/Seoul')
NX, NY = 37, 133  # 경기도 파주시

GRADE = {'1': '좋음', '2': '보통', '3': '나쁨', '4': '매우나쁨'}
SKY_MAP = {'1': '맑음', '3': '구름많음', '4': '흐림'}
PTY_MAP = {'0': '없음', '1': '비', '2': '비/눈', '3': '눈', '4': '소나기'}


def _base_datetime():
    now = datetime.now(KST)
    hours = [2, 5, 8, 11, 14, 17, 20, 23]
    for h in reversed(hours):
        if now.hour > h or (now.hour == h and now.minute >= 10):
            return now.strftime('%Y%m%d'), f'{h:02d}00'
    prev = now - timedelta(days=1)
    return prev.strftime('%Y%m%d'), '2300'


def get_forecast():
    base_date, base_time = _base_datetime()
    url = 'http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst'
    params = {
        'serviceKey': KEY,
        'numOfRows': 500,
        'dataType': 'JSON',
        'base_date': base_date,
        'base_time': base_time,
        'nx': NX,
        'ny': NY,
    }
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    items = resp.json()['response']['body']['items']['item']

    now = datetime.now(KST)
    today = now.strftime('%Y%m%d')
    now_hhmm = now.strftime('%H%M')

    data = {}
    for item in items:
        if item['fcstDate'] != today:
            continue
        cat, t, val = item['category'], item['fcstTime'], item['fcstValue']
        data.setdefault(cat, {})[t] = val

    def nearest(cat):
        if cat not in data:
            return '-'
        times = sorted(data[cat])
        for t in times:
            if t >= now_hhmm:
                return data[cat][t]
        return data[cat][times[-1]]

    am_pops = [int(v) for t, v in data.get('POP', {}).items() if t <= '1200']
    pm_pops = [int(v) for t, v in data.get('POP', {}).items() if t > '1200']
    tmp_vals = [int(v) for v in data.get('TMP', {}).values()]

    return {
        'tmp':     nearest('TMP'),
        'tmp_min': min(tmp_vals) if tmp_vals else '-',
        'tmp_max': max(tmp_vals) if tmp_vals else '-',
        'sky':     SKY_MAP.get(nearest('SKY'), '-'),
        'pty':     PTY_MAP.get(nearest('PTY'), '없음'),
        'am_pop':  max(am_pops) if am_pops else '-',
        'pm_pop':  max(pm_pops) if pm_pops else '-',
    }


def get_air():
    url = 'http://apis.data.go.kr/B552584/ArpltnInforInqireSvc/getMsrstnAcctoRltmMesureDnsty'
    params = {
        'serviceKey': KEY,
        'returnType': 'json',
        'numOfRows': 1,
        'stationName': '파주',
        'dataTerm': 'DAILY',
        'ver': '1.0',
    }
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    items = resp.json()['response']['body']['items']
    if not items:
        return None
    item = items[0]
    return {
        'pm10':       item.get('pm10Value', '-'),
        'pm10_grade': GRADE.get(item.get('pm10Grade1h', ''), '-'),
        'pm25':       item.get('pm25Value', '-'),
        'pm25_grade': GRADE.get(item.get('pm25Grade1h', ''), '-'),
    }
