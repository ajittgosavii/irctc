"""
🔴 Live Train Status — Real-time running position
"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.session import init_session, is_logged_in, log_search
from utils.ui import inject_css, sidebar_nav, page_header, error_card
from utils.api_client import get_live_train_status, demo_mode_notice

st.set_page_config(page_title="Live Status | IR Tracker", page_icon="🔴", layout="wide")
init_session()
sidebar_nav()
inject_css()
page_header("Live Train Status", "Real-time running position, delays & next station", "🔴")


# ── Helper functions ──────────────────────────────────────────

def _render_delay_badge(mins: int) -> str:
    if mins == 0:
        return '<span style="color:#00E676;font-weight:700">✅ On Time</span>'
    elif mins > 0:
        return f'<span style="color:#FF5252;font-weight:700">⚠️ {mins} min late</span>'
    else:
        return f'<span style="color:#00E676;font-weight:700">✅ {abs(mins)} min early</span>'


def _render_station_timeline(stations: list):
    for stn in stations:
        name   = stn.get("stationName") or stn.get("name", "—")
        code   = stn.get("stationCode") or stn.get("code", "—")
        sched_arr = stn.get("scheduledArrival") or stn.get("arr", "—")
        sched_dep = stn.get("scheduledDeparture") or stn.get("dep", "—")
        act_arr   = stn.get("actualArrival") or stn.get("actualArr", "")
        act_dep   = stn.get("actualDeparture") or stn.get("actualDep", "")
        delay_m   = int(stn.get("delayInArrival") or stn.get("delay") or 0)
        halt      = stn.get("haltTime") or stn.get("halt", "")
        departed  = stn.get("hasDeparted") or stn.get("departed", False)
        is_current = stn.get("isCurrent", False)

        if is_current:
            dot_color = "#FF4B2B"
            bg = "background:linear-gradient(90deg,#FF4B2B11,transparent)"
            border = "border-left:3px solid #FF4B2B"
        elif departed:
            dot_color = "#00E676"
            bg = ""
            border = "border-left:3px solid #00E67666"
        else:
            dot_color = "#2A2D3E"
            bg = ""
            border = "border-left:3px solid #2A2D3E"

        delay_tag = ""
        if delay_m > 0:
            delay_tag = f'<span style="color:#FF5252;font-size:.7rem;margin-left:6px">+{delay_m}m</span>'
        elif delay_m < 0:
            delay_tag = f'<span style="color:#00E676;font-size:.7rem;margin-left:6px">{delay_m}m</span>'

        current_tag = '<span style="background:#FF4B2B;color:white;border-radius:4px;padding:1px 6px;font-size:.68rem;margin-left:8px">CURRENT</span>' if is_current else ""

        st.markdown(f"""
        <div style="display:flex;align-items:flex-start;gap:12px;padding:10px 14px;
                    margin-bottom:6px;border-radius:8px;{bg};{border}">
            <div style="width:11px;height:11px;border-radius:50%;background:{dot_color};
                        flex-shrink:0;margin-top:5px"></div>
            <div style="flex:1;min-width:0">
                <div style="font-weight:600;font-size:.9rem">
                    {name} <span style="color:#8892A4;font-size:.75rem">({code})</span>
                    {current_tag}
                </div>
                <div style="display:flex;gap:20px;margin-top:4px;flex-wrap:wrap;font-size:.78rem;color:#8892A4">
                    <span>Arr: <b style="color:#FAFAFA">{sched_arr}</b>
                        {f' → <b style="color:#FF4B2B">{act_arr}</b>' if act_arr else ''}
                        {delay_tag}
                    </span>
                    <span>Dep: <b style="color:#FAFAFA">{sched_dep}</b>
                        {f' → <b style="color:#FF4B2B">{act_dep}</b>' if act_dep else ''}
                    </span>
                    {f'<span>Halt: <b style="color:#FAFAFA">{halt}</b></span>' if halt else ''}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)


def _render_live_result(data: dict):
    if not data:
        st.warning("No live data available. Train may not have started or data is unavailable.")
        return

    train_no   = data.get("trainNo") or data.get("trainNumber", "—")
    train_name = data.get("trainName", "—")
    current_stn = data.get("currentStation") or data.get("currentStationName", "—")
    next_stn    = data.get("nextStation") or data.get("nextStationName", "—")
    delay       = int(data.get("delayInMinutes") or data.get("delay") or 0)
    speed       = data.get("avgSpeed") or data.get("speed", "—")
    dist_travelled = data.get("distanceTravelled") or data.get("distance", "—")
    stations    = data.get("stationList") or data.get("stations", [])

    # ── Live info card ────────────────────────────────────────
    st.markdown(f"""
    <div class="ir-card">
        <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px">
            <div>
                <div style="font-size:1.15rem;font-weight:700">🚄 {train_name}</div>
                <div style="color:#8892A4;font-size:.8rem">#{train_no}</div>
            </div>
            <div style="display:flex;align-items:center;gap:6px">
                <div style="width:10px;height:10px;background:#FF4B2B;border-radius:50%;
                            animation:pulse 1s infinite"></div>
                <span style="color:#FF4B2B;font-weight:600;font-size:.88rem">LIVE</span>
            </div>
        </div>

        <div style="display:flex;gap:28px;margin-top:16px;flex-wrap:wrap">
            <div>
                <div style="font-size:.78rem;color:#8892A4">Current / Last Station</div>
                <div style="font-weight:700;font-size:1rem;margin-top:2px">{current_stn}</div>
            </div>
            <div>
                <div style="font-size:.78rem;color:#8892A4">Next Station</div>
                <div style="font-weight:700;font-size:1rem;margin-top:2px;color:#FF4B2B">{next_stn}</div>
            </div>
            <div>
                <div style="font-size:.78rem;color:#8892A4">Delay</div>
                <div style="margin-top:4px">{_render_delay_badge(delay)}</div>
            </div>
        </div>

        <div style="display:flex;gap:28px;margin-top:14px;flex-wrap:wrap">
            <div class="stat-card" style="flex:1;min-width:100px">
                <div class="stat-value">{speed}</div>
                <div class="stat-label">Avg Speed (km/h)</div>
            </div>
            <div class="stat-card" style="flex:1;min-width:100px">
                <div class="stat-value">{dist_travelled}</div>
                <div class="stat-label">Distance (km)</div>
            </div>
            <div class="stat-card" style="flex:1;min-width:100px">
                <div class="stat-value">{abs(delay)}</div>
                <div class="stat-label">{'Min Late' if delay > 0 else 'Min Early' if delay < 0 else 'On Time'}</div>
            </div>
        </div>
    </div>
    <style>
    @keyframes pulse {{ 0%,100%{{opacity:1}} 50%{{opacity:.3}} }}
    </style>
    """, unsafe_allow_html=True)

    # ── Station list timeline ──────────────────────────────────
    if stations:
        st.markdown("### 📍 Station-wise Running Status")
        _render_station_timeline(stations)


def _render_demo_live(tn: str):
    st.markdown("### Live Running Status (Demo Mode)")
    demo_stations = [
        {"stationName": "NEW DELHI", "stationCode": "NDLS", "scheduledArrival": "—",
         "scheduledDeparture": "14:05", "actualDeparture": "14:09", "delay": 4,
         "hasDeparted": True},
        {"stationName": "MATHURA JN", "stationCode": "MTJ", "scheduledArrival": "15:55",
         "scheduledDeparture": "16:00", "actualArrival": "16:03", "delay": 8,
         "hasDeparted": True},
        {"stationName": "AGRA CANTT", "stationCode": "AGC", "scheduledArrival": "16:35",
         "scheduledDeparture": "16:40", "actualArrival": "16:50", "delay": 15,
         "hasDeparted": False, "isCurrent": True},
        {"stationName": "GWALIOR", "stationCode": "GWL", "scheduledArrival": "17:55",
         "scheduledDeparture": "18:00", "delay": 0, "hasDeparted": False},
        {"stationName": "JHANSI JN", "stationCode": "JHS", "scheduledArrival": "19:15",
         "scheduledDeparture": "19:25", "delay": 0, "hasDeparted": False},
        {"stationName": "HOWRAH JN", "stationCode": "HWH", "scheduledArrival": "10:00",
         "scheduledDeparture": "—", "delay": 0, "hasDeparted": False},
    ]
    demo_data = {
        "trainNo": tn, "trainName": "Howrah Rajdhani Express",
        "currentStation": "AGRA CANTT (AGC)", "nextStation": "GWALIOR (GWL)",
        "delayInMinutes": 15, "avgSpeed": 87, "distanceTravelled": 204,
        "stationList": demo_stations,
    }
    _render_live_result(demo_data)


# ── Auto-refresh toggle ────────────────────────────────────────
col_form, col_refresh = st.columns([3, 1])
with col_refresh:
    auto_refresh = st.toggle("🔄 Auto Refresh (60s)", value=False)

# ── Form ──────────────────────────────────────────────────────
with st.form("live_form"):
    c1, c2 = st.columns(2)
    with c1:
        train_no = st.text_input(
            "🚄 Train Number *",
            placeholder="e.g. 12301",
            help="Enter the 5-digit train number"
        )
    with c2:
        start_day = st.selectbox(
            "🗓 Train Started On",
            options=[0, 1, 2],
            format_func=lambda x: ["Today", "Yesterday", "Day Before Yesterday"][x],
            help="When did the train start its journey from the origin station?"
        )
    submitted = st.form_submit_button("📡 Get Live Status", use_container_width=True)

if auto_refresh:
    import time
    st.markdown("""
    <div class="ir-alert-info">
        🔄 Auto-refresh is ON — page will refresh every 60 seconds.
    </div>
    """, unsafe_allow_html=True)
    time.sleep(60)
    st.rerun()

if submitted:
    tn = train_no.strip()
    if not tn:
        st.error("⚠️ Please enter a train number.")
        st.stop()

    api_key = st.session_state.get("rapidapi_key", "")
    if not api_key:
        demo_mode_notice()
        _render_demo_live(tn)
    else:
        with st.spinner(f"📡 Fetching live status for train #{tn}..."):
            result = get_live_train_status(tn, start_day)

        if is_logged_in():
            log_search(st.session_state.user_id, "live_status", tn)

        if result["ok"]:
            data = result["data"].get("data", result["data"])
            _render_live_result(data)
        else:
            error_card(result["error"])
