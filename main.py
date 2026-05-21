from datetime import datetime
from zoneinfo import ZoneInfo
from weather import get_forecast, get_air
from kakao import send_message

GRADE_EMOJI = {'좋음': '🟢', '보통': '🟡', '나쁨': '🔴', '매우나쁨': '🟣'}


def build_message(forecast, air):
    date_str = datetime.now(ZoneInfo('Asia/Seoul')).strftime('%Y년 %m월 %d일')

    lines = [
        f"{forecast['emoji']} 파주시 오늘 날씨  {date_str}",
        "─" * 24,
        f"🌡 현재 {forecast['tmp']}°C  (체감 {forecast['feel_tmp']}°C)  {forecast['weather']}",
        f"   최저 {forecast['tmp_min']}°C  /  최고 {forecast['tmp_max']}°C",
        f"   💧 습도 {forecast['humidity']}%   💨 바람 {forecast['wind']}m/s",
        "",
        "⏰ 시간대별",
    ]

    for h in forecast['hourly']:
        lines.append(f"  {h['emoji']} {h['time']}  {h['tmp']}°C  {h['weather']}  강수 {h['pop']}%")

    lines.append("")

    if air:
        lines.append("🌫 미세먼지 (시간대별)")
        for h in air['hourly']:
            pm10_e = GRADE_EMOJI.get(h['pm10_grade'], '⚪')
            pm25_e = GRADE_EMOJI.get(h['pm25_grade'], '⚪')
            lines.append(
                f"  {h['time']}  PM10 {pm10_e}{h['pm10']}㎍  PM2.5 {pm25_e}{h['pm25']}㎍"
            )
        lines.append("")
    else:
        lines += ["🌫 미세먼지 정보 없음", ""]

    tmr = forecast['tomorrow']
    lines += [
        "📅 내일 예보",
        f"  {tmr['emoji']} {tmr['weather']}  최저 {tmr['tmp_min']}°C / 최고 {tmr['tmp_max']}°C",
        f"  강수확률  오전 {tmr['am_pop']}%  /  오후 {tmr['pm_pop']}%",
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
