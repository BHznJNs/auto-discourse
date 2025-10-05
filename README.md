# AI 自动刷 Discourse 站点

## 使用方法

clone 这个仓库：
```
git clone https://github.com/BHznJNs/auto-discourse
```
配置环境变量：
```
cp .env.example .env
```

在 `.env` 文件中配置以下环境变量：

- `OPENAI_API_KEY`: OpenAI API 密钥，用于调用 AI 模型判断话题是否感兴趣
- `OPENAI_BASE_URL`: OpenAI API 的基础 URL，可选，用于配置自定义的 API 端点
- `MODEL_ID`: 使用的 AI 模型 ID，可选，默认为 `gpt-4`
- `USER_INSTERESTS`: 用户感兴趣的关键字，用逗号分隔，用于判断话题是否感兴趣
- `CHECK_IN_BATCH`: 批量检查话题的数量，可选，默认为 `5`

运行脚本：
```
python main.py
```
