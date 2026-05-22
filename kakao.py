import requests
import json
import os

REST_KEY      = os.environ['KAKAO_REST_API_KEY']
CLIENT_SECRET = os.environ['KAKAO_CLIENT_SECRET']
REFRESH_TOKEN = os.environ['KAKAO_REFRESH_TOKEN']


def _get_access_token():
    resp = requests.post('https://kauth.kakao.com/oauth/token', data={
        'grant_type':    'refresh_token',
        'client_id':     REST_KEY,
        'client_secret': CLIENT_SECRET,
        'refresh_token': REFRESH_TOKEN,
    })
    if not resp.ok:
        print(f"카카오 토큰 갱신 실패: {resp.status_code} / {resp.text}")
    resp.raise_for_status()
    return resp.json()['access_token']


def send_message(text):
    token = _get_access_token()
    template = json.dumps({
        'object_type': 'text',
        'text': text,
        'link': {'web_url': 'https://www.weather.go.kr'},
    }, ensure_ascii=False)
    resp = requests.post(
        'https://kapi.kakao.com/v2/api/talk/memo/default/send',
        headers={'Authorization': f'Bearer {token}'},
        data={'template_object': template},
    )
    resp.raise_for_status()


def send_weather_message(title, description, image_url=None, page_url=None):
    token    = _get_access_token()
    link_url = page_url or 'https://www.weather.go.kr'

    if image_url:
        template = {
            'object_type': 'feed',
            'content': {
                'title':        title,
                'description':  description,
                'image_url':    image_url,
                'image_width':  1500,
                'image_height': 2100,
                'link': {
                    'web_url':        link_url,
                    'mobile_web_url': link_url,
                },
            },
        }
        if page_url:
            template['buttons'] = [{
                'title': '자세히 보기 →',
                'link': {
                    'web_url':        page_url,
                    'mobile_web_url': page_url,
                },
            }]
    else:
        # 이미지 없을 때 텍스트 fallback
        from main_text import build_message
        template = {
            'object_type': 'text',
            'text': f"{title}\n{description}" + (f"\n\n🔗 {page_url}" if page_url else ''),
            'link': {'web_url': link_url},
        }

    resp = requests.post(
        'https://kapi.kakao.com/v2/api/talk/memo/default/send',
        headers={'Authorization': f'Bearer {token}'},
        data={'template_object': json.dumps(template, ensure_ascii=False)},
    )
    resp.raise_for_status()
