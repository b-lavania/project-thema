# Simplify CONCEPT3/index.html

Strip the index page back to a clean, readable, editorially consistent single-page portfolio. The diagnosis from the original audit still holds; this revision locks decisions, accounts for post-audit work (toolkit skills bar), and hardens the aggressive dedupe path.

## Current baseline

| Asset | Size / state |
|-------|----------------|
| [`index.html`](CONCEPT3/index.html) | ~1635 lines (~631 lines inline `<style>`) |
| [`theme.css`](CONCEPT3/theme.css) | ~1033 lines |
| [`nav.js`](CONCEPT3/nav.js) | Sticky-header scroll-spy, mobile menu, TOC scroll-spy, skill-filter toggle, section jump-to-top injection |
| Recent addition | **Skills in this section** bar (`work-skills-bar`) + per-item `.work-skill-chip` tags in Selected Work |

**Target after implementation:** ~900–1100 lines in `index.html`; inline `<style>` near zero.

---

## Audit summary

### 1. Duplicated content

| What's duplicated | Where |
|-------------------|-------|
| **Navigation links appear 3 times** | `<header class="site-header">` (sticky nav) → `<aside class="page-toc">` (sidebar TOC) → `<nav class="work-quick-nav">` (jump-to-work grid). Three mechanisms for a single-page layout. |
| **Toolkit chips appear twice** | About `tech-stack` (full vocabulary) → Selected Work `work-skills-bar` (same ~28 chips, all clickable). Per-item `.case-study-skills` tags are the right layer; the section bar should not repeat the full About dump. |
| **"Built for" logos grid** | Repeats project names already in jump-to-work, case headers, and Career Arc. Also the only clean home for live product URLs (moovez.ca, quoteperfectly.com, bvxpress.com) — migrate those before deleting. |
| **"How I Deliver" capability cards** | "Proof in:" links and example bullets duplicate jump-to-work, sidebar TOC, and case study bodies immediately below. |
| **"Systems I Work In" tag cloud** | ATS keyword dump with no narrative; overlaps About tech-stack and per-item skill tags. |

### 2. Color / contrast problems

| Issue | Details |
|-------|---------|
| **Case study headers use 3 different dark backgrounds** | `#111111`, `#2d2d2d`, `#404040` in the inline block — inconsistent hierarchy. `theme.css` softened borders but does not override these header backgrounds. |
| **Inline `<style>` fights with `theme.css`** | Inline `:root` sets `--border-color: #000`, `--text-muted: #555`, `--bg-color: #fff`; `theme.css` overrides tokens with the warm palette. Layout/case rules (fit-block, cs-grid, `.cs-header.*`, details) still live inline and must move deliberately — not blindly deleted. |
| **Career Arc + My Approach use raw inline styles** | Career timeline is `style="display:grid;..."`; principles list uses inline spans for examples. Both need CSS classes. |
| **`.metric-highlight` background `#fffbea`** | Does not match `--amber-light: #fff6e8` in `theme.css`. |
| **`.case-expand-hint`** | Uses `opacity: 0.9` on dark headers — fragile contrast; use explicit light text color instead. |

### 3. Structural bloat

- **1635 lines** for 5 expandable case studies + 6 deep-dive cards.
- **~631 lines of inline CSS** — much of the token layer is overridden by `theme.css`, but case-study layout and hero rules are still active inline. Consolidate into `theme.css` (or a dedicated `index.css` if `theme.css` would bloat).
- **Selected Work chrome stacks up**: skills bar (full toolkit) + 3-column jump nav + tier headers — more navigation than content framing.

---

## Locked decisions

No Conservative/Aggressive fork. **Aggressive dedupe** is the path.

| Decision | Rationale |
|----------|-----------|
| Remove sidebar TOC + `.page-with-toc` wrapper | Sticky header is sufficient; TOC only appears >1200px and adds a fourth nav layer. |
| Strip TOC scroll-spy from `nav.js` | Dead code once `page-toc` is removed. |
| Keep sticky header nav | Primary section navigation for desktop and mobile. |
| Remove "Systems I Work In" | Drop `#systems` from header nav and sidebar TOC (before TOC removal). |
| Collapse "How I Deliver" into Selected Work intro | Keep three themes (Pricing Architecture, Operational Intelligence, Zero-to-One) as prose in a short lede — not three proof-link cards. |
| Remove "Built for" logos grid **after URL migration** | Move live product URLs into case `cs-meta` and/or Career Arc, then delete the grid. |
| Simplify jump-to-work to a compact single-row link strip | Anchor links to tier ids and case ids — not a 3-column mini-sitemap. |
| Narrow skills bar to filter-only chips | Show only chips that have ≥1 match in `data-skills` on case/deep-dive items. About `tech-stack` remains the full vocabulary source. |
| Keep About fit-block + full tech-stack | Do not collapse toolkit into one unlabeled line; that fights the skills-mapping work. |
| Unify `.cs-header` to one dark background | `var(--text-main)`; differentiation via existing left-border accent colors (teal, amber, blue, energy). |
| Scope: index + theme + nav.js only | 6 deep-dive HTML pages unchanged. |

---

## Proposed changes

### Phase 1 — Structural deduplication (HTML)

#### [MODIFY] [`index.html`](CONCEPT3/index.html)

1. **Remove `<aside class="page-toc">` and `.page-with-toc` wrapper** — flatten to `.container` only.

2. **Simplify jump-to-work** — replace `work-quick-nav` 3-column grid with a compact single-row strip:
   - Tier anchors: `#featured-work`, `#additional-work`, `#deep-dives`
   - Case anchors: `#case-moovez`, `#case-epsilon`, `#case-bvxpress`, `#case-pricing`, `#case-netsweeper`
   - No column titles, counts, or external marks.

3. **Migrate URLs, then remove "Built for"** — before deleting `.logos-section`:
   - Add `moovez.ca`, `quoteperfectly.com`, `bvxpress.com` links to relevant case `cs-meta` lines (Moovez, BVXpress).
   - HRIS / telehealth / cyber links already exist in deep-dive cards and footer; no duplicate needed.
   - Then delete the logos grid entirely.

4. **Collapse "How I Deliver" → Selected Work intro** — remove `#how-i-deliver` section and `.capabilities-grid`. Replace with 2–3 sentences above Selected Work that name the three operating themes without "Proof in:" link lists. Update sticky nav: drop "How I work" or retarget to `#selected-work`.

5. **Narrow the skills bar** — in `work-skills-bar`, keep only chips whose `data-skill` slug appears on at least one `.skill-filter-target[data-skills]`. Remove zero-match chips (e.g. `context-engineering`, `hubspot`, `lovable`, `n8n` unless tagged on an item). Group labels stay; empty groups are removed.

6. **Remove "Systems I Work In"** — delete `#systems` section and `.systems-tags`.

7. **Fix heading hierarchy** — change the first `<h2>` under `<h1>` (sub-headline) to `<p class="subhead">`.

8. **Career Arc + My Approach** — replace inline `style=` with `.career-grid`, `.career-date`, `.career-entry`, `.principle-example` classes (defined in Phase 2).

### Phase 2 — CSS consolidation

#### [MODIFY] [`theme.css`](CONCEPT3/theme.css)

1. **Move surviving inline rules from `index.html` into `theme.css`** — fit-block, cs-grid, case-study details, capabilities (if any remain), logos (deleted), systems (deleted), page-toc (deleted). Inline block shrinks to zero or a single page-specific override file.

2. **Unify `.cs-header` backgrounds** — one `background: var(--text-main)` for all variants; keep `.cs-header.teal|amber|blue|energy` left-border accents only.

3. **Fix `.metric-highlight`** — `background: var(--amber-light)`; `border-color: var(--amber)`.

4. **Add Career Arc + My Approach classes** — `.career-grid`, `.career-date`, `.career-entry`, `.career-certs`, `.principle-example`.

5. **Fix `.case-expand-hint` contrast** — `color: rgba(255, 255, 255, 0.85)` (or similar) instead of opacity inheritance.

6. **Remove dead TOC styles** — `.page-toc`, `.page-with-toc` rules once HTML is gone.

7. **Simplify jump-nav styles** — replace 3-column `work-quick-nav` grid with single-row strip layout.

### Phase 3 — JS cleanup

#### [MODIFY] [`nav.js`](CONCEPT3/nav.js)

1. **Remove TOC scroll-spy block** — the `page-toc` / `setActiveToc` section (~lines 89–117).

2. **Verify skill filter still works** — after skills-bar markup changes, confirm `.work-skills-filter` click toggle and `.skill-dimmed` still target `.skill-filter-target` elements.

3. **Verify header scroll-spy** — after removing `#how-i-deliver` and `#systems`, update `sectionLinks` targets so `aria-current` highlights correctly.

4. **Keep** — mobile menu, back-to-top, section jump-to-top injection, skill-filter toggle.

#### [UNCHANGED] [`footer.js`](CONCEPT3/footer.js), deep-dive pages

---

## Non-goals

- Editing deep-dive HTML pages (`bvxpress-pricing.html`, `quotely-evals.html`, etc.)
- Removing or duplicating the About `tech-stack` block
- Auto-generating skill tags from case text
- Collapsing About toolkit into a single unlabeled line
- Adding new sections or net-new content beyond URL migration

---

## Verification plan

### Manual checks

- [ ] Open `index.html` before/after — visual hierarchy reads as one editorial page, not a dashboard
- [ ] All `#case-*`, `#featured-work`, `#additional-work`, `#deep-dives` anchors resolve
- [ ] Sticky header nav links match surviving sections (no dead `#how-i-deliver` or `#systems`)
- [ ] Mobile: hamburger opens/closes; nav links close menu; layout stacks cleanly
- [ ] Deep-dive links (`bvxpress-pricing.html`, etc.) and footer nav unchanged
- [ ] Live product URLs (moovez.ca, quoteperfectly.com, bvxpress.com) still reachable after Built for removal
- [ ] Skills bar: only tagged skills appear; click filters dim non-matching items; "Show all" resets
- [ ] Hash navigation: `#case-moovez` (etc.) auto-opens `<details>` via inline hash script
- [ ] WCAG AA contrast on case study headers, expand hints, and metric highlights
- [ ] No regressions in `nav.js` when `page-toc` is absent (no console errors)

### Files touched

| File | Change |
|------|--------|
| [`CONCEPT3/index.html`](CONCEPT3/index.html) | Dedupe HTML, URL migration, heading fix, inline CSS removal |
| [`CONCEPT3/theme.css`](CONCEPT3/theme.css) | Consolidated styles, header unification, new utility classes |
| [`CONCEPT3/nav.js`](CONCEPT3/nav.js) | Remove TOC spy; update header spy targets |
