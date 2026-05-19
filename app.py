import streamlit as st
import feedparser
from datetime import datetime
import time

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Global Education Inequality Monitor",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Source+Sans+3:wght@300;400;600&display=swap');

/* ── Base ── */
html, body, [class*="css"] {
    font-family: 'Source Sans 3', sans-serif;
    background-color: #F5F0E8;
    color: #1A1A1A;
}

.block-container {
    padding-top: 2rem;
    max-width: 1100px;
}

/* ── Header ── */
.hero {
    background: #1A1A2E;
    color: #F5F0E8;
    border-radius: 4px;
    padding: 2.5rem 3rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: "";
    position: absolute;
    top: -60px; right: -60px;
    width: 220px; height: 220px;
    border-radius: 50%;
    background: rgba(255,200,60,0.12);
}
.hero-tag {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #FFC83C;
    margin-bottom: 0.6rem;
}
.hero-title {
    font-family: 'Playfair Display', serif;
    font-size: 2.4rem;
    line-height: 1.15;
    margin: 0 0 0.8rem 0;
    color: #F5F0E8;
}
.hero-subtitle {
    font-size: 0.95rem;
    font-weight: 300;
    color: #B0A99A;
    max-width: 560px;
}

/* ── Stats bar ── */
.stats-bar {
    display: flex;
    gap: 2rem;
    padding: 1rem 0 1.4rem 0;
    border-bottom: 1px solid #D6CFC0;
    margin-bottom: 1.6rem;
    flex-wrap: wrap;
}
.stat-item { line-height: 1.3; }
.stat-num {
    font-family: 'Playfair Display', serif;
    font-size: 1.7rem;
    color: #1A1A2E;
}
.stat-label {
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #7A7060;
}

/* ── Controls ── */
.controls-row {
    display: flex;
    gap: 1rem;
    align-items: center;
    margin-bottom: 1.8rem;
    flex-wrap: wrap;
}

/* ── Card ── */
.card {
    background: #FFFDF7;
    border: 1px solid #E0D8C8;
    border-radius: 4px;
    padding: 1.3rem 1.5rem;
    margin-bottom: 0.85rem;
    transition: border-color 0.2s, box-shadow 0.2s;
    position: relative;
}
.card:hover {
    border-color: #1A1A2E;
    box-shadow: 3px 3px 0 #1A1A2E;
}
.card-source-badge {
    display: inline-block;
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    padding: 0.22em 0.7em;
    border-radius: 2px;
    margin-bottom: 0.55rem;
}
.badge-bbc    { background: #CC0000; color: #fff; }
.badge-guardian { background: #052962; color: #fff; }
.badge-reuters { background: #FF6200; color: #fff; }
.badge-other  { background: #444; color: #fff; }

.card-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.05rem;
    color: #1A1A2E;
    line-height: 1.4;
    margin-bottom: 0.4rem;
    text-decoration: none;
}
.card-title a {
    color: #1A1A2E;
    text-decoration: none;
}
.card-title a:hover { text-decoration: underline; }

.card-meta {
    font-size: 0.78rem;
    color: #7A7060;
    font-weight: 300;
}

/* ── Keyword chips ── */
.keyword-chips {
    display: flex;
    flex-wrap: wrap;
    gap: 0.45rem;
    margin-bottom: 1.5rem;
}
.chip {
    font-size: 0.72rem;
    padding: 0.28em 0.75em;
    background: #1A1A2E;
    color: #F5F0E8;
    border-radius: 100px;
    letter-spacing: 0.04em;
    font-weight: 400;
    cursor: default;
}

/* ── Empty state ── */
.empty-state {
    text-align: center;
    padding: 4rem 2rem;
    color: #7A7060;
    font-size: 0.95rem;
}

/* ── Footer ── */
.footer {
    text-align: center;
    padding: 2rem 0 1rem 0;
    font-size: 0.75rem;
    color: #9A9080;
    border-top: 1px solid #D6CFC0;
    margin-top: 2rem;
    letter-spacing: 0.04em;
}

/* Streamlit overrides */
div[data-testid="stTextInput"] input {
    background: #FFFDF7;
    border: 1px solid #D6CFC0;
    border-radius: 4px;
    font-family: 'Source Sans 3', sans-serif;
    font-size: 0.9rem;
    color: #1A1A1A;
}
div[data-testid="stTextInput"] input:focus {
    border-color: #1A1A2E;
    box-shadow: none;
}
button[kind="primary"], .stButton > button {
    background: #1A1A2E !important;
    color: #F5F0E8 !important;
    border: none !important;
    border-radius: 4px !important;
    font-family: 'Source Sans 3', sans-serif !important;
    font-weight: 600 !important;
    letter-spacing: 0.05em !important;
    padding: 0.5rem 1.4rem !important;
    transition: background 0.2s !important;
}
button[kind="primary"]:hover, .stButton > button:hover {
    background: #FFC83C !important;
    color: #1A1A2E !important;
}
</style>
""", unsafe_allow_html=True)


# ── RSS Sources & Keywords ────────────────────────────────────────────────────
RSS_FEEDS = {
    "BBC": [
        "https://feeds.bbci.co.uk/news/education/rss.xml",
        "https://feeds.bbci.co.uk/news/world/rss.xml",
    ],
    "The Guardian": [
        "https://www.theguardian.com/education/rss",
        "https://www.theguardian.com/global-development/rss",
        "https://www.theguardian.com/technology/rss",
    ],
    "Reuters": [
        "https://feeds.reuters.com/reuters/educationNews",
        "https://feeds.reuters.com/reuters/technologyNews",
        "https://feeds.reuters.com/Reuters/worldNews",
    ],
}

KEYWORDS = [
    "education inequality",
    "global education gap",
    "digital divide in education",
    "AI in education",
    "access to education",
    "education disparity",
    "online learning access",
    "UNESCO education",
]

BADGE_CLASS = {
    "BBC": "badge-bbc",
    "The Guardian": "badge-guardian",
    "Reuters": "badge-reuters",
}


# ── Helpers ───────────────────────────────────────────────────────────────────
def parse_date(entry) -> str:
    for attr in ("published_parsed", "updated_parsed"):
        t = getattr(entry, attr, None)
        if t:
            try:
                return datetime(*t[:6]).strftime("%b %d, %Y")
            except Exception:
                pass
    return "—"


def is_relevant(title: str, summary: str) -> bool:
    text = (title + " " + summary).lower()
    return any(kw.lower() in text for kw in KEYWORDS)


@st.cache_data(ttl=300, show_spinner=False)
def fetch_all_articles():
    articles = []
    for source, urls in RSS_FEEDS.items():
        for url in urls:
            try:
                feed = feedparser.parse(url)
                for entry in feed.entries:
                    title   = entry.get("title", "").strip()
                    link    = entry.get("link", "#")
                    summary = entry.get("summary", "")
                    date    = parse_date(entry)
                    if title and is_relevant(title, summary):
                        articles.append({
                            "title":  title,
                            "link":   link,
                            "date":   date,
                            "source": source,
                        })
            except Exception:
                pass
    # deduplicate by link
    seen, unique = set(), []
    for a in articles:
        if a["link"] not in seen:
            seen.add(a["link"])
            unique.append(a)
    return unique


def source_count(articles):
    counts = {}
    for a in articles:
        counts[a["source"]] = counts.get(a["source"], 0) + 1
    return counts


# ── UI ────────────────────────────────────────────────────────────────────────
# Header
st.markdown("""
<div class="hero">
    <div class="hero-tag">🌍 Real-time News Monitor</div>
    <div class="hero-title">Global Education<br>Inequality</div>
    <div class="hero-subtitle">
        Aggregating headlines from BBC, The Guardian &amp; Reuters —
        filtered for topics around educational access, disparity, and the digital divide.
    </div>
</div>
""", unsafe_allow_html=True)

# Keyword chips
chips_html = '<div class="keyword-chips">' + "".join(
    f'<span class="chip">{kw}</span>' for kw in KEYWORDS
) + '</div>'
st.markdown(chips_html, unsafe_allow_html=True)

# Controls row
col_search, col_btn, col_spacer = st.columns([3, 1, 2])
with col_search:
    query = st.text_input("", placeholder="🔍  Search headlines…", label_visibility="collapsed")
with col_btn:
    refresh = st.button("↻  Refresh", use_container_width=True)

# Fetch data
if refresh:
    fetch_all_articles.clear()

with st.spinner("Fetching latest headlines…"):
    articles = fetch_all_articles()

# Filter by search query
if query.strip():
    q = query.strip().lower()
    articles = [a for a in articles if q in a["title"].lower()]

# Stats bar
src_counts = source_count(articles)
stats_html = '<div class="stats-bar">'
stats_html += f'<div class="stat-item"><div class="stat-num">{len(articles)}</div><div class="stat-label">Headlines</div></div>'
for src, cnt in src_counts.items():
    stats_html += f'<div class="stat-item"><div class="stat-num">{cnt}</div><div class="stat-label">{src}</div></div>'
stats_html += f'<div class="stat-item" style="margin-left:auto"><div class="stat-label">Last updated</div><div style="font-size:0.85rem;color:#7A7060;">{datetime.now().strftime("%H:%M:%S")}</div></div>'
stats_html += '</div>'
st.markdown(stats_html, unsafe_allow_html=True)

# Article cards
if articles:
    for art in articles:
        badge_cls = BADGE_CLASS.get(art["source"], "badge-other")
        card_html = f"""
<div class="card">
    <span class="card-source-badge {badge_cls}">{art['source']}</span>
    <div class="card-title"><a href="{art['link']}" target="_blank">{art['title']}</a></div>
    <div class="card-meta">📅 {art['date']}</div>
</div>"""
        st.markdown(card_html, unsafe_allow_html=True)
else:
    st.markdown("""
<div class="empty-state">
    <div style="font-size:2rem;margin-bottom:1rem">📭</div>
    <div>No headlines found matching your search.<br>Try a different keyword or refresh to reload.</div>
</div>""", unsafe_allow_html=True)

# Footer
st.markdown("""
<div class="footer">
    Sources: BBC · The Guardian · Reuters &nbsp;|&nbsp;
    Data refreshes automatically every 5 minutes &nbsp;|&nbsp;
    Built with Streamlit &amp; feedparser
</div>
""", unsafe_allow_html=True)
