import os
from openai import OpenAI

openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
if not openrouter_api_key:
    raise RuntimeError("Missing OPENROUTER_API_KEY in .env")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=openrouter_api_key,  
)

def call_deepseek(messages):
    completion = client.chat.completions.create(
        model="deepseek/deepseek-chat",
        messages=messages,
        extra_headers={
            "HTTP-Referer": "http://localhost",
            "X-Title": "LangGraph Supervisor Demo",
        },
    )
    return completion.choices[0].message.content
