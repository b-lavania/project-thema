"""
app.py — LinkedIn Post Agent (consumable queue)

Flow:
1. Open page -> app loads the queue from GitHub. If the queue is below
   MIN_QUEUE_SIZE, it auto-tops-up with fresh articles (no button).
2. You always see the HEAD of the queue.
3. "Skip" removes the head (you don't want to write about it) and shows the next.
4. Write your take -> generate -> copy the post -> "Done" removes the head.
Items leave the queue ONLY by your action. Removals persist to GitHub.

Persistence: requires GITHUB_TOKEN + GITHUB_OWNER + GITHUB_REPO in Streamlit
secrets. Without them, skips/done work for the session only and reset on reload
(the app warns you).
"""

import json
import os
import sys
import base64
from datetime import datetime, timezone
from pathlib import Path

import requests
import streamlit as st

# ── Password Gate ─────────────────────────────────────────────────────────────

def check_password():
    def password_entered():
        st.session_state["authenticated"] = (
            st.session_state["password"] == st.secrets["APP_PASSWORD"]
        )
    if "authenticated" not in st.session_state:
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        st.stop()
    elif not st.session_state["authenticated"]:
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        st.error("Incorrect password")
        st.stop()

check_password()

sys.path.insert(0, str(Path(__file__).parent / "agent"))
from generate_post import generate_posts, generate_summary, generate_quick_post
from fetch_articles import topup_queue, prune_stale, MIN_QUEUE_SIZE

# ── Config ────────────────────────────────────────────────────────────────────

GITHUB_OWNER  = os.environ.get("GITHUB_OWNER", "")
GITHUB_REPO   = os.environ.get("GITHUB_REPO", "")
GITHUB_BRANCH = os.environ.get("GITHUB_BRANCH", "main")
GITHUB_TOKEN  = os.environ.get("GITHUB_TOKEN", "")
PERSIST_ENABLED = bool(GITHUB_TOKEN and GITHUB_OWNER and GITHUB_REPO)

st.set_page_config(page_title="Post Agent", page_icon="✍️",
                   layout="centered", initial_sidebar_state="expanded")

# ── Content Calendar (Sidebar) ───────────────────────────────────────────────────

with st.sidebar:
    st.markdown("### 📅 Content Calendar")
    st.caption("12-week ops-AI LinkedIn strategy")

    calendar_data = {
        "Weeks 1-4": "Problem Reframing Foundation",
        "Weeks 5-8": "Depth & Credibility",
        "Weeks 9-12": "Outreach & Conversion"
    }

    for week_range, focus in calendar_data.items():
        st.markdown(f"**{week_range}**")
        st.caption(focus)
        st.divider()

    st.markdown("### 📊 Post Pillars")
    pillars = {
        "Problem Reframing (40%)": "Find the real problem",
        "AI in Operations (30%)": "Production AI experience",
        "Metrics & Measurement (20%)": "Outcome-focused",
        "Industry Analysis (10%)": "Ecosystem credibility"
    }

    for pillar, desc in pillars.items():
        st.markdown(f"**{pillar}**")
        st.caption(desc)

    st.divider()
    st.markdown("### 📈 Metrics")
    if st.session_state.state and "metrics" in st.session_state.state:
        metrics = st.session_state.state["metrics"]
        st.metric("Posts Generated", metrics.get("posts_generated", 0))
        st.metric("Quick Posts", metrics.get("quick_posts", 0))
        st.metric("Article Posts", metrics.get("article_posts", 0))
    else:
        st.caption("No metrics yet")

# ── GitHub state I/O (single source of truth) ─────────────────────────────────

def pull_state_with_sha():
    """Fetch latest state.json + its blob SHA via the GitHub API (freshest read).
    Falls back to raw if no token. Returns (state_dict, sha_or_None)."""
    if PERSIST_ENABLED:
        url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/contents/state.json"
        headers = {"Authorization": f"token {GITHUB_TOKEN}",
                   "Accept": "application/vnd.github.v3+json"}
        try:
            r = requests.get(url, headers=headers, params={"ref": GITHUB_BRANCH}, timeout=10)
            if r.status_code == 200:
                data = r.json()
                content = base64.b64decode(data["content"]).decode()
                state = json.loads(content)
                # Ensure metrics exists
                if "metrics" not in state:
                    state["metrics"] = {"posts_generated": 0, "quick_posts": 0, "article_posts": 0}
                return state, data["sha"]
        except Exception:
            pass
    # Fallback: raw (no sha, read-only)
    try:
        raw = f"https://raw.githubusercontent.com/{GITHUB_OWNER}/{GITHUB_REPO}/{GITHUB_BRANCH}/state.json"
        r = requests.get(raw, params={"t": os.urandom(4).hex()}, timeout=10)
        if r.status_code == 200:
            state = r.json()
            if "metrics" not in state:
                state["metrics"] = {"posts_generated": 0, "quick_posts": 0, "article_posts": 0}
            return state, None
    except Exception:
        pass
    return {"queue": [], "history": [], "generated_at": None, "metrics": {"posts_generated": 0, "quick_posts": 0, "article_posts": 0}}, None

def put_state(state, sha):
    if not PERSIST_ENABLED:
        return False
    url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/contents/state.json"
    headers = {"Authorization": f"token {GITHUB_TOKEN}",
               "Accept": "application/vnd.github.v3+json"}
    if not sha:  # ensure we have the latest sha before writing
        try:
            sha = requests.get(url, headers=headers, params={"ref": GITHUB_BRANCH},
                               timeout=10).json().get("sha", "")
        except Exception:
            sha = ""
    content = base64.b64encode(json.dumps(state, indent=2).encode()).decode()
    body = {"message": "Update queue [skip ci]", "content": content,
            "branch": GITHUB_BRANCH}
    if sha:
        body["sha"] = sha
    try:
        r = requests.put(url, headers=headers, json=body, timeout=15)
        return r.status_code in (200, 201)
    except Exception:
        return False

def commit_mutation(mutate_fn):
    """Read-modify-write against the freshest GitHub state, so concurrent cron
    writes don't clobber user actions. mutate_fn(state) -> new_state."""
    state, sha = pull_state_with_sha()
    new_state = mutate_fn(state)
    ok = put_state(new_state, sha) if PERSIST_ENABLED else False
    st.session_state.state = new_state  # session always reflects the change
    return ok

# ── Queue operations ──────────────────────────────────────────────────────────

def ensure_fresh(state):
    """Guarantee the queue holds only in-window articles, and refill when low.
    Pruning is cheap (no network) and runs every load; fetching only happens
    when the pruned queue drops below MIN_QUEUE_SIZE. Returns (state, changed)."""
    before = [a["url"] for a in state.get("queue", [])]

    # 1. Always drop anything that has aged out (cheap, no network).
    state["queue"] = prune_stale(state.get("queue", []))

    # 2. Only hit the network if we're actually low.
    if len(state["queue"]) < MIN_QUEUE_SIZE:
        state["queue"], state["history"] = topup_queue(state["queue"], state.get("history", []))

    after = [a["url"] for a in state["queue"]]
    if after != before:
        state["generated_at"] = datetime.now(timezone.utc).isoformat()
        return state, True
    return state, False

def remove_head(reason="skip"):
    """Drop the current head, top up if needed, persist."""
    head_id = st.session_state.state["queue"][0]["id"] if st.session_state.state["queue"] else None

    def _mutate(state):
        q = state.get("queue", [])
        if q and head_id and q[0]["id"] == head_id:
            q = q[1:]
        elif q:
            q = q[1:]
        state["queue"] = q
        # self-heal: refill in the same action if we dropped below threshold
        state["queue"], state["history"] = topup_queue(q, state.get("history", []))
        state["generated_at"] = datetime.now(timezone.utc).isoformat()
        return state

    ok = commit_mutation(_mutate)
    reset_post_state()
    if PERSIST_ENABLED and not ok:
        st.session_state.persist_error = True

# ── Session state ─────────────────────────────────────────────────────────────

for key, default in [
    ("linkedin_draft", ""), ("facebook_draft", ""), ("generated", False),
    ("ai_summary", ""), ("summary_loaded", False), ("state", None),
    ("persist_error", False), ("mode", "article"),  # "article" or "quick"
    ("template_type", "framework"), ("company_context", ""),
]:
    if key not in st.session_state:
        st.session_state[key] = default

def reset_post_state():
    st.session_state.summary_loaded = False
    st.session_state.ai_summary = ""
    st.session_state.generated = False
    st.session_state.linkedin_draft = ""
    st.session_state.facebook_draft = ""

# ── Styles ────────────────────────────────────────────────────────────────────

st.markdown("""
<style>
    .main { max-width: 720px; margin: 0 auto; }
    .article-card { background:#f8f9fa; border-left:4px solid #0a66c2;
        padding:16px 20px; border-radius:4px; margin-bottom:16px; }
    .source-tag { font-size:12px; color:#666; text-transform:uppercase;
        letter-spacing:0.5px; margin-bottom:6px; }
    .step-label { font-size:11px; font-weight:700; color:#0a66c2;
        text-transform:uppercase; letter-spacing:1px; margin-bottom:4px; }
    .summary-box { background:#eef4fb; border-radius:6px; padding:14px 18px;
        margin-bottom:20px; font-size:14px; line-height:1.7; color:#333; }
</style>
""", unsafe_allow_html=True)

# ── Boot ──────────────────────────────────────────────────────────────────────

st.title("✍️ Post Agent")

# Mode selector
col1, col2 = st.columns([1, 1])
with col1:
    mode = st.radio("Mode", ["📰 Article-based", "⚡ Quick Post"], horizontal=True, label_visibility="collapsed")
    st.session_state.mode = "article" if mode == "📰 Article-based" else "quick"

# ── Quick Post Mode ────────────────────────────────────────────────────────────

if st.session_state.mode == "quick":
    st.divider()
    st.markdown("### ⚡ Quick Post Generator")
    st.caption("Generate posts without an article using templates")

    # Load templates
    import json
    templates_path = Path(__file__).parent / "config" / "post_templates.json"
    with open(templates_path) as f:
        templates_data = json.load(f)
    template_options = {k: v["name"] for k, v in templates_data["templates"].items()}

    # Template selection
    st.session_state.template_type = st.selectbox(
        "Post Type",
        options=list(template_options.keys()),
        format_func=lambda x: template_options[x],
        index=0
    )

    # Load target companies
    companies_path = Path(__file__).parent / "config" / "target_companies.json"
    with open(companies_path) as f:
        companies_data = json.load(f)
    company_list = [(c["name"], f"{c['name']} - {c['sub_vertical']}") for c in companies_data["batch_1"]]

    # Company selection (optional, auto-fills context)
    selected_company = st.selectbox(
        "Target Company (optional)",
        options=[("", "None")] + company_list,
        format_func=lambda x: x[1] if isinstance(x, tuple) else x,
        index=0
    )

    # Auto-fill company context if selected
    if selected_company:
        company_name = selected_company[0]
        company_info = next((c for c in companies_data["batch_1"] if c["name"] == company_name), None)
        if company_info:
            st.session_state.company_context = f"{company_info['name']} - {company_info['sub_vertical']}: {company_info['bottleneck_hypothesis']}"

    # Manual company context override
    st.session_state.company_context = st.text_input(
        "Company Context (editable)",
        placeholder="e.g., Greenscreens.ai - dynamic freight pricing",
        value=st.session_state.company_context
    )

    st.divider()

    # Raw idea input
    st.markdown('<div class="step-label">Your Idea</div>', unsafe_allow_html=True)
    st.caption("Bullet points or prose — what do you want to say?")
    raw_idea = st.text_area(
        "Your idea",
        placeholder="- Brokers price on gut feel\n- Real bottleneck is decision latency on lane-level margin\n- Need structured decision support",
        height=140,
        label_visibility="collapsed",
    )

    generate_clicked = st.button("Generate Posts →", type="primary", disabled=not raw_idea.strip())

    # Generation
    if generate_clicked and raw_idea.strip():
        with st.spinner("Writing your posts..."):
            try:
                posts = generate_quick_post(
                    st.session_state.template_type,
                    raw_idea,
                    st.session_state.company_context
                )
                st.session_state.linkedin_draft = posts.get("linkedin", "")
                st.session_state.facebook_draft = posts.get("facebook", "")
                st.session_state.generated = True

                # Update metrics
                if PERSIST_ENABLED:
                    def _update_metrics(s):
                        if "metrics" not in s:
                            s["metrics"] = {"posts_generated": 0, "quick_posts": 0, "article_posts": 0}
                        s["metrics"]["posts_generated"] += 1
                        s["metrics"]["quick_posts"] += 1
                        return s
                    commit_mutation(_update_metrics)
            except Exception as e:
                st.error(f"Generation failed: {e}")
                st.stop()

    # Review and edit
    if st.session_state.generated:
        st.divider()
        st.markdown('<div class="step-label">Review & Edit</div>', unsafe_allow_html=True)
        tab_li, tab_fb = st.tabs(["🔵 LinkedIn", "🔷 Facebook"])
        with tab_li:
            st.session_state.linkedin_draft = st.text_area(
                "LinkedIn Post", value=st.session_state.linkedin_draft,
                height=300, label_visibility="collapsed")
            st.caption(f"{len(st.session_state.linkedin_draft.split())} words · "
                       f"{len(st.session_state.linkedin_draft)} chars")
        with tab_fb:
            st.session_state.facebook_draft = st.text_area(
                "Facebook Post", value=st.session_state.facebook_draft,
                height=300, label_visibility="collapsed")
            st.caption(f"{len(st.session_state.facebook_draft.split())} words · "
                       f"{len(st.session_state.facebook_draft)} chars")

        st.divider()
        st.markdown('<div class="step-label">Copy & Post</div>', unsafe_allow_html=True)
        st.caption("Copy the text above into LinkedIn/Facebook.")
        p1, p2 = st.columns(2)
        with p1:
            st.link_button("🔵 LinkedIn", "https://www.linkedin.com/feed/", use_container_width=True)
        with p2:
            st.link_button("🔷 Facebook", "https://www.facebook.com/", use_container_width=True)

        if st.button("✅ Done — Clear", use_container_width=True):
            reset_post_state()
            st.rerun()

    st.stop()  # Don't show article queue in quick mode

if not PERSIST_ENABLED:
    st.warning("⚠️ GitHub persistence is OFF (set GITHUB_TOKEN, GITHUB_OWNER, "
               "GITHUB_REPO in Streamlit secrets). Skips work for this session "
               "only and will reset when you reload.")

# Load + auto-stock once per session load
if st.session_state.state is None:
    with st.spinner("Loading your queue..."):
        state, sha = pull_state_with_sha()
        state, changed = ensure_fresh(state)
        if changed and PERSIST_ENABLED:
            put_state(state, sha)
        st.session_state.state = state

state = st.session_state.state
queue = state.get("queue", [])

if st.session_state.persist_error:
    st.error("Last save to GitHub failed. Check the token's `repo` scope. "
             "Your change applied for this session only.")

# Empty queue (nothing qualified) — let user force a fetch
if not queue:
    st.info("No fresh articles available right now (nothing recent cleared the "
            "score threshold). Try again later, widen the recency window in "
            "fetch_articles.py, or add sources.")
    if st.button("🔄 Try fetching now", type="primary"):
        def _mutate(s):
            s["queue"], s["history"] = topup_queue(s.get("queue", []), s.get("history", []))
            s["generated_at"] = datetime.now(timezone.utc).isoformat()
            return s
        with st.spinner("Fetching..."):
            commit_mutation(_mutate)
        st.rerun()
    st.stop()

# ── Head article ──────────────────────────────────────────────────────────────

article = queue[0]
st.caption(f"{len(queue)} articles in queue")

st.markdown(f"""
<div class="article-card">
  <div class="source-tag">{article.get('source','Unknown Source')}</div>
  <strong style="font-size:17px; line-height:1.4;">{article.get('title','')}</strong>
</div>
""", unsafe_allow_html=True)

c1, c2 = st.columns([1, 1])
with c1:
    st.link_button("📄 Read Full Article", article.get("url", "#"), use_container_width=True)
with c2:
    if st.button("⏭️ Skip (remove)", use_container_width=True,
                 help="Not writing about this one — drop it from the queue"):
        with st.spinner("Removing..."):
            remove_head("skip")
        st.rerun()

st.divider()

# ── Summary ───────────────────────────────────────────────────────────────────

st.markdown('<div class="step-label">What This Article Is About</div>', unsafe_allow_html=True)
if not st.session_state.summary_loaded:
    with st.spinner("Summarizing..."):
        try:
            st.session_state.ai_summary = generate_summary(article)
        except Exception:
            st.session_state.ai_summary = article.get("summary", "")[:400]
        st.session_state.summary_loaded = True
st.markdown(f'<div class="summary-box">{st.session_state.ai_summary}</div>', unsafe_allow_html=True)

st.divider()

# ── Step 1: Opinion ───────────────────────────────────────────────────────────

st.markdown('<div class="step-label">Step 1 — Your Take</div>', unsafe_allow_html=True)
st.caption("Bullet points or prose — either works. Just write what you actually think.")
opinion = st.text_area(
    "Your opinion",
    placeholder="- AI adoption is outpacing org readiness\n- Most teams don't have clean enough data\n- The real bottleneck is decision-making culture, not the tech",
    height=140, label_visibility="collapsed",
)
generate_clicked = st.button("Generate Posts →", type="primary", disabled=not opinion.strip())

# ── Step 2: Draft ─────────────────────────────────────────────────────────────

if generate_clicked and opinion.strip():
    with st.spinner("Writing your posts..."):
        try:
            posts = generate_posts(article, opinion)
            st.session_state.linkedin_draft = posts.get("linkedin", "")
            st.session_state.facebook_draft = posts.get("facebook", "")
            st.session_state.generated = True

            # Update metrics
            if PERSIST_ENABLED:
                def _update_metrics(s):
                    if "metrics" not in s:
                        s["metrics"] = {"posts_generated": 0, "quick_posts": 0, "article_posts": 0}
                    s["metrics"]["posts_generated"] += 1
                    s["metrics"]["article_posts"] += 1
                    return s
                commit_mutation(_update_metrics)
        except Exception as e:
            st.error(f"Generation failed: {e}")
            st.stop()

if st.session_state.generated:
    st.divider()
    st.markdown('<div class="step-label">Step 2 — Review & Edit</div>', unsafe_allow_html=True)
    tab_li, tab_fb = st.tabs(["🔵 LinkedIn", "🔷 Facebook"])
    with tab_li:
        st.session_state.linkedin_draft = st.text_area(
            "LinkedIn Post", value=st.session_state.linkedin_draft,
            height=300, label_visibility="collapsed")
        st.caption(f"{len(st.session_state.linkedin_draft.split())} words · "
                   f"{len(st.session_state.linkedin_draft)} chars")
    with tab_fb:
        st.session_state.facebook_draft = st.text_area(
            "Facebook Post", value=st.session_state.facebook_draft,
            height=300, label_visibility="collapsed")
        st.caption(f"{len(st.session_state.facebook_draft.split())} words · "
                   f"{len(st.session_state.facebook_draft)} chars")

    st.divider()
    st.markdown('<div class="step-label">Step 3 — Copy, Post, Done</div>', unsafe_allow_html=True)
    st.caption("Copy the text above into LinkedIn/Facebook. Then mark it done to "
               "clear it from your queue.")
    p1, p2, p3 = st.columns(3)
    with p1:
        st.link_button("🔵 LinkedIn", "https://www.linkedin.com/feed/", use_container_width=True)
    with p2:
        st.link_button("🔷 Facebook", "https://www.facebook.com/", use_container_width=True)
    with p3:
        if st.button("✅ Done — next", type="primary", use_container_width=True,
                     help="Remove this article from the queue and move on"):
            with st.spinner("Clearing..."):
                remove_head("done")
            st.rerun()
