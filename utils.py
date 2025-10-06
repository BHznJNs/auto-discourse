import json
from discourse_operations import UserApiKeyPayload

def read_user_key() -> UserApiKeyPayload:
    with open('key.json', 'r') as f:
        config =  json.load(f)
    return UserApiKeyPayload(**config)
