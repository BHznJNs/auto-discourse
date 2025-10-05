import asyncio
import json
import os
import time
from dotenv import load_dotenv
from dataclasses import asdict
from openai import AsyncOpenAI
from defs import Topic
from discourse_operations import DEFAULT_SCOPES, fetch_latest, generate_user_api_key
from utils import read_config

load_dotenv()

SITE_URL = "https://linux.do"
CLIENT_NAME = "auto-discourse"
CLIENT_ID = "Tv3eZYxfvYo3VU6reYX20ogXgbUHhYpG"
SITE_REQUEST_INTERVAL = 30

USER_INSTERESTS = os.environ.get("USER_INSTERESTS")
USER_UNINSTERESTS = os.environ.get("USER_UNINSTERESTS")

SYSTEM_INSTRUCTION = f"""
你是一个 AI 助手，你的任务是判断一个话题用户是否可能感兴趣。
你可以使用以下关键词来辅助判断：
- 用户感兴趣的关键词：{USER_INSTERESTS}
- 用户不感兴趣的关键词：{USER_UNINSTERESTS}

请判断给定的话题用户是否感兴趣，并回答`true`或`false`。

**注意：你的回答只能是`true`或`false`，不要输出其他内容，也不要有任何解释。**
"""

client = AsyncOpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
    base_url=os.environ.get("OPENAI_BASE_URL"),
    default_headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
)
topic_cache = set()

def print_topic(topic: Topic):
    print(f"""
标题：{topic['title']}
链接：https://linux.do/t/topic/{topic['id']}
""")

async def check_is_insterested(topic: str) -> bool:
    RETRY_COUNT = 3
    i = 1
    while i <= RETRY_COUNT:
        try:
            completion = await client.chat.completions.create(
                model=os.environ.get("MODEL_ID") or "gpt-4",
                messages=[
                    {"role": "system", "content": SYSTEM_INSTRUCTION},
                    {"role": "user", "content": topic},
                ]
            )
            if completion.choices[0].message.content is not None:
                return completion.choices[0].message.content.strip() == "true"
        except: pass
        i += 1
    print(f"Failed to check interest for topic: {topic}")
    return False

async def check_topics(topics: list[Topic]):
    batch_size = int(os.environ.get("CHECK_IN_BATCH") or "5")
    for i in range(0, len(topics), batch_size):
        batch = topics[i:i+batch_size]
        tasks = [check_is_insterested(topic['title']) for topic in batch]
        results = await asyncio.gather(*tasks)

        for _, (topic, is_insterested) in enumerate(zip(batch, results)):
            if is_insterested:
                print_topic(topic)
                topic_cache.add(topic['title'])

def main() -> None:
    try:
        user_api_key_payload = read_config()
    except FileNotFoundError:
        result = generate_user_api_key(
            SITE_URL,
            application_name=CLIENT_NAME,
            client_id=CLIENT_ID,
            scopes=DEFAULT_SCOPES,
        )
        with open('config.json', 'w') as f:
            json.dump(asdict(result.payload), f)
        user_api_key_payload = result.payload

    while True:
        latest_topics = fetch_latest(SITE_URL, user_api_key_payload)
        if latest_topics is None:
            time.sleep(3)
            continue
        topics = latest_topics["topic_list"]["topics"]
        start_time = time.monotonic()
        asyncio.run(
            check_topics(
                list(filter(lambda topic: topic['title'] not in topic_cache, topics))))
        end_time = time.monotonic()
        sleep_time = max(0, SITE_REQUEST_INTERVAL - (end_time - start_time))
        time.sleep(sleep_time)

if __name__ == '__main__':
    main()
