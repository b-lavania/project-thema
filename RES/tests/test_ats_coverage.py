"""Tests for ATS keyword coverage matching."""

import unittest

from ats_coverage import (
    check_keyword_coverage,
    jd_tools_supported,
    match_keyword,
    normalize_for_match,
    parse_extracted_keywords,
)


SAMPLE_RESUME = """
Fixes GenAI product launches by defining measurement loops before scale.
Discovery: Runs opportunity maps and tree tests before roadmap bets.
Build: Ships AI-powered logistics tools with OR engines and Jira-backed release tracking.
Measure: Instruments funnels in Segment, Mixpanel, Heap, and Pendo for cohort decisions.
Commercialize: Leads full GTM and go-to-market for major releases using Aha! roadmaps.
Designs prototypes in Figma; specs in Notion; validates with Amplitude and Google Analytics.
Productboard used for backlog prioritization alongside Confluence.
"""

USER_JD_EXTRACT = """
DUTIES:
1. Should have demonstrated success or interest in launching AI-powered software products or integrating AI/ML into product operations.
2. Lead full GTM go-to-market efforts for major releases and new products.
3. Experience with JIRA required and well versed using latest Product Management software (like Notion, Aha!, Amplitude, Productboard, Figma, Google Analytics, Pendo, etc.).

REQUIREMENTS:
1. 5+ years PM experience
2. B2B SaaS background

TOOLS_AND_KEYWORDS:
- JIRA
- Notion
- Aha!
- Amplitude
- Productboard
- Figma
- Google Analytics
- Pendo
- GTM
- AI/ML
- AI-powered software
"""


class TestAtsCoverage(unittest.TestCase):
    def test_normalize_strips_punctuation(self):
        self.assertEqual(
            normalize_for_match("Google Analytics,"),
            "google analytics",
        )

    def test_match_single_token_jira(self):
        norm = normalize_for_match(SAMPLE_RESUME)
        self.assertTrue(match_keyword("JIRA", norm))

    def test_match_gtm_alias(self):
        norm = normalize_for_match(SAMPLE_RESUME)
        self.assertTrue(match_keyword("go-to-market", norm))

    def test_jd_tools_supported(self):
        tools = ["JIRA", "Figma", "Salesforce"]
        supported = jd_tools_supported(tools)
        self.assertIn("Jira", supported)
        self.assertIn("Figma", supported)
        self.assertNotIn("Salesforce", supported)

    def test_user_three_duties_coverage(self):
        found, missing, coverage, meta = check_keyword_coverage(
            USER_JD_EXTRACT, SAMPLE_RESUME
        )
        self.assertGreaterEqual(coverage, 0.6)
        self.assertTrue(
            any("ai" in f.lower() or "gtm" in f.lower() for f in found),
            f"expected AI or GTM duty found, got {found}",
        )
        for tool in ("Jira", "Notion", "Figma", "Pendo"):
            self.assertTrue(
                match_keyword(tool, normalize_for_match(SAMPLE_RESUME)),
                f"{tool} should be in resume sample",
            )
        self.assertGreater(len(meta["tools_found"]), 0)

    def test_parse_tools_section(self):
        parsed = parse_extracted_keywords(USER_JD_EXTRACT)
        self.assertIn("JIRA", parsed["tools"])
        self.assertEqual(len(parsed["duties"]), 3)


if __name__ == "__main__":
    unittest.main()
