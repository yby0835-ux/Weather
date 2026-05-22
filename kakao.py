import requests
import json
import os
import base64

REST_KEY      = os.environ['KAKAO_REST_API_KEY']
CLIENT_SECRET = os.environ['KAKAO_CLIENT_SECRET']
REFRESH_TOKEN = os.environ['KAKAO_REFRESH_TOKEN']


def _update_github_secret(secret_name, secret_value):
    """GitHub Secret을 새 값으로 업데이트."""
    token = os.environ.get('GITHUB_TOKEN', '')
    repo  = os.environ.get('GITHUB_REPOSITORY', 'yby0835-ux/Weather')
    if not token:
        print("GITHUB_TOKEN 없음 — Secret 자동 업데이트 건너뜀")
        return

    headers = {
        'Authorization': f'Bearer {token}',
        'Accept':        'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28',
    }
    base = f'https://api.github.com/repos/{repo}'

    # 저장소 공개키 조회 (Secret 암호화용)
    r = requests.get(f'{base}/actions/secrets/public-key', headers=headers)
    r.raise_for_status()
    pub_key_b64 = r.json()['key']
    key_id      = r.json()['key_id']

    # libsodium SealedBox 암호화
    from nacl import encoding, public
    pub_key    = public.PublicKey(pub_key_b64.encode(), encoding.Base64Encoder())
    sealed_box = public.SealedBox(pub_key)
    encrypted  = base64.b64encode(sealed_box.encrypt(secret_value.encode())).decode()

    # Secret 업데이트
    r = requests.put(
        f'{base}/actions/secrets/{secret_name}',
        headers=headers,
        json={'encrypted_value': encrypted, 'key_id': key_id},
    )
    r.raise_for_status()
    print(f"GitHub Secret '{secret_name}' 자동 갱신 완료")


def _get_access_token():
    global REFRESH_TOKEN
    resp = requests.post('https://kauth.kakao.com/oauth/token', data={
        'grant_type':    'refresh_token',
        'client_id':     REST_KEY,
        'client_secret': CLIENT_SECRET,
        'refresh_token': REFRESH_TOKEN,
    })
    if not resp.ok:
        print(f"카카오 토큰 갱신 실패: {resp.status_code} / {resp.text}")
    resp.raise_for_status()

    data = resp.json()

    # 새 refresh_token이 응답에 포함된 경우 (만료 1개월 미만) 자동 갱신
    if 'refresh_token' in data:
        REFRESH_TOKEN = data['refresh_token']
        print("새 refresh_token 수신 → GitHub Secret 자동 업데이트 중...")
        try:
            _update_github_secret('KAKAO_REFRESH_TOKEN', REFRESH_TOKEN)
        except Exception as e:
            print(f"Secret 업데이트 실패 (수동 갱신 필요): {e}")

    return data['access_token']


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
