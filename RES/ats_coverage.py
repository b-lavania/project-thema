"""ATS keyword coverage: normalized matching, tool aliases, JD keyword parsing."""

from __future__ import annotations

import re
from typing import Any

# Canonical display name -> normalized match keys
CANDIDATE_TOOL_ENTRIES: list[tuple[str, frozenset[str]]] = [
    ("Jira", frozenset({"jira", "jira software"})),
    ("Confluence", frozenset({"confluence"})),
    ("Notion", frozenset({"notion"})),
    ("Figma", frozenset({"figma"})),
    ("Aha!", frozenset({"aha", "aha!"})),
    ("Amplitude", frozenset({"amplitude"})),
    ("Productboard", frozenset({"productboard"})),
    ("Google Analytics", frozenset({"google analytics", "ga4", "google analytics 4"})),
    ("Pendo", frozenset({"pendo"})),
    ("Mixpanel", frozenset({"mixpanel"})),
    ("Segment", frozenset({"segment"})),
    ("Heap", frozenset({"heap"})),
    ("Hotjar", frozenset({"hotjar"})),
    ("Microsoft Clarity", frozenset({"clarity", "microsoft clarity"})),
    ("HubSpot", frozenset({"hubspot"})),
    ("ActiveCampaign", frozenset({"activecampaign"})),
    ("Zoho", frozenset({"zoho"})),
    ("Cursor", frozenset({"cursor"})),
    ("Windsurf", frozenset({"windsurf"})),
    ("Lovable", frozenset({"lovable"})),
    ("n8n", frozenset({"n8n"})),
    ("Zapier", frozenset({"zapier"})),
    ("R", frozenset({"r"})),
    ("SQL", frozenset({"sql"})),
    ("Stripe", frozenset({"stripe"})),
    ("Square", frozenset({"square"})),
    ("PyPSA", frozenset({"pypsa"})),
]

# Alias groups: if any member appears in keyword or output, treat as match
ALIAS_GROUPS: list[frozenset[str]] = [
    frozenset({"gtm", "go to market", "go-to-market", "go to market efforts"}),
    frozenset({"ai ml", "ai/ml", "machine learning", "ai powered", "ai-powered", "ai ml products"}),
    frozenset({"product management", "product manager", "product management software"}),
    frozenset({"a b testing", "ab testing", "a/b testing", "experimentation"}),
    frozenset({"user research", "discovery", "opportunity maps"}),
    frozenset({"operations research", "or engine", "or"}),
    frozenset({"media mix", "mmm", "bayesian media mix", "media mix modeling"}),
    frozenset({"go to market", "gtm", "commercialize", "launch"}),
]

STOPWORDS = frozenset({
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with",
    "by", "from", "as", "is", "are", "was", "were", "be", "been", "being", "have", "has",
    "had", "do", "does", "did", "will", "would", "should", "could", "may", "might",
    "must", "can", "this", "that", "these", "those", "it", "its", "they", "them", "their",
    "you", "your", "we", "our", "i", "my", "not", "no", "all", "any", "both", "each",
    "few", "more", "most", "other", "some", "such", "than", "too", "very", "just",
    "also", "into", "through", "during", "before", "after", "above", "below", "between",
    "under", "again", "further", "then", "once", "here", "there", "when", "where", "why",
    "how", "what", "which", "who", "whom", "while", "using", "use", "used", "like", "etc",
    "well", "versed", "latest", "required", "experience", "demonstrated", "success",
    "interest", "should", "have", "lead", "full", "major", "new", "products", "software",
})

SALIENT_TOKEN_THRESHOLD = 0.42
_NUMBERED_LINE = re.compile(r"^\s*(?:\d+[\.\)]\s*|-\s*|•\s*)(.+)$", re.I)


def normalize_for_match(text: str) -> str:
    if not text:
        return ""
    t = text.lower()
    t = t.replace("/", " ").replace("-", " ").replace("_", " ")
    t = re.sub(r"[^\w\s+#]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def _expand_aliases(normalized_term: str) -> set[str]:
    variants = {normalized_term}
    for group in ALIAS_GROUPS:
        if normalized_term in group:
            variants |= set(group)
        else:
            for member in group:
                if member in normalized_term or normalized_term in member:
                    variants |= set(group)
                    break
    return variants


def match_keyword(keyword: str, normalized_output: str) -> bool:
    """True if keyword (or alias) appears in normalized resume text."""
    kw = normalize_for_match(keyword)
    if not kw or not normalized_output:
        return False
    for variant in _expand_aliases(kw):
        if not variant:
            continue
        if variant in normalized_output:
            return True
        if len(variant) >= 2 and re.search(
            r"\b" + re.escape(variant) + r"\b", normalized_output
        ):
            return True
    return False


def resolve_candidate_tool(tool: str) -> str | None:
    """Return canonical display name if tool is in candidate vocabulary."""
    norm = normalize_for_match(tool)
    if not norm:
        return None
    for display, keys in CANDIDATE_TOOL_ENTRIES:
        if norm in keys:
            return display
        for key in keys:
            if match_keyword(key, norm) or match_keyword(norm, key):
                return display
    return None


def jd_tools_supported(jd_tools: list[str]) -> list[str]:
    """JD tools that map to candidate vocabulary (deduped, display spelling)."""
    seen: set[str] = set()
    out: list[str] = []
    for raw in jd_tools:
        display = resolve_candidate_tool(raw)
        if display and display not in seen:
            seen.add(display)
            out.append(display)
    return out


def _parse_numbered_lines(block: str) -> list[str]:
    terms: list[str] = []
    for line in block.split("\n"):
        line = line.strip()
        if not line:
            continue
        m = _NUMBERED_LINE.match(line)
        if m:
            terms.append(m.group(1).strip())
        elif line and not line.endswith(":"):
            terms.append(line)
    return terms


def parse_extracted_keywords(extracted_text: str) -> dict[str, list[str]]:
    """Split LLM extract into duties, requirements, tools lists."""
    text = extracted_text or ""
    duties: list[str] = []
    requirements: list[str] = []
    tools: list[str] = []

    parts = re.split(
        r"(?i)(DUTIES|REQUIREMENTS|TOOLS_AND_KEYWORDS)\s*:\s*",
        text,
    )
    if len(parts) >= 2:
        i = 1
        while i + 1 < len(parts):
            label = parts[i].strip().upper()
            content = parts[i + 1]
            items = _parse_numbered_lines(content)
            if label == "DUTIES":
                duties = items
            elif label == "REQUIREMENTS":
                requirements = items
            elif label.startswith("TOOLS"):
                tools = items
            i += 2

    if not duties and re.search(r"(?i)DUTIES\s*:", text):
        chunk = re.split(r"(?i)REQUIREMENTS\s*:", text)[0]
        duties = _parse_numbered_lines(re.split(r"(?i)DUTIES\s*:", chunk)[-1])
    if not requirements and re.search(r"(?i)REQUIREMENTS\s*:", text):
        req_chunk = re.split(r"(?i)REQUIREMENTS\s*:", text, maxsplit=1)[-1]
        req_chunk = re.split(r"(?i)TOOLS_AND_KEYWORDS\s*:", req_chunk)[0]
        requirements = _parse_numbered_lines(req_chunk)
    if not tools:
        m = re.search(r"(?i)TOOLS_AND_KEYWORDS\s*:\s*(.*)", text, re.DOTALL)
        if m:
            tools = _parse_numbered_lines(m.group(1))

    return {"duties": duties, "requirements": requirements, "tools": tools}


def _extract_inline_tools_from_sentence(sentence: str) -> list[str]:
    """Pull tool names from '(like Notion, Aha!, ...)' style lists."""
    tools: list[str] = []
    for m in re.finditer(r"\(like\s+([^)]+)\)", sentence, re.I):
        chunk = m.group(1)
        chunk = re.sub(r"\s*etc\.?\s*$", "", chunk, flags=re.I)
        for part in re.split(r",\s*|\s+and\s+", chunk):
            part = part.strip().strip(".")
            if part and len(part) > 1:
                tools.append(part)
    return tools


def _salient_tokens(text: str) -> list[str]:
    norm = normalize_for_match(text)
    tokens = []
    for w in norm.split():
        if w in STOPWORDS:
            continue
        if len(w) <= 2 and w not in {"ai", "ml", "or", "pm"}:
            continue
        tokens.append(w)
    return tokens


def _sentence_covered(term: str, normalized_output: str) -> bool:
    """Duty/requirement line: tools in parentheses + salient token overlap + n-grams."""
    if match_keyword(term, normalized_output):
        return True

    for tool in _extract_inline_tools_from_sentence(term):
        if match_keyword(tool, normalized_output):
            return True

    # Standalone tool names mentioned in the sentence (JIRA, etc.)
    for display, keys in CANDIDATE_TOOL_ENTRIES:
        for key in keys:
            if key in normalize_for_match(term) and match_keyword(key, normalized_output):
                return True

    tokens = _salient_tokens(term)
    if not tokens:
        return False

    hits = sum(1 for t in tokens if match_keyword(t, normalized_output))
    if hits / len(tokens) >= SALIENT_TOKEN_THRESHOLD:
        return True

    # n-gram fallback (2-3 words, punctuation-safe)
    words = normalize_for_match(term).split()
    if len(words) >= 3:
        for i in range(len(words) - 2):
            tri = " ".join(words[i : i + 3])
            if tri in normalized_output:
                return True
    if len(words) >= 2:
        for i in range(len(words) - 1):
            bi = " ".join(words[i : i + 2])
            if bi in normalized_output:
                return True
    return False


# fix typo SALIENTENT_THRESHOLD - I introduced a bug, remove that line


def check_keyword_coverage(
    extracted_keywords_text: str,
    combined_output: str,
) -> tuple[list[str], list[str], float, dict[str, Any]]:
    """
    Returns (found, missing, coverage_pct, meta).
    meta includes tools_found, tools_missing, duties_found, etc.
    """
    parsed = parse_extracted_keywords(extracted_keywords_text)
    norm_out = normalize_for_match(combined_output)

    items: list[tuple[str, str]] = []
    for d in parsed["duties"]:
        items.append((d, "sentence"))
    for r in parsed["requirements"]:
        items.append((r, "sentence"))
    for t in parsed["tools"]:
        items.append((t, "tool"))

    found: list[str] = []
    missing: list[str] = []
    tools_found: list[str] = []
    tools_missing: list[str] = []

    for term, kind in items:
        if kind == "tool":
            if match_keyword(term, norm_out):
                found.append(term)
                tools_found.append(term)
            else:
                missing.append(term)
                tools_missing.append(term)
        else:
            if _sentence_covered(term, norm_out):
                found.append(term)
            else:
                missing.append(term)

    # Also score tools embedded in requirement sentences individually
    for term, kind in items:
        if kind != "sentence":
            continue
        for tool in _extract_inline_tools_from_sentence(term):
            if match_keyword(tool, norm_out):
                if tool not in tools_found:
                    tools_found.append(tool)
            elif tool not in tools_missing:
                tools_missing.append(tool)

    coverage = len(found) / len(items) if items else 0.0
    meta = {
        "tools_found": tools_found,
        "tools_missing": tools_missing,
        "parsed": parsed,
    }
    return found, missing, coverage, meta
