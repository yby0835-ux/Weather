import requests
import json
import os

REST_KEY      = os.environ['KAKAO_REST_API_KEY']
REFRESH_TOKEN = os.environ['KAKAO_REFRESH_TOKEN']


def _get_access_token():
    resp = requests.post('https://kauth.kakao.com/oauth/token', data={
        'grant_type':    'refresh_token',
        'client_id':     REST_KEY,
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
