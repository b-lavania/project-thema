"""Tests for JD-tailored How I Work wiring (no LLM)."""

import unittest
from pathlib import Path

from generator import _extract_how_i_work_source, load_prompt


RES_ROOT = Path(__file__).resolve().parent.parent
MASTER = (RES_ROOT / "data" / "master_context.md").read_text(encoding="utf-8")


class TestHowIWorkSourcePalettes(unittest.TestCase):
    def test_generation_source_has_palettes_and_n8n(self):
        src = _extract_how_i_work_source(MASTER)
        self.assertIn("Industries", src)
        self.assertIn("Product categories", src)
        self.assertIn("n8n", src)
        self.assertIn("Zapier", src)
        self.assertIn("TMS/WMS", src)
        self.assertIn("Skills-only familiarity", src)

    def test_skills_prompt_has_jd_context_placeholder(self):
        text = (RES_ROOT / "prompts" / "skills_statements.md").read_text(encoding="utf-8")
        self.assertIn("{jd_context}", text)
        self.assertIn("JD CONTEXT MIRRORING", text)
        self.assertIn("SKILLS-ONLY TOOLS", text)

    def test_load_prompt_accepts_jd_context(self):
        sys_p, usr_p = load_prompt(
            "skills_statements.md",
            track_line="",
            voice_line="",
            ANTI_FLUFF="",
            target_role="PM",
            jd_duties="1. Ship pricing tools",
            jd_context="DUTIES:\n1. Logistics TMS\nREQUIREMENTS:\n1. Segment",
            narrative_brief="",
            how_i_work_source="Discover lane",
            master_context="",
            required_tools="",
        )
        self.assertIn("Logistics TMS", usr_p)
        self.assertIn("jd context mirroring", sys_p.lower())


if __name__ == "__main__":
    unittest.main()
