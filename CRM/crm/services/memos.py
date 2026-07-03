"""LLM-powered bottleneck memo generation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from ..db import get_session, init_db
from ..models import Company, Memo, _today_iso

PROMPTS_DIR = Path(__file__).resolve().parents[2] / "prompts"


def _to_dict(m: Memo) -> dict:
    return {
        "id": m.id,
        "company_id": m.company_id,
        "stated_problem": m.stated_problem,
        "real_bottleneck": m.real_bottleneck,
        "wrong_solution": m.wrong_solution,
        "metric_to_move": m.metric_to_move,
        "full_memo": m.full_memo,
        "date_created": m.date_created,
        "version": m.version,
    }


def load_prompt(name: str) -> str:
    path = PROMPTS_DIR / name
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""


def get_memo(company_id: str) -> Optional[dict]:
    init_db()
    with get_session() as sess:
        m = sess.query(Memo).filter(Memo.company_id == company_id).order_by(
            Memo.version.desc()
        ).first()
        return _to_dict(m) if m else None


def get_all_memos(company_id: str) -> list[dict]:
    init_db()
    with get_session() as sess:
        memos = sess.query(Memo).filter(Memo.company_id == company_id).order_by(
            Memo.version.desc()
        ).all()
        return [_to_dict(m) for m in memos]


def save_memo(
    company_id: str,
    stated_problem: str,
    real_bottleneck: str,
    wrong_solution: str,
    metric_to_move: str,
    full_memo: str = "",
) -> dict:
    """Save a memo (auto-increments version)."""
    init_db()
    with get_session() as sess:
        last = sess.query(Memo).filter(Memo.company_id == company_id).order_by(
            Memo.version.desc()
        ).first()
        version = (last.version + 1) if last else 1
        m = Memo(
            company_id=company_id,
            stated_problem=stated_problem,
            real_bottleneck=real_bottleneck,
            wrong_solution=wrong_solution,
            metric_to_move=metric_to_move,
            full_memo=full_memo,
            version=version,
        )
        sess.add(m)
        sess.commit()
        return _to_dict(m)


def generate_memo_llm(llm, company: dict) -> dict:
    """Use LLM to generate a bottleneck memo for a company."""
    from ..db import get_session
    from ..models import Company

    prompt_template = load_prompt("bottleneck_memo.md")
    if not prompt_template:
        return {
            "stated_problem": "",
            "real_bottleneck": "",
            "wrong_solution": "",
            "metric_to_move": "",
            "full_memo": "(prompt template not found)",
        }

    # Gather context
    hypothesis = company.get("hypothesis", "") or ""
    notes = company.get("notes", "") or ""
    industry = company.get("industry", "") or ""
    name = company.get("name", "") or ""

    prompt = prompt_template.format(
        company_name=name,
        industry=industry,
        hypothesis=hypothesis,
        company_notes=notes,
    )

    # Call LLM using existing infrastructure
    from llm_client import call_llm
    result = call_llm(
        llm,
        system_prompt="You are a logistics and ops AI analyst. Write a concise bottleneck hypothesis memo.",
        user_prompt=prompt,
        max_tokens=800,
        temperature=0.3,
        tier="default",
        require_nonempty=True,
        step_label="Bottleneck memo generation",
    )
    text, usage = result if isinstance(result, tuple) else (result, {})

    # Parse sections from output
    sections = {
        "stated_problem": "",
        "real_bottleneck": "",
        "wrong_solution": "",
        "metric_to_move": "",
        "full_memo": text,
    }
    current_key = None
    for line in text.split("\n"):
        lower = line.lower().strip()
        if "stated problem" in lower:
            current_key = "stated_problem"
        elif "real bottleneck" in lower or "actual bottleneck" in lower:
            current_key = "real_bottleneck"
        elif "wrong solution" in lower or "avoid" in lower:
            current_key = "wrong_solution"
        elif "metric" in lower or "measure" in lower:
            current_key = "metric_to_move"
        elif current_key and line.strip().startswith(("-", "•")):
            sections[current_key] += line.strip().lstrip("-•").strip() + "\n"

    # Clean up
    for k in sections:
        if k != "full_memo":
            sections[k] = sections[k].strip()

    # Save to DB
    save_memo(
        company["id"],
        stated_problem=sections["stated_problem"],
        real_bottleneck=sections["real_bottleneck"],
        wrong_solution=sections["wrong_solution"],
        metric_to_move=sections["metric_to_move"],
        full_memo=text,
    )

    return sections
