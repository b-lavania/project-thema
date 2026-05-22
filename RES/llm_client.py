"""Unified LLM access for OpenAI and Google AI Studio (Gemini)."""

from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from typing import Any, Literal

from openai import OpenAI

Provider = Literal["openai", "gemini"]

OPENAI_MODELS = {
    "default": ["gpt-4o", "gpt-4.1", "gpt-4o-mini"],
    "profile": ["gpt-4.1", "gpt-4o"],
    "pain": ["o4-mini", "gpt-4.1", "gpt-4o-mini"],
}

GEMINI_MODELS = {
    "default": [
        "gemini-2.5-flash",
        "gemini-2.5-flash-lite",
        "gemini-2.0-flash",
        "gemini-2.0-flash-lite",
    ],
    "profile": ["gemini-2.5-pro", "gemini-2.5-flash", "gemini-2.0-flash"],
    "pain": [
        "gemini-2.5-flash",
        "gemini-2.5-flash-lite",
        "gemini-2.0-flash",
    ],
}

OPENAI_DEFAULTS = {
    "default": "gpt-4o",
    "profile": "gpt-4.1",
    "pain": os.environ.get("PAIN_POINT_MODEL", "o4-mini"),
    "pain_fallback": os.environ.get("PAIN_POINT_FALLBACK", "gpt-4.1"),
}

GEMINI_DEFAULTS = {
    "default": os.environ.get("GEMINI_DEFAULT_MODEL", "gemini-2.5-flash"),
    "profile": os.environ.get("GEMINI_PROFILE_MODEL", "gemini-2.5-pro"),
    "pain": os.environ.get("GEMINI_PAIN_MODEL", "gemini-2.5-flash"),
    "pain_fallback": os.environ.get("GEMINI_PAIN_FALLBACK", "gemini-2.0-flash"),
}


@dataclass
class LLMClient:
    """Wrapper for provider-specific SDK clients."""

    provider: Provider
    _client: Any
    model_overrides: dict[str, str] = field(default_factory=dict)

    @property
    def is_gemini(self) -> bool:
        return self.provider == "gemini"


def get_llm_client(
    provider: str,
    api_key: str,
    model_overrides: dict[str, str] | None = None,
) -> LLMClient:
    """Create an LLM client for OpenAI or Gemini (AI Studio)."""
    if not api_key or not api_key.strip():
        raise ValueError(f"API key required for provider: {provider}")

    provider = provider.lower()
    if provider == "openai":
        return LLMClient(
            provider="openai",
            _client=OpenAI(api_key=api_key.strip()),
            model_overrides=model_overrides or {},
        )
    if provider == "gemini":
        from google import genai

        return LLMClient(
            provider="gemini",
            _client=genai.Client(api_key=api_key.strip()),
            model_overrides=model_overrides or {},
        )
    raise ValueError(f"Unknown provider: {provider}. Use 'openai' or 'gemini'.")


def resolve_model(
    llm: LLMClient,
    tier: str = "default",
    explicit: str | None = None,
) -> str:
    """Resolve model id for tier: default | profile | pain | pain_fallback."""
    if explicit:
        return explicit
    if tier in llm.model_overrides:
        return llm.model_overrides[tier]
    if llm.provider == "gemini":
        return GEMINI_DEFAULTS.get(tier, GEMINI_DEFAULTS["default"])
    return OPENAI_DEFAULTS.get(tier, OPENAI_DEFAULTS["default"])


def model_choices(provider: str, tier: str) -> list[str]:
    """Return selectable model IDs for UI dropdowns."""
    if provider == "gemini":
        return GEMINI_MODELS.get(tier, GEMINI_MODELS["default"])
    return OPENAI_MODELS.get(tier, OPENAI_MODELS["default"])


def _usage_from_gemini(response) -> dict:
    meta = getattr(response, "usage_metadata", None)
    if not meta:
        return {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
    prompt = (
        getattr(meta, "prompt_token_count", None)
        or getattr(meta, "prompt_tokens", None)
        or 0
    )
    completion = (
        getattr(meta, "candidates_token_count", None)
        or getattr(meta, "response_token_count", None)
        or getattr(meta, "completion_tokens", None)
        or 0
    )
    total = getattr(meta, "total_token_count", None) or (prompt + completion)
    return {
        "prompt_tokens": int(prompt),
        "completion_tokens": int(completion),
        "total_tokens": int(total),
    }


def _call_openai_raw(
    client: OpenAI,
    system_prompt: str,
    user_prompt: str,
    max_tokens: int,
    temperature: float,
    model: str,
    retries: int,
) -> tuple[str, dict]:
    last_error = None
    for attempt in range(retries):
        try:
            params: dict = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "max_completion_tokens": max_tokens,
            }
            if not model.startswith("gpt-5"):
                params["temperature"] = temperature
            response = client.chat.completions.create(**params)
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            }
            content = response.choices[0].message.content
            if not content:
                print(
                    f"[DEBUG] Blank OpenAI response from {model}. "
                    f"finish_reason={response.choices[0].finish_reason!r}"
                )
            return (content or "").strip(), usage
        except Exception as e:
            last_error = e
            if attempt < retries - 1:
                time.sleep(2**attempt)
    raise last_error


def _call_gemini_raw(
    client,
    system_prompt: str,
    user_prompt: str,
    max_tokens: int,
    temperature: float,
    model: str,
    retries: int,
) -> tuple[str, dict]:
    from google.genai import types

    last_error = None
    for attempt in range(retries):
        try:
            response = client.models.generate_content(
                model=model,
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    max_output_tokens=max_tokens,
                    temperature=temperature,
                ),
            )
            text = getattr(response, "text", None) or ""
            if not text and getattr(response, "candidates", None):
                parts = response.candidates[0].content.parts
                text = "".join(getattr(p, "text", "") or "" for p in parts)
            return text.strip(), _usage_from_gemini(response)
        except Exception as e:
            last_error = e
            if attempt < retries - 1:
                time.sleep(2**attempt)
    raise last_error


def call_llm(
    llm: LLMClient,
    system_prompt: str,
    user_prompt: str,
    max_tokens: int = 600,
    temperature: float = 0.4,
    retries: int = 3,
    model: str | None = None,
    tier: str = "default",
) -> tuple[str, dict]:
    """
    Call the configured provider. Returns (content, usage_dict).

    Pass `model` explicitly or use `tier` (default | profile | pain).
    """
    resolved = resolve_model(llm, tier=tier, explicit=model)
    if llm.provider == "openai":
        return _call_openai_raw(
            llm._client,
            system_prompt,
            user_prompt,
            max_tokens,
            temperature,
            resolved,
            retries,
        )
    return _call_gemini_raw(
        llm._client,
        system_prompt,
        user_prompt,
        max_tokens,
        temperature,
        resolved,
        retries,
    )


# Backward-compatible alias
get_openai_client = lambda api_key: get_llm_client("openai", api_key)
