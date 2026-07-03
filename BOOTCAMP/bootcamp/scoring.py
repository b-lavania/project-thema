"""Daily/weekly/camp scoring from the bootcamp rubric."""

from __future__ import annotations

from typing import Any

# ── Daily scoring ────────────────────────────────────────────────

QUOTA_POINTS = 10  # per quota
DAILY_MAX = 80  # 60 base + 20 bonus


def compute_daily_score(
    quotas_completed: int,
    bonuses: list[str],
    penalties: list[str],
) -> dict[str, Any]:
    """Compute daily score from completions.

    Args:
        quotas_completed: Number of quotas hit (0-6).
        bonuses: List of bonus codes earned.
        penalties: List of penalty codes incurred.

    Returns dict with base, bonus, penalty, total, and grade.
    """
    base = quotas_completed * QUOTA_POINTS  # 0-60

    bonus_map: dict[str, int] = {
        "public_artifact": 10,
        "extra_drill": 5,
        "stakeholder_simulation": 5,
        "executive_compression": 5,
    }
    bonus_pts = sum(bonus_map.get(b, 0) for b in bonuses)
    bonus_pts = min(bonus_pts, 20)  # cap at 20

    penalty_map: dict[str, int] = {
        "miss_1_quota": 10,
        "miss_2plus_week": 20,
        "phone_during_block": 15,
        "passive_content": 10,
        "hidden_miss": 30,
        "new_side_project": 50,
        "new_identity": 50,
        "skipped_review": 20,
        "skipped_audit": 40,
        "missed_artifact": 30,
    }
    penalty_pts = sum(penalty_map.get(p, 0) for p in penalties)

    total = max(0, base + bonus_pts - penalty_pts)

    # Daily letter grade
    if total >= 70:
        grade = "A"
    elif total >= 55:
        grade = "B"
    elif total >= 35:
        grade = "C"
    else:
        grade = "F"

    return {
        "base": base,
        "bonus": bonus_pts,
        "penalty": penalty_pts,
        "total": min(total, DAILY_MAX),
        "grade": grade,
        "quotas_hit": quotas_completed,
    }


# ── Weekly scoring ───────────────────────────────────────────────

WEEKLY_THRESHOLDS: dict[int, tuple[int, int, int]] = {
    # week → (A_min, B_min, C_min)
    1: (400, 320, 240),
    2: (420, 340, 260),
    3: (440, 360, 280),
    4: (460, 380, 300),
}


def compute_weekly_score(
    daily_scores: list[dict],
    week: int = 1,
    weekly_bonus: float = 0,
    weekly_penalty: float = 0,
    artifact_shipped: bool = False,
    total_misses: int = 0,
) -> dict[str, Any]:
    """Compute weekly score from 7 daily scores.

    Weekly score = sum of daily totals + weekly bonuses - weekly penalties.
    """
    daily_total = sum(d.get("total", 0) for d in daily_scores)
    adjusted = daily_total + weekly_bonus - weekly_penalty
    adjusted = max(0, adjusted)

    a_min, b_min, c_min = WEEKLY_THRESHOLDS.get(week, (400, 320, 240))

    if adjusted >= a_min and total_misses <= 1 and artifact_shipped:
        grade = "A"
    elif adjusted >= b_min:
        grade = "B"
    elif adjusted >= c_min:
        grade = "C"
    else:
        grade = "F"

    return {
        "raw_total": daily_total,
        "bonus": weekly_bonus,
        "penalty": weekly_penalty,
        "adjusted": adjusted,
        "grade": grade,
        "misses": total_misses,
        "artifact_shipped": artifact_shipped,
    }


# ── Camp scoring ─────────────────────────────────────────────────

CAMP_TARGET = 8_000


def compute_camp_score(
    total_points: float,
    week_grades: list[str],
    public_artifacts: int,
    portfolio_assets: int,
    review_streak: int,
) -> dict[str, Any]:
    """Compute final camp result."""
    passed = (
        total_points >= CAMP_TARGET
        and sum(1 for g in week_grades if g in ("A", "B")) >= 3
        and "F" not in week_grades
        and public_artifacts >= 4
        and portfolio_assets >= 1
        and review_streak >= 25
    )

    failures = []
    if total_points < CAMP_TARGET:
        failures.append(f"Score {total_points:.0f} < {CAMP_TARGET} target")
    if sum(1 for g in week_grades if g in ("A", "B")) < 3:
        failures.append(f"Need 3/4 weeks A or B (got {week_grades})")
    if "F" in week_grades:
        failures.append(f"F week(s) not allowed: {[i+1 for i, g in enumerate(week_grades) if g == 'F']}")
    if public_artifacts < 4:
        failures.append(f"Need 4 public artifacts (got {public_artifacts})")
    if portfolio_assets < 1:
        failures.append("Need 1 portfolio-grade strategy asset")
    if review_streak < 25:
        failures.append(f"Need 25+ day review streak (got {review_streak})")

    grade = "PASS" if passed else "FAIL"

    return {
        "total_score": total_points,
        "week_grades": week_grades,
        "public_artifacts": public_artifacts,
        "portfolio_assets": portfolio_assets,
        "review_streak": review_streak,
        "passed": passed,
        "grade": grade,
        "failures": failures,
    }
