# ADK Weather Agent

Google Agent Development Kit (ADK) を使った天気検索エージェント。
Open-Meteo API を利用して、現在の天気と最大16日先までの予報を取得できます。

## セットアップ

```bash
uv sync
```

### 環境変数

`weather_agent/.env` を編集:

```bash
# Vertex AI を使う場合
GOOGLE_GENAI_USE_VERTEXAI=TRUE
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=asia-northeast1

# Google AI Studio を使う場合
# GOOGLE_GENAI_USE_VERTEXAI=FALSE
# GOOGLE_API_KEY=your-api-key
```

## ローカル動作確認

```bash
# ターミナルで対話
uv run adk run weather_agent --agents_dir .

# Web UI で起動 (http://127.0.0.1:8000)
uv run adk web .
```

## デプロイ (Agent Engine)

```bash
# 新規作成
uv run adk deploy agent_engine \
  --project=gaudiy-ai \
  --region=asia-northeast1 \
  --display_name="Weather Agent" \
  weather_agent

# 既存インスタンスの更新
uv run adk deploy agent_engine \
  --project=gaudiy-ai \
  --region=asia-northeast1 \
  --display_name="Weather Agent" \
  --agent_engine_id=RESOURCE_ID \
  weather_agent
```

## Lint / 型チェック

```bash
uv run ruff check .        # リンター
uv run ruff check --fix .  # 自動修正
uv run mypy weather_agent/ # 型チェック
```
