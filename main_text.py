from datetime import datetime
from zoneinfo import ZoneInfo

GRADE_EMOJI = {'좋음': '🟢', '보통': '🟡', '나쁨': '🔴', '매우나쁨': '🟣'}
DAY_KR      = ['월', '화', '수', '목', '금', '토', '일']


def _pop(p):
    v = int(p)
    return f"💧{v}%" if v > 0 else "      "


def _hourly_block(label, slots):
    lines = [f"  {label}"]
    for h in slots:
        lines.append(
            f"   {h['time']:>3}  {h['emoji']}  {h['tmp']:>2}°  {_pop(h['pop'])}"
        )
    return lines


def build_message(forecast, air):
    now      = datetime.now(ZoneInfo('Asia/Seoul'))
    date_str = f"{now.month}월 {now.day}일"
    day_str  = DAY_KR[now.weekday()]

    SEP = '─' * 26

    # ── 헤더 ──
    lines = [
        f"{forecast['emoji']}  파주시 날씨",
        f"📅  {date_str} ({day_str})",
        SEP,
    ]

    # ── 현재 기온 ──
    lines += [
        f"",
        f"  🌡  {forecast['tmp']}°C    체감 {forecast['feel_tmp']}°C",
        f"  {forecast['weather']}",
        f"  ↓ 최저 {forecast['tmp_min']}°   ↑ 최고 {forecast['tmp_max']}°",
        f"  💧 습도 {forecast['humidity']}%    💨 {forecast['wind']}m/s",
        f"",
        SEP,
    ]

    # ── 미세먼지 ──
    if air:
        pm10_e = GRADE_EMOJI.get(air['pm10_grade'], '⚪')
        pm25_e = GRADE_EMOJI.get(air['pm25_grade'], '⚪')
        lines += [
            f"",
            f"  🌫  미세먼지",
            f"  PM10    {pm10_e} {air['pm10_grade']}   {air['pm10']}㎍/㎥",
            f"  PM2.5   {pm25_e} {air['pm25_grade']}   {air['pm25']}㎍/㎥",
            f"",
            SEP,
        ]

    # ── 시간대별 (오전 / 낮 / 저녁) ──
    hourly = forecast['hourly']
    by_label = [
        ('🌅 오전',  [h for h in hourly if int(h['time'].replace('시','')) in [6,7,8]]),
        ('☀️  낮',   [h for h in hourly if int(h['time'].replace('시','')) in [11,12,13]]),
        ('🌆 저녁',  [h for h in hourly if int(h['time'].replace('시','')) in [17,18,19]]),
    ]

    lines += ['', '  ⏰  시간대별']
    for label, slots in by_label:
        if slots:
            lines.append('')
            lines += _hourly_block(label, slots)

    # ── 내일 예보 ──
    tmr = forecast['tomorrow']
    lines += [
        f"",
        SEP,
        f"",
        f"  📅  내일 예보",
        f"  {tmr['emoji']}  {tmr['weather']}",
        f"  ↓ {tmr['tmp_min']}°   ↑ {tmr['tmp_max']}°",
        f"  💧 오전 {tmr['am_pop']}%   오후 {tmr['pm_pop']}%",
    ]

    return "\n".join(lines)
