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

# Google retired 2.0 Flash for new API keys (404). Remap env/session leftovers.
GEMINI_DEPRECATED_MODEL_MAP = {
    "gemini-2.0-flash": "gemini-2.5-flash-lite",
    "gemini-2.0-flash-lite": "gemini-2.5-flash-lite",
}

GEMINI_MODELS = {
    "default": [
        "gemini-2.5-flash",
        "gemini-2.5-flash-lite",
        "gemini-2.5-pro",
    ],
    "profile": ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-2.5-flash-lite"],
    "pain": [
        "gemini-2.5-flash",
        "gemini-2.5-flash-lite",
        "gemini-2.5-pro",
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
    # Flash is more reliable than Pro on free tier (Pro quota often 0) and avoids
    # thinking tokens consuming the entire max_output_tokens budget.
    "profile": os.environ.get("GEMINI_PROFILE_MODEL", "gemini-2.5-flash"),
    "pain": os.environ.get("GEMINI_PAIN_MODEL", "gemini-2.5-flash"),
    "pain_fallback": os.environ.get("GEMINI_PAIN_FALLBACK", "gemini-2.5-flash-lite"),
}


def normalize_gemini_model_id(model: str) -> str:
    """Map retired model IDs to supported ones."""
    return GEMINI_DEPRECATED_MODEL_MAP.get(model, model)


class LLMResponseError(RuntimeError):
    """Raised when the model returns empty or unusably truncated text."""

    def __init__(
        self,
        message: str,
        *,
        model: str = "",
        finish_reason: str | None = None,
        step: str | None = None,
    ):
        self.model = model
        self.finish_reason = finish_reason
        self.step = step
        super().__init__(message)


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
    model_id = explicit
    if not model_id and tier in llm.model_overrides:
        model_id = llm.model_overrides[tier]
    if not model_id:
        if llm.provider == "gemini":
            model_id = GEMINI_DEFAULTS.get(tier, GEMINI_DEFAULTS["default"])
        else:
            model_id = OPENAI_DEFAULTS.get(tier, OPENAI_DEFAULTS["default"])
    if llm.provider == "gemini":
        return normalize_gemini_model_id(model_id)
    return model_id


def model_choices(provider: str, tier: str) -> list[str]:
    """Return selectable model IDs for UI dropdowns."""
    if provider == "gemini":
        return GEMINI_MODELS.get(tier, GEMINI_MODELS["default"])
    return OPENAI_MODELS.get(tier, OPENAI_MODELS["default"])


def _gemini_finish_reason(response) -> str | None:
    candidates = getattr(response, "candidates", None) or []
    if not candidates:
        return None
    reason = getattr(candidates[0], "finish_reason", None)
    if reason is None:
        return None
    return str(reason).upper()


def _gemini_output_truncated(response, text: str) -> bool:
    """True only when Gemini hit the output token cap — not for STOP (normal end)."""
    reason = _gemini_finish_reason(response) or ""
    # e.g. MAX_OUTPUT_TOKENS, FinishReason.MAX_OUTPUT_TOKENS
    if "MAX" in reason and "TOKEN" in reason:
        return True
    # Do not infer truncation from punctuation: JD pain / bullets often end without periods.
    return False


def _gemini_effective_max_tokens(model: str, max_tokens: int) -> int:
    """2.5 models need headroom: thinking can consume output budget before visible text."""
    m = model.lower()
    if "2.5-pro" in m:
        return max(max_tokens, 2048)
    if "2.5" in m:
        return max(max_tokens, 1024)
    return max(max_tokens, 512)


def _gemini_thinking_config(model: str):
    """Prefer no internal thinking on Flash; Pro requires minimum thinking budget."""
    from google.genai import types

    m = model.lower()
    if "2.5-pro" in m:
        return types.ThinkingConfig(thinking_budget=128)
    if "2.5" in m:
        return types.ThinkingConfig(thinking_budget=0)
    return None


def _extract_gemini_text(response) -> str:
    """Collect visible text from a Gemini response; never assume parts is iterable."""
    text = getattr(response, "text", None) or ""
    if text:
        return text.strip()

    candidates = getattr(response, "candidates", None) or []
    if not candidates:
        return ""

    content = getattr(candidates[0], "content", None)
    if not content:
        return ""

    parts = getattr(content, "parts", None)
    if not parts:
        return ""

    chunks = []
    for part in parts:
        chunk = getattr(part, "text", None)
        if chunk:
            chunks.append(chunk)
    return "".join(chunks).strip()


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
    *,
    require_nonempty: bool = False,
    step_label: str | None = None,
) -> tuple[str, dict]:
    from google.genai import types

    last_error = None
    token_budget = _gemini_effective_max_tokens(model, max_tokens)
    thinking_config = _gemini_thinking_config(model)
    usage_total = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}

    for attempt in range(retries):
        try:
            config_kw: dict = {
                "system_instruction": system_prompt,
                "max_output_tokens": token_budget,
                "temperature": temperature,
            }
            if thinking_config is not None:
                config_kw["thinking_config"] = thinking_config

            response = client.models.generate_content(
                model=model,
                contents=user_prompt,
                config=types.GenerateContentConfig(**config_kw),
            )
            usage = _usage_from_gemini(response)
            for key in usage_total:
                usage_total[key] += usage.get(key, 0)

            text = _extract_gemini_text(response)
            finish = _gemini_finish_reason(response)
            truncated = _gemini_output_truncated(response, text)

            if not text or truncated:
                print(
                    f"[DEBUG] Gemini {'blank' if not text else 'truncated'} from {model} "
                    f"(attempt {attempt + 1}/{retries}, max_output={token_budget}). "
                    f"finish_reason={finish!r}"
                )
                if attempt < retries - 1:
                    token_budget = min(int(token_budget * 1.75), 8192)
                    time.sleep(2**attempt)
                    continue
                if require_nonempty and not text:
                    label = step_label or "LLM step"
                    raise LLMResponseError(
                        f"{label} returned empty text from {model}. "
                        f"Try gemini-2.5-flash for profile, check API quota, or switch to OpenAI.",
                        model=model,
                        finish_reason=finish,
                        step=step_label,
                    )
                if require_nonempty and truncated:
                    label = step_label or "LLM step"
                    raise LLMResponseError(
                        f"{label} hit the output token limit on {model} "
                        f"(finish_reason={finish}). Retry or raise max tokens in Advanced models.",
                        model=model,
                        finish_reason=finish,
                        step=step_label,
                    )
            return text, usage_total
        except LLMResponseError:
            raise
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
    require_nonempty: bool = False,
    step_label: str | None = None,
) -> tuple[str, dict]:
    """
    Call the configured provider. Returns (content, usage_dict).

    Pass `model` explicitly or use `tier` (default | profile | pain).
    Set require_nonempty=True to retry then raise LLMResponseError on blank/truncated Gemini output.
    """
    resolved = resolve_model(llm, tier=tier, explicit=model)
    if llm.provider == "openai":
        text, usage = _call_openai_raw(
            llm._client,
            system_prompt,
            user_prompt,
            max_tokens,
            temperature,
            resolved,
            retries,
        )
        if require_nonempty and not (text or "").strip():
            raise LLMResponseError(
                f"{step_label or 'LLM step'} returned empty text from {resolved}.",
                model=resolved,
                step=step_label,
            )
        return text, usage
    return _call_gemini_raw(
        llm._client,
        system_prompt,
        user_prompt,
        max_tokens,
        temperature,
        resolved,
        retries,
        require_nonempty=require_nonempty,
        step_label=step_label,
    )


# Backward-compatible alias
get_openai_client = lambda api_key: get_llm_client("openai", api_key)
