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

    # 1단계: 이미지 생성
    image_bytes = None
    try:
        print("STEP1: 이미지 생성 중...")
        image_bytes = generate_chart(forecast, air)
        print(f"STEP1 완료: {len(image_bytes)} bytes")
    except Exception as e:
        print(f"STEP1 실패: {type(e).__name__}: {e}")
        traceback.print_exc()

    # 2단계: 업로드
    image_url = None
    if image_bytes:
        try:
            print("STEP2: 이미지 업로드 중...")
            image_url = upload_image(image_bytes)
            print(f"STEP2 완료: {image_url}")
        except Exception as e:
            print(f"STEP2 실패: {type(e).__name__}: {e}")
            traceback.print_exc()

    # 3단계: 카카오톡 전송
    if image_url:
        try:
            print("STEP3: 카카오톡 이미지 전송 중...")
            send_image_message(image_url, title, desc)
            print("STEP3 완료: 카카오톡 전송 완료 (이미지)")
        except Exception as e:
            print(f"STEP3 실패: {type(e).__name__}: {e}")
            traceback.print_exc()
            image_url = None

    # 이미지 실패 시 텍스트 대체
    if not image_url:
        print("텍스트 방식으로 대체 전송합니다.")
        from main_text import build_message
        send_message(build_message(forecast, air))
        print("카카오톡 전송 완료 (텍스트 대체)")
