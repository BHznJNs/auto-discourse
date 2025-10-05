import base64
import json
import secrets
import urllib.parse
import uuid
import webbrowser
from curl_cffi import requests
from collections.abc import Iterable
from dataclasses import dataclass
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from defs import TopicsResponse

# From: https://github.com/discourse/discourse/blob/main/app/models/user_api_key_scope.rb
ALL_SCOPES = [
    'read',
    'write',
    'message_bus',
    'push',
    'one_time_password',
    'notifications',
    'session_info',
    'bookmarks_calendar',
    'user_status',
]
DEFAULT_SCOPES = ['read']

@dataclass
class UserApiKeyPayload:
    key: str
    nonce: str
    push: bool
    api: int

@dataclass
class UserApiKeyRequestResult:
    client_id: str
    payload: UserApiKeyPayload

# Ref:
# https://meta.discourse.org/t/user-api-keys-specification/48536
# https://github.com/discourse/discourse/blob/main/app/controllers/user_api_keys_controller.rb
def generate_user_api_key(
    base_url: str,
    application_name: str,
    client_id: str | None = None,
    scopes: Iterable[str] | None = None,
) -> UserApiKeyRequestResult:
    # Generate RSA key pair.
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=4096,
    )
    public_key = private_key.public_key()
    public_key_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode('ascii')
 
    # Generate a random client ID if not provided.
    client_id_to_use = str(uuid.uuid4()) if client_id is None else client_id
    nonce = secrets.token_urlsafe(32)
 
    # Validate scopes.
    scopes_list = DEFAULT_SCOPES if scopes is None else list(scopes)
    if not set(scopes_list) <= set(ALL_SCOPES):
        raise ValueError('Invalid scopes')
 
    # Build request URL and open in browser.
    params_dict: dict[str, str] = {
        'application_name': application_name,
        'client_id': client_id_to_use,
        'scopes': ','.join(scopes_list),
        'public_key': public_key_pem,
        'nonce': nonce,
    }
    params_str = '&'.join(f'{k}={urllib.parse.quote(v)}' for k, v in params_dict.items())
    webbrowser.open(f'{base_url}/user-api-key/new?{params_str}')
 
    # Receive, decrypt and check response payload from server.
    enc_payload = input('Paste the response payload here: ')
    dec_payload = UserApiKeyPayload(**json.loads(private_key.decrypt(
        base64.b64decode(enc_payload),
        padding.PKCS1v15(),
    )))
    if dec_payload.nonce != nonce:
        raise ValueError('Nonce mismatch')
 
    # Return client ID and response payload.
    return UserApiKeyRequestResult(
        client_id=client_id_to_use,
        payload=dec_payload,
    )

def fetch_latest(base_url: str, payload: UserApiKeyPayload) -> TopicsResponse | None:
    response = requests.get(
        f"{base_url}/latest.json",
        headers={
            "User-Api-Key": payload.key,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
            "Referer": "https://www.google.com/",
            "Accept-Language": "zh-CN,zh;q=0.9"
        },
    )
    if response.status_code != 200:
        print(f"Request failed with status code {response.status_code}")
        return
    new_topics = TopicsResponse(response.json())
    return new_topics
