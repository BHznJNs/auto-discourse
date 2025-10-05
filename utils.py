import json
from discourse_operations import UserApiKeyPayload

def read_config() -> UserApiKeyPayload:
    with open('config.json', 'r') as f:
        config =  json.load(f)
    return UserApiKeyPayload(**config)
