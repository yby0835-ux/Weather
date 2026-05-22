from datetime import datetime
from zoneinfo import ZoneInfo
from weather import get_forecast, get_air
from kakao import send_image_message, send_message
from chart import generate_chart, upload_image


if __name__ == '__main__':
    forecast = get_forecast()
    try:
        air = get_air()
    except Exception as e:
        print(f"미세먼지 조회 실패: {e}")
        air = None

    now      = datetime.now(ZoneInfo('Asia/Seoul'))
    date_str = now.strftime('%Y년 %m월 %d일')
    title    = f"파주시 오늘 날씨  {date_str}"
    desc     = (f"현재 {forecast['tmp']}°C · {forecast['weather']} · "
                f"최저 {forecast['tmp_min']}° / 최고 {forecast['tmp_max']}°")

    import traceback

    try:
        print("날씨 카드 이미지 생성 중...")
        image_bytes = generate_chart(forecast, air)
        print(f"이미지 생성 완료 ({len(image_bytes)} bytes)")

        print("이미지 업로드 중...")
        image_url = upload_image(image_bytes)
        print(f"업로드 완료: {image_url}")

        send_image_message(image_url, title, desc)
        print("카카오톡 전송 완료 (이미지)")
    except Exception as e:
        print(f"[오류] {type(e).__name__}: {e}")
        traceback.print_exc()
        print("텍스트 방식으로 대체 전송합니다.")
        from main_text import build_message
        send_message(build_message(forecast, air))
        print("카카오톡 전송 완료 (텍스트 대체)")
