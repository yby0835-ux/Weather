from datetime import datetime
from zoneinfo import ZoneInfo
from weather import get_forecast, get_air
from kakao import send_message


def build_message(forecast, air):
    now = datetime.now(ZoneInfo('Asia/Seoul')).strftime('%Y년 %m월 %d일 %H:%M')
    weather = forecast['sky'] if forecast['pty'] == '없음' else forecast['pty']

    lines = [
        f"[ 파주시 오늘 날씨 ]  {now}",
        "",
        f"현재 기온     : {forecast['tmp']}°C",
        f"최저 / 최고   : {forecast['tmp_min']}°C / {forecast['tmp_max']}°C",
        f"날씨          : {weather}",
        f"강수확률      : 오전 {forecast['am_pop']}%  /  오후 {forecast['pm_pop']}%".replace('-%', '-'),
        "",
    ]

    if air:
        lines += [
            f"미세먼지 (PM10)    : {air['pm10']} ㎍/㎥  [{air['pm10_grade']}]",
            f"초미세먼지 (PM2.5) : {air['pm25']} ㎍/㎥  [{air['pm25_grade']}]",
        ]
    else:
        lines.append("미세먼지 정보를 가져올 수 없습니다.")

    return "\n".join(lines)


if __name__ == '__main__':
    forecast = get_forecast()
    try:
        air = get_air()
    except Exception as e:
        print(f"미세먼지 조회 실패 (API 미승인 또는 오류): {e}")
        air = None
    message = build_message(forecast, air)
    print(message)
    send_message(message)
    print("카카오톡 전송 완료")
