"""Scorecard save/load + progress.json persistence."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
PROGRESS_PATH = DATA_DIR / "progress.json"
SCORECARDS_DIR = DATA_DIR / "scorecards"
ARTIFACTS_DIR = DATA_DIR / "artifacts"

# Ensure directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
SCORECARDS_DIR.mkdir(parents=True, exist_ok=True)
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)


# ── Data structures ──────────────────────────────────────────────


@dataclass
class DayProgress:
    completed: bool = False
    score: float | None = None
    grade: str | None = None
    quotas_hit: int = 0


@dataclass
class WeekProgress:
    total: float = 0.0
    grade: str | None = None
    bonus: float = 0.0
    penalty: float = 0.0
    misses: int = 0
    artifact_shipped: bool = False


@dataclass
class CampProgress:
    current_day: int = 1
    start_date: str = ""
    days: dict[int, DayProgress] = field(default_factory=dict)
    weeks: dict[int, WeekProgress] = field(default_factory=dict)

    @property
    def total_score(self) -> float:
        return sum(d.score or 0 for d in self.days.values())

    @property
    def review_streak(self) -> int:
        """Consecutive days with completed scorecard up to current day."""
        streak = 0
        for i in range(1, self.current_day):
            d = self.days.get(i)
            if d and d.completed:
                streak += 1
            else:
                break
        return streak


# ── Progress JSON ────────────────────────────────────────────────


def _encoder(obj: Any) -> Any:
    if isinstance(obj, (DayProgress, WeekProgress, CampProgress)):
        return asdict(obj)
    return obj


def save_progress(progress: CampProgress) -> None:
    """Persist progress to progress.json."""
    data = {
        "current_day": progress.current_day,
        "start_date": progress.start_date,
        "days": {str(k): asdict(v) for k, v in progress.days.items()},
        "weeks": {str(k): asdict(v) for k, v in progress.weeks.items()},
    }
    PROGRESS_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")


def load_progress() -> CampProgress:
    """Load progress from progress.json or return fresh CampProgress."""
    if not PROGRESS_PATH.exists():
        return CampProgress()

    try:
        data = json.loads(PROGRESS_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, ValueError):
        return CampProgress()

    progress = CampProgress(
        current_day=data.get("current_day", 1),
        start_date=data.get("start_date", ""),
    )
    for k, v in data.get("days", {}).items():
        progress.days[int(k)] = DayProgress(**v)
    for k, v in data.get("weeks", {}).items():
        progress.weeks[int(k)] = WeekProgress(**v)

    return progress


# ── Scorecard MD save/load ───────────────────────────────────────


def _scorecard_path(day: int) -> Path:
    return SCORECARDS_DIR / f"day-{day}-scorecard.md"


def save_scorecard_md(day: int, data: dict) -> None:
    """Write a human-readable scorecard markdown file."""
    lines = [
        f"# Day {day} Scorecard — PM Shock Cycle Bootcamp",
        f"",
        f"_Saved: {datetime.now().strftime('%Y-%m-%d %H:%M')}_",
        f"",
        f"## Morning Setup",
        f"- Wake time: {data.get('wake_time', '—')}",
        f"- Phone away: {'✅' if data.get('phone_away') else '❌'}",
        f"- Day plan: {data.get('day_plan', '—')}",
        f"",
        f"## Quotas Hit: {data.get('quotas_hit', 0)} / 6",
        f"",
    ]
    for q in [
        ("decision", "Hard product decision"),
        ("artifact", "Written artifact"),
        ("verbal", "Verbal communication rep"),
        ("cut", "Backlog cut"),
        ("rewrite", "Anti-defensiveness rewrite"),
        ("scoreboard", "Scoreboard entry"),
    ]:
        done = data.get(f"{q[0]}_completed", False)
        lines.append(f"- {'✅' if done else '❌'} {q[1]}")

    lines.extend(
        [
            f"",
            f"## Block Completion",
        ]
    )
    for b in ("A", "B", "C", "HIIT1", "HIIT2", "stakeholder", "compression"):
        done = data.get(f"block_{b.lower()}_completed", False)
        activity = data.get(f"block_{b.lower()}_activity", "")
        lines.append(f"- {'✅' if done else '❌'} Block {b}: {activity}")

    lines.extend(
        [
            f"",
            f"## Drill Grades",
            f"- HIIT 1 grade: {data.get('hiit1_grade', '—')}/10",
            f"- HIIT 2 grade: {data.get('hiit2_grade', '—')}/10",
            f"",
            f"## Punishments Applied",
        ]
    )
    for p in ["missed_quota_drill", "missed_2plus", "missed_artifact", "relapse"]:
        if data.get(p, False):
            lines.append(f"- ⚠️  {p.replace('_', ' ').title()}")

    lines.extend(
        [
            f"",
            f"## Daily Review",
            f"- Self-grade: {data.get('self_grade', '—')}",
            f"- Tomorrow's one thing: {data.get('tomorrow_one_thing', '—')}",
            f"- Avoidance patterns: {', '.join(data.get('avoidance_patterns', [])) or '—'}",
            f"",
            f"## Score",
            f"- Total: {data.get('score', 0)} / 80",
            f"- Grade: {data.get('grade', '—')}",
        ]
    )

    _scorecard_path(day).write_text("\n".join(lines), encoding="utf-8")


def load_scorecard_md(day: int) -> dict | None:
    """Load scorecard data from markdown file (returns basic metadata)."""
    path = _scorecard_path(day)
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8")
    return {
        "day": day,
        "saved": True,
        "preview": text[:200],
    }


# ── Artifacts ────────────────────────────────────────────────────


def save_artifact(day: int, title: str, content: str) -> Path:
    """Save a public artifact to data/artifacts/."""
    path = ARTIFACTS_DIR / f"artifact-day-{day}.md"
    text = (
        f"# Artifact — Day {day}\n"
        f"**Title:** {title}\n"
        f"**Date:** {date.today().isoformat()}\n"
        f"---\n\n{content}"
    )
    path.write_text(text, encoding="utf-8")
    return path


def list_artifacts() -> list[dict]:
    """List all saved artifacts with metadata."""
    artifacts = []
    for p in sorted(ARTIFACTS_DIR.glob("artifact-day-*.md")):
        text = p.read_text(encoding="utf-8")
        title = ""
        for line in text.splitlines():
            if line.startswith("**Title:**"):
                title = line.replace("**Title:**", "").strip()
                break
        artifacts.append({
            "day": int(p.stem.split("-")[-1]),
            "title": title,
            "path": str(p),
        })
    return artifacts
