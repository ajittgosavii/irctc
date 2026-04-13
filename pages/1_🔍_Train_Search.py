"""
🔍 Train Search — search by train number or name
"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.session import init_session
from utils.ui import inject_css, sidebar_nav, page_header, no_results_card, error_card
from utils.api_client import search_train, demo_mode_notice
from utils.session import log_search, is_logged_in

st.set_page_config(page_title="Train Search | IR Tracker", page_icon="🔍", layout="wide")
init_session()
sidebar_nav()
inject_css()
page_header("Train Search", "Find any train by number or name", "🔍")


# ── Helper functions ──────────────────────────────────────────

def _render_train_card(t: dict, demo: bool = False):
    classes_html = "".join(
        f'<span style="background:#2A2D3E;border-radius:4px;padding:2px 8px;'
        f'font-size:.72rem;margin-right:4px">{c}</span>'
        for c in (t.get("classes") or t.get("trainClasses", "").split(",") if isinstance(t.get("trainClasses"), str) else [])
    )
    badge = f'<span class="train-badge">{t.get("trainType","")}</span>' if t.get("trainType") else ""
    demo_tag = '<span style="color:#FFD740;font-size:.7rem"> (demo)</span>' if demo else ""

    st.markdown(f"""
    <div class="ir-card">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:8px">
            <div>
                <div style="font-size:1.05rem;font-weight:700">
                    🚄 {t.get('trainName','—')} {demo_tag}
                </div>
                <div style="color:#8892A4;font-size:.8rem;margin-top:2px">
                    #{t.get('trainNo','—')} &nbsp;|&nbsp; {t.get('origin','')} ({t.get('originCode','')})
                    → {t.get('destination','')} ({t.get('destCode','')})
                </div>
            </div>
            <div style="text-align:right">
                {badge}
                <div style="font-size:.78rem;color:#8892A4;margin-top:4px">
                    🗓 {t.get('runsOn','—')}
                </div>
            </div>
        </div>
        <div style="display:flex;gap:24px;margin-top:12px;flex-wrap:wrap">
            <div>
                <div style="font-size:1.2rem;font-weight:700;color:#FF4B2B">
                    {t.get('departureTime','—')}
                </div>
                <div style="font-size:.75rem;color:#8892A4">Departure</div>
            </div>
            <div style="font-size:1.2rem;color:#8892A4;padding-top:4px">→</div>
            <div>
                <div style="font-size:1.2rem;font-weight:700">
                    {t.get('arrivalTime','—')}
                </div>
                <div style="font-size:.75rem;color:#8892A4">Arrival</div>
            </div>
            <div style="margin-left:auto">
                <div style="font-size:.9rem;font-weight:600;color:#29B6F6">
                    ⏱ {t.get('duration','—')}
                </div>
                <div style="font-size:.72rem;color:#8892A4">Duration</div>
            </div>
        </div>
        <div style="margin-top:10px">{classes_html}</div>
    </div>
    """, unsafe_allow_html=True)


# ── Search form ────────────────────────────────────────────────
with st.form("search_form"):
    query = st.text_input(
        "Enter Train Number or Name",
        placeholder="e.g. 12301 or Rajdhani or Shatabdi",
        help="You can enter a partial name or the full train number"
    )
    submitted = st.form_submit_button("🔍 Search Train", use_container_width=True)

if submitted and query.strip():
    api_key = st.session_state.get("rapidapi_key", "")

    if not api_key:
        demo_mode_notice()
        # Show sample demo data
        st.markdown("### Sample Results (Demo Mode)")
        demo_trains = [
            {"trainNo": "12301", "trainName": "Howrah Rajdhani Express", "trainType": "RAJDHANI",
             "origin": "HOWRAH JN", "originCode": "HWH", "destination": "NEW DELHI", "destCode": "NDLS",
             "departureTime": "14:05", "arrivalTime": "10:00", "duration": "19h 55m",
             "classes": ["1A","2A","3A"], "runsOn": "Mon Tue Wed Thu Fri Sat Sun"},
            {"trainNo": "12302", "trainName": "New Delhi Rajdhani Express", "trainType": "RAJDHANI",
             "origin": "NEW DELHI", "originCode": "NDLS", "destination": "HOWRAH JN", "destCode": "HWH",
             "departureTime": "16:55", "arrivalTime": "13:00", "duration": "20h 05m",
             "classes": ["1A","2A","3A"], "runsOn": "Daily"},
            {"trainNo": "12951", "trainName": "Mumbai Rajdhani Express", "trainType": "RAJDHANI",
             "origin": "MUMBAI CENTRAL", "originCode": "MMCT", "destination": "NEW DELHI", "destCode": "NDLS",
             "departureTime": "17:00", "arrivalTime": "08:35", "duration": "15h 35m",
             "classes": ["1A","2A","3A"], "runsOn": "Daily"},
        ]
        for t in demo_trains:
            _render_train_card(t, demo=True)
    else:
        with st.spinner("🔍 Searching trains..."):
            result = search_train(query.strip())

        if result["ok"]:
            data = result["data"]
            trains = data.get("data", [])
            if is_logged_in():
                log_search(st.session_state.user_id, "train_search", query.strip())

            if not trains:
                no_results_card(f"No trains found for '{query}'. Try a different name or number.")
            else:
                st.success(f"✅ Found **{len(trains)}** train(s) matching '{query}'")
                for t in trains:
                    _render_train_card(t)
        else:
            error_card(result["error"])

elif submitted:
    st.warning("Please enter a train name or number to search.")
