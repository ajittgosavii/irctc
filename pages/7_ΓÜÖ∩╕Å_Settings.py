"""
⚙️ Settings — API Key, Login/Register, History, Favourites
"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.session import (
    init_session, is_logged_in, logout,
    register_user, login_user, save_api_key,
    get_search_history, get_favourites, remove_favourite,
)
from utils.ui import inject_css, sidebar_nav, page_header

st.set_page_config(page_title="Settings | IR Tracker", page_icon="⚙️", layout="wide")
init_session()
sidebar_nav()
inject_css()
page_header("Settings", "Configure API key, account & preferences", "⚙️")

# ─────────────────────────────────────────────────────────────
# TAB LAYOUT
# ─────────────────────────────────────────────────────────────
tab_api, tab_account, tab_history, tab_favs, tab_help = st.tabs([
    "🔑 API Key", "👤 Account", "🕐 History", "⭐ Favourites", "❓ Help"
])


# ── TAB: API Key ──────────────────────────────────────────────
with tab_api:
    st.markdown("### 🔑 RapidAPI Key Configuration")
    st.markdown("""
    <div class="ir-alert-info">
        This app uses the <b>IRCTC1 API</b> on RapidAPI for all live Indian Railways data.
        A FREE tier is available with 100 requests/day.
    </div>
    """, unsafe_allow_html=True)

    current_key = st.session_state.get("rapidapi_key", "")
    masked = f"{'•' * (len(current_key) - 4)}{current_key[-4:]}" if len(current_key) > 4 else ""

    if current_key:
        st.success(f"✅ API Key configured: `{masked}`")

    new_key = st.text_input(
        "Enter RapidAPI Key",
        type="password",
        placeholder="Paste your RapidAPI key here",
        help="Get a free key at rapidapi.com"
    )

    if st.button("💾 Save API Key", use_container_width=True):
        if new_key.strip():
            st.session_state["rapidapi_key"] = new_key.strip()
            if is_logged_in():
                save_api_key(st.session_state.user_id, new_key.strip())
            st.success("✅ API Key saved successfully!")
            st.rerun()
        else:
            st.error("Please enter a valid API key.")

    if current_key and st.button("🗑 Clear API Key"):
        st.session_state["rapidapi_key"] = ""
        if is_logged_in():
            save_api_key(st.session_state.user_id, "")
        st.success("API key cleared.")
        st.rerun()

    st.markdown("---")
    st.markdown("### 📖 How to Get Your Free API Key")
    with st.expander("Step-by-step instructions", expanded=True):
        st.markdown("""
        1. **Visit** [rapidapi.com](https://rapidapi.com) and create a free account
        2. **Search** for `IRCTC1` in the API marketplace
        3. **Subscribe** to the free tier (Basic — 100 requests/day)
        4. Go to the **"Endpoints"** tab and copy your `X-RapidAPI-Key` from the code examples
        5. **Paste** it above and click Save

        **Free tier limits:**
        - 100 API requests per day
        - All endpoints available
        - No credit card required

        **Upgrade options:**
        - Basic Pro: 500 req/day
        - Ultra: 5,000 req/day
        """)


# ── TAB: Account ──────────────────────────────────────────────
with tab_account:
    if is_logged_in():
        st.markdown(f"### 👤 Welcome, **{st.session_state.username}**!")
        st.success("You are logged in.")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div class="ir-card">
                <div style="font-size:.8rem;color:#8892A4">Username</div>
                <div style="font-weight:700;margin-top:4px">{st.session_state.username}</div>
                <div style="font-size:.8rem;color:#8892A4;margin-top:10px">User ID</div>
                <div style="font-size:.75rem;color:#8892A4">{st.session_state.user_id[:8]}...</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            history = get_search_history(st.session_state.user_id, limit=100)
            st.markdown(f"""
            <div class="ir-card">
                <div style="font-size:.8rem;color:#8892A4">Total Searches</div>
                <div class="stat-value">{len(history)}</div>
                <div style="font-size:.8rem;color:#8892A4;margin-top:10px">Favourites</div>
                <div class="stat-value">{len(get_favourites(st.session_state.user_id))}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚪 Logout", use_container_width=True, type="primary"):
            logout()
    else:
        login_tab, register_tab = st.tabs(["🔐 Login", "📝 Register"])

        with login_tab:
            st.markdown("### 🔐 Login")
            with st.form("login_form"):
                username = st.text_input("Username", placeholder="your_username")
                password = st.text_input("Password", type="password", placeholder="••••••••")
                login_submitted = st.form_submit_button("Login", use_container_width=True)

            if login_submitted:
                if not username or not password:
                    st.error("Please enter username and password.")
                else:
                    ok, user_data = login_user(username, password)
                    if ok:
                        st.session_state["logged_in"] = True
                        st.session_state["user_id"]   = user_data["user_id"]
                        st.session_state["username"]  = user_data["username"]
                        if user_data.get("api_key"):
                            st.session_state["rapidapi_key"] = user_data["api_key"]
                        st.success(f"✅ Welcome back, **{username}**!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid username or password.")

        with register_tab:
            st.markdown("### 📝 Create Account")
            with st.form("register_form"):
                new_username = st.text_input("Choose Username", placeholder="e.g. ajit_singh")
                new_password = st.text_input("Choose Password", type="password",
                                             help="Minimum 6 characters")
                confirm_pw   = st.text_input("Confirm Password", type="password")
                reg_submitted = st.form_submit_button("Register", use_container_width=True)

            if reg_submitted:
                if not new_username or not new_password:
                    st.error("Please fill in all fields.")
                elif len(new_password) < 6:
                    st.error("Password must be at least 6 characters.")
                elif new_password != confirm_pw:
                    st.error("Passwords do not match.")
                else:
                    ok, result = register_user(new_username, new_password)
                    if ok:
                        st.success(f"✅ Account created! Please login.")
                    else:
                        st.error(f"❌ {result}")


# ── TAB: History ──────────────────────────────────────────────
with tab_history:
    st.markdown("### 🕐 Recent Search History")
    if not is_logged_in():
        st.info("🔐 Login to view your search history.")
    else:
        history = get_search_history(st.session_state.user_id, limit=50)
        if not history:
            st.markdown("""
            <div class="ir-card" style="text-align:center;padding:30px">
                <div style="font-size:2rem">🔍</div>
                <div style="color:#8892A4;margin-top:8px">No searches yet. Start exploring!</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            type_icons = {
                "train_search": "🔍",
                "between_stations": "🚉",
                "seat_availability": "💺",
                "pnr_status": "📋",
                "live_status": "🔴",
                "schedule": "📅",
            }
            for h in history:
                icon = type_icons.get(h["type"], "🔎")
                label = h["type"].replace("_", " ").title()
                ts = h["at"][:16].replace("T", " ")
                st.markdown(f"""
                <div style="display:flex;align-items:center;gap:12px;padding:8px 14px;
                            background:#1C1F2E;border-radius:8px;margin-bottom:6px">
                    <span style="font-size:1.1rem">{icon}</span>
                    <div style="flex:1">
                        <div style="font-size:.85rem;font-weight:600">{h['query']}</div>
                        <div style="font-size:.72rem;color:#8892A4">{label} &nbsp;|&nbsp; {ts}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)


# ── TAB: Favourites ───────────────────────────────────────────
with tab_favs:
    st.markdown("### ⭐ Saved Favourites")
    if not is_logged_in():
        st.info("🔐 Login to view and manage your favourites.")
    else:
        favs = get_favourites(st.session_state.user_id)
        if not favs:
            st.markdown("""
            <div class="ir-card" style="text-align:center;padding:30px">
                <div style="font-size:2rem">⭐</div>
                <div style="color:#8892A4;margin-top:8px">
                    No favourites saved yet. You can save trains and routes from search results.
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            for fav in favs:
                c1, c2 = st.columns([5, 1])
                with c1:
                    data = fav["data"]
                    st.markdown(f"""
                    <div class="ir-card" style="margin-bottom:8px">
                        <div style="font-weight:600">{data.get('trainName') or data.get('name','—')}</div>
                        <div style="font-size:.78rem;color:#8892A4">
                            {fav['type']} &nbsp;|&nbsp; Saved: {fav['at'][:10]}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                with c2:
                    if st.button("🗑", key=f"del_{fav['id']}"):
                        remove_favourite(fav["id"])
                        st.rerun()


# ── TAB: Help ─────────────────────────────────────────────────
with tab_help:
    st.markdown("### ❓ Help & FAQ")
    with st.expander("What API is used?"):
        st.markdown("""
        This app uses the **IRCTC1 API** available on [RapidAPI](https://rapidapi.com/IRCTCAPI/api/irctc1).
        It provides real-time data from Indian Railways including train schedules, live status, PNR and seat availability.
        """)
    with st.expander("Is this official IRCTC?"):
        st.markdown("""
        This is an **unofficial third-party tracker** that uses the IRCTC data API.
        For official bookings, visit [irctc.co.in](https://www.irctc.co.in).
        """)
    with st.expander("How accurate is live train status?"):
        st.markdown("""
        Live train status data is sourced from the National Train Enquiry System (NTES) via the IRCTC API.
        Data is typically updated every 5–15 minutes. Delays may occasionally differ from actual running status.
        """)
    with st.expander("Can I book tickets from this app?"):
        st.markdown("""
        No. This app is a **tracking and planning tool only**. 
        To book tickets, use the official [IRCTC website](https://www.irctc.co.in) or 
        apps like IRCTC Rail Connect, ConfirmTkt, ixigo, or MakeMyTrip.
        """)
    with st.expander("Data accuracy & disclaimer"):
        st.markdown("""
        - Data is fetched in real-time from IRCTC API via RapidAPI
        - All times are in **Indian Standard Time (IST)**
        - For critical travel decisions, always verify on the official IRCTC platform
        - This app stores your search history locally in an SQLite database on the Streamlit Cloud server
        """)
