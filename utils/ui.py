"""Shared UI components and styling."""

import streamlit as st
from utils.session import is_logged_in, logout


CUSTOM_CSS = """
<style>
/* ── Base ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* ── Hide Streamlit chrome ── */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0F1117 0%, #1C1F2E 100%) !important;
    border-right: 1px solid #2A2D3E;
}

/* ── Cards ── */
.ir-card {
    background: linear-gradient(135deg, #1C1F2E 0%, #23273A 100%);
    border: 1px solid #2A2D3E;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 14px;
    transition: border-color .2s;
}
.ir-card:hover { border-color: #FF4B2B; }

/* ── Train badge ── */
.train-badge {
    background: linear-gradient(90deg, #FF4B2B, #FF8751);
    color: white;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 600;
    display: inline-block;
}

/* ── Status chips ── */
.status-avail  { color: #00E676; font-weight: 600; }
.status-wl     { color: #FFD740; font-weight: 600; }
.status-rac    { color: #FF9100; font-weight: 600; }
.status-regret { color: #FF5252; font-weight: 600; }

/* ── Section header ── */
.section-header {
    font-size: 1.4rem;
    font-weight: 700;
    color: #FF4B2B;
    margin-bottom: 4px;
}
.section-sub {
    font-size: 0.85rem;
    color: #8892A4;
    margin-bottom: 20px;
}

/* ── Timeline ── */
.timeline-row {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 0;
    border-bottom: 1px solid #2A2D3E;
}
.timeline-time {
    min-width: 55px;
    font-weight: 600;
    color: #FF4B2B;
    font-size: 0.9rem;
}
.timeline-dot {
    width: 10px; height: 10px;
    border-radius: 50%;
    background: #FF4B2B;
    flex-shrink: 0;
}
.timeline-station {
    font-size: 0.88rem;
    font-weight: 500;
}
.timeline-code {
    font-size: 0.75rem;
    color: #8892A4;
}

/* ── Hero gradient ── */
.hero-gradient {
    background: linear-gradient(135deg, #FF4B2B22 0%, #1C1F2E 100%);
    border: 1px solid #FF4B2B44;
    border-radius: 16px;
    padding: 30px;
    margin-bottom: 24px;
}

/* ── Stat card ── */
.stat-card {
    background: #1C1F2E;
    border: 1px solid #2A2D3E;
    border-radius: 10px;
    padding: 16px;
    text-align: center;
}
.stat-value {
    font-size: 1.6rem;
    font-weight: 700;
    color: #FF4B2B;
}
.stat-label {
    font-size: 0.78rem;
    color: #8892A4;
    margin-top: 2px;
}

/* ── Input override ── */
.stTextInput > div > div > input,
.stSelectbox > div > div,
.stDateInput > div > div > input {
    background-color: #1C1F2E !important;
    border: 1px solid #2A2D3E !important;
    border-radius: 8px !important;
    color: #FAFAFA !important;
}

/* ── Button ── */
.stButton > button {
    background: linear-gradient(90deg, #FF4B2B, #FF8751);
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    padding: 0.4rem 1.2rem;
    transition: opacity .2s;
}
.stButton > button:hover { opacity: .88; }

/* ── Divider ── */
hr.ir-divider {
    border: none;
    border-top: 1px solid #2A2D3E;
    margin: 18px 0;
}

/* ── Alert boxes ── */
.ir-alert-warn {
    background: #2A2610;
    border-left: 4px solid #FFD740;
    border-radius: 6px;
    padding: 12px 16px;
    margin: 10px 0;
    color: #FFD740;
    font-size: .88rem;
}
.ir-alert-info {
    background: #102030;
    border-left: 4px solid #29B6F6;
    border-radius: 6px;
    padding: 12px 16px;
    margin: 10px 0;
    color: #29B6F6;
    font-size: .88rem;
}
</style>
"""


def inject_css():
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def page_header(title: str, subtitle: str = "", icon: str = "🚄"):
    st.markdown(f"""
    <div class="hero-gradient">
        <div style="display:flex;align-items:center;gap:12px">
            <span style="font-size:2rem">{icon}</span>
            <div>
                <div class="section-header">{title}</div>
                <div class="section-sub">{subtitle}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def stat_row(stats: list[dict]):
    cols = st.columns(len(stats))
    for col, s in zip(cols, stats):
        with col:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-value">{s['value']}</div>
                <div class="stat-label">{s['label']}</div>
            </div>
            """, unsafe_allow_html=True)


def availability_badge(status: str) -> str:
    s = str(status).upper()
    if "AVL" in s or "AVAILABLE" in s:
        return f'<span class="status-avail">🟢 {status}</span>'
    elif "WL" in s:
        return f'<span class="status-wl">🟡 {status}</span>'
    elif "RAC" in s:
        return f'<span class="status-rac">🟠 {status}</span>'
    elif "REGRET" in s or "NOT AVAILABLE" in s:
        return f'<span class="status-regret">🔴 {status}</span>'
    return f"<span>{status}</span>"


def sidebar_nav():
    """Render sidebar navigation."""
    inject_css()
    with st.sidebar:
        st.markdown("""
        <div style="text-align:center; padding: 16px 0 8px 0">
            <div style="font-size:2.4rem">🚆</div>
            <div style="font-size:1.1rem; font-weight:700; color:#FF4B2B; margin-top:4px">
                Indian Railways
            </div>
            <div style="font-size:0.72rem; color:#8892A4">Live Train Tracker & Planner</div>
        </div>
        <hr style="border-color:#2A2D3E; margin:10px 0 16px 0">
        """, unsafe_allow_html=True)

        if is_logged_in():
            st.markdown(f"""
            <div style="background:#1C1F2E;border:1px solid #2A2D3E;border-radius:8px;
                        padding:10px 14px;margin-bottom:16px;font-size:.85rem">
                👤 <b>{st.session_state.username}</b>
                <span style="color:#8892A4;font-size:.75rem;display:block;margin-top:2px">Logged in</span>
            </div>
            """, unsafe_allow_html=True)

            if st.button("🚪 Logout", use_container_width=True):
                logout()
        else:
            st.info("🔐 Login to save history & favourites", icon="ℹ️")

        st.markdown("<div style='margin-top:20px'></div>", unsafe_allow_html=True)
        key_snippet = st.session_state.get("rapidapi_key", "")
        if key_snippet:
            st.markdown(
                f"<div style='font-size:.72rem;color:#00E676;'>✅ API Key Active</div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                "<div style='font-size:.72rem;color:#FFD740;'>⚠️ No API Key — Set in ⚙️ Settings</div>",
                unsafe_allow_html=True,
            )

        st.markdown("<hr style='border-color:#2A2D3E;margin:14px 0'>", unsafe_allow_html=True)
        st.markdown(
            "<div style='font-size:.7rem;color:#8892A4;text-align:center'>"
            "Data via IRCTC RapidAPI<br>© 2025 IR Tracker"
            "</div>",
            unsafe_allow_html=True,
        )


def login_wall():
    """Show login prompt if not logged in."""
    st.markdown("""
    <div class="ir-card" style="text-align:center;padding:40px">
        <div style="font-size:3rem">🔐</div>
        <div style="font-size:1.2rem;font-weight:600;margin:10px 0">Login Required</div>
        <div style="color:#8892A4;font-size:.88rem">
            Please login or register to use this feature.
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/7_⚙️_Settings.py", label="Go to Login / Register", icon="🔐")


def no_results_card(msg: str = "No results found."):
    st.markdown(f"""
    <div class="ir-card" style="text-align:center;padding:30px">
        <div style="font-size:2.5rem">🔍</div>
        <div style="color:#8892A4;margin-top:8px">{msg}</div>
    </div>
    """, unsafe_allow_html=True)


def error_card(msg: str):
    st.markdown(f"""
    <div style="background:#2A1010;border-left:4px solid #FF5252;border-radius:6px;
                padding:14px 16px;margin:10px 0;color:#FF8888;font-size:.88rem">
        {msg}
    </div>
    """, unsafe_allow_html=True)
