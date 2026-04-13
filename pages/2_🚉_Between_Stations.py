"""
🚉 Trains Between Stations
"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.session import init_session, is_logged_in, log_search
from utils.ui import inject_css, sidebar_nav, page_header, no_results_card, error_card
from utils.api_client import (
    trains_between_stations, search_station, format_date_for_api, demo_mode_notice,
    CLASS_TYPES
)
from datetime import date, timedelta
import pandas as pd

st.set_page_config(page_title="Between Stations | IR Tracker", page_icon="🚉", layout="wide")
init_session()
sidebar_nav()
inject_css()
page_header("Trains Between Stations", "Find all trains running between any two stations", "🚉")


# ── Helper functions ──────────────────────────────────────────

def station_picker(label: str, key: str):
    col1, col2 = st.columns([3, 1])
    with col1:
        name = st.text_input(f"{label} Name", key=f"{key}_name",
                             placeholder="Type station name (e.g. Mumbai Central)")
    with col2:
        code = st.text_input(f"{label} Code", key=f"{key}_code",
                             placeholder="e.g. MMCT",
                             help="Enter the 3-5 letter station code")
    return name.strip(), code.strip().upper()


def _render_train_row(t: dict, journey_date=None):
    avail_html = ""
    for a in (t.get("availability") or []):
        cls = a.get("class") or a.get("classType", "")
        status = a.get("available") or a.get("availabilityStatus", "—")
        s_upper = str(status).upper()
        color = "#00E676" if "AVL" in s_upper else ("#FFD740" if "WL" in s_upper else ("#FF9100" if "RAC" in s_upper else "#FF5252"))
        avail_html += (
            f'<span style="background:#1C1F2E;border:1px solid {color};border-radius:6px;'
            f'padding:3px 8px;font-size:.75rem;margin-right:6px;color:{color}">'
            f'{cls}: {status}</span>'
        )

    st.markdown(f"""
    <div class="ir-card">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:8px">
            <div>
                <div style="font-size:1rem;font-weight:700">
                    🚄 {t.get('trainName','—')}
                </div>
                <div style="color:#8892A4;font-size:.78rem;margin-top:2px">
                    #{t.get('trainNo','—')} &nbsp;|&nbsp;
                    {t.get('distance','—')} km &nbsp;|&nbsp;
                    🗓 {t.get('runsOn','—')}
                </div>
            </div>
            <span class="train-badge">{t.get('trainType','EXPRESS')}</span>
        </div>

        <div style="display:flex;gap:28px;margin:12px 0;flex-wrap:wrap;align-items:center">
            <div>
                <div style="font-size:1.3rem;font-weight:700;color:#FF4B2B">{t.get('departureTime','—')}</div>
                <div style="font-size:.72rem;color:#8892A4">Departure</div>
            </div>
            <div>
                <div style="font-size:.8rem;color:#8892A4;text-align:center">
                    ──── ⏱ {t.get('duration','—')} ────
                </div>
            </div>
            <div>
                <div style="font-size:1.3rem;font-weight:700">{t.get('arrivalTime','—')}</div>
                <div style="font-size:.72rem;color:#8892A4">Arrival</div>
            </div>
        </div>

        <div style="margin-top:6px">{avail_html if avail_html else '<span style="color:#8892A4;font-size:.8rem">Availability data not available — check Seat Availability page</span>'}</div>
    </div>
    """, unsafe_allow_html=True)


# ── Form ──────────────────────────────────────────────────────
with st.form("between_form"):
    col_from, col_to = st.columns(2)
    with col_from:
        st.markdown("**🟢 From Station**")
        from_name = st.text_input("Station Name", key="from_name",
                                   placeholder="e.g. New Delhi")
        from_code = st.text_input("Station Code *", key="from_code",
                                   placeholder="e.g. NDLS",
                                   help="Required — 3-5 letter station code")
    with col_to:
        st.markdown("**🔴 To Station**")
        to_name = st.text_input("Station Name", key="to_name",
                                 placeholder="e.g. Mumbai Central")
        to_code = st.text_input("Station Code *", key="to_code",
                                 placeholder="e.g. MMCT")

    journey_date = st.date_input(
        "📅 Date of Journey",
        value=date.today(),
        min_value=date.today(),
        max_value=date.today() + timedelta(days=120),
    )

    col_a, col_b = st.columns(2)
    with col_a:
        filter_class = st.selectbox(
            "Filter by Class (optional)",
            options=["All Classes"] + list(CLASS_TYPES.keys()),
            format_func=lambda x: x if x == "All Classes" else f"{x} — {CLASS_TYPES[x]}",
        )
    with col_b:
        sort_by = st.selectbox("Sort By", ["Departure Time", "Duration", "Arrival Time"])

    submitted = st.form_submit_button("🔍 Find Trains", use_container_width=True)

if submitted:
    fc = from_code.strip().upper()
    tc = to_code.strip().upper()

    if not fc or not tc:
        st.error("⚠️ Both From and To station codes are required.")
        st.stop()

    api_key = st.session_state.get("rapidapi_key", "")
    if not api_key:
        demo_mode_notice()
        # Demo data
        st.markdown("### Sample Results (Demo Mode)")
        demo_trains = [
            {
                "trainNo": "12951", "trainName": "Mumbai Rajdhani Exp", "trainType": "RAJDHANI",
                "departureTime": "17:00", "arrivalTime": "08:35", "duration": "15h 35m",
                "distance": "1384", "runsOn": "Daily",
                "availability": [
                    {"class": "1A", "available": "AVL 12"},
                    {"class": "2A", "available": "AVL 45"},
                    {"class": "3A", "available": "WL 3"},
                ]
            },
            {
                "trainNo": "12953", "trainName": "August Kranti Rajdhani", "trainType": "RAJDHANI",
                "departureTime": "17:40", "arrivalTime": "10:35", "duration": "16h 55m",
                "distance": "1384", "runsOn": "Daily",
                "availability": [
                    {"class": "1A", "available": "AVL 6"},
                    {"class": "2A", "available": "RAC 2"},
                    {"class": "3A", "available": "WL 12"},
                ]
            },
            {
                "trainNo": "12909", "trainName": "Garib Rath Express", "trainType": "G-RATH",
                "departureTime": "21:30", "arrivalTime": "17:45", "duration": "20h 15m",
                "distance": "1384", "runsOn": "Mon Wed Fri",
                "availability": [
                    {"class": "3A", "available": "AVL 92"},
                ]
            },
        ]
        for t in demo_trains:
            _render_train_row(t, journey_date)
    else:
        date_str = format_date_for_api(journey_date)
        with st.spinner(f"🔍 Searching trains from **{fc}** to **{tc}** on {journey_date.strftime('%d %b %Y')}..."):
            result = trains_between_stations(fc, tc, date_str)

        if result["ok"]:
            data = result["data"]
            trains = data.get("data", [])

            if is_logged_in():
                log_search(st.session_state.user_id, "between_stations", f"{fc}→{tc} on {date_str}")

            if not trains:
                no_results_card(f"No trains found between {fc} and {tc} on {journey_date.strftime('%d %b %Y')}.")
            else:
                # Optional class filter
                if filter_class != "All Classes":
                    trains = [
                        t for t in trains
                        if filter_class in (t.get("trainClasses", "") or "")
                        or any(c.get("classType") == filter_class for c in t.get("availability", []))
                    ]

                # Sort
                def _sort_key(t):
                    if sort_by == "Duration":
                        dur = t.get("duration", "99:99")
                        try:
                            h, m = dur.replace("h", "").replace("m", "").split()
                            return int(h) * 60 + int(m)
                        except Exception:
                            return 9999
                    elif sort_by == "Arrival Time":
                        return t.get("arrivalTime", "23:59")
                    return t.get("departureTime", "23:59")

                trains.sort(key=_sort_key)

                st.success(f"✅ **{len(trains)}** train(s) found from **{fc}** → **{tc}** on {journey_date.strftime('%d %b %Y')}")

                # Summary row
                col1, col2, col3 = st.columns(3)
                col1.metric("Trains Found", len(trains))
                col2.metric("Journey Date", journey_date.strftime("%d %b %Y"))
                col3.metric("Route", f"{fc} → {tc}")
                st.markdown("<br>", unsafe_allow_html=True)

                for t in trains:
                    _render_train_row(t, journey_date)
        else:
            error_card(result["error"])


# ── Popular routes ─────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
with st.expander("📌 Popular Station Codes Reference"):
    col_a, col_b, col_c = st.columns(3)
    routes = [
        ("NDLS", "New Delhi"),
        ("MMCT", "Mumbai Central"),
        ("HWH", "Howrah"),
        ("MAS", "Chennai Central"),
        ("SBC", "KSR Bengaluru"),
        ("PUNE", "Pune Jn"),
        ("ADI", "Ahmedabad"),
        ("BPL", "Bhopal Jn"),
        ("LKO", "Lucknow"),
        ("CNB", "Kanpur Central"),
        ("VSKP", "Vishakhapatnam"),
        ("SC", "Secunderabad"),
        ("GHY", "Guwahati"),
        ("JP", "Jaipur"),
        ("DDN", "Dehradun"),
    ]
    for i, (code, name) in enumerate(routes):
        col = [col_a, col_b, col_c][i % 3]
        col.markdown(f"`{code}` — {name}")
