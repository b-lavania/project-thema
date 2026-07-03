"""Parse 30-day-calendar.md into structured Day objects."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

CALENDAR_PATH = Path(__file__).resolve().parent.parent / "30-day-calendar.md"

DRILL_NAMES = {
    1: "Teardown",
    2: "Recommendation",
    3: "Anti-Defensive",
    4: "Translation",
    5: "Triage",
    6: "Compression",
    7: "Hostile Response",
    8: "Spoken Diagnosis",
}


@dataclass
class Block:
    letter: str
    description: str


@dataclass
class Drill:
    slot: int  # 1 or 2
    drill_number: int
    drill_name: str
    description: str


@dataclass
class Day:
    number: int
    day_of_week: str
    week: int
    theme: str
    focus: str
    blocks: list[Block] = field(default_factory=list)
    hiit1: Drill | None = None
    hiit2: Drill | None = None
    quotas: list[str] = field(default_factory=list)
    has_pa: bool = False


def _parse_week_themes(text: str) -> dict[int, str]:
    """Extract week number → theme mapping."""
    themes: dict[int, str] = {}
    for m in re.finditer(r"^## Week (\d+): (.+)", text, re.MULTILINE):
        themes[int(m.group(1))] = m.group(2).strip()
    return themes


def _day_week(num: int) -> int:
    """Compute which week (1-4) a day number belongs to."""
    return min((num - 1) // 7 + 1, 4)


def _extract_day(
    content: str, num: int, dow: str, week: int, theme: str
) -> Day:
    focus_m = re.search(r"\*\*Focus\*\*:\s*(.+)", content)
    focus = focus_m.group(1).strip() if focus_m else ""

    blocks: list[Block] = []
    for letter in ("A", "B", "C"):
        m = re.search(r"\*\*Block " + letter + r"\*\*:\s*(.+)", content)
        if m:
            blocks.append(Block(letter=letter, description=m.group(1).strip()))

    hi1 = re.search(
        r"\*\*HIIT 1\*\*:\s*Drill\s*(\d+)\s*[—–-]\s*(.+)", content
    )
    hi2 = re.search(
        r"\*\*HIIT 2\*\*:\s*Drill\s*(\d+)\s*[—–-]\s*(.+)", content
    )

    hiit1: Drill | None = None
    if hi1:
        dn = int(hi1.group(1))
        hiit1 = Drill(
            slot=1,
            drill_number=dn,
            drill_name=DRILL_NAMES.get(dn, str(dn)),
            description=hi1.group(2).strip(),
        )

    hiit2: Drill | None = None
    if hi2:
        dn = int(hi2.group(1))
        hiit2 = Drill(
            slot=2,
            drill_number=dn,
            drill_name=DRILL_NAMES.get(dn, str(dn)),
            description=hi2.group(2).strip(),
        )

    quotas_m = re.search(r"\*\*Daily quotas\*\*:\s*(.+)", content)
    quotas = [q.strip() for q in quotas_m.group(1).split(",")] if quotas_m else []

    has_pa = "PA" in content  # Sundays always have PA

    return Day(
        number=num,
        day_of_week=dow,
        week=week,
        theme=theme,
        focus=focus,
        blocks=blocks,
        hiit1=hiit1,
        hiit2=hiit2,
        quotas=quotas,
        has_pa=has_pa,
    )


def parse_calendar() -> list[Day]:
    """Parse 30-day-calendar.md into a list of Day objects."""
    text = CALENDAR_PATH.read_text(encoding="utf-8")
    week_themes = _parse_week_themes(text)

    # Locate every day header
    day_headers = list(re.finditer(r"^### Day (\d+) \(([^)]+)\)", text, re.MULTILINE))

    days: list[Day] = []
    for i, m in enumerate(day_headers):
        num = int(m.group(1))
        dow = m.group(2)
        start = m.start()
        end = day_headers[i + 1].start() if i + 1 < len(day_headers) else len(text)
        content = text[start:end]
        week = _day_week(num)
        theme = week_themes.get(week, "")
        days.append(_extract_day(content, num, dow, week, theme))

    return days


# Module-level cache
_CALENDAR: list[Day] | None = None


def get_calendar() -> list[Day]:
    """Return cached calendar, parsing on first call."""
    global _CALENDAR
    if _CALENDAR is None:
        _CALENDAR = parse_calendar()
    return _CALENDAR
