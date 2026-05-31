"""Tests for Quick Take dash and metric sanitization."""

import re
import unittest
from pathlib import Path

from generator import (
    normalize_quick_take_text,
    quick_take_has_metric,
)


class TestNormalizeQuickTake(unittest.TestCase):
    def test_strips_em_dash_and_metrics(self):
        raw = (
            "PM: Building tools for marketplaces\n"
            "Fixes broken workflows—cut manual quoting from an hour to 3 minutes with 85% adoption."
        )
        out = normalize_quick_take_text(raw)
        self.assertNotIn("—", out)
        self.assertNotIn("85%", out)
        self.assertNotIn("3 minutes", out.lower())
        self.assertFalse(quick_take_has_metric(out))

    def test_preserves_compound_hyphens(self):
        raw = "PM: GenAI-powered pricing for B2B SaaS\nFixes quote-to-cash by redesigning pricing engines."
        out = normalize_quick_take_text(raw)
        self.assertIn("GenAI-powered", out)
        self.assertIn("quote-to-cash", out)

    def test_clause_break_hyphen_becomes_comma(self):
        raw = "PM: Hook for AI workflows\nFixes adoption gaps - focuses on outcome owners before scale."
        out = normalize_quick_take_text(raw)
        self.assertNotRegex(out, r"(?<!\w)\s-\s(?!\w)")

    def test_strips_dollar_and_multiplier(self):
        raw = "PM: Pricing for marketplaces\nDelivered $500k GMV lift and 20x quoting speed."
        out = normalize_quick_take_text(raw)
        self.assertFalse(quick_take_has_metric(out))
        self.assertNotIn("$500", out)
        self.assertNotIn("20x", out.lower())


class TestPromptAudit(unittest.TestCase):
  PROMPTS = Path(__file__).resolve().parent.parent / "prompts"

  def test_mission_statement_forbids_metric_echo(self):
      text = (self.PROMPTS / "mission_statement.md").read_text(encoding="utf-8")
      self.assertNotIn("one metric max", text.lower())
      self.assertIn("ZERO METRICS", text)
      self.assertIn("PROOF_SNIPPET", text)
      self.assertIn("Do not quote them in Quick Take", text)

  def test_profile_lint_no_metric_allowance(self):
      text = (self.PROMPTS / "profile_lint.md").read_text(encoding="utf-8")
      self.assertNotIn("one metric max", text.lower())
      self.assertIn("no metrics", text.lower())

  def test_mission_structure_examples_no_em_dash(self):
      text = (self.PROMPTS / "mission_statement.md").read_text(encoding="utf-8")
      structure = text.split("STRUCTURE")[1].split("SELF-CRITIQUE")[0]
      self.assertNotIn("—", structure)


if __name__ == "__main__":
    unittest.main()
