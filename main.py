from weather import get_forecast, get_air
from kakao   import send_message
from main_text import build_message

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
