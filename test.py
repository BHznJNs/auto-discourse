import requests
import random

URL = "https://linux.do/user-api-key/new"
response = requests.post(URL, {
    "application_name": "auto-discourse",
    "nonce": random.random(),
    "scopes": {
        "read": True,
    }
})

print(response)
