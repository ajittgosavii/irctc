"""
⚠️ Cancelled Trains & Alerts
"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.session import init_session
from utils.ui import inject_css, sidebar_nav, page_header, error_card
from utils.api_client import get_cancelled_trains, format_date_for_api, demo_mode_notice
from datetime import date

st.set_page_config(page_title="Alerts | IR Tracker", page_icon="⚠️", layout="wide")
init_session()
sidebar_nav()
inject_css()
page_header("Cancelled Trains & Alerts", "Check cancelled, diverted and rescheduled trains", "⚠️")


# ── Helper functions ──────────────────────────────────────────

def _render_cancel_card(t: dict):
    cancel_type = t.get("cancelType") or t.get("type", "Cancelled")
    color = "#FF5252" if "Full" in cancel_type else "#FFD740"
    reason = t.get("reason") or t.get("remarkReason", "—")

    st.markdown(f"""
    <div class="ir-card" style="border-left:4px solid {color}">
        <div style="display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px">
            <div>
                <div style="font-weight:700">{t.get('trainName','—')}</div>
                <div style="color:#8892A4;font-size:.8rem">
                    #{t.get('trainNo','—')} &nbsp;|&nbsp;
                    {t.get('fromStation','—')} → {t.get('toStation','—')}
                </div>
            </div>
            <span style="background:{color}22;color:{color};border:1px solid {color};
                         border-radius:6px;padding:3px 10px;font-size:.78rem;font-weight:600">
                {cancel_type}
            </span>
        </div>
        <div style="margin-top:8px;font-size:.82rem;color:#8892A4">
            📝 Reason: {reason}
        </div>
    </div>
    """, unsafe_allow_html=True)


# ── Main page content ─────────────────────────────────────────

st.markdown("""
<div class="ir-alert-warn">
    ⚠️ Always verify cancellations on the official IRCTC portal or call <b>139</b> (Railway enquiry).
</div>
""", unsafe_allow_html=True)

with st.form("cancel_form"):
    check_date = st.date_input(
        "📅 Check Date",
        value=date.today(),
        min_value=date.today(),
        help="Check for cancellations on this date"
    )
    submitted = st.form_submit_button("🔍 Check Cancelled Trains", use_container_width=True)

if submitted:
    api_key = st.session_state.get("rapidapi_key", "")
    if not api_key:
        demo_mode_notice()
        st.markdown("### Cancelled Trains (Demo Mode)")
        demo_cancels = [
            {"trainNo": "12002", "trainName": "Bhopal Shatabdi Express", "fromStation": "NDLS",
             "toStation": "BPL", "cancelType": "Fully Cancelled", "reason": "Maintenance work"},
            {"trainNo": "15119", "trainName": "Awadh Express", "fromStation": "MFP",
             "toStation": "CSTM", "cancelType": "Partially Cancelled", "reason": "Fog"},
        ]
        for t in demo_cancels:
            _render_cancel_card(t)
    else:
        date_str = format_date_for_api(check_date)
        with st.spinner("🔍 Fetching cancellation data..."):
            result = get_cancelled_trains(date_str)

        if result["ok"]:
            data = result["data"]
            trains = data.get("data", [])
            if not trains:
                st.success(f"✅ No cancelled trains found for {check_date.strftime('%d %b %Y')}.")
            else:
                st.warning(f"⚠️ **{len(trains)}** cancelled/affected train(s) on {check_date.strftime('%d %b %Y')}")
                for t in trains:
                    _render_cancel_card(t)
        else:
            error_card(result["error"])


# ── Emergency numbers ─────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
with st.expander("📞 Indian Railways Helpline Numbers"):
    st.markdown("""
    | Service | Number |
    |---|---|
    | **Railway Enquiry** | 139 |
    | **Booking Enquiry** | 139 |
    | **Security Helpline** | 182 |
    | **Medical Emergency** | 138 |
    | **Women Helpline** | 182 |
    | **IRCTC Customer Care** | 0755-6610661 |
    """)
