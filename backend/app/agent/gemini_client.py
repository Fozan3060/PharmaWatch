"""Gemini chat factory (google-genai SDK).

`make_chat()` returns an AsyncChat configured with the agent system prompt
and all registered tools. Lazy: the SDK client is created on first call so
the app boots without GEMINI_API_KEY (useful for tests with a fake chat).
"""

from __future__ import annotations

from google import genai
from google.genai import types

from app.agent.system_prompt import SYSTEM_PROMPT
from app.agent.tools import to_gemini_function_declarations
from app.config import get_settings

_client: genai.Client | None = None


def _get_client() -> genai.Client:
    global _client
    if _client is not None:
        return _client
    settings = get_settings()
    if not settings.gemini_api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not set. Get a free key at https://aistudio.google.com/app/apikey "
            "and add it to backend/.env."
        )
    _client = genai.Client(api_key=settings.gemini_api_key)
    return _client


def make_chat():
    client = _get_client()
    settings = get_settings()
    declarations = [
        types.FunctionDeclaration(
            name=d["name"],
            description=d["description"],
            parameters_json_schema=d["parameters"],
        )
        for d in to_gemini_function_declarations()
    ]
    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        tools=[types.Tool(function_declarations=declarations)],
    )
    return client.aio.chats.create(model=settings.gemini_agent_model, config=config)
