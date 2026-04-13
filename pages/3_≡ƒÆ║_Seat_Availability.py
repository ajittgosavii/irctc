"""
💺 Seat Availability — Check seat availability by class, quota and date
"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.session import init_session, is_logged_in, log_search
from utils.ui import inject_css, sidebar_nav, page_header, no_results_card, error_card, availability_badge
from utils.api_client import (
    check_seat_availability, format_date_for_api, demo_mode_notice,
    CLASS_TYPES, QUOTA_TYPES
)
from datetime import date, timedelta

st.set_page_config(page_title="Seat Availability | IR Tracker", page_icon="💺", layout="wide")
init_session()
sidebar_nav()
inject_css()
page_header("Seat Availability", "Check real-time seat availability by class, quota & date range", "💺")

# ── Form ──────────────────────────────────────────────────────
with st.form("avail_form"):
    c1, c2 = st.columns(2)
    with c1:
        train_no = st.text_input("🚄 Train Number *", placeholder="e.g. 12301")
        from_code = st.text_input("🟢 From Station Code *", placeholder="e.g. NDLS")
        class_type = st.selectbox(
            "🎫 Class *",
            options=list(CLASS_TYPES.keys()),
            format_func=lambda x: f"{x} — {CLASS_TYPES[x]}",
        )
    with c2:
        to_code = st.text_input("🔴 To Station Code *", placeholder="e.g. HWH")
        quota = st.selectbox(
            "📌 Quota *",
            options=list(QUOTA_TYPES.keys()),
            format_func=lambda x: f"{x} — {QUOTA_TYPES[x]}",
        )
        check_multiple = st.checkbox(
            "Check next 5 dates automatically",
            value=True,
            help="Shows availability for the chosen date + next 4 days"
        )

    journey_date = st.date_input(
        "📅 Journey Date *",
        value=date.today() + timedelta(days=1),
        min_value=date.today(),
        max_value=date.today() + timedelta(days=120),
    )

    submitted = st.form_submit_button("🔍 Check Availability", use_container_width=True)


if submitted:
    tn  = train_no.strip()
    fc  = from_code.strip().upper()
    tc  = to_code.strip().upper()

    if not tn or not fc or not tc:
        st.error("⚠️ Train number, From and To station codes are required.")
        st.stop()

    api_key = st.session_state.get("rapidapi_key", "")

    if not api_key:
        demo_mode_notice()
        # Demo availability
        st.markdown("### Sample Availability (Demo Mode)")
        _render_demo_availability(tn, fc, tc, class_type, quota, journey_date)
    else:
        dates_to_check = [journey_date + timedelta(days=i) for i in range(5)] if check_multiple else [journey_date]
        results = []

        with st.spinner("⏳ Fetching seat availability..."):
            for d in dates_to_check:
                date_str = format_date_for_api(d)
                res = check_seat_availability(tn, fc, tc, class_type, quota, date_str)
                results.append({"date": d, "result": res})

        if is_logged_in():
            log_search(
                st.session_state.user_id,
                "seat_availability",
                f"{tn} {fc}→{tc} {class_type}/{quota}"
            )

        # ── Summary header ────────────────────────────────────
        st.markdown(f"""
        <div class="ir-card" style="margin-bottom:16px">
            <div style="font-size:.9rem;color:#8892A4">Availability Check Results</div>
            <div style="font-size:1.1rem;font-weight:700;margin-top:4px">
                Train #{tn} &nbsp;|&nbsp; {fc} → {tc} &nbsp;|&nbsp;
                <span class="train-badge">{class_type}</span>
                &nbsp;
                <span style="background:#2A2D3E;border-radius:14px;padding:3px 10px;font-size:.78rem">{quota}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        any_ok = False
        for item in results:
            d = item["date"]
            res = item["result"]

            if res["ok"]:
                any_ok = True
                data = res["data"]
                avail_list = data.get("data", [])
                if not avail_list:
                    avail_list = [data] if isinstance(data, dict) else []

                for entry in avail_list:
                    status = (
                        entry.get("availabilityStatus")
                        or entry.get("status")
                        or entry.get("availability")
                        or "—"
                    )
                    fare = entry.get("fare") or entry.get("totalFare") or "—"
                    _render_avail_row(d, status, class_type, fare)
            else:
                st.markdown(f"""
                <div style="display:flex;align-items:center;gap:12px;padding:8px 14px;
                            background:#1C1F2E;border-radius:8px;margin-bottom:8px">
                    <span style="min-width:100px;font-weight:600">{d.strftime('%d %b %Y')}</span>
                    <span style="color:#8892A4;font-size:.83rem">{res['error']}</span>
                </div>
                """, unsafe_allow_html=True)

        if not any_ok:
            error_card("Could not fetch availability. Please verify the train number and station codes.")


def _render_avail_row(d, status: str, cls: str, fare):
    s = str(status).upper()
    if "AVL" in s:
        color, emoji, label = "#00E676", "🟢", "AVAILABLE"
    elif "WL" in s:
        color, emoji, label = "#FFD740", "🟡", "WAITLIST"
    elif "RAC" in s:
        color, emoji, label = "#FF9100", "🟠", "RAC"
    elif "REGRET" in s or "NOT" in s:
        color, emoji, label = "#FF5252", "🔴", "REGRET"
    else:
        color, emoji, label = "#8892A4", "⚪", "UNKNOWN"

    fare_str = f"₹{fare}" if fare not in ("—", None, "") else "—"

    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:16px;padding:12px 16px;
                background:#1C1F2E;border:1px solid {color}44;border-radius:10px;
                margin-bottom:8px;flex-wrap:wrap">
        <div style="min-width:105px">
            <div style="font-weight:700;font-size:.95rem">{d.strftime('%d %b %Y')}</div>
            <div style="font-size:.72rem;color:#8892A4">{d.strftime('%A')}</div>
        </div>
        <div style="flex:1;min-width:160px">
            <div style="color:{color};font-weight:700;font-size:1rem">{emoji} {status}</div>
            <div style="font-size:.72rem;color:#8892A4">{label}</div>
        </div>
        <div style="text-align:right">
            <div style="font-size:.9rem;font-weight:600;color:#29B6F6">{fare_str}</div>
            <div style="font-size:.72rem;color:#8892A4">Fare ({cls})</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def _render_demo_availability(tn, fc, tc, cls, quota, start_date):
    demo_statuses = [
        ("AVL 42", "₹2,045"), ("AVL 18", "₹2,045"),
        ("RAC 4", "₹2,045"), ("WL 11", "₹2,045"), ("WL 23", "₹2,045"),
    ]
    for i, (status, fare) in enumerate(demo_statuses):
        d = start_date + timedelta(days=i)
        _render_avail_row(d, status, cls, fare)

    st.markdown("""
    <div class="ir-alert-info" style="margin-top:12px">
        💡 Set your RapidAPI key in ⚙️ Settings to see real-time availability data.
    </div>
    """, unsafe_allow_html=True)


# ── Tips ──────────────────────────────────────────────────────
with st.expander("ℹ️ Availability Status Guide"):
    st.markdown("""
    | Status | Meaning |
    |---|---|
    | **AVL N** | N seats available for booking |
    | **WL N/M** | Waitlist — N is current WL, M is predicted WL |
    | **RAC N** | Reservation Against Cancellation — N is RAC number |
    | **REGRET** | Booking not available (WL full) |
    | **AVAILABLE** | Berths available |

    **Tatkal Quota (TQ):** Opens 1 day before departure at 10:00 AM.  
    **Premium Tatkal (PT):** Opens 1 day before departure at 11:00 AM (dynamic pricing).
    """)
