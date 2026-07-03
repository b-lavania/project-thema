"""Weekly artifact generation + management."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from ..db import get_session, init_db
from ..models import Artifact, _today_iso

PROMPTS_DIR = Path(__file__).resolve().parents[2] / "prompts"
PUBLISHED_DIR = Path(__file__).resolve().parents[2] / "data" / "published"


def _to_dict(a: Artifact) -> dict:
    return {
        "id": a.id,
        "title": a.title,
        "topic": a.topic,
        "body": a.body,
        "file_path": a.file_path,
        "date_created": a.date_created,
        "published": bool(a.published),
        "published_to": a.published_to,
    }


def list_artifacts(limit: int = 50) -> list[dict]:
    init_db()
    with get_session() as sess:
        arts = sess.query(Artifact).order_by(Artifact.date_created.desc()).limit(limit).all()
        return [_to_dict(a) for a in arts]


def get_artifact(artifact_id: str) -> Optional[dict]:
    init_db()
    with get_session() as sess:
        a = sess.get(Artifact, artifact_id)
        return _to_dict(a) if a else None


def save_artifact(title: str, topic: str, body: str, published_to: str = "") -> dict:
    init_db()
    with get_session() as sess:
        a = Artifact(
            title=title,
            topic=topic,
            body=body,
            published_to=published_to,
        )
        sess.add(a)
        sess.commit()
        return _to_dict(a)


def mark_published(artifact_id: str, published_to: str = "linkedin") -> Optional[dict]:
    init_db()
    with get_session() as sess:
        a = sess.get(Artifact, artifact_id)
        if not a:
            return None
        a.published = 1
        a.published_to = published_to

        # Save to file
        PUBLISHED_DIR.mkdir(parents=True, exist_ok=True)
        slug = a.title.lower().replace(" ", "_")[:50]
        filename = f"{a.date_created}_{slug}.md"
        filepath = PUBLISHED_DIR / filename
        filepath.write_text(
            f"# {a.title}\n\n*{a.topic} — {a.date_created}*\n\n{a.body}",
            encoding="utf-8",
        )
        a.file_path = str(filepath)
        sess.commit()
        return _to_dict(a)


def generate_artifact_llm(llm, topic: str, insight: str) -> dict:
    """Use LLM to draft a weekly proof artifact."""
    prompt_template = ""
    p = PROMPTS_DIR / "artifact_draft.md"
    if p.exists():
        prompt_template = p.read_text(encoding="utf-8")

    if not prompt_template:
        return {"title": "", "body": "(prompt template not found)"}

    prompt = prompt_template.format(topic=topic, insight=insight)

    from llm_client import call_llm
    result = call_llm(
        llm,
        system_prompt="You are a logistics ops thought leader writing a short proof artifact.",
        user_prompt=prompt,
        max_tokens=1200,
        temperature=0.4,
        tier="default",
        require_nonempty=True,
        step_label="Artifact generation",
    )
    text, usage = result if isinstance(result, tuple) else (result, {})

    # Extract title (first line starting with #)
    title = topic.title()
    for line in text.split("\n"):
        if line.strip().startswith("# "):
            title = line.strip().lstrip("#").strip()
            break

    saved = save_artifact(title=title, topic=topic, body=text)
    return saved
