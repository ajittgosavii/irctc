"""
📅 Train Schedule — Full station-wise timetable
"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.session import init_session, is_logged_in, log_search
from utils.ui import inject_css, sidebar_nav, page_header, error_card
from utils.api_client import get_train_schedule, demo_mode_notice
import pandas as pd

st.set_page_config(page_title="Train Schedule | IR Tracker", page_icon="📅", layout="wide")
init_session()
sidebar_nav()
inject_css()
page_header("Train Schedule", "Full station-wise timetable for any train", "📅")

# ── Form ──────────────────────────────────────────────────────
with st.form("schedule_form"):
    train_no = st.text_input(
        "🚄 Train Number",
        placeholder="Enter train number, e.g. 12301",
        help="5-digit train number"
    )
    submitted = st.form_submit_button("📋 Get Schedule", use_container_width=True)

if submitted:
    tn = train_no.strip()
    if not tn:
        st.error("⚠️ Please enter a train number.")
        st.stop()

    api_key = st.session_state.get("rapidapi_key", "")
    if not api_key:
        demo_mode_notice()
        _render_demo_schedule(tn)
    else:
        with st.spinner(f"⏳ Loading schedule for train #{tn}..."):
            result = get_train_schedule(tn)

        if is_logged_in():
            log_search(st.session_state.user_id, "schedule", tn)

        if result["ok"]:
            data = result["data"].get("data", result["data"])
            _render_schedule(data)
        else:
            error_card(result["error"])


def _render_schedule(data: dict | list):
    # Handle different response shapes
    if isinstance(data, list):
        stations = data
        meta = {}
    elif isinstance(data, dict):
        stations = data.get("stationList") or data.get("stations") or data.get("stops", [])
        meta = data
    else:
        st.warning("Unexpected schedule data format.")
        return

    train_name = meta.get("trainName", "")
    train_no   = meta.get("trainNo") or meta.get("trainNumber", "")
    runs_on    = meta.get("runsOn") or meta.get("runDays", "—")
    distance   = meta.get("totalDistance") or meta.get("distance", "—")

    if train_name:
        st.markdown(f"""
        <div class="ir-card" style="margin-bottom:16px">
            <div style="font-size:1.1rem;font-weight:700">🚄 {train_name}</div>
            <div style="color:#8892A4;font-size:.8rem;margin-top:4px">
                #{train_no} &nbsp;|&nbsp; Runs: {runs_on} &nbsp;|&nbsp; Total: {distance} km
            </div>
        </div>
        """, unsafe_allow_html=True)

    if not stations:
        st.info("Schedule data not available for this train.")
        return

    # ── View Toggle ───────────────────────────────────────────
    view = st.radio("View As", ["🗓 Timeline", "📊 Table"], horizontal=True)

    if "Table" in view:
        rows = []
        for i, s in enumerate(stations, 1):
            rows.append({
                "#": i,
                "Station": f"{s.get('stationName') or s.get('name','—')} ({s.get('stationCode') or s.get('code','—')})",
                "Arrival": s.get("arrivalTime") or s.get("arr", "—"),
                "Departure": s.get("departureTime") or s.get("dep", "—"),
                "Halt (min)": s.get("haltTime") or s.get("halt", 0),
                "Dist (km)": s.get("distance") or s.get("dist", "—"),
                "Day": s.get("dayCount") or s.get("day", 1),
            })
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        # ── Timeline view ──────────────────────────────────────
        for i, s in enumerate(stations):
            name = s.get("stationName") or s.get("name", "—")
            code = s.get("stationCode") or s.get("code", "—")
            arr  = s.get("arrivalTime") or s.get("arr", "—")
            dep  = s.get("departureTime") or s.get("dep", "—")
            halt = s.get("haltTime") or s.get("halt", "")
            dist = s.get("distance") or s.get("dist", "")
            day  = int(s.get("dayCount") or s.get("day") or 1)

            is_first = i == 0
            is_last  = i == len(stations) - 1

            dot_color = "#FF4B2B" if is_first or is_last else "#2A2D3E"
            line_color = "#2A2D3E"
            time_str = dep if is_first else (arr if is_last else arr)
            dep_str  = f"→ {dep}" if (not is_last and arr != dep and dep not in ("—", "", None)) else ""
            day_badge = f'<span style="background:#2A2D3E;border-radius:4px;padding:1px 6px;font-size:.68rem;color:#8892A4">Day {day}</span>' if day > 1 else ""
            origin_badge = '<span style="background:#FF4B2B;color:white;border-radius:4px;padding:1px 6px;font-size:.68rem;margin-left:4px">ORIGIN</span>' if is_first else ""
            dest_badge = '<span style="background:#00E676;color:black;border-radius:4px;padding:1px 6px;font-size:.68rem;margin-left:4px">DESTINATION</span>' if is_last else ""

            st.markdown(f"""
            <div style="display:flex;gap:0;align-items:stretch">
                <div style="display:flex;flex-direction:column;align-items:center;width:24px;flex-shrink:0">
                    <div style="width:12px;height:12px;border-radius:50%;background:{dot_color};
                                flex-shrink:0;margin-top:10px;border:2px solid {'#FF4B2B' if is_first or is_last else '#8892A4'}"></div>
                    {'<div style="width:2px;flex:1;background:#2A2D3E;min-height:20px"></div>' if not is_last else ''}
                </div>
                <div style="flex:1;padding:6px 12px 16px 10px">
                    <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:6px">
                        <div>
                            <div style="font-weight:{'700' if is_first or is_last else '500'};font-size:.92rem">
                                {name} {origin_badge}{dest_badge}
                            </div>
                            <div style="font-size:.75rem;color:#8892A4">
                                {code}
                                {f' &nbsp;|&nbsp; {dist} km from origin' if dist else ''}
                                {f' &nbsp;|&nbsp; Halt: {halt} min' if halt and not is_first and not is_last else ''}
                            </div>
                        </div>
                        <div style="text-align:right">
                            <div style="font-weight:700;color:#FF4B2B">{time_str}</div>
                            <div style="font-size:.72rem;color:#8892A4">{dep_str} {day_badge}</div>
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)


def _render_demo_schedule(tn: str):
    st.markdown("### Train Schedule (Demo Mode)")
    demo_data = {
        "trainName": "Howrah Rajdhani Express",
        "trainNo": tn,
        "runsOn": "Daily",
        "totalDistance": "1447",
        "stationList": [
            {"stationName": "NEW DELHI",        "stationCode": "NDLS",  "arrivalTime": "—",     "departureTime": "14:05", "haltTime": "—",  "distance": 0,    "dayCount": 1},
            {"stationName": "KANPUR CENTRAL",    "stationCode": "CNB",   "arrivalTime": "18:43", "departureTime": "18:48", "haltTime": 5,    "distance": 440,  "dayCount": 1},
            {"stationName": "ALLAHABAD JN",      "stationCode": "ALD",   "arrivalTime": "20:45", "departureTime": "20:50", "haltTime": 5,    "distance": 643,  "dayCount": 1},
            {"stationName": "MUGHAL SARAI JN",   "stationCode": "MGS",   "arrivalTime": "22:28", "departureTime": "22:33", "haltTime": 5,    "distance": 788,  "dayCount": 1},
            {"stationName": "PATNA JN",          "stationCode": "PNBE",  "arrivalTime": "01:05", "departureTime": "01:10", "haltTime": 5,    "distance": 995,  "dayCount": 2},
            {"stationName": "GAYA JN",           "stationCode": "GAYA",  "arrivalTime": "02:35", "departureTime": "02:37", "haltTime": 2,    "distance": 1115, "dayCount": 2},
            {"stationName": "DHANBAD JN",        "stationCode": "DHN",   "arrivalTime": "04:40", "departureTime": "04:45", "haltTime": 5,    "distance": 1272, "dayCount": 2},
            {"stationName": "ASANSOL JN",        "stationCode": "ASN",   "arrivalTime": "05:25", "departureTime": "05:27", "haltTime": 2,    "distance": 1335, "dayCount": 2},
            {"stationName": "HOWRAH JN",         "stationCode": "HWH",   "arrivalTime": "10:00", "departureTime": "—",     "haltTime": "—",  "distance": 1447, "dayCount": 2},
        ],
    }
    _render_schedule(demo_data)
