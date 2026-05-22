import io
from datetime import datetime
from zoneinfo import ZoneInfo

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
import matplotlib.font_manager as fm

WEATHER_COLOR = {
    '맑음':    '#FFB300',
    '구름많음': '#90A4AE',
    '흐림':    '#607D8B',
    '비':      '#1565C0',
    '비/눈':   '#5C6BC0',
    '눈':      '#80DEEA',
    '소나기':  '#1E88E5',
    '':        '#FFB300',
}
GRADE_COLOR = {
    '좋음':    '#43A047',
    '보통':    '#FB8C00',
    '나쁨':    '#E53935',
    '매우나쁨': '#8E24AA',
    '-':       '#9E9E9E',
}


def _setup_font():
    candidates = ['NanumGothic', 'Malgun Gothic', 'Apple SD Gothic Neo', 'DejaVu Sans']
    available  = {f.name for f in fm.fontManager.ttflist}
    for font in candidates:
        if font in available:
            plt.rcParams['font.family'] = font
            break
    plt.rcParams['axes.unicode_minus'] = False


def generate_chart(forecast, air):
    _setup_font()

    hours   = [int(h['time'].replace('시', '')) for h in forecast['hourly']]
    temps   = [int(h['tmp'])                    for h in forecast['hourly']]
    pops    = [int(h['pop'])                    for h in forecast['hourly']]
    w_names = [h['weather']                     for h in forecast['hourly']]

    now      = datetime.now(ZoneInfo('Asia/Seoul'))
    date_str = now.strftime('%Y년 %m월 %d일')

    fig = plt.figure(figsize=(12, 7), facecolor='#FAFAFA')
    gs  = gridspec.GridSpec(3, 1, figure=fig,
                            height_ratios=[4, 1.5, 1.2],
                            hspace=0.08,
                            top=0.88, bottom=0.04, left=0.06, right=0.97)

    # ── 제목 ──────────────────────────────────────────────────────────
    fig.text(0.5, 0.95,
             f'파주시 오늘 날씨   {date_str}',
             ha='center', va='center',
             fontsize=16, fontweight='bold', color='#212121')

    fig.text(0.5, 0.91,
             f"{forecast['weather']}   현재 {forecast['tmp']}°C  "
             f"체감 {forecast['feel_tmp']}°C   "
             f"최저 {forecast['tmp_min']}° / 최고 {forecast['tmp_max']}°   "
             f"습도 {forecast['humidity']}%   바람 {forecast['wind']}m/s",
             ha='center', va='center',
             fontsize=11, color='#424242')

    # ── 기온 꺾은선 그래프 ────────────────────────────────────────────
    ax1 = fig.add_subplot(gs[0])
    ax1.set_facecolor('#FAFAFA')

    t_min, t_max = min(temps), max(temps)
    margin = max(2, (t_max - t_min) * 0.3)

    ax1.plot(hours, temps, color='#EF6C00', linewidth=2.5, zorder=4,
             marker='o', markersize=5, markerfacecolor='white',
             markeredgecolor='#EF6C00', markeredgewidth=2)
    ax1.fill_between(hours, temps, t_min - margin,
                     alpha=0.12, color='#EF6C00')

    # 기온 라벨
    for x, y in zip(hours, temps):
        ax1.annotate(f'{y}°', (x, y),
                     textcoords='offset points', xytext=(0, 9),
                     ha='center', fontsize=9, color='#BF360C', fontweight='bold')

    # 날씨 상태 점 (하단)
    dot_y = t_min - margin * 0.6
    for x, wname in zip(hours, w_names):
        color = WEATHER_COLOR.get(wname, '#FFB300')
        ax1.plot(x, dot_y, 'o', markersize=8, color=color,
                 markeredgecolor='white', markeredgewidth=0.8, zorder=5)

    # 날씨 텍스트 (점 아래)
    txt_y = t_min - margin * 0.9
    shown = set()
    for x, wname in zip(hours, w_names):
        short = wname[:2] if wname else '맑'
        if (x, short) not in shown:
            ax1.text(x, txt_y, short, ha='center', va='top',
                     fontsize=7, color='#616161')
            shown.add((x, short))

    ax1.set_xlim(min(hours) - 0.5, max(hours) + 0.5)
    ax1.set_ylim(t_min - margin * 1.2, t_max + margin)
    ax1.set_xticks(hours)
    ax1.set_xticklabels([f'{h}시' for h in hours], fontsize=8, color='#757575')
    ax1.set_yticks([])
    for spine in ['top', 'right', 'left']:
        ax1.spines[spine].set_visible(False)
    ax1.spines['bottom'].set_color('#E0E0E0')
    ax1.tick_params(axis='x', length=0, pad=4)

    # ── 강수확률 바 ───────────────────────────────────────────────────
    ax2 = fig.add_subplot(gs[1], sharex=ax1)
    ax2.set_facecolor('#FAFAFA')

    bar_colors = ['#1565C0' if p >= 30 else '#90CAF9' for p in pops]
    ax2.bar(hours, pops, color=bar_colors, width=0.6, alpha=0.85, zorder=3)

    for x, p in zip(hours, pops):
        if p > 0:
            ax2.text(x, p + 2, f'{p}%', ha='center', va='bottom',
                     fontsize=7, color='#1565C0')

    ax2.set_ylim(0, 110)
    ax2.set_yticks([0, 50, 100])
    ax2.set_yticklabels(['0%', '50%', '100%'], fontsize=7, color='#9E9E9E')
    ax2.set_ylabel('강수확률', fontsize=8, color='#9E9E9E', labelpad=2)
    ax2.tick_params(axis='x', bottom=False, labelbottom=False)
    for spine in ['top', 'right', 'bottom']:
        ax2.spines[spine].set_visible(False)
    ax2.spines['left'].set_color('#E0E0E0')

    # ── 하단 정보 패널 ─────────────────────────────────────────────────
    ax3 = fig.add_subplot(gs[2])
    ax3.set_facecolor('#F0F0F0')
    ax3.axis('off')

    # 미세먼지
    if air:
        pm10_c = GRADE_COLOR.get(air['pm10_grade'], '#9E9E9E')
        pm25_c = GRADE_COLOR.get(air['pm25_grade'], '#9E9E9E')
        ax3.text(0.02, 0.55,
                 f"미세먼지 (PM10)   {air['pm10']}㎍/㎥",
                 transform=ax3.transAxes, fontsize=10, color='#424242', va='center')
        ax3.text(0.22, 0.55,
                 f"[{air['pm10_grade']}]",
                 transform=ax3.transAxes, fontsize=10,
                 color=pm10_c, fontweight='bold', va='center')
        ax3.text(0.38, 0.55,
                 f"초미세먼지 (PM2.5)   {air['pm25']}㎍/㎥",
                 transform=ax3.transAxes, fontsize=10, color='#424242', va='center')
        ax3.text(0.62, 0.55,
                 f"[{air['pm25_grade']}]",
                 transform=ax3.transAxes, fontsize=10,
                 color=pm25_c, fontweight='bold', va='center')
    else:
        ax3.text(0.02, 0.55, '미세먼지 정보 없음',
                 transform=ax3.transAxes, fontsize=10, color='#9E9E9E', va='center')

    # 내일 예보
    tmr = forecast['tomorrow']
    ax3.text(0.02, 0.1,
             f"내일   {tmr['weather']}   "
             f"최저 {tmr['tmp_min']}° / 최고 {tmr['tmp_max']}°   "
             f"강수 오전 {tmr['am_pop']}%  오후 {tmr['pm_pop']}%",
             transform=ax3.transAxes, fontsize=10, color='#424242', va='center')

    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150,
                bbox_inches='tight', facecolor='#FAFAFA')
    plt.close(fig)
    buf.seek(0)
    return buf.read()


def upload_image(image_bytes):
    import requests
    import os

    token = os.environ['GITHUB_TOKEN']
    repo  = os.environ.get('GITHUB_REPOSITORY', 'yby0835-ux/Weather')
    tag   = 'weather-chart'

    headers = {
        'Authorization': f'Bearer {token}',
        'Accept':        'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28',
    }
    base = f'https://api.github.com/repos/{repo}'

    # 기존 릴리즈 삭제
    r = requests.get(f'{base}/releases/tags/{tag}', headers=headers)
    if r.status_code == 200:
        release_id = r.json()['id']
        requests.delete(f'{base}/releases/{release_id}', headers=headers)
    requests.delete(f'{base}/git/refs/tags/{tag}', headers=headers)

    # 새 릴리즈 생성
    r = requests.post(f'{base}/releases', headers=headers, json={
        'tag_name':   tag,
        'name':       'Weather Chart',
        'draft':      False,
        'prerelease': True,
    })
    r.raise_for_status()
    upload_url = r.json()['upload_url'].split('{')[0]

    # 이미지 업로드
    r = requests.post(
        f'{upload_url}?name=weather.png',
        headers={**headers, 'Content-Type': 'image/png'},
        data=image_bytes,
        timeout=30,
    )
    r.raise_for_status()
    return r.json()['browser_download_url']
