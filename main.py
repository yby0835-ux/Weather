from datetime import datetime
from zoneinfo import ZoneInfo
from weather import get_forecast, get_air
from kakao   import send_message

GRADE_EMOJI = {'좋음': '🟢', '보통': '🟡', '나쁨': '🔴', '매우나쁨': '🟣'}
DAY_KR      = ['월', '화', '수', '목', '금', '토', '일']


def _pop(p):
    v = int(p)
    return f"💧{v}%" if v > 0 else ""


def build_message(forecast, air):
    now      = datetime.now(ZoneInfo('Asia/Seoul'))
    date_str = f"{now.month}월 {now.day}일"
    day_str  = DAY_KR[now.weekday()]

    lines = [
        f"{forecast['emoji']}  파주시 날씨",
        f"📅  {date_str} ({day_str})",
        "",
        f"  🌡  {forecast['tmp']}°C    체감 {forecast['feel_tmp']}°C",
        f"  {forecast['weather']}",
        f"  ↓ 최저 {forecast['tmp_min']}°   ↑ 최고 {forecast['tmp_max']}°",
        f"  💧 습도 {forecast['humidity']}%    💨 {forecast['wind']}m/s",
    ]

    if air:
        pm10_e = GRADE_EMOJI.get(air['pm10_grade'], '⚪')
        pm25_e = GRADE_EMOJI.get(air['pm25_grade'], '⚪')
        lines += [
            "",
            f"  🌫  미세먼지",
            f"  PM10    {pm10_e} {air['pm10_grade']}   {air['pm10']}㎍/㎥",
            f"  PM2.5   {pm25_e} {air['pm25_grade']}   {air['pm25']}㎍/㎥",
        ]

    hourly = forecast['hourly']
    groups = [
        ('🌅 오전', [6, 7, 8]),
        ('☀️  낮',  [11, 12, 13]),
        ('🌆 저녁', [17, 18, 19]),
    ]

    lines += ["", "  ⏰  시간대별"]
    for label, hours in groups:
        slots = [h for h in hourly if int(h['time'].replace('시', '')) in hours]
        if slots:
            lines.append(f"\n  {label}")
            for h in slots:
                pop = _pop(h['pop'])
                lines.append(f"   {h['time']:>3}  {h['emoji']}  {h['tmp']:>2}°  {pop}")

    tmr = forecast['tomorrow']
    lines += [
        "",
        f"  📅  내일 예보",
        f"  {tmr['emoji']}  {tmr['weather']}",
        f"  ↓ {tmr['tmp_min']}°   ↑ {tmr['tmp_max']}°",
        f"  💧 오전 {tmr['am_pop']}%   오후 {tmr['pm_pop']}%",
    ]

    return "\n".join(lines)


if __name__ == '__main__':
    forecast = get_forecast()
    try:
        air = get_air()
    except Exception as e:
        print(f"미세먼지 조회 실패: {e}")
        air = None

    message = build_message(forecast, air)
    print(message)
    send_message(message)
    print("카카오톡 전송 완료")
