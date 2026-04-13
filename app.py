"""
🚆 Indian Railways Live Tracker & Planner
Main entry point — Home Dashboard
"""

import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from utils.session import init_session
from utils.ui import inject_css, sidebar_nav, stat_row, page_header
from datetime import date

st.set_page_config(
    page_title="Indian Railways Tracker",
    page_icon="🚆",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": "Indian Railways Live Tracker — Powered by IRCTC RapidAPI",
    },
)

init_session()
sidebar_nav()
inject_css()

# ── Hero ───────────────────────────────────────────────────────
st.markdown("""
<div style="background:linear-gradient(135deg,#FF4B2B22 0%,#1C1F2E 60%,#0F1117 100%);
            border:1px solid #FF4B2B44;border-radius:20px;padding:40px 36px;margin-bottom:28px">
    <div style="display:flex;align-items:center;gap:18px;flex-wrap:wrap">
        <div style="font-size:3.5rem">🚆</div>
        <div>
            <div style="font-size:2rem;font-weight:800;color:#FAFAFA;line-height:1.2">
                Indian Railways<br>
                <span style="color:#FF4B2B">Live Tracker</span>
            </div>
            <div style="color:#8892A4;margin-top:8px;font-size:.9rem">
                Real-time train tracking · PNR status · Seat availability · Schedules
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Quick stats ────────────────────────────────────────────────
stat_row([
    {"value": "13,000+", "label": "Daily Trains"},
    {"value": "8,000+", "label": "Stations"},
    {"value": "23M+",    "label": "Daily Passengers"},
    {"value": "67,000+", "label": "Route KM"},
])

st.markdown("<br>", unsafe_allow_html=True)

# ── Quick navigation tiles ─────────────────────────────────────
st.markdown('<div class="section-header">🧭 Quick Access</div>', unsafe_allow_html=True)
st.markdown('<div class="section-sub">Jump directly to any feature</div>', unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)

TILES = [
    ("🔍", "Train Search", "Search by train number or name", "pages/1_🔍_Train_Search.py"),
    ("🚉", "Trains Between Stations", "Find all trains on a route", "pages/2_🚉_Between_Stations.py"),
    ("💺", "Seat Availability", "Check seat availability by class & quota", "pages/3_💺_Seat_Availability.py"),
    ("📋", "PNR Status", "Track your booking status", "pages/4_📋_PNR_Status.py"),
    ("🔴", "Live Train Status", "Real-time train running position", "pages/5_🔴_Live_Status.py"),
    ("📅", "Train Schedule", "Full station-wise timetable", "pages/6_📅_Schedule.py"),
]

for i, (icon, title, desc, page) in enumerate(TILES):
    col = [c1, c2, c3][i % 3]
    with col:
        st.markdown(f"""
        <div class="ir-card" style="cursor:pointer;text-align:center;padding:24px 16px">
            <div style="font-size:2.2rem">{icon}</div>
            <div style="font-weight:700;margin:8px 0 4px;font-size:.95rem">{title}</div>
            <div style="color:#8892A4;font-size:.78rem">{desc}</div>
        </div>
        """, unsafe_allow_html=True)
        st.page_link(page, label=f"Open {title}", use_container_width=True)

# ── Today's info ───────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown(f"""
<div class="ir-alert-info">
    📅 Today: <b>{date.today().strftime("%A, %d %B %Y")}</b>  — 
    Indian Railways runs <b>~13,000 passenger trains</b> daily connecting <b>8,000+ stations</b> across India.
</div>
""", unsafe_allow_html=True)

# ── Getting started ────────────────────────────────────────────
with st.expander("🚀 Getting Started — How to use this app", expanded=False):
    st.markdown("""
    ### Setup in 3 Steps

    **Step 1 — Get a FREE RapidAPI Key**
    1. Go to [rapidapi.com](https://rapidapi.com)
    2. Sign up for a free account
    3. Search for **"IRCTC"** and subscribe to the **IRCTC1** API (free tier available)
    4. Copy your API key from the dashboard

    **Step 2 — Configure the App**
    - Open ⚙️ **Settings** from the sidebar
    - Paste your RapidAPI key and save
    - Register / Login to enable search history & favourites

    **Step 3 — Start Exploring!**
    | Feature | What you can do |
    |---|---|
    | 🔍 Train Search | Search any train by number or name |
    | 🚉 Between Stations | Find all trains between source & destination |
    | 💺 Seat Availability | Check availability for specific class, quota & date |
    | 📋 PNR Status | Get your booking & passenger status |
    | 🔴 Live Status | Real-time train location & delays |
    | 📅 Schedule | Full timetable with all stops |

    ---
    **Data Source:** [IRCTC1 API via RapidAPI](https://rapidapi.com/IRCTCAPI/api/irctc1)
    — Official IRCTC data, updated in real-time.
    """)

# ── Class guide ────────────────────────────────────────────────
with st.expander("🎫 Train Class Guide", expanded=False):
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("""
        | Code | Class |
        |---|---|
        | **1A** | First AC (4-berth cabins) |
        | **2A** | Second AC (6-berth cabins) |
        | **3A** | Third AC (8-berth open) |
        | **SL** | Sleeper Class |
        | **CC** | AC Chair Car |
        """)
    with col_b:
        st.markdown("""
        | Code | Class |
        |---|---|
        | **2S** | Second Sitting |
        | **FC** | First Class (non-AC) |
        | **EC** | Executive Chair Car |
        | **3E** | Third AC Economy |
        | **GN** | General/Unreserved |
        """)

# ── Quota guide ───────────────────────────────────────────────
with st.expander("🎟️ Reservation Quota Guide", expanded=False):
    st.markdown("""
    | Quota | Description |
    |---|---|
    | **GN** | General (default) |
    | **TQ** | Tatkal (last-minute booking, higher fare) |
    | **PT** | Premium Tatkal |
    | **LD** | Ladies quota |
    | **HP** | Physically Handicapped |
    | **SS** | Senior Citizen (60+ years, discounted) |
    | **YU** | Youth quota |
    """)
