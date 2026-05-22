import os
import traceback
from datetime import datetime
from zoneinfo import ZoneInfo

from weather import get_forecast, get_air
from kakao  import send_weather_message
from chart  import generate_chart, upload_image
from page   import generate_page, deploy_to_github


if __name__ == '__main__':
    forecast = get_forecast()
    try:
        air = get_air()
    except Exception as e:
        print(f"미세먼지 조회 실패: {e}")
        air = None

    token = os.environ.get('GITHUB_TOKEN', '')
    repo  = os.environ.get('GITHUB_REPOSITORY', 'yby0835-ux/Weather')

    now      = datetime.now(ZoneInfo('Asia/Seoul'))
    date_str = now.strftime('%Y년 %m월 %d일')
    title    = f"파주시 오늘 날씨  {date_str}"
    desc     = (f"현재 {forecast['tmp']}°C · {forecast['weather']} · "
                f"최저 {forecast['tmp_min']}° / 최고 {forecast['tmp_max']}°")

    # ── 1단계: GitHub Pages 배포 ──────────────────────────────────────
    page_url = None
    try:
        print("STEP1: 날씨 페이지 생성 중...")
        html = generate_page(forecast, air)
        page_url = deploy_to_github(html, token, repo)
        print(f"STEP1 완료: {page_url}")
    except Exception as e:
        print(f"STEP1 실패: {type(e).__name__}: {e}")
        traceback.print_exc()

    # ── 2단계: 차트 이미지 생성 및 업로드 ────────────────────────────
    image_url = None
    try:
        print("STEP2: 이미지 생성 중...")
        image_bytes = generate_chart(forecast, air)
        print(f"STEP2 이미지 생성 완료 ({len(image_bytes)} bytes)")
        image_url = upload_image(image_bytes)
        print(f"STEP2 업로드 완료: {image_url}")
    except Exception as e:
        print(f"STEP2 실패: {type(e).__name__}: {e}")
        traceback.print_exc()

    # ── 3단계: 카카오톡 전송 ─────────────────────────────────────────
    try:
        print("STEP3: 카카오톡 전송 중...")
        send_weather_message(title, desc, image_url, page_url)
        print("STEP3 완료: 카카오톡 전송 완료")
    except Exception as e:
        print(f"STEP3 실패: {type(e).__name__}: {e}")
        traceback.print_exc()
