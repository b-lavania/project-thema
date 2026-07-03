"""CLI entry point: scrape all configured sources and persist leads.

Two parallel paths:
  Google Jobs — SerpAPI primary, SearchAPI.io fallback (--mode)
  Direct ATS  — Greenhouse + Lever + Ashby + SmartRecruiters

Usage:
    python -m scraper.run                            # all enabled sources
    python -m scraper.run --source greenhouse         # single source
    python -m scraper.run --lane ops_ai               # ops-AI lane (domain queries, fit gate)
    python -m scraper.run --lane ops_ai --allowlist-only  # ATS only, verified companies
    python -m scraper.run --discover                  # search + discover new boards from results
    python -m scraper.run --discover-boards           # scoped ops-AI board discovery
    python -m scraper.run --dry-run                   # print, don't save
"""

from __future__ import annotations

import argparse
import sys

from .board_apis import (
    scrape_greenhouse,
    scrape_lever,
    scrape_ashby,
    scrape_smartrecruiters,
)
from .company_pages import scrape_career_pages
from .company_fit import filter_by_fit
from .config import load_profile, load_target_companies, generate_search_queries
from .board_discovery import discover_boards, merge_into_targets
from .discover import extract_board_tokens, scrape_discovered_boards
from .env import validate_api_keys
from .filter import filter_leads
from .leads import append_leads
from .search import run_search_queries


def _make_args(max_results: int = 10, mode: str = "auto", discover: bool = False):
    """Build a simple namespace object for run_google_jobs."""
    return argparse.Namespace(max_results=max_results, mode=mode, discover=discover)


def run_google_jobs(profile: dict, args) -> list:
    """Google Jobs path: domain queries when lane=ops_ai, else role×location."""
    queries = generate_search_queries(profile)
    leads = run_search_queries(queries, max_results=args.max_results, mode=args.mode)
    print(f"  search: {len(leads)} jobs ({len(queries)} queries)")
    return leads


def run_direct_ats(companies: dict) -> list:
    """Direct ATS path: scrapes Greenhouse + Lever + Ashby + SmartRecruiters."""
    all_leads = []

    ats_sources = {
        "greenhouse": (scrape_greenhouse, companies.get("greenhouse", [])),
        "lever": (scrape_lever, companies.get("lever", [])),
        "ashby": (scrape_ashby, companies.get("ashby", [])),
        "smartrecruiters": (scrape_smartrecruiters, companies.get("smartrecruiters", [])),
    }

    for name, (fn, items) in ats_sources.items():
        for item in items:
            try:
                leads = fn(item)
                all_leads.extend(leads)
                print(f"  {name}/{item}: {len(leads)} jobs")
            except Exception as e:
                print(f"  {name}/{item}: error — {e}", file=sys.stderr)

    if companies.get("career_pages"):
        for site in companies["career_pages"]:
            try:
                leads = scrape_career_pages([site])
                all_leads.extend(leads)
                print(f"  career_page/{site}: {len(leads)} jobs")
            except Exception as e:
                print(f"  career_page/{site}: error — {e}", file=sys.stderr)

    return all_leads


def _apply_filters(
    all_leads: list,
    profile: dict,
    *,
    lane: str | None,
    allowlist_only: bool,
) -> list:
    """Title filter then company fit gate."""
    filtered = filter_leads(
        all_leads,
        exclude_senior=True,
        profile_keywords=profile.get("keywords"),
        exclude_titles=profile.get("exclude_titles"),
        require_product_adjacent=True,
    )
    title_skipped = len(all_leads) - len(filtered)
    if title_skipped:
        print(f"  title filter: skipped {title_skipped}")

    use_lane = lane == "ops_ai" or profile.get("lane") == "ops_ai"
    if use_lane:
        filtered, rejected = filter_by_fit(
            filtered,
            allowlist_only=allowlist_only,
        )
        if rejected:
            print(f"  fit gate: skipped {len(rejected)} (allowlist_only={allowlist_only})")
    return filtered


def main():
    parser = argparse.ArgumentParser(description="Scrape job listings.")
    parser.add_argument(
        "--source",
        choices=["greenhouse", "lever", "ashby", "smartrecruiters", "career_pages", "search", "all"],
        default="all",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print results without saving")
    parser.add_argument("--discover", action="store_true", help="Discover board tokens from search URLs")
    parser.add_argument("--max-results", "-n", type=int, default=10, help="Max results per query")
    parser.add_argument("--mode", choices=["api", "scrape", "auto"], default="auto")
    parser.add_argument("--discover-boards", action="store_true", help="Scoped ops-AI board discovery")
    parser.add_argument("--lane", choices=["ops_ai", "generic"], default=None,
                        help="Search lane (ops_ai uses domain_queries + fit gate)")
    parser.add_argument("--allowlist-only", action="store_true",
                        help="Only save leads from verified company_candidates")
    args = parser.parse_args()

    if args.mode != "scrape":
        validate_api_keys()

    if args.discover_boards:
        print("  [discover] Scoped ops-AI board discovery...")
        discovered = discover_boards(scoped=True)
        merge_into_targets(discovered)
        return

    profile = load_profile()
    companies = load_target_companies()
    lane = args.lane or profile.get("lane")

    all_leads = []

    # ATS-first when ops_ai + allowlist-only (Tuesday weekly cadence)
    if args.allowlist_only or (lane == "ops_ai" and args.source == "all"):
        ats_sources = ["greenhouse", "lever", "ashby", "smartrecruiters", "career_pages"]
        for src in ats_sources:
            ats = {src: companies.get(src, [])}
            if src == "career_pages":
                ats["career_pages"] = companies.get("career_pages", [])
            all_leads.extend(run_direct_ats(ats))
        if args.source == "all" and not args.allowlist_only:
            all_leads.extend(run_google_jobs(profile, args))
    else:
        sources = [args.source] if args.source != "all" else [
            "greenhouse", "lever", "ashby", "smartrecruiters", "career_pages", "search",
        ]
        for src in sources:
            if src == "search":
                all_leads.extend(run_google_jobs(profile, args))
            else:
                ats = {src: companies.get(src, [])}
                if src == "career_pages":
                    ats["career_pages"] = companies.get("career_pages", [])
                all_leads.extend(run_direct_ats(ats))

    if args.discover:
        discovered = extract_board_tokens(all_leads)
        total_tokens = sum(len(v) for v in discovered.values())
        if total_tokens:
            print(f"\n  Discovered {total_tokens} board tokens from search results:")
            known = set()
            for source in ("greenhouse", "lever", "ashby"):
                known.update(companies.get(source, []))
            new_leads = scrape_discovered_boards(discovered, known)
            all_leads.extend(new_leads)

    filtered = _apply_filters(
        all_leads,
        profile,
        lane=lane,
        allowlist_only=args.allowlist_only,
    )
    skipped = len(all_leads) - len(filtered)

    if not filtered:
        print(f"No new jobs found ({skipped} skipped).")
        return

    if args.dry_run:
        for l in filtered:
            print(f"  [{l.source}] {l.title} @ {l.company} — {l.url}")
        print(f"\nTotal: {len(filtered)} jobs (skipped {skipped}, dry run)")
        return

    count = append_leads(filtered)
    print(f"\nSaved {count} new leads ({skipped} skipped)")


if __name__ == "__main__":
    main()
