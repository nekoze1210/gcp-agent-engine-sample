"""Weather agent definition using Google Agent Development Kit."""

from google.adk.agents import Agent

from .tools import get_weather, get_weather_forecast

root_agent = Agent(
    name="weather_agent",
    model="gemini-2.5-flash",
    description=(
        "A helpful agent that provides current weather"
        " and forecast information for cities worldwide."
    ),
    instruction=(
        "あなたは天気情報を提供するエージェントです。\n"
        "ユーザーが都市名を指定したら、適切なツールを使って天気を取得してください。\n"
        "- 現在の天気を聞かれたら get_weather を使ってください。\n"
        "- 明日以降や週間予報など未来の天気を聞かれたら get_weather_forecast を使ってください。\n"
        "結果は日本語で分かりやすく伝えてください。\n"
        "都市名が不明確な場合は、ユーザーに確認してください。"
    ),
    tools=[get_weather, get_weather_forecast],
)
