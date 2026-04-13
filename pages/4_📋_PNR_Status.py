"""
📋 PNR Status — Track your booking
"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.session import init_session, is_logged_in, log_search
from utils.ui import inject_css, sidebar_nav, page_header, error_card, availability_badge
from utils.api_client import get_pnr_status, demo_mode_notice

st.set_page_config(page_title="PNR Status | IR Tracker", page_icon="📋", layout="wide")
init_session()
sidebar_nav()
inject_css()
page_header("PNR Status", "Check your booking & passenger reservation status", "📋")

# ── What is PNR info ──────────────────────────────────────────
with st.expander("ℹ️ What is a PNR Number?"):
    st.markdown("""
    A **PNR (Passenger Name Record)** is a 10-digit unique number assigned to every railway booking.
    - Find it on your ticket, IRCTC booking confirmation email, or SMS
    - Format: 10 digits, e.g. `4234567890`
    - You can check PNR status up to **4 hours after departure**
    """)

# ── Recent PNRs from session ───────────────────────────────────
if is_logged_in():
    from utils.session import get_search_history
    history = get_search_history(st.session_state.user_id)
    pnr_history = [h["query"] for h in history if h["type"] == "pnr_status"][:5]
    if pnr_history:
        st.markdown("**🕐 Recent PNR Checks:**")
        cols = st.columns(min(len(pnr_history), 5))
        for i, pnr in enumerate(pnr_history):
            with cols[i]:
                if st.button(pnr, key=f"hist_{i}", use_container_width=True):
                    st.session_state["pnr_input"] = pnr

# ── Form ──────────────────────────────────────────────────────
with st.form("pnr_form"):
    pnr_number = st.text_input(
        "🎟 Enter PNR Number",
        value=st.session_state.get("pnr_input", ""),
        placeholder="10-digit PNR number, e.g. 4234567890",
        max_chars=10,
        help="Enter the 10-digit PNR from your railway ticket",
    )
    submitted = st.form_submit_button("🔍 Check PNR Status", use_container_width=True)

if submitted:
    pnr = pnr_number.strip()
    if len(pnr) != 10 or not pnr.isdigit():
        st.error("⚠️ Please enter a valid 10-digit numeric PNR number.")
        st.stop()

    api_key = st.session_state.get("rapidapi_key", "")
    if not api_key:
        demo_mode_notice()
        _render_demo_pnr(pnr)
    else:
        with st.spinner("🔍 Fetching PNR status..."):
            result = get_pnr_status(pnr)

        if is_logged_in():
            log_search(st.session_state.user_id, "pnr_status", pnr)

        if result["ok"]:
            data = result["data"].get("data", result["data"])
            _render_pnr_result(data)
        else:
            error_card(result["error"])


def _status_color(status: str) -> tuple:
    s = str(status).upper()
    if "CNF" in s or "CONFIRMED" in s:
        return "#00E676", "🟢"
    elif "WL" in s:
        return "#FFD740", "🟡"
    elif "RAC" in s:
        return "#FF9100", "🟠"
    elif "CAN" in s:
        return "#FF5252", "🔴"
    return "#8892A4", "⚪"


def _render_pnr_result(data: dict):
    if not data:
        st.warning("No data returned. The PNR may have expired or is invalid.")
        return

    train_no   = data.get("trainNumber") or data.get("trainNo", "—")
    train_name = data.get("trainName", "—")
    from_stn   = data.get("boardingStationName") or data.get("fromStation", "—")
    to_stn     = data.get("reservationUpto") or data.get("toStation", "—")
    doj        = data.get("dateOfJourney") or data.get("doj", "—")
    cls        = data.get("journeyClass", "—")
    chart      = data.get("chartPrepared", False)
    passengers = data.get("passengerList") or data.get("passengers", [])

    chart_badge = (
        '<span style="background:#00E676;color:#000;border-radius:4px;padding:2px 8px;font-size:.72rem;font-weight:700">CHART PREPARED</span>'
        if chart else
        '<span style="background:#FFD740;color:#000;border-radius:4px;padding:2px 8px;font-size:.72rem;font-weight:700">CHART NOT PREPARED</span>'
    )

    # ── Train info card ────────────────────────────────────────
    st.markdown(f"""
    <div class="ir-card">
        <div style="display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px">
            <div>
                <div style="font-size:1.1rem;font-weight:700">🚄 {train_name}</div>
                <div style="color:#8892A4;font-size:.8rem;margin-top:2px">#{train_no}</div>
            </div>
            {chart_badge}
        </div>
        <div style="display:flex;gap:28px;margin-top:14px;flex-wrap:wrap">
            <div>
                <div style="font-weight:600">{from_stn}</div>
                <div style="font-size:.72rem;color:#8892A4">Boarding</div>
            </div>
            <div style="color:#8892A4;font-size:1.2rem">→</div>
            <div>
                <div style="font-weight:600">{to_stn}</div>
                <div style="font-size:.72rem;color:#8892A4">Destination</div>
            </div>
            <div style="margin-left:auto;text-align:right">
                <div style="font-weight:600">{doj}</div>
                <div style="font-size:.72rem;color:#8892A4">Journey Date</div>
            </div>
        </div>
        <div style="margin-top:10px">
            <span class="train-badge">{cls}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Passengers ─────────────────────────────────────────────
    if passengers:
        st.markdown("### 👤 Passenger Status")
        for i, p in enumerate(passengers, 1):
            booking_status = p.get("bookingStatus") or p.get("currentStatus", "—")
            current_status = p.get("currentStatus") or p.get("bookingStatus", "—")
            coach  = p.get("coachId") or p.get("coach", "—")
            berth  = p.get("berthNo") or p.get("berth", "—")
            berth_type = p.get("berthType", "")
            color, emoji = _status_color(current_status)

            st.markdown(f"""
            <div style="background:#1C1F2E;border:1px solid {color}55;border-radius:10px;
                        padding:14px 16px;margin-bottom:8px;display:flex;
                        align-items:center;gap:16px;flex-wrap:wrap">
                <div style="background:#2A2D3E;border-radius:50%;width:32px;height:32px;
                            display:flex;align-items:center;justify-content:center;
                            font-weight:700;flex-shrink:0">{i}</div>
                <div style="flex:1;min-width:140px">
                    <div style="font-size:.78rem;color:#8892A4">Booking Status</div>
                    <div style="font-weight:600">{booking_status}</div>
                </div>
                <div style="flex:1;min-width:140px">
                    <div style="font-size:.78rem;color:#8892A4">Current Status</div>
                    <div style="color:{color};font-weight:700">{emoji} {current_status}</div>
                </div>
                <div style="text-align:right">
                    <div style="font-size:.78rem;color:#8892A4">Coach / Berth</div>
                    <div style="font-weight:600">{coach} — {berth} {berth_type}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Passenger details not available yet. Chart may not have been prepared.")


def _render_demo_pnr(pnr: str):
    st.markdown("### PNR Status Result (Demo Mode)")
    demo = {
        "trainNumber": "12301",
        "trainName": "Howrah Rajdhani Express",
        "boardingStationName": "NEW DELHI (NDLS)",
        "reservationUpto": "HOWRAH JN (HWH)",
        "dateOfJourney": "25-Dec-2025",
        "journeyClass": "2A",
        "chartPrepared": False,
        "passengerList": [
            {"bookingStatus": "CNF/B3/45/LB", "currentStatus": "CNF/B3/45/LB",
             "coachId": "B3", "berthNo": 45, "berthType": "Lower Berth"},
            {"bookingStatus": "WL/32", "currentStatus": "CNF/B3/47/UB",
             "coachId": "B3", "berthNo": 47, "berthType": "Upper Berth"},
        ],
    }
    _render_pnr_result(demo)
