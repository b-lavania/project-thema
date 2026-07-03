#!/usr/bin/env python3
"""Discover ops-AI company candidates from YC + Crunchbase CSV exports.

Monthly cadence (~30 min):
  1. Export YC directory (batches 2021-2024, logistics/supply chain tags)
  2. Export Crunchbase CSV (Series A/Seed, logistics categories, 10-100 employees)
  3. Run: python scripts/discover_candidates.py --yc yc_export.csv --crunch crunch.csv
  4. Human review candidates_review.md → merge verified into company_candidates.json

Does not require paid APIs — uses manual CSV exports.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
CANDIDATES_PATH = BASE / "company_candidates.json"
REVIEW_PATH = BASE / "candidates_review.md"

OPS_KEYWORDS = re.compile(
    r"\b(logistics|freight|trucking|dispatch|supply\s+chain|field\s+service|"
    r"brokerage|tms|last\s+mile|warehouse|carrier)\b",
    re.I,
)


def _normalize(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (name or "").lower()).strip()


def load_existing() -> dict[str, dict]:
    if not CANDIDATES_PATH.exists():
        return {}
    data = json.loads(CANDIDATES_PATH.read_text(encoding="utf-8"))
    return {_normalize(c["name"]): c for c in data}


def parse_yc_csv(path: Path) -> list[dict]:
    """Parse YC directory export — expects Name, Batch, Tags/Industry columns."""
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row.get("Name") or row.get("name") or ""
            tags = " ".join(
                row.get(k, "") for k in ("Tags", "tags", "Industry", "industry", "One Liner", "one_liner")
            )
            batch = row.get("Batch") or row.get("batch") or ""
            if not name:
                continue
            if not OPS_KEYWORDS.search(tags) and not OPS_KEYWORDS.search(name):
                continue
            if batch and not re.search(r"20(2[1-4])", batch):
                continue
            rows.append({
                "name": name.strip(),
                "source": "yc_export",
                "domain_tags": OPS_KEYWORDS.findall(tags.lower()),
                "fit_score": 60,
                "verified": False,
                "hypothesis": "",
                "stage": "unknown",
            })
    return rows


def parse_crunchbase_csv(path: Path) -> list[dict]:
    """Parse Crunchbase CSV — expects Organization Name, Categories, Last Funding Type."""
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row.get("Organization Name") or row.get("name") or ""
            cats = row.get("Categories") or row.get("Industry") or ""
            funding = row.get("Last Funding Type") or row.get("funding_stage") or ""
            employees = row.get("Number of Employees") or row.get("employees") or ""
            founded = row.get("Founded Date") or row.get("founded") or ""
            if not name:
                continue
            if not OPS_KEYWORDS.search(cats) and not OPS_KEYWORDS.search(name):
                continue
            if funding and not re.search(r"seed|series\s*a|pre-seed", funding, re.I):
                continue
            score = 65
            if re.search(r"series\s*a", funding, re.I):
                score = 75
            rows.append({
                "name": name.strip(),
                "source": "crunchbase_csv",
                "domain_tags": OPS_KEYWORDS.findall(cats.lower()),
                "fit_score": score,
                "verified": False,
                "hypothesis": "",
                "stage": "series_a" if re.search(r"series\s*a", funding, re.I) else "seed",
                "eng_estimate": employees,
                "founded": founded[:4] if founded else None,
            })
    return rows


def write_review(new_candidates: list[dict]):
    lines = [
        "# Company Candidates Review\n",
        "Human verify: pass/fail, add hypothesis, set verified=true in company_candidates.json.\n",
        "| Name | Source | Fit | Stage | Action |\n",
        "|------|--------|-----|-------|--------|\n",
    ]
    for c in new_candidates:
        lines.append(
            f"| {c['name']} | {c['source']} | {c.get('fit_score', '?')} | "
            f"{c.get('stage', '?')} | [ ] verify |\n"
        )
    REVIEW_PATH.write_text("".join(lines), encoding="utf-8")
    print(f"Wrote {len(new_candidates)} candidates to {REVIEW_PATH}")


def main():
    parser = argparse.ArgumentParser(description="Discover ops-AI company candidates")
    parser.add_argument("--yc", type=Path, help="YC directory CSV export")
    parser.add_argument("--crunch", type=Path, help="Crunchbase CSV export")
    args = parser.parse_args()

    existing = load_existing()
    new: list[dict] = []

    if args.yc and args.yc.exists():
        for c in parse_yc_csv(args.yc):
            if _normalize(c["name"]) not in existing:
                new.append(c)
    if args.crunch and args.crunch.exists():
        for c in parse_crunchbase_csv(args.crunch):
            if _normalize(c["name"]) not in existing:
                new.append(c)

    if not new:
        print("No new candidates found (provide --yc and/or --crunch CSV paths).")
        return

    write_review(new)
    print(f"Next: review {REVIEW_PATH}, then merge verified rows into {CANDIDATES_PATH}")


if __name__ == "__main__":
    main()
