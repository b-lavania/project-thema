"""
generate_post.py
Generates LinkedIn and Facebook posts in the user's voice using Claude.
Accepts bullet points or prose as opinion input.
Also supports template-based generation for quick posts (no article required).
"""

import os
import json
import anthropic
from pathlib import Path

ROOT = Path(__file__).parent.parent
VOICE_PROFILE_PATH = ROOT / "voice_profile.md"
TEMPLATES_PATH = ROOT / "config" / "post_templates.json"

# Current model strings. Summary is a trivial task -> cheaper/faster Sonnet.
# Post generation -> Opus for voice quality.
SUMMARY_MODEL = "claude-sonnet-4-6"
POST_MODEL = "claude-opus-4-8"

def load_voice_profile():
    with open(VOICE_PROFILE_PATH) as f:
        return f.read()

def load_templates():
    with open(TEMPLATES_PATH) as f:
        return json.load(f)

def generate_summary(article: dict) -> str:
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    message = client.messages.create(
        model=SUMMARY_MODEL,
        max_tokens=300,
        messages=[{
            "role": "user",
            "content": f"""Summarize this article in 3-4 sentences for a B2B SaaS and AI marketer.
Be direct and specific. Focus on what actually happened or what the key argument is.
No filler phrases like "The article discusses..." — just the substance.

Title: {article.get('title', '')}
Source: {article.get('source', '')}
Content: {article.get('summary', '')}"""
        }]
    )
    return message.content[0].text.strip()


def generate_posts(article: dict, opinion: str) -> dict:
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    voice_profile = load_voice_profile()

    system_prompt = f"""You are a ghostwriter producing LinkedIn and Facebook posts for a B2B SaaS and AI marketer.

Your job is to translate their raw opinion — which may be bullet points or rough prose — into a polished post that sounds exactly like them. Not like a content marketer, not like an AI assistant, not like a press release.

Here is their complete voice profile. Follow it precisely:

{voice_profile}

CRITICAL RULES:
- If the input is bullet points, weave them into a cohesive narrative — do not just list them out
- Never start a post with "I" — weak opener on LinkedIn
- No phrases like "Great read", "Fascinating article", "This is a must-read"
- No fake enthusiasm or hollow affirmations
- Do not summarize the article — the post is about THEIR take, not the article
- The article is context. The opinion is the content.
- Do not make up facts or statistics not provided
- Preserve and sharpen the user's specific argument
- LinkedIn post: 150-250 words, no markdown, line breaks between thoughts, 3 hashtags max at the end
- Facebook post: same length, slightly warmer tone, no hashtags needed
- Return ONLY valid JSON — no preamble, no explanation, no markdown fences
"""

    user_prompt = f"""Article:
Title: {article['title']}
Source: {article['source']}
URL: {article['url']}
Summary: {article['summary']}

My raw opinion (may be bullet points or prose):
{opinion}

Generate both posts. Return ONLY this JSON structure:
{{
  "linkedin": "the full linkedin post text here",
  "facebook": "the full facebook post text here"
}}"""

    message = client.messages.create(
        model=POST_MODEL,
        max_tokens=1500,
        messages=[{"role": "user", "content": user_prompt}],
        system=system_prompt,
    )

    raw = message.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()
    return json.loads(raw)


def generate_quick_post(template_type: str, raw_idea: str, company_context: str = "") -> dict:
    """Generate a post without an article, using a template."""
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    voice_profile = load_voice_profile()
    templates = load_templates()

    if template_type not in templates["templates"]:
        raise ValueError(f"Unknown template type: {template_type}")

    template = templates["templates"][template_type]
    template_prompt = template["prompt"]

    system_prompt = f"""You are a ghostwriter producing LinkedIn and Facebook posts for an ops-AI founding product lead.

Your job is to translate their raw idea — which may be bullet points or rough prose — into a polished post that sounds exactly like them using the specified template structure.

Here is their complete voice profile. Follow it precisely:

{voice_profile}

CRITICAL RULES:
- If the input is bullet points, weave them into a cohesive narrative — do not just list them out
- Never start a post with "I" — weak opener on LinkedIn
- No phrases like "Great read", "Fascinating article", "This is a must-read"
- No fake enthusiasm or hollow affirmations
- Do not make up facts or statistics not provided
- Preserve and sharpen the user's specific argument
- LinkedIn post: 150-250 words, no markdown, line breaks between thoughts, 3 hashtags max at the end
- Facebook post: same length, slightly warmer tone, no hashtags needed
- Return ONLY valid JSON — no preamble, no explanation, no markdown fences
"""

    user_prompt = f"""Template Type: {template_type}
Template Structure: {template['structure']}

Template Instructions:
{template_prompt}

My raw idea (may be bullet points or prose):
{raw_idea}

{f"Company Context: {company_context}" if company_context else ""}

Generate both posts. Return ONLY this JSON structure:
{{
  "linkedin": "the full linkedin post text here",
  "facebook": "the full facebook post text here"
}}"""

    message = client.messages.create(
        model=POST_MODEL,
        max_tokens=1500,
        messages=[{"role": "user", "content": user_prompt}],
        system=system_prompt,
    )

    raw = message.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()
    return json.loads(raw)
