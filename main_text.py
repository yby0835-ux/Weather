from datetime import datetime
from zoneinfo import ZoneInfo

GRADE_EMOJI = {'좋음': '🟢', '보통': '🟡', '나쁨': '🔴', '매우나쁨': '🟣'}


def build_message(forecast, air):
    now      = datetime.now(ZoneInfo('Asia/Seoul'))
    date_str = now.strftime('%Y년 %m월 %d일')
    day_str  = ['월', '화', '수', '목', '금', '토', '일'][now.weekday()]

    lines = [
        f"{forecast['emoji']}  파주시 날씨  {date_str} ({day_str})",
        "═" * 26,
        "",
        f"  🌡 현재  {forecast['tmp']}°C    체감 {forecast['feel_tmp']}°C",
        f"  {forecast['weather']}    최저 {forecast['tmp_min']}° / 최고 {forecast['tmp_max']}°",
        f"  💧 습도 {forecast['humidity']}%    💨 바람 {forecast['wind']}m/s",
        "",
    ]

    if air:
        pm10_e = GRADE_EMOJI.get(air['pm10_grade'], '⚪')
        pm25_e = GRADE_EMOJI.get(air['pm25_grade'], '⚪')
        lines += [
            "═" * 26,
            "",
            f"  🌫 미세먼지",
            f"  PM10    {pm10_e} {air['pm10']}㎍/㎥   [{air['pm10_grade']}]",
            f"  PM2.5   {pm25_e} {air['pm25']}㎍/㎥   [{air['pm25_grade']}]",
            "",
        ]

    lines += [
        "═" * 26,
        "",
        "  ⏰ 시간대별",
        "",
    ]

    for h in forecast['hourly']:
        pop     = int(h['pop'])
        pop_str = f"강수 {pop:2d}%" if pop > 0 else "       "
        lines.append(
            f"  {h['emoji']}  {h['time']:>3}   {h['tmp']:>2}°C   {pop_str}"
        )

    tmr = forecast['tomorrow']
    lines += [
        "",
        "═" * 26,
        "",
        f"  📅 내일  {tmr['emoji']} {tmr['weather']}",
        f"  최저 {tmr['tmp_min']}° / 최고 {tmr['tmp_max']}°",
        f"  강수   오전 {tmr['am_pop']}%  /  오후 {tmr['pm_pop']}%",
    ]

    return "\n".join(lines)
